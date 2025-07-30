import librosa
import numpy as np
import scipy.signal
import scipy.ndimage
from math import sqrt
from pydub import AudioSegment
from pydub.playback import play

# Constants
SMOOTHING_SIZE_SEC = 2.5  # Smoothing filter size in seconds for similarity matrix denoising
N_FFT = 2**14  # FFT (Fast Fourier Transform) size
LINE_THRESHOLD = 0.12  # Threshold for detecting lines in the similarity matrix
MIN_LINES = 8  # Minimum number of lines required to find a highlight segment
NUM_ITERATIONS = 8  # Number of iterations for adjusting the threshold during line detection
OVERLAP_PERCENT_MARGIN = 0.2  # Allowed margin for overlap calculation between lines
HOP_LENGTH = 512  # Hop length for STFT (Short-Time Fourier Transform)


def create_chroma(input_file, n_fft=N_FFT):
    """
    Extracts chromagram, audio signal, sample rate, song length, tempo, and STFT-based energy
    from an audio file.

    Args:
        input_file (str): Path to the input audio file.
        n_fft (int): FFT size to be used for STFT calculation.

    Returns:
        tuple: Chromagram, audio signal (y), sample rate (sr), song length in seconds (song_length_sec),
               tempo (tempo), and STFT-based energy (stft_base).
    """
    y, sr = librosa.load(input_file, sr=11025)  # Load the audio file with a sample rate of 11025 Hz
    song_length_sec = len(y) / sr  # Calculate the total length of the song in seconds
    S = np.abs(librosa.stft(y, n_fft=n_fft))**2  # Compute the magnitude spectrogram of the STFT
    chroma = librosa.feature.chroma_stft(S=S, sr=sr)  # Extract chromagram from the STFT spectrogram
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)  # Estimate the tempo (BPM) of the audio
    stft = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP_LENGTH))  # STFT for energy calculation
    stft_base = np.mean(stft, axis=0)  # Calculate the mean of the STFT result for energy-based features
    return chroma, y, sr, song_length_sec, tempo, stft_base


class SimilarityMatrix:
    """
    Abstract base class for computing similarity matrices.
    """
    def __init__(self, chroma):
        """
        Initializes the SimilarityMatrix.

        Args:
            chroma (np.ndarray): The chromagram array.
        """
        self.chroma = chroma
        self.matrix = self.compute_similarity_matrix(chroma)

    def compute_similarity_matrix(self, chroma):
        """
        Abstract method to compute the similarity matrix. Must be implemented by subclasses.

        Args:
            chroma (np.ndarray): The chromagram array.

        Raises:
            NotImplementedError: Raised if this method is not implemented in a subclass.
        """
        raise NotImplementedError


class TimeTimeSimilarityMatrix(SimilarityMatrix):
    """
    Class for computing the Time-Time Similarity Matrix.
    """
    def compute_similarity_matrix(self, chroma):
        """
        Computes the time-time similarity matrix based on the chromagram.
        This matrix represents the similarity between each time point in the audio.

        Args:
            chroma (np.ndarray): The chromagram array.

        Returns:
            np.ndarray: The computed time-time similarity matrix.
        """
        x = np.expand_dims(chroma, 2)  # Add a new dimension to the chromagram
        y = np.swapaxes(np.expand_dims(chroma, 2), 1, 2)  # Add a new dimension and swap axes
        # Compute similarity using Euclidean distance (1 minus normalized distance)
        return 1 - (np.linalg.norm(x - y, axis=0) / sqrt(12))


class TimeLagSimilarityMatrix(SimilarityMatrix):
    """
    Class for computing and denoising the Time-Lag Similarity Matrix.
    """
    def compute_similarity_matrix(self, chroma):
        """
        Computes the time-lag similarity matrix based on the chromagram.
        This matrix represents the similarity between each time point and its corresponding lag.

        Args:
            chroma (np.ndarray): The chromagram array.

        Returns:
            np.ndarray: The computed time-lag similarity matrix.
        """
        n = chroma.shape[1]  # Number of time frames in the chromagram
        x = np.repeat(np.expand_dims(chroma, 2), n + 1, axis=2)
        y = np.tile(chroma, (1, n + 1)).reshape(12, n, n + 1)
        # Compute similarity using Euclidean distance (1 minus normalized distance)
        mat = 1 - (np.linalg.norm(x - y, axis=0) / sqrt(12))
        return np.rot90(mat, k=1)[:n, :n]  # Rotate the matrix by 90 degrees and return

    def denoise(self, time_time_matrix, smoothing_size):
        """
        Denoises the time-lag similarity matrix.

        Args:
            time_time_matrix (np.ndarray): The time-time similarity matrix.
            smoothing_size (int): The size of the smoothing filter.
        """
        n = self.matrix.shape[0]  # Size of the matrix
        h_window = np.ones((1, smoothing_size)) / smoothing_size  # Horizontal smoothing window
        v_window = np.ones((smoothing_size, 1)) / smoothing_size  # Vertical smoothing window

        h_avg = scipy.signal.convolve2d(self.matrix, h_window, mode="full")  # Horizontal convolution
        l_avg, r_avg = h_avg[:, :n], h_avg[:, smoothing_size - 1:]  # Left/right averages
        max_h = np.maximum(l_avg, r_avg)  # Maximum in horizontal direction

        v_avg = scipy.signal.convolve2d(self.matrix, v_window, mode="full")  # Vertical convolution
        d_avg = scipy.signal.convolve2d(time_time_matrix, h_window, mode="full")  # Convolution on time-time matrix

        ll, ur = np.zeros((n, n)), np.zeros((n, n))
        for x in range(n):
            for y in range(x):
                ll[y, x] = d_avg[x - y, x]
                ur[y, x] = d_avg[x - y, x + smoothing_size - 1]

        # Calculate neighborhood max and min
        nh_max = np.maximum.reduce([v_avg[:n, :], v_avg[smoothing_size - 1:, :], ll, ur])
        nh_min = np.minimum.reduce([v_avg[:n, :], v_avg[smoothing_size - 1:, :], ll, ur])

        # Compute noise suppression
        suppression = (max_h > nh_max) * nh_min + (max_h <= nh_max) * nh_max
        # Apply Gaussian filter for denoising
        denoised = scipy.ndimage.gaussian_filter1d(np.triu(self.matrix - suppression), smoothing_size, axis=1)
        self.matrix = np.maximum(denoised, 0)  # Keep all values non-negative
        self.matrix[:5, :] = 0  # Set the first 5 rows to 0 to exclude initial lag segments


class Line:
    """
    Represents a 'line' detected in the similarity matrix.
    Each line includes start time, end time, and lag information.
    """
    def __init__(self, start, end, lag):
        """
        Initializes a Line object.

        Args:
            start (int): The starting index of the line.
            end (int): The ending index of the line.
            lag (int): The lag value of the line.
        """
        self.start = start
        self.end = end
        self.lag = lag

    def __repr__(self):
        """
        Returns the string representation of the Line object.
        """
        return f"Line ({self.start} {self.end} {self.lag})"


def local_maxima_rows(matrix):
    """
    Finds the indices of rows that contain local maxima in the given matrix.
    This is used to identify strong repeating patterns at certain lag values.

    Args:
        matrix (np.ndarray): The time-lag similarity matrix.

    Returns:
        np.ndarray: An array of row indices corresponding to local maxima.
    """
    row_sums = np.sum(matrix, axis=1)  # Calculate the sum of each row
    norm_rows = row_sums / np.arange(len(row_sums), 0, -1)  # Normalize row sums by length
    return scipy.signal.argrelextrema(norm_rows, np.greater)[0]  # Return indices of local maxima


def detect_lines(matrix, rows, min_len):
    """
    Detects 'lines' representing repeating patterns in the similarity matrix.
    The threshold is iteratively adjusted to find the optimal set of lines.

    Args:
        matrix (np.ndarray): The time-lag similarity matrix.
        rows (np.ndarray): Indices of rows with local maxima.
        min_len (int): Minimum length of a line to be detected.

    Returns:
        list: A list of detected Line objects.
    """
    threshold = LINE_THRESHOLD  # Initial line detection threshold
    for _ in range(NUM_ITERATIONS):  # Iterate multiple times to adjust the threshold
        lines = []
        for row in rows:
            if row < min_len:  # Skip rows shorter than the minimum length
                continue
            start = None
            for col in range(row, matrix.shape[0]):
                if matrix[row, col] > threshold:  # Potential start of a line if above threshold
                    if start is None:
                        start = col
                else:
                    if start is not None and (col - start) > min_len:  # Add line if sufficiently long
                        lines.append(Line(start, col, row))
                    start = None
        if len(lines) >= MIN_LINES:  # If enough lines are detected, return them
            return lines
        threshold *= 0.97  # Decrease threshold if not enough lines are found
    return lines  # Return the final detected lines


def count_overlapping_lines(lines, margin, min_len):
    """
    Calculates overlap scores for detected lines.
    Greater overlap indicates a more significant repeating pattern.

    Args:
        lines (list): A list of Line objects.
        margin (float): The allowed margin when determining overlap.
        min_len (int): Minimum line length (used for lag difference calculation).

    Returns:
        dict: A dictionary with overlap scores for each Line object.
    """
    scores = {line: 0 for line in lines}  # Initialize scores for each line
    for l1 in lines:
        for l2 in lines:
            # Check for overlap based on start/end times or adjusted by lag
            if (l2.start < l1.start + margin and l2.end > l1.end - margin and abs(l2.lag - l1.lag) > min_len) or \
               ((l2.start - l2.lag) < (l1.start - l1.lag + margin) and \
                (l2.end - l2.lag) > (l1.end - l1.lag - margin) and \
                abs(l2.lag - l1.lag) > min_len):
                scores[l1] += 1
    return scores


def find_repeated_segment(chroma, sr, duration, tempo, min_bars=4):
    """
    Finds repeated musical segments in the audio.
    This is done by generating similarity matrices based on chromagrams,
    detecting lines, and calculating overlap scores.

    Args:
        chroma (np.ndarray): The chromagram array.
        sr (int): Sample rate.
        duration (float): Total duration of the song in seconds.
        tempo (float): Tempo of the song in BPM.
        min_bars (int): Minimum number of bars for a segment to be considered repeated.

    Returns:
        list or None: A list of (start_time, end_time, overlap_score) tuples, or None if not found.
    """
    chroma_sr = chroma.shape[1] / duration  # Chromagram's sample rate (frames/second)
    ttm = TimeTimeSimilarityMatrix(chroma)  # Create Time-Time Similarity Matrix
    tlm = TimeLagSimilarityMatrix(chroma)  # Create Time-Lag Similarity Matrix
    smoothing_size = int(SMOOTHING_SIZE_SEC * chroma_sr)  # Calculate smoothing filter size
    tlm.denoise(ttm.matrix, smoothing_size)  # Denoise the Time-Lag Similarity Matrix
    min_len = int(60 / tempo * 4 * min_bars * chroma_sr)  # Calculate minimum line length (in frames)
    rows = local_maxima_rows(tlm.matrix)  # Find rows with local maxima
    lines = detect_lines(tlm.matrix, rows, min_len)  # Detect lines
    if not lines:  # If no lines are detected, return None
        return None
    scores = count_overlapping_lines(lines, OVERLAP_PERCENT_MARGIN * min_len, min_len)  # Calculate line overlap scores
    # Sort and return (start_time, end_time, overlap_score) tuples
    return sorted([(l.start / chroma_sr, l.end / chroma_sr, s) for l, s in scores.items()], key=lambda x: x[1] - x[0], reverse=True)


def find_segments_energy(y, sr, target_duration, stft_base, step_num=32):
    """
    Finds segments in the audio with high energy levels.
    Extracts segments of a target duration and calculates their average energy.

    Args:
        y (np.ndarray): The audio signal.
        sr (int): Sample rate.
        target_duration (int): The target length of the segment in seconds.
        stft_base (np.ndarray): STFT-based energy features.
        step_num (int): Step size in multiples of HOP_LENGTH for segment extraction.

    Returns:
        list: A list of (start_time, end_time, average_energy) tuples.
    """
    segment_len = int(target_duration * sr)  # Number of samples for the target duration
    step_size = HOP_LENGTH * step_num  # Segment extraction step size (in samples)
    total_samples = len(y)  # Total number of audio samples
    duration = total_samples / sr  # Total duration of the song in seconds
    exclude_start, exclude_end = 0.03 * duration, 0.90 * duration  # Exclude start and end portions of the song
    segments = []
    for start in range(0, total_samples - segment_len + 1, step_size):
        end = start + segment_len
        start_sec, end_sec = start / sr, end / sr
        if start_sec < exclude_start or end_sec > exclude_end:  # Skip if within excluded regions
            continue
        idx_start, idx_end = start // HOP_LENGTH, end // HOP_LENGTH
        avg_energy = np.mean(stft_base[idx_start:idx_end])  # Calculate average energy of the segment
        segments.append((start_sec, end_sec, avg_energy))
    return segments


def remove_high_overlap_segments(data, a, b, threshold=0.75):
    """
    Removes segments from a list that have a high overlap with a given reference interval (a, b).
    This is primarily to prevent highlights from being concentrated in specific parts of the song
    (e.g., the very end).

    Args:
        data (list): A list of (start_time, end_time, ...) tuples.
        a (float): Start time of the reference interval.
        b (float): End time of the reference interval.
        threshold (float): Overlap ratio threshold.

    Returns:
        list: The list with highly overlapping segments removed.
    """
    result = []
    for seg in data:
        s, e = seg[:2]  # Start and end times of the segment
        seg_len, ref_len = e - s, b - a  # Segment length and reference interval length
        overlap = max(0, min(e, b) - max(s, a))  # Calculate overlap length
        # Remove segment if it overlaps too much with the reference interval, or is entirely contained
        if (seg_len >= ref_len and (overlap / seg_len) >= threshold) or (seg_len < ref_len and s >= a and e <= b):
            continue
        result.append(seg)
    return result


def extract_highlight(file_path, target_duration=15, threshold=0.75):
    """
    Extracts a highlight segment from the given audio file.
    It considers both repeating musical patterns and energy levels to find the optimal segment.

    Args:
        file_path (str): Path to the audio file.
        target_duration (int): Target length of the highlight segment in seconds.
        threshold (float): Overlap threshold for highlight determination.

    Returns:
        tuple: A tuple containing (highlight_start_time, highlight_end_time).
    """
    # Extract audio features
    chroma, y, sr, song_len, tempo, stft_base = create_chroma(file_path)
    min_bars = 4
    # Find repeated segments
    segment = find_repeated_segment(chroma, sr, song_len, tempo, min_bars)

    # If no repeated segments are found, reduce min_bars and try again
    while segment is None and min_bars > 2:
        min_bars *= 0.9
        segment = find_repeated_segment(chroma, sr, song_len, tempo, min_bars)

    total_duration = len(y) / sr
    if segment:
        # Remove segments with high overlap with the end of the song
        segment = remove_high_overlap_segments(segment, total_duration * 0.95, total_duration)

    # Extract energy-based segments and sort by energy score in descending order
    energy_segments = sorted(find_segments_energy(y, sr, target_duration, stft_base), key=lambda x: x[2], reverse=True)
    # Filter for repeated segments with an overlap score of 1 or more (highly similar)
    high_score = [(s, e) for s, e, score in segment if score >= 1] if segment else []

    # Iterate through high-energy segments (top 50%) and check for overlap with high-scoring repeated segments
    for seg in energy_segments[:int(len(energy_segments) * 0.5)]:
        for rep in high_score:
            o_start, o_end = max(seg[0], rep[0]), min(seg[1], rep[1])
            if max(0, o_end - o_start) / (seg[1] - seg[0]) >= threshold:
                return seg[0], seg[1]

    # If no match found above, iterate through slightly more high-energy segments (top 60%)
    # and check for overlap with any repeated segment (regardless of score)
    for seg in energy_segments[:int(len(energy_segments) * 0.6)]:
        for rep in segment or []:
            o_start, o_end = max(seg[0], rep[0]), min(seg[1], rep[1])
            if max(0, o_end - o_start) / (seg[1] - seg[0]) >= threshold:
                return seg[0], seg[1]

    # If no highlight is found based on the above conditions, return the segment with the highest energy
    return energy_segments[0][:2]


if __name__ == "__main__":
    # This block of code will only execute when the script is run directly
    file_path = "MP3s/Alessia Cara - How far I'll go.mp3"  # Path to the MP3 file to be analyzed
    start, end = extract_highlight(file_path)  # Extract the highlight segment
    print(f"Best Segment: {start:.2f} - {end:.2f} sec")  # Print the extracted segment (formatted to two decimal places)
    audio = AudioSegment.from_file(file_path, format="mp3")  # Load the audio file using pydub
    # Slice the audio to the extracted highlight segment, and add fade-in/fade-out effects
    clip = audio[int(start * 1000):int(end * 1000)].fade_in(1000).fade_out(1000)
    play(clip)  # Play the extracted highlight clip
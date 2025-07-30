# highlight_extractor

🎧 A Python package to extract highlight segments from songs using chroma repetition and energy analysis.

## Features

- Detects repeated musical segments via chroma similarity
- Combines with energy-based peak detection
- Filters out intro/outro noise and fade-outs
- Outputs the most suitable highlight section (default 15s)

## Installation

### From GitHub

```bash
pip install git+https://github.com/yourusername/highlight_extractor.git
```

## 🧱 Project Structure

```
highlight_extractor/
├── highlight_extractor/
│   ├── __init__.py
│   └── core.py
├── examples/
│   └── run_example.py
├── setup.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE
```

## ⚙️ Dependencies

- librosa
- numpy
- scipy
- pydub

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Author

- Developed by **Marohan Min**
- GitHub: [@marohan](https://github.com/marohan)

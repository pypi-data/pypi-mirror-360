from setuptools import setup, find_packages

setup(
    name='highlight_extractor',
    version='0.1.0',
    description='Audio highlight extractor using chroma and energy analysis',
    author='Marohan Min',
    author_email='fragantmaro@naver.com',
    url='https://github.com/marohan/highlight_extractor',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'librosa',
        'numpy',
        'scipy',
        'pydub'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)

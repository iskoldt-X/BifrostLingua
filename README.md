# Bifrost Lingua

Bifrost Lingua is a powerful tool designed to bridge languages through the automated processing of audio and text files. It segments text, aligns audio with text, translates text to English, segments audio into sentences, and combines audio files for bilingual learning purposes. This tool is particularly useful for language learners, educators, and researchers looking to enhance their learning materials with audio-visual aids. Currently only support Danish learning using English.

## Features

- Text segmentation and tokenization.
- Audio-text alignment using the aeneas tool.
- Automatic translation of text to English and generation of English audio.
- Segmentation of audio files into sentence-wise clips.
- Combination of English and original language audio clips for bilingual learning.

## Installation

Pull the Docker image from Docker Hub:

```bash
docker pull iskoldt/bifrostlingua:latest
```

## Usage

Run the Docker container:

```bash
docker run --rm -v $(pwd):/data iskoldt/bifrostlingua:latest /data/your_audio.mp3 /data/your_text.txt [optional arguments]
```

Replace `your_audio.mp3` and `your_text.txt` with the paths to your input audio and text files, respectively.

## Optional Arguments

You can customize the behavior of Bifrost Lingua by passing additional arguments:

- --max_words: Maximum number of words per segment (default: 12)
- --fixed_gap_length: Length of silence in milliseconds between sentences (default: 2000)
- --weight: Weight for the gap length calculation after Danish sentences (default: 1.2)
- --danish_repeats: Number of times Danish sentences are repeated (default: 2)

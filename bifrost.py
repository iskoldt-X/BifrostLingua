import argparse
import sys
import nltk
import json
import os
import subprocess
from nltk.tokenize import sent_tokenize, word_tokenize
from pydub import AudioSegment

def split_sentence_by_words(sentence, max_words):
    words = word_tokenize(sentence, language='danish')
    for i in range(0, len(words), max_words):
        yield ' '.join(words[i:i+max_words])

def segment_text(input_text_path, output_text_path, max_words):
    with open(input_text_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    sentences = sent_tokenize(text, language='danish')
    
    with open(output_text_path, 'w', encoding='utf-8') as out_file:
        for sentence in sentences:
            if len(word_tokenize(sentence, language='danish')) > max_words:
                for chunk in split_sentence_by_words(sentence, max_words):
                    out_file.write(chunk + '\n')
            else:
                out_file.write(sentence + '\n')


def run_aeneas(mp3_path, text_path, json_path):
    aeneas_command = [
        'python3', '-m', 'aeneas.tools.execute_task',
        mp3_path,
        text_path,
        "task_language=dan|os_task_file_format=json|is_text_type=plain",
        json_path
    ]
    subprocess.run(aeneas_command, check=True)

def segment_audio(json_file_path, audio_path, sentences_dir):
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    os.makedirs(sentences_dir, exist_ok=True)
    for i, fragment in enumerate(data['fragments'], start=1):
        start_time = fragment['begin']
        end_time = fragment['end']
        output_file = os.path.join(sentences_dir, f'sentence_{i:03}.mp3')
        duration = str(float(end_time) - float(start_time))
        cmd = ['ffmpeg', '-y', '-i', audio_path, '-ss', start_time, '-t', duration, '-acodec', 'copy', output_file]
        subprocess.run(cmd, check=True)

def translate_to_english_audio(sentence, output_filename):
    command = [
        '/app/trans', '-b', '-s', 'da', '-t', 'en',
        '-download-audio-as', output_filename,
        sentence
    ]
    subprocess.run(command, check=True)

def english_audio(output_text_path, english_sentences_dir):
    os.makedirs(english_sentences_dir, exist_ok=True)
    with open(output_text_path, 'r', encoding='utf-8') as file:
        sentences = file.readlines()
    for i, sentence in enumerate(sentences, start=1):
        output_filename = os.path.join(english_sentences_dir, f'sentence_{i:03}.mp3')
        translate_to_english_audio(sentence, output_filename)

def is_audio_file_valid(filepath):
    try:
        # Attempt to load the file with PyDub
        audio = AudioSegment.from_mp3(filepath)
        return True
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return False

def combine_audio_units(english_sentences_dir, danish_sentences_dir, fixed_gap_length=2000, weight=1.2, danish_repeats=2):
    if not os.path.exists(english_sentences_dir) or not os.path.exists(danish_sentences_dir):
        print("One or both of the specified directories do not exist.")
        return
    
    output_file_path = f'/data/combined_audio_weight_{str(weight)}_repeats{str(danish_repeats)}.mp3'  # Adjust your output path as needed
    combined = AudioSegment.empty()
    english_files = sorted([f for f in os.listdir(english_sentences_dir) if f.endswith('.mp3')],
                           key=lambda f: int(f.split('_')[-1].split('.')[0]))
    danish_files = sorted([f for f in os.listdir(danish_sentences_dir) if f.endswith('.mp3')],
                          key=lambda f: int(f.split('_')[-1].split('.')[0]))
    
    for english_file, danish_file in zip(english_files, danish_files):
        english_filepath = os.path.join(english_sentences_dir, english_file)
        danish_filepath = os.path.join(danish_sentences_dir, danish_file)
        
        if not is_audio_file_valid(english_filepath) or not is_audio_file_valid(danish_filepath):
            print(f"Skipping invalid files: {english_file}, {danish_file}")
            continue
        
        english_audio = AudioSegment.from_mp3(english_filepath)
        danish_audio = AudioSegment.from_mp3(danish_filepath)
        
        # Add English audio
        combined += english_audio + AudioSegment.silent(duration=fixed_gap_length)
        
        # Add Danish audio, repeats, and weighted gaps
        for _ in range(danish_repeats):
            combined += danish_audio + AudioSegment.silent(duration=int(len(danish_audio) * weight))
    
    # Export combined audio
    combined.export(output_file_path, format='mp3')
    print(f'Combined audio file created at: {output_file_path}')

def main(mp3_path, input_text_path, max_words, fixed_gap_length, weight, danish_repeats):
    output_text_path = '/data/segmented_text.txt'
    json_path = '/data/alignment.json'
    sentences_dir = '/data/danish_sentences'
    english_sentences_dir = '/data/english_sentences'

    # Segment text
    segment_text(input_text_path, output_text_path, max_words)

    # Run aeneas for audio-text alignment
    run_aeneas(mp3_path, output_text_path, json_path)

    # English audio
    english_audio(output_text_path, english_sentences_dir)

    # Segment audio
    segment_audio(json_path, mp3_path, sentences_dir)

    # Combine audio units
    combine_audio_units(english_sentences_dir, sentences_dir, fixed_gap_length, weight, danish_repeats)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('mp3_path', type=str, help='Path to the MP3 file')
    parser.add_argument('input_text_path', type=str, help='Path to the input text file')
    parser.add_argument('--max_words', type=int, default=12, help='Maximum words per sentence segment')
    parser.add_argument('--fixed_gap_length', type=int, default=2000, help='Fixed gap length in milliseconds between sentences')
    parser.add_argument('--weight', type=float, default=1.2, help='Weight for the gap length after Danish sentences')
    parser.add_argument('--danish_repeats', type=int, default=2, help='Number of times Danish sentences are repeated')

    args = parser.parse_args()

    main(args.mp3_path, args.input_text_path, args.max_words, args.fixed_gap_length, args.weight, args.danish_repeats)

import sys
import nltk
import json
import os
import subprocess
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment

def segment_text(input_text_path, output_text_path):
    with open(input_text_path, 'r', encoding='utf-8') as file:
        text = file.read()
    sentences = sent_tokenize(text, language='danish')
    with open(output_text_path, 'w', encoding='utf-8') as out_file:
        for sentence in sentences:
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
        './trans', '-b', '-s', 'da', '-t', 'en',
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

def combine_audio_units(english_sentences_dir, danish_sentences_dir, fixed_gap_length=2000, weight=1.2, danish_repeats=2):
    if not os.path.exists(english_sentences_dir) or not os.path.exists(danish_sentences_dir):
        print("One or both of the specified directories do not exist.")
        return
    output_file_path = f'combined_audio_{danish_repeats}_repeats_{weight}_weight.mp3'
    combined = AudioSegment.empty()
    english_files = sorted([f for f in os.listdir(english_sentences_dir) if f.endswith('.mp3')],
                           key=lambda f: int(f.split('_')[-1].split('.')[0]))
    danish_files = sorted([f for f in os.listdir(danish_sentences_dir) if f.endswith('.mp3')],
                          key=lambda f: int(f.split('_')[-1].split('.')[0]))
    
    for english_file, danish_file in zip(english_files, danish_files):
        english_audio = AudioSegment.from_mp3(os.path.join(english_sentences_dir, english_file))
        danish_audio = AudioSegment.from_mp3(os.path.join(danish_sentences_dir, danish_file))
        
        # Add English audio
        combined += english_audio
        
        # Fixed gap between English and Danish audio
        combined += AudioSegment.silent(duration=fixed_gap_length)
        
        # Add Danish audio, repeats, and weighted gaps
        for _ in range(danish_repeats):
            combined += danish_audio
            # Weighted gap after Danish audio, based on the length of the Danish audio
            weighted_gap_length = int(len(danish_audio) * weight)
            combined += AudioSegment.silent(duration=weighted_gap_length)
    
    # Export combined audio
    if not os.path.exists(os.path.dirname(output_file_path)):
        os.makedirs(os.path.dirname(output_file_path))
    combined.export(output_file_path, format='mp3')
    print(f'Combined audio file created at: {output_file_path}')

def main(mp3_path, input_text_path):
    output_text_path = '/data/segmented_text.txt'
    json_path = '/data/alignment.json'
    sentences_dir = '/data/danish_sentences'
    english_sentences_dir = '/data/english_sentences'

    # Segment text
    segment_text(input_text_path, output_text_path)

    # Run aeneas for audio-text alignment
    run_aeneas(mp3_path, output_text_path, json_path)

    # English audio
    english_audio(output_text_path, english_sentences_dir)

    # Segment audio
    segment_audio(json_path, mp3_path, sentences_dir)

    # Combine audio units
    combine_audio_units(english_sentences_dir, sentences_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bifrost.py <mp3_path> <input_text_path>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

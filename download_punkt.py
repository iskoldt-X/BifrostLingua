import os
import nltk

# Download the Punkt tokenizer models for nltk
try:
    nltk.download('punkt')
except Exception as e:
    print(f'Error downloading punkt: {e}')

# Download trans and make it executable
try:
    os.system('wget git.io/trans -O trans')
    os.system('chmod +x ./trans')
except Exception as e:
    print(f'Error setting up trans: {e}')

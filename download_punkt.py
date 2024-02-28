import os
import nltk

# Download the Punkt tokenizer models for nltk
try:
    nltk.download('punkt')
except Exception as e:
    print(f'Error downloading punkt: {e}')

# Download trans and make it executable
try:
    # Define the full path where trans will be saved
    trans_path = '/app/trans'
    
    # Download trans to the specified location
    os.system(f'wget git.io/trans -O {trans_path}')
    
    # Make trans executable
    os.system(f'chmod +x {trans_path}')
except Exception as e:
    print(f'Error setting up trans: {e}')
    

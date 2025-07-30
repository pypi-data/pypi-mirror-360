import re

def preprocess_text(text):  # ✅ rename this to match what's used in build_kg.py
    # Remove special characters, multiple spaces, and newlines
    text = re.sub(r'\s+', ' ', text)           # Remove extra spaces
    text = re.sub(r'\[[^\]]*\]', '', text)     # Remove [bracketed text]
    text = re.sub(r'[^a-zA-Z0-9., ]', '', text) # Remove special symbols
    return text.strip()

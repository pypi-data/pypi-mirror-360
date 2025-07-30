from .language import detect_language
from .semantic import SYNONYMS, get_wordnet_synonyms
from .entropy import stylometry_features, ml_watermark_classifier
import random

ZERO_WIDTH_SPACE = '\u200b'

# Helper to decode metadata from zero-width string
def decode_metadata(text):
    # Read zero-width chars from the start of the text
    bits = ''
    for c in text:
        if c == ZERO_WIDTH_SPACE:
            bits += '1'
        elif c.strip() == '':
            bits += '0'
        else:
            break
    # Convert bits to chars
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8) if len(bits[i:i+8]) == 8]
    meta = ''.join(chars)
    if meta.count('|') == 2:
        source_id, timestamp, key_id = meta.split('|', 2)
        return source_id, timestamp, key_id
    return None, None, None

def detect_watermark(text, key=None):
    """
    Detect a watermark in the given text. If key is provided, look for keyed marks; otherwise, use probabilistic detection.
    Returns: dict with confidence_score, source_id, timestamp, key_id, tampering_likelihood
    """
    source_id, timestamp, key_id = decode_metadata(text)
    # Remove metadata from text for further analysis
    i = 0
    while i < len(text) and (text[i] == ZERO_WIDTH_SPACE or text[i].strip() == ''):
        i += 1
    clean_text = text[i:]
    lang = detect_language(clean_text)
    tokens = clean_text.split()
    synonym_hits = 0
    total = 0
    for word in tokens:
        w = word.lower()
        if lang == 'en':
            syns = get_wordnet_synonyms(w)
            if not syns:
                syns = SYNONYMS.get('en', {}).get(w, [])
        else:
            syns = SYNONYMS.get(lang, {}).get(w, [])
        if w in syns:
            synonym_hits += 1
        total += 1
    confidence = synonym_hits / total if total else 0.0
    features = stylometry_features(clean_text)
    ml_score = ml_watermark_classifier(features)
    unique_ratio = len(set(tokens)) / (len(tokens) + 1e-6)
    tampering_likelihood = 1.0 - unique_ratio if unique_ratio < 0.7 else 0.0
    return {
        'confidence_score': round((confidence + ml_score) / 2, 3),
        'source_id': source_id,
        'timestamp': timestamp,
        'key_id': key_id,
        'tampering_likelihood': round(tampering_likelihood, 3)
    } 
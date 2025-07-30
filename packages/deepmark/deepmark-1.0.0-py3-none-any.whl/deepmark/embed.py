from .language import multilingual_mark
import datetime
import hashlib

ZERO_WIDTH_SPACE = '\u200b'

# Helper to encode metadata as zero-width string
def encode_metadata(source_id, timestamp, key_hash):
    # Format: source_id|timestamp|key_hash (first 8 hex chars)
    meta = f"{source_id}|{timestamp}|{key_hash}"
    bits = ''.join(f'{ord(c):08b}' for c in meta)
    return ''.join(ZERO_WIDTH_SPACE if b == '1' else '' for b in bits)

# Helper to hash the key
def key_hash(key):
    h = hashlib.sha256(key.encode()).hexdigest()
    return h[:8]

# Helper to decode metadata from zero-width string
# (Detection will need a similar function)

def mark_text(text, key, strength=0.7, mode="auto", source_id=None, timestamp=None):
    """
    Embed a watermark into the given text using the provided key.
    Optionally embed source_id, timestamp, and key hash as zero-width chars.
    """
    if not source_id:
        source_id = "unknown"
    if not timestamp:
        timestamp = datetime.datetime.utcnow().isoformat()
    khash = key_hash(key)
    marked = multilingual_mark(text, key, strength)
    meta = encode_metadata(source_id, timestamp, khash)
    return meta + marked 
# deepmark Python SDK

## Overview
A model-agnostic, robust, and compliance-ready text watermarking library for LLMs and content platforms. Supports both generation-time and post-processing watermark embedding, with detection tools for developers.

## Features
- Generation-time and post-generation watermarking
- Model-agnostic (OpenAI, HuggingFace, custom LLMs)
- Robust to paraphrasing, translation, and editing
- Python SDK for easy integration
- Batch detection, confidence scoring
- Multilingual support (English, Spanish, French, German, Italian, Portuguese)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
### Marking Text
```python
from deepmark import mark_text

# Mark text with a watermark
marked = mark_text("Hello world", key="your-secret-key", source_id="GPT-4")
print(marked)
```

### Detecting Watermarks
```python
from deepmark import detect_watermark

# Detect watermark in text
result = detect_watermark(marked)
print(result)
# Output: {'confidence_score': ..., 'source_id': ..., 'timestamp': ..., 'key_id': ..., 'tampering_likelihood': ...}
```

## Extensibility
- Add more languages by downloading spaCy models and updating synonym logic.
- Add more metadata by extending the zero-width encoding.
- Integrate with LLMs or pipelines by calling `mark_text` and `detect_watermark`.

## License
MIT 
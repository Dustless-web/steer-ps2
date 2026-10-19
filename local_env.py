"""Load project-local settings without exposing secret values."""
import os
from pathlib import Path

def load():
    path = Path(__file__).resolve().parent / '.env'
    if not path.exists():
        return
    allowed = {'AI_PROVIDER', 'GROQ_API_KEY', 'GROQ_MODEL', 'GEMINI_API_KEY', 'GEMINI_MODEL', 'OPENAI_API_KEY', 'OPENAI_MODEL', 'PORT', 'FFMPEG_PATH'}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if not line.strip() or line.lstrip().startswith('#') or '=' not in line:
            continue
        name, value = line.split('=', 1)
        name, value = name.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if name in allowed and value:
            os.environ.setdefault(name, value)

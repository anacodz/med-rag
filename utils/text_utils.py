"""Small text utilities used across the pipeline."""
import re


def clean_whitespace(text: str) -> str:
    if not text:
        return ''
    return re.sub(r'\s+', ' ', text).strip()


def snippet(text: str, length: int = 300) -> str:
    if not text:
        return ''
    return (text[:length] + '...') if len(text) > length else text

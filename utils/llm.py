"""LLM abstraction layer — supports Google Gemini (via google-generativeai).

This module provides a minimal `generate_text` wrapper. It will use the
`GEMINI_API_KEY` environment variable (recommended) and the
`google-generativeai` package when available. If the package isn't
installed or the key is missing, the functions raise informative errors.

Note: This is a small scaffold for integration. For production use add
error handling, retries/backoff, token limits and cost controls.
"""
import os
from typing import Optional

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


def _import_genai():
    try:
        import google.generativeai as genai
        return genai
    except Exception as e:
        raise ImportError('google-generativeai package is required for Gemini support. Install via `pip install google-generativeai`.') from e


def generate_text(prompt: str, model: str = 'models/text-bison-001', max_output_tokens: int = 512, temperature: float = 0.0) -> str:
    """Generate text using Gemini (Google Generative AI).

    Args:
        prompt: the input string/prompt
        model: model resource name (default is `models/text-bison-001`)
        max_output_tokens: maximum tokens to generate
        temperature: sampling temperature

    Returns:
        generated text (string)
    """
    if not GEMINI_API_KEY:
        raise RuntimeError('GEMINI_API_KEY not set in environment; set GEMINI_API_KEY in your .env or environment variables')

    genai = _import_genai()
    # configure client
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        # some versions use genai.client or different config; attempt both
        try:
            genai.client.configure(api_key=GEMINI_API_KEY)
        except Exception:
            pass

    # Call the generate endpoint
    # The google-generativeai client exposes `genai.generate()` in recent versions.
    try:
        response = genai.generate(model=model, prompt=prompt, max_output_tokens=max_output_tokens, temperature=temperature)
        # response may be a dict-like object; attempt to extract text
        if hasattr(response, 'content'):
            # some clients return an object with .content
            return response.content
        # fallback common shapes
        if isinstance(response, dict):
            # message -> content
            msg = response.get('candidates') or response.get('output') or response.get('choices')
            if msg:
                # attempt to find text
                if isinstance(msg, list) and len(msg) > 0:
                    cand = msg[0]
                    # candidate may be dict with 'content' or 'output'
                    return cand.get('content') or cand.get('text') or str(cand)
            return str(response)
        return str(response)
    except Exception as e:
        raise RuntimeError(f'Gemini generation failed: {e}') from e

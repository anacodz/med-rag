"""Simple bias-check utilities for screening metadata/abstracts.

This contains quick heuristics to flag potential methodological weaknesses
relevant to classification studies (e.g., no independent test set, no
cross-validation reporting, small sample size reporting, potential leakage).
These are heuristic and intended to surface records for manual review, not
to automatically exclude high-quality studies.
"""
from typing import Dict
import re


BIAS_INDICATORS = {
    'cv_mentions': [r'cross-?validation', r'k-?fold', r'leave-?one-?subject', r'loso', r'leave-?one-?out'],
    'external_test': [r'external validation', r'independent test', r'external test set', r'test set independent'],
    'small_sample': [r'\b(n=\d{1,2})\b', r'\b(number of subjects|participants)\b'],
    'overfit_warnings': [r'overfit', r'over-?fitting', r'data leakage', r'leakage']
}


def assess_bias(record: Dict) -> Dict:
    """Return a small dict with bias score (0-1) and flags.

    The function inspects title and abstract (and year if present) and
    returns a bias summary for human review.
    """
    text = ' '.join([str(record.get('title') or ''), str(record.get('abstract') or '')]).lower()
    flags = {}
    score = 0.0

    # check for cross-validation / good practices
    cv_found = any(re.search(p, text) for p in BIAS_INDICATORS['cv_mentions'])
    external_found = any(re.search(p, text) for p in BIAS_INDICATORS['external_test'])
    small_sample = any(re.search(p, text) for p in BIAS_INDICATORS['small_sample'])
    overfit = any(re.search(p, text) for p in BIAS_INDICATORS['overfit_warnings'])

    flags['cv_reported'] = bool(cv_found)
    flags['external_test_reported'] = bool(external_found)
    flags['small_sample_mentioned'] = bool(small_sample)
    flags['overfit_terms_found'] = bool(overfit)

    # crude scoring: fewer good-practice mentions -> higher caution score
    # baseline 0 (low concern). Add weight for missing CV/external test, small sample warnings add to concern.
    if not cv_found:
        score += 0.35
    if not external_found:
        score += 0.25
    if small_sample:
        score += 0.20
    if overfit:
        score += 0.20

    # clamp to [0,1]
    score = min(1.0, score)
    return {'bias_score': round(score, 2), 'flags': flags}

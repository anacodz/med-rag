# screeners/full_text_screener.py
import re

DL_KEYWORDS = ['cnn','convolution','rnn','lstm','transformer','deep neural','deep network','neural network']
METRIC_KEYWORDS = ['accuracy','f1','roc','auc','sensitivity','specificity','precision','recall','confusion matrix']


def find_snippet(text, keywords, window=200):
    if not text:
        return None
    t = text.lower()
    for k in keywords:
        idx = t.find(k)
        if idx != -1:
            start = max(0, idx - window)
            end = min(len(t), idx + window)
            return text[start:end]
    return None


def full_text_screen(record, cfg):
    full = record.get('full_text', {})
    text = full.get('pdf_text') or ''
    if record.get('member_ids') and len(record.get('member_ids')) > 1:
        return {'decision':'Exclude','stage':'full_text','exclusion_label':'Duplicate study','evidence_snippet':'Duplicate group','confidence':0.99}

    dl_snip = find_snippet(text, DL_KEYWORDS)
    if not dl_snip:
        if not any(k in (record.get('abstract') or '').lower() for k in DL_KEYWORDS):
            return {'decision':'Exclude','stage':'full_text','exclusion_label':'Insufficient methodological detail','evidence_snippet':'No DL architecture mention in full text or abstract','confidence':0.8}
    metric_snip = find_snippet(text, METRIC_KEYWORDS)
    if not metric_snip:
        return {'decision':'Exclude','stage':'full_text','exclusion_label':'No performance metrics reported','evidence_snippet':'No metrics found in full text','confidence':0.9}
    return {'decision':'Include','stage':'full_text','exclusion_label':None,'evidence_snippet':(dl_snip or metric_snip)[:400],'confidence':0.95}

# screeners/title_abstract_screener.py
from datetime import datetime
from utils.bias import assess_bias

# Focus keywords for EEG classification studies
DL_KEYWORDS = ['deep learning','neural network','cnn','conv','rnn','lstm','transformer','deep network']
EEG_KEYWORDS = ['eeg','electroencephalography','brain-computer interface','bci']
CLASSIFICATION_KEYWORDS = ['classif', 'classifier', 'accuracy', 'f1', 'roc', 'auc', 'sensitivity', 'specificity']
REVIEW_KEYWORDS = ['review','survey','systematic review','meta-analysis']


def contains_any(text, keywords):
    if not text:
        return False
    t = text.lower()
    return any(k in t for k in keywords)


def title_abstract_screen(record, cfg):
    """Screen on title/abstract with an added bias assessment.

    This function does not automatically exclude for bias; it returns an
    assessment that can be exported for human review.
    """
    title = record.get('title','') or ''
    abstract = record.get('abstract','') or ''
    year = record.get('year')
    text = (title or '') + ' ' + (abstract or '')

    # date filtering
    try:
        if year:
            y = int(str(year)[:4])
            if y < int(cfg['search']['date_from'][:4]) or y > int(cfg['search']['date_to'][:4]):
                bias_info = assess_bias(record)
                return {'decision':'Exclude','stage':'title_abstract','exclusion_label':'Outside date range','evidence_snippet':title or abstract,'confidence':0.95,'bias':bias_info}
    except Exception:
        pass

    # exclude reviews
    if contains_any(text, REVIEW_KEYWORDS):
        bias_info = assess_bias(record)
        return {'decision':'Exclude','stage':'title_abstract','exclusion_label':'Review/survey papers','evidence_snippet':title or abstract,'confidence':0.95,'bias':bias_info}

    # ensure EEG focus
    if not contains_any(text, EEG_KEYWORDS):
        bias_info = assess_bias(record)
        return {'decision':'Exclude','stage':'title_abstract','exclusion_label':'Not EEG-BCI focused','evidence_snippet':title or abstract,'confidence':0.9,'bias':bias_info}

    # require classification-related term to focus the search
    if not contains_any(text, CLASSIFICATION_KEYWORDS):
        bias_info = assess_bias(record)
        return {'decision':'Exclude','stage':'title_abstract','exclusion_label':'Not classification-focused','evidence_snippet':title or abstract,'confidence':0.85,'bias':bias_info}

    # language check: assume metadata gives language; if not, assume English
    lang = record.get('language','English')
    if lang and lang.lower() != 'english':
        bias_info = assess_bias(record)
        return {'decision':'Exclude','stage':'title_abstract','exclusion_label':'Non-English','evidence_snippet':'language:'+str(lang),'confidence':0.98,'bias':bias_info}

    # Passed initial filters; include with bias assessment provided for human review
    bias_info = assess_bias(record)
    return {'decision':'Include','stage':'title_abstract','exclusion_label':None,'evidence_snippet':(title or abstract)[:400],'confidence':0.95,'bias':bias_info}

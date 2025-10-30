import pandas as pd


def write_csv(records, path):
    rows = []
    for r in records:
        row = {
            'canonical_id': r.get('id'),
            'source': r.get('source'),
            'original_ids': ';'.join(r.get('member_ids', [r.get('id')])),
            'title': r.get('title'),
            'authors': ';'.join(r.get('authors') or []),
            'year': r.get('year'),
            'doi': r.get('doi'),
            'abstract': r.get('abstract'),
            'pdf_url': (r.get('full_text') or {}).get('pdf_url'),
            'url': r.get('url'),
            'language': r.get('language', 'English'),
            'stage_title_abstract_decision': (r.get('ta_decision') or {}).get('decision'),
            'stage_title_abstract_label': (r.get('ta_decision') or {}).get('exclusion_label'),
            'stage_title_abstract_evidence': (r.get('ta_decision') or {}).get('evidence_snippet'),
            'stage_full_text_decision': (r.get('ft_decision') or {}).get('decision') if r.get('ft_decision') else None,
            'stage_full_text_label': (r.get('ft_decision') or {}).get('exclusion_label') if r.get('ft_decision') else None,
            'stage_full_text_evidence': (r.get('ft_decision') or {}).get('evidence_snippet') if r.get('ft_decision') else None,
            'task_category': r.get('task_category'),
            'confidence': (r.get('ft_decision') or r.get('ta_decision') or {}).get('confidence'),
            # bias fields (from title/abstract stage)
            'bias_score': (r.get('ta_decision') or {}).get('bias', {}).get('bias_score'),
            'bias_flags': ';'.join([k for k,v in ((r.get('ta_decision') or {}).get('bias', {}).get('flags') or {}).items() if v])
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)

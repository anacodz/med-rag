# connectors/crossref_connector.py
import requests

BASE = 'https://api.crossref.org/works'


def search_crossref(cfg, query=None, rows=100):
    params = {'rows': rows}
    if query:
        params['query.bibliographic'] = query
    r = requests.get(BASE, params=params, headers={'User-Agent': cfg.get('user_agent', 'rag-pipeline/1.0')})
    r.raise_for_status()
    items = r.json()['message']['items']
    records = []
    for it in items:
        rec = {
            'id': 'crossref:' + it.get('DOI', 'no-doi'),
            'title': it.get('title', [None])[0],
            'authors': [f"{a.get('given','')} {a.get('family','')}".strip() for a in it.get('author', [])],
            'year': it.get('issued', {}).get('date-parts', [[None]])[0][0],
            'doi': it.get('DOI'),
            'abstract': it.get('abstract'),
            'url': it.get('URL'),
            'source': 'CrossRef'
        }
        records.append(rec)
    return records

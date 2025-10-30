# connectors/repo_connector.py
import os
import requests
from dotenv import load_dotenv
load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


def search_repos(cfg):
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    q = 'EEG deep learning OR CNN OR LSTM OR transformer'
    url = 'https://api.github.com/search/repositories'
    params = {'q': q, 'per_page': 50}
    r = requests.get(url, params=params, headers=headers)
    if r.status_code != 200:
        return []
    items = r.json().get('items', [])
    recs = []
    for it in items:
        recs.append({
            'id': f"github:{it['id']}",
            'title': it['name'],
            'authors': [it['owner']['login']],
            'year': None,
            'doi': None,
            'abstract': it.get('description'),
            'url': it['html_url'],
            'source': 'GitHub'
        })
    return recs


def fetch_fulltext(rec):
    # Strategy: if rec has pdf_url, return it; otherwise return landing page.
    return {'pdf_text': None, 'pdf_url': rec.get('pdf_url') or rec.get('url')}

# connectors/ieee_connector.py
import os
import requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('IEEE_API_KEY')
BASE = 'https://ieeexploreapi.ieee.org/api/v1/search/articles'


def search_ieee(query, cfg, max_records=500):
    params = {
        'apikey': API_KEY,
        'format': 'json',
        'max_records': max_records,
        'querytext': query,
        'start_record': 1
    }
    r = requests.get(BASE, params=params)
    r.raise_for_status()
    data = r.json()
    articles = data.get('articles', [])
    records = []
    for a in articles:
        rec = {
            'id': f"ieee:{a.get('article_number')}",
            'title': a.get('title'),
            'authors': [auth.get('name') for auth in a.get('authors', [])] if a.get('authors') else [],
            'year': a.get('publication_year'),
            'doi': a.get('doi'),
            'abstract': a.get('abstract'),
            'url': a.get('html_url') or a.get('pdf_url'),
            'source': 'IEEE Xplore'
        }
        records.append(rec)
    return records

# connectors/scholar_connector.py
# WARNING: scraping Google Scholar can lead to IP blocks. Use carefully.
import time
import requests
from bs4 import BeautifulSoup


def search_scholar(query, cfg, pages=3):
    USER_AGENT = cfg.get('user_agent', 'rag-pipeline/1.0')
    base = 'https://scholar.google.com/scholar'
    results = []
    for page in range(pages):
        params = {'q': query, 'start': page * 10}
        r = requests.get(base, params=params, headers={'User-Agent': USER_AGENT})
        if r.status_code != 200:
            break
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.gs_ri'):
            title_tag = item.select_one('.gs_rt')
            title = title_tag.text if title_tag else ''
            href = title_tag.a['href'] if title_tag and title_tag.a else None
            abstract = item.select_one('.gs_rs').text if item.select_one('.gs_rs') else ''
            meta = item.select_one('.gs_a').text if item.select_one('.gs_a') else ''
            results.append({'id': f'gs:{hash(title+meta)}', 'title': title, 'abstract': abstract, 'url': href, 'source': 'Google Scholar'})
        time.sleep(5)
    return results

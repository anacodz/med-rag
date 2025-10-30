# connectors/pubmed_connector.py
import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('PUBMED_API_KEY')
BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'


def search(query, cfg, retmax=1000):
    '''Return a list of metadata dicts from PubMed (id, title, authors, year, doi, abstract, url)'''
    params = {
        'db': 'pubmed',
        'term': query,
        'retmax': retmax,
        'api_key': API_KEY
    }
    resp = requests.get(f"{BASE}/esearch.fcgi?{urlencode(params)}")
    resp.raise_for_status()
    from xml.etree import ElementTree as ET
    root = ET.fromstring(resp.text)
    ids = [idn.text for idn in root.findall('.//Id')]
    records = []
    if not ids:
        return records
    fetch_params = {
        'db': 'pubmed',
        'id': ','.join(ids[:retmax]),
        'retmode': 'xml',
        'api_key': API_KEY
    }
    r2 = requests.get(f"{BASE}/efetch.fcgi?{urlencode(fetch_params)}")
    r2.raise_for_status()
    root2 = ET.fromstring(r2.text)
    for article in root2.findall('.//PubmedArticle'):
        try:
            title = article.find('.//ArticleTitle').text or ''
        except Exception:
            title = ''
        abstract_elems = article.findall('.//AbstractText')
        abstract = ' '.join([a.text or '' for a in abstract_elems])
        year = None
        try:
            year = article.find('.//PubDate/Year').text
        except Exception:
            pass
        doi = None
        for idv in article.findall('.//ArticleId'):
            if idv.attrib.get('IdType') == 'doi':
                doi = idv.text
        authors = []
        for a in article.findall('.//Author'):
            lname = a.find('LastName')
            fname = a.find('ForeName')
            if lname is not None and fname is not None:
                authors.append(f"{fname.text} {lname.text}")
        pmid = article.find('.//PMID').text
        url = f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'
        records.append({
            'id': f'pubmed:{pmid}',
            'title': title,
            'authors': authors,
            'year': year,
            'doi': doi,
            'abstract': abstract,
            'url': url,
            'source': 'PubMed'
        })
    return records

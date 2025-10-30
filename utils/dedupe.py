# utils/dedupe.py
import re
from rapidfuzz import fuzz
from unidecode import unidecode
from collections import defaultdict
import logging

logger = logging.getLogger('dedupe')

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.I)
STOPWORDS = set(['a', 'an', 'the', 'of', 'in', 'on', 'and', 'for', 'with', 'to', 'by'])


def normalize_title(t: str) -> str:
    if not t:
        return ''
    s = unidecode(t).lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    tokens = [tok for tok in s.split() if tok not in STOPWORDS]
    return ' '.join(tokens)


def extract_doi(text: str):
    if not text:
        return None
    m = DOI_RE.search(text)
    return m.group(0) if m else None


def dedupe_records(records, cfg):
    # records: list of dicts with keys including: id,title,authors,year,doi,source
    doi_map = {}
    canonical = []
    doi_groups = defaultdict(list)
    no_doi = []

    # 1. DOI exact grouping
    for r in records:
        doi = r.get('doi') or extract_doi(r.get('url', '') or r.get('abstract', '') or '')
        r['_norm_title'] = normalize_title(r.get('title', ''))
        if doi:
            doi = doi.lower()
            r['doi'] = doi
            doi_groups[doi].append(r)
        else:
            no_doi.append(r)

    duplicate_report = {'same_doi': [], 'fuzzy_groups': [], 'human_review': []}

    # canonicalize DOI groups
    canonical_records = []
    for doi, members in doi_groups.items():
        members_sorted = sorted(members, key=lambda x: 0 if 'journal' in (x.get('source') or '').lower() else 1)
        canon = members_sorted[0]
        canon['member_ids'] = [m['id'] for m in members]
        canonical_records.append(canon)
        duplicate_report['same_doi'].append({'canonical': canon['id'], 'members': canon['member_ids']})

    # 2. fuzzy match on no_doi
    used = set([r['id'] for r in canonical_records])
    for i, r in enumerate(no_doi):
        if r['id'] in used:
            continue
        group = [r]
        for j in range(i + 1, len(no_doi)):
            s = no_doi[j]
            score = fuzz.token_set_ratio(r['_norm_title'], s['_norm_title']) / 100.0
            if score >= cfg.get('fuzzy_threshold_exact', 0.92):
                group.append(s)
            elif score >= cfg.get('fuzzy_threshold_candidate', 0.85):
                fa_r = r.get('authors', [None])[0] if r.get('authors') else None
                fa_s = s.get('authors', [None])[0] if s.get('authors') else None
                yr_r = r.get('year')
                yr_s = s.get('year')
                same_author = False
                if fa_r and fa_s:
                    same_author = fa_r.split()[-1].lower() == fa_s.split()[-1].lower()
                year_close = False
                try:
                    if yr_r and yr_s and abs(int(yr_r) - int(yr_s)) <= 1:
                        year_close = True
                except Exception:
                    pass
                if same_author and year_close:
                    group.append(s)
                else:
                    if score >= cfg.get('human_review_threshold_low', 0.80):
                        duplicate_report['human_review'].append({'pair': (r['id'], s['id']), 'score': score, 'titles': (r.get('title'), s.get('title'))})
            else:
                continue
        if len(group) > 1:
            canon = group[0]
            canon['member_ids'] = [m['id'] for m in group]
            canonical_records.append(canon)
            duplicate_report['fuzzy_groups'].append({'canonical': canon['id'], 'members': canon['member_ids']})
        else:
            canonical_records.append(r)
    return canonical_records, duplicate_report

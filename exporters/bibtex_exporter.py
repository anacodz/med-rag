import bibtexparser


def write_bibtex(records, path):
    entries = []
    for r in records:
        bib = {
            'ID': r.get('doi') or r.get('id'),
            'ENTRYTYPE': 'article',
            'title': r.get('title', ''),
            'author': ' and '.join(r.get('authors') or []),
            'year': str(r.get('year') or ''),
            'doi': r.get('doi') or '',
            'url': r.get('url') or ''
        }
        entries.append(bib)
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = entries
    writer = bibtexparser.bwriter.BibTexWriter()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(writer.write(db))

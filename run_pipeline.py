#!/usr/bin/env python
"""Main orchestrator for the RAG EEG-BCI pipeline."""
import argparse
import yaml
import os
from connectors import pubmed_connector, ieee_connector, crossref_connector, scholar_connector, repo_connector
from utils.dedupe import dedupe_records
from screeners.title_abstract_screener import title_abstract_screen
from screeners.full_text_screener import full_text_screen
from exporters.csv_exporter import write_csv
from exporters.json_exporter import write_prisma_json
from exporters.bibtex_exporter import write_bibtex
from utils.logger import get_logger

logger = get_logger('run_pipeline')


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main(config_path, dry_run=False):
    cfg = load_config(config_path)
    artifacts_dir = cfg['output']['artifacts_dir']
    os.makedirs(artifacts_dir, exist_ok=True)

    # 1. Search / harvest from connectors (respect order)
    records_by_source = {}
    total_identified = 0

    # PUBMED
    logger.info('Searching PubMed...')
    pubmed_q = cfg['search']['queries']['pubmed']
    pubmed_records = pubmed_connector.search(pubmed_q, cfg)
    records_by_source['PubMed'] = pubmed_records
    total_identified += len(pubmed_records)

    # IEEE
    logger.info('Searching IEEE Xplore...')
    ieee_q = cfg['search']['queries']['ieee']
    ieee_records = ieee_connector.search_ieee(ieee_q, cfg)
    records_by_source['IEEE Xplore'] = ieee_records
    total_identified += len(ieee_records)

    # CrossRef (to catch DOIs and more)
    logger.info('Searching CrossRef...')
    crossref_records = crossref_connector.search_crossref(cfg, query=cfg['search']['queries'].get('ieee'))
    records_by_source['CrossRef'] = crossref_records
    total_identified += len(crossref_records)

    # Google Scholar fallback (optional)
    logger.info('Searching Google Scholar (fallback)...')
    gs_records = scholar_connector.search_scholar(cfg['search']['queries']['google_scholar'], cfg)
    records_by_source['Google Scholar'] = gs_records
    total_identified += len(gs_records)

    # Repositories (GitHub, Zenodo)
    logger.info('Searching Repositories...')
    repo_records = repo_connector.search_repos(cfg)
    records_by_source['Repositories'] = repo_records
    total_identified += len(repo_records)

    # Summary counts
    logger.info(f'Total records identified (raw): {total_identified}')

    # Merge into flat list
    flat_records = []
    for src, recs in records_by_source.items():
        for r in recs:
            r['source'] = src
            flat_records.append(r)

    # 2. Deduplicate
    logger.info('Deduplicating records...')
    canonical_records, duplicate_report = dedupe_records(flat_records, cfg['dedupe'])

    # Save intermediate artifacts
    write_prisma_json({'records_identified': {k: len(v) for k, v in records_by_source.items()}, 'total_identified': total_identified}, cfg['output']['prisma_json'])

    # 3. Title/abstract screening
    logger.info('Title/Abstract screening...')
    screened = []
    for rec in canonical_records:
        decision = title_abstract_screen(rec, cfg)
        rec.update({'ta_decision': decision})
        screened.append(rec)

    # 4. Determine which to fetch full text
    to_fulltext = [r for r in screened if r['ta_decision']['decision'] == 'Include']
    logger.info(f'Full-text to assess: {len(to_fulltext)}')

    if not dry_run:
        # 5. Fetch full text + run full text screen
        logger.info('Fetching full-texts and running full-text screen...')
        final_included = []
        for rec in to_fulltext:
            # try PDF retrieval via CrossRef/PMC/IEEE or direct url
            rec['full_text'] = repo_connector.fetch_fulltext(rec)
            ft_decision = full_text_screen(rec, cfg)
            rec.update({'ft_decision': ft_decision})
            if ft_decision['decision'] == 'Include':
                final_included.append(rec)

        # 6. Export results
        logger.info('Exporting artifacts...')
        write_csv(canonical_records, cfg['output']['csv'])
        write_prisma_json({
            'records_by_source': {k: len(v) for k, v in records_by_source.items()},
            'duplicates': duplicate_report,
            'total_identified': total_identified,
            'de_dup_count': len(canonical_records),
        }, cfg['output']['prisma_json'])
        write_bibtex(final_included, cfg['output']['bib'])
        logger.info('Pipeline finished.')
    else:
        logger.info('Dry run finished. No full-text fetched.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    main(args.config, args.dry_run)

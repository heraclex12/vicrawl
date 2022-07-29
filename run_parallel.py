import os
from joblib import Parallel, delayed
import json
import argparse
import warnings

from voz_selenium import VozCrawler

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Arguments for parallel running crawler.")
    parser.add_argument('--site', required=True, type=str,
                        help="Forum site to start crawling (choose in ['voz', 'tinhte']")
    parser.add_argument('--output', required=True, type=str, help="Output path to save extracted data.")
    args = parser.parse_args()

    if args.site == 'voz':
        crawler = VozCrawler()
    elif args.site == 'tinhte':
        crawler = None
    else:
        raise ValueError(f"{args.site} currently is not supported. "
                         f"You can contribute to our repo/request us by creating an issue.")

    categories = crawler.get_all_category_urls()
    results = Parallel(n_jobs=-1)(delayed(crawler.extract_thread_urls)(category_name, category_url)
                                  for category_name, category_url in categories.items())

    if not args.output.endswith('.json'):
        warnings.warn("The output should be path to .json file.\nChoose default filename: data.json")
        output_path = args.output.strip('/') + '/' + 'data.json'
    else:
        output_path = args.output

    with open(output_path, 'w', encoding='utf-8') as out_file:
        for row in results:
            json.dump(row, out_file, ensure_ascii=False)
            out_file.write('\n')

"""Command-line entry point: collect -> clean -> store -> summarize.

Examples (run from the project folder):

    python main.py --source sample            # use data/sample_products.csv
    python main.py --source live              # scrape the practice website
    python main.py --source live --no-db      # scrape but skip MongoDB
    python main.py --source sample --no-db    # fully offline demo
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from analysis.analysis import summary_stats
from database.mongodb import DatabaseError, ProductDatabase
from scraper.amazon_scraper import CsvProductSource, PracticeSiteScraper
from utils.data_cleaning import (
    clean_dataframe, dataframe_to_records, missing_value_report)

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_CSV = PROJECT_ROOT / "data" / "sample_products.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "scraped_products.csv"


def parse_args():
    parser = argparse.ArgumentParser(description="Product data pipeline")
    parser.add_argument("--source", choices=["live", "sample"],
                        default="sample",
                        help="live = scrape practice site, sample = CSV file")
    parser.add_argument("--max-pages", type=int, default=3,
                        help="listing pages per category (live only)")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="seconds to wait between requests (live only)")
    parser.add_argument("--no-db", action="store_true",
                        help="do not connect to MongoDB Atlas")
    return parser.parse_args()


def collect(args):
    """Step 1: get raw product records from the chosen source."""
    if args.source == "live":
        source = PracticeSiteScraper(max_pages=args.max_pages,
                                     delay=args.delay)
    else:
        source = CsvProductSource(SAMPLE_CSV)
    return source.fetch_products()


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")
    args = parse_args()

    try:
        products = collect(args)
    except Exception as error:  # network problems, bad CSV, robots.txt ...
        print(f"Collection failed: {error}")
        print("Tip: try  python main.py --source sample --no-db")
        return 1

    if not products:
        print("No products were collected. Nothing to do.")
        return 1
    print(f"Collected {len(products)} products from '{args.source}' source.")

    df = clean_dataframe(pd.DataFrame(products))
    print(f"After cleaning: {len(df)} products.")
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved cleaned data to {OUTPUT_CSV.relative_to(PROJECT_ROOT)}")

    if not args.no_db:
        try:
            db = ProductDatabase()
            # Convert pandas types to plain Python types before saving.
            result = db.save_products(dataframe_to_records(df))
            print(f"MongoDB: {result}. Total stored: {db.count()}")
            db.close()
        except DatabaseError as error:
            print(f"MongoDB step skipped: {error}")

    print("\n--- Summary ---")
    for name, value in summary_stats(df).items():
        print(f"{name}: {value}")
    print("\n--- Missing values ---")
    print(missing_value_report(df).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

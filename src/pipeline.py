"""
Main orchestrator module for the Instagram Influencer Analytics data pipeline.

Usage:
    python src/pipeline.py --mode test --max-profiles 30
    python src/pipeline.py --mode full --max-profiles 2500
    python src/pipeline.py --mode import --input-file path/to/data.csv
    python src/pipeline.py --mode clean_only --input-file data/raw/raw_profiles.csv
"""

import os
import sys
import argparse
import logging
import pandas as pd

# Add src to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collect import run_collection, import_from_csv
from clean import run_cleaning
from calculate_metrics import run_metrics_calculation
from validate import run_validation

# Configure logging
os.makedirs('logs', exist_ok=True)
logger = logging.getLogger('pipeline')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File handler
fh = logging.FileHandler('logs/pipeline.log')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def print_banner(step_num: int, title: str) -> None:
    """Print a progress banner."""
    print('\n' + '=' * 60)
    print(f'  STEP {step_num}: {title}')
    print('=' * 60)


def load_seed_usernames(seed_file: str) -> list:
    """Load seed usernames from a CSV or text file.
    
    Supports:
    - CSV with a 'username' column
    - Plain text file with one username per line
    """
    if not os.path.exists(seed_file):
        raise FileNotFoundError(f"Seed file not found: {seed_file}")
    
    if seed_file.endswith('.csv'):
        df = pd.read_csv(seed_file)
        if 'username' in df.columns:
            return df['username'].dropna().str.strip().tolist()
        else:
            # Use the first column
            return df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    else:
        with open(seed_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]


def run_pipeline(mode: str = 'test', max_profiles: int = 50, delay: float = 5.0,
                 seed_file: str = None, input_file: str = None, hashtags: list = None) -> None:
    """Run the full data pipeline.
    
    Modes:
    - 'test': Discover and collect 20-50 profiles for testing
    - 'full': Full collection of 2000+ profiles
    - 'import': Import from existing CSV file
    - 'clean_only': Only run cleaning + metrics + validation on existing raw data
    
    Steps:
    1. Collection (collect.py)
    2. Cleaning (clean.py)
    3. Metrics calculation (calculate_metrics.py)
    4. Validation (validate.py)
    """
    logger.info(f"Starting pipeline in '{mode}' mode with max_profiles={max_profiles}")
    
    raw_data_path = None
    
    # ───────────────── STEP 1: Data Collection ─────────────────
    if mode == 'clean_only':
        if not input_file:
            logger.error("clean_only mode requires --input-file")
            print("Error: --input-file must be provided for clean_only mode.")
            return
        raw_data_path = input_file
        print(f"\n  Skipping collection — using existing file: {input_file}")
        
    elif mode == 'import':
        print_banner(1, "Data Collection (Import Mode)")
        logger.info("Executing Step 1: Data Import")
        
        if not input_file:
            logger.error("import mode requires --input-file")
            print("Error: --input-file must be provided for import mode.")
            return
        
        try:
            df_imported = import_from_csv(input_file)
            os.makedirs('data/raw', exist_ok=True)
            raw_data_path = 'data/raw/imported_profiles.csv'
            df_imported.to_csv(raw_data_path, index=False)
            logger.info(f"Imported {len(df_imported)} profiles from {input_file}")
            print(f"  Imported {len(df_imported)} profiles → {raw_data_path}")
        except Exception as e:
            logger.error(f"Import failed: {e}", exc_info=True)
            print(f"Error during import: {e}")
            return
            
    elif mode in ['test', 'full']:
        print_banner(1, "Data Collection")
        logger.info("Executing Step 1: Data Collection")
        
        try:
            # Determine collection sub-mode
            seed_usernames = None
            collection_mode = 'discover'
            
            if seed_file:
                seed_usernames = load_seed_usernames(seed_file)
                collection_mode = 'seed'
                logger.info(f"Loaded {len(seed_usernames)} seed usernames from {seed_file}")
                print(f"  Loaded {len(seed_usernames)} seed usernames from {seed_file}")
            
            raw_data_path = run_collection(
                mode=collection_mode,
                seed_usernames=seed_usernames,
                hashtags=hashtags,
                max_profiles=max_profiles,
                output_dir='data/raw',
                delay=delay
            )
            print(f"  Collection complete → {raw_data_path}")
        except Exception as e:
            logger.error(f"Collection step failed: {e}", exc_info=True)
            print(f"Error during collection: {e}")
            return
    else:
        logger.error(f"Unknown mode: {mode}")
        print(f"Error: Unknown mode '{mode}'")
        return
    
    if not raw_data_path or not os.path.exists(raw_data_path):
        logger.error(f"Raw data file not found: {raw_data_path}")
        print(f"Error: Raw data file not found: {raw_data_path}")
        return
    
    # ───────────────── STEP 2: Data Cleaning ─────────────────
    print_banner(2, "Data Cleaning")
    logger.info("Executing Step 2: Data Cleaning")
    try:
        cleaned_data_path = run_cleaning(
            input_path=raw_data_path,
            output_dir='data/processed'
        )
        print(f"  Cleaning complete → {cleaned_data_path}")
    except Exception as e:
        logger.error(f"Cleaning step failed: {e}", exc_info=True)
        print(f"Error during cleaning: {e}")
        return

    # ───────────────── STEP 3: Metrics Calculation ─────────────────
    print_banner(3, "Metrics Calculation")
    logger.info("Executing Step 3: Metrics Calculation")
    try:
        metrics_data_path = run_metrics_calculation(
            input_path=cleaned_data_path,
            output_dir='data/processed'
        )
        print(f"  Metrics calculation complete → {metrics_data_path}")
    except Exception as e:
        logger.error(f"Metrics calculation step failed: {e}", exc_info=True)
        print(f"Error during metrics calculation: {e}")
        return

    # ───────────────── STEP 4: Validation ─────────────────
    print_banner(4, "Validation")
    logger.info("Executing Step 4: Validation")
    try:
        results = run_validation(
            input_path=metrics_data_path,
            report_dir='reports'
        )
        print(f"\n  Validation report saved to reports/validation_report.txt")
    except Exception as e:
        logger.error(f"Validation step failed: {e}", exc_info=True)
        print(f"Error during validation: {e}")
        return
    
    # ───────────────── DONE ─────────────────
    logger.info("Pipeline completed successfully.")
    print('\n' + '=' * 60)
    print('  PIPELINE COMPLETED SUCCESSFULLY')
    print('=' * 60)
    print(f'\n  Final dataset: {metrics_data_path}')
    print(f'  Validation report: reports/validation_report.txt\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Instagram Influencer Analytics Data Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Test mode (20-50 profiles):
    python src/pipeline.py --mode test --max-profiles 30

  Full collection (2000+ profiles):
    python src/pipeline.py --mode full --max-profiles 2500

  Import from CSV:
    python src/pipeline.py --mode import --input-file path/to/data.csv

  Clean existing raw data:
    python src/pipeline.py --mode clean_only --input-file data/raw/raw_profiles.csv

  With seed file:
    python src/pipeline.py --mode test --seed-file seeds.csv --max-profiles 50

  With specific hashtags:
    python src/pipeline.py --mode test --hashtags "foodblogger,travelblogger" --max-profiles 30
        """
    )
    parser.add_argument('--mode', type=str, choices=['test', 'full', 'import', 'clean_only'],
                        default='test', help="Pipeline execution mode (default: test)")
    parser.add_argument('--max-profiles', type=int, default=50,
                        help="Maximum profiles to collect (default: 50)")
    parser.add_argument('--delay', type=float, default=5.0,
                        help="Delay between requests in seconds (default: 5.0)")
    parser.add_argument('--seed-file', type=str, default=None,
                        help="Path to seed usernames CSV or text file")
    parser.add_argument('--input-file', type=str, default=None,
                        help="Path to raw CSV for import/clean_only mode")
    parser.add_argument('--hashtags', type=str, default=None,
                        help="Comma-separated hashtags for discovery")

    args = parser.parse_args()

    hashtag_list = [h.strip() for h in args.hashtags.split(',')] if args.hashtags else None

    run_pipeline(
        mode=args.mode,
        max_profiles=args.max_profiles,
        delay=args.delay,
        seed_file=args.seed_file,
        input_file=args.input_file,
        hashtags=hashtag_list
    )

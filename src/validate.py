"""
Validation module for processed Instagram Influencer dataset.
"""

import os
import logging
import pandas as pd
from typing import Dict, Any

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/validation.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_dataset(df: pd.DataFrame) -> dict:
    """Run all validation checks. Returns a dict with:
    - total_profiles: int
    - duplicate_usernames: int (count of duplicates)
    - duplicate_username_list: list of duplicate usernames
    - missing_usernames: int
    - missing_followers: int
    - profiles_above_1m: int
    - profiles_above_1m_list: list of usernames with >= 1M followers
    - missing_required_fields: dict mapping field_name -> count of missing
    - valid_profiles: int (profiles that pass all checks)
    - profiles_per_category: dict mapping category -> count
    - avg_engagement_rate: float
    - median_engagement_rate: float
    - avg_followers: float
    - median_followers: float
    """
    logger.info("Starting dataset validation.")
    results = {}
    
    try:
        results['total_profiles'] = int(len(df))
        
        # Check duplicates
        if 'username' in df.columns:
            dupes = df[df.duplicated(subset=['username'], keep=False)]
            dupe_usernames = dupes['username'].dropna().unique().tolist()
            results['duplicate_usernames'] = len(dupe_usernames)
            results['duplicate_username_list'] = dupe_usernames
        else:
            results['duplicate_usernames'] = 0
            results['duplicate_username_list'] = []

        # Missing values
        required_fields = ['username', 'followers', 'category', 'engagement_rate', 'data_source']
        missing_dict = {}
        valid_mask = pd.Series(True, index=df.index)
        
        for field in required_fields:
            if field in df.columns:
                missing_count = int(df[field].isna().sum())
                missing_dict[field] = missing_count
                valid_mask = valid_mask & df[field].notna()
            else:
                missing_dict[field] = int(len(df))
                valid_mask = valid_mask & False
                
        results['missing_required_fields'] = missing_dict
        
        results['missing_usernames'] = missing_dict.get('username', 0)
        results['missing_followers'] = missing_dict.get('followers', 0)
        
        # Valid profiles (no missing required fields and not a duplicate)
        if 'username' in df.columns:
            is_duplicate = df.duplicated(subset=['username'], keep=False)
            valid_mask = valid_mask & (~is_duplicate)
        results['valid_profiles'] = int(valid_mask.sum())
        
        # Unique usernames
        results['unique_usernames'] = int(df['username'].nunique()) if 'username' in df.columns else 0
        
        # Followers stats
        if 'followers' in df.columns:
            followers_series = pd.to_numeric(df['followers'], errors='coerce')
            above_1m = df[followers_series >= 1_000_000]
            under_1m = df[(followers_series > 0) & (followers_series < 1_000_000)]
            invalid_followers = df[followers_series.isna() | (followers_series <= 0)]
            
            results['profiles_above_1m'] = int(len(above_1m))
            results['profiles_above_1m_list'] = above_1m['username'].dropna().tolist() if 'username' in df.columns else []
            results['profiles_under_1m'] = int(len(under_1m))
            results['invalid_follower_values'] = int(len(invalid_followers))
            
            results['avg_followers'] = float(followers_series.mean()) if not followers_series.dropna().empty else 0.0
            results['median_followers'] = float(followers_series.median()) if not followers_series.dropna().empty else 0.0
        else:
            results['profiles_above_1m'] = 0
            results['profiles_above_1m_list'] = []
            results['profiles_under_1m'] = 0
            results['invalid_follower_values'] = 0
            results['avg_followers'] = 0.0
            results['median_followers'] = 0.0
            
        # Engagement rate stats
        if 'engagement_rate' in df.columns:
            er_series = pd.to_numeric(df['engagement_rate'], errors='coerce')
            invalid_er = df[er_series.isna() | (er_series < 0)]
            results['invalid_engagement_rates'] = int(len(invalid_er))
            results['avg_engagement_rate'] = float(er_series.mean()) if not er_series.dropna().empty else 0.0
            results['median_engagement_rate'] = float(er_series.median()) if not er_series.dropna().empty else 0.0
        else:
            results['invalid_engagement_rates'] = 0
            results['avg_engagement_rate'] = 0.0
            results['median_engagement_rate'] = 0.0
            
        # Public contact information check
        if 'contact_details' in df.columns:
            no_contact = df[df['contact_details'].isna() | (df['contact_details'] == 'Not publicly available') | (df['contact_details'] == '')]
            has_contact = df[df['contact_details'].notna() & (df['contact_details'] != 'Not publicly available') & (df['contact_details'] != '')]
            results['profiles_without_public_contact'] = int(len(no_contact))
            results['profiles_with_public_contact'] = int(len(has_contact))
        else:
            results['profiles_without_public_contact'] = int(len(df))
            results['profiles_with_public_contact'] = 0
            
        # Automation usage check
        if 'automation_usage' in df.columns:
            unknown_auto = df[df['automation_usage'].isna() | (df['automation_usage'] == 'Unknown') | (df['automation_usage'] == '')]
            known_auto = df[df['automation_usage'].notna() & (df['automation_usage'] != 'Unknown') & (df['automation_usage'] != '')]
            results['profiles_unknown_automation'] = int(len(unknown_auto))
            results['profiles_known_automation'] = int(len(known_auto))
        else:
            results['profiles_unknown_automation'] = int(len(df))
            results['profiles_known_automation'] = 0
            
        # Category stats
        if 'category' in df.columns:
            cats = df['category'].value_counts().to_dict()
            results['profiles_per_category'] = {str(k): int(v) for k, v in cats.items()}
        else:
            results['profiles_per_category'] = {}
            
        logger.info("Validation completed successfully.")
        return results
        
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}", exc_info=True)
        return {}

def print_validation_report(results: dict) -> None:
    """Print a formatted validation report to console."""
    if not results:
        print("No validation results to display.")
        return
        
    print("=" * 60)
    print(f"{' DATASET VALIDATION REPORT ':=^60}")
    print("=" * 60)
    
    print(f"Total Records:                 {results.get('total_profiles', 0)}")
    print(f"Unique Usernames:              {results.get('unique_usernames', 0)}")
    print(f"Valid Profiles (Passed All):   {results.get('valid_profiles', 0)}")
    print("-" * 60)
    
    print("--- DATA INTEGRITY & QUALITY ---")
    print(f"Duplicate Usernames:           {results.get('duplicate_usernames', 0)}")
    if results.get('duplicate_usernames', 0) > 0:
        print(f"  List: {results.get('duplicate_username_list', [])}")
        
    print(f"Missing Usernames:             {results.get('missing_usernames', 0)}")
    print(f"Missing Followers:             {results.get('missing_followers', 0)}")
    print(f"Followers < 1,000,000:         {results.get('profiles_under_1m', 0)}")
    print(f"Followers >= 1,000,000:        {results.get('profiles_above_1m', 0)}")
    print(f"Invalid Follower Values (<=0): {results.get('invalid_follower_values', 0)}")
    print(f"Invalid Engagement Rates (<0): {results.get('invalid_engagement_rates', 0)}")
    print("-" * 60)
    
    print("--- CONTACT & AUTOMATION AUDIT ---")
    print(f"Profiles With Public Contact:  {results.get('profiles_with_public_contact', 0)}")
    print(f"Profiles Without Contact Info: {results.get('profiles_without_public_contact', 0)} ('Not publicly available')")
    print(f"Profiles With Detected Auto:   {results.get('profiles_known_automation', 0)}")
    print(f"Profiles Unknown Automation:   {results.get('profiles_unknown_automation', 0)} ('Unknown')")
    print("-" * 60)
    
    print("--- REQUIRED FIELDS AUDIT ---")
    for field, count in results.get('missing_required_fields', {}).items():
        print(f"  Missing {field}: {count}")
    print("-" * 60)
    
    print("--- METRICS SUMMARY ---")
    print(f"Average Followers:             {results.get('avg_followers', 0):,.2f}")
    print(f"Median Followers:              {results.get('median_followers', 0):,.2f}")
    print(f"Average Engagement Rate:       {results.get('avg_engagement_rate', 0):.4f}%")
    print(f"Median Engagement Rate:        {results.get('median_engagement_rate', 0):.4f}%")
    print("-" * 60)
    
    print("--- CATEGORY DISTRIBUTION ---")
    for cat, count in results.get('profiles_per_category', {}).items():
        print(f"  {cat}: {count}")
        
    print("=" * 60)

def save_validation_report(results: dict, output_path: str) -> None:
    """Save validation report to a text file in reports/ directory."""
    logger.info(f"Saving validation report to {output_path}")
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"{' DATASET VALIDATION REPORT ':=^60}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Total Records:                 {results.get('total_profiles', 0)}\n")
            f.write(f"Unique Usernames:              {results.get('unique_usernames', 0)}\n")
            f.write(f"Valid Profiles (Passed All):   {results.get('valid_profiles', 0)}\n")
            f.write("-" * 60 + "\n\n")
            
            f.write("--- DATA INTEGRITY & QUALITY ---\n")
            f.write(f"Duplicate Usernames:           {results.get('duplicate_usernames', 0)}\n")
            if results.get('duplicate_usernames', 0) > 0:
                f.write(f"  List: {results.get('duplicate_username_list', [])}\n")
                
            f.write(f"Missing Usernames:             {results.get('missing_usernames', 0)}\n")
            f.write(f"Missing Followers:             {results.get('missing_followers', 0)}\n")
            f.write(f"Followers < 1,000,000:         {results.get('profiles_under_1m', 0)}\n")
            f.write(f"Followers >= 1,000,000:        {results.get('profiles_above_1m', 0)}\n")
            f.write(f"Invalid Follower Values (<=0): {results.get('invalid_follower_values', 0)}\n")
            f.write(f"Invalid Engagement Rates (<0): {results.get('invalid_engagement_rates', 0)}\n")
            f.write("-" * 60 + "\n\n")
            
            f.write("--- CONTACT & AUTOMATION AUDIT ---\n")
            f.write(f"Profiles With Public Contact:  {results.get('profiles_with_public_contact', 0)}\n")
            f.write(f"Profiles Without Contact Info: {results.get('profiles_without_public_contact', 0)} ('Not publicly available')\n")
            f.write(f"Profiles With Detected Auto:   {results.get('profiles_known_automation', 0)}\n")
            f.write(f"Profiles Unknown Automation:   {results.get('profiles_unknown_automation', 0)} ('Unknown')\n")
            f.write("-" * 60 + "\n\n")
            
            f.write("--- REQUIRED FIELDS AUDIT ---\n")
            for field, count in results.get('missing_required_fields', {}).items():
                f.write(f"  Missing {field}: {count}\n")
            f.write("-" * 60 + "\n\n")
            
            f.write("--- METRICS SUMMARY ---\n")
            f.write(f"Average Followers:             {results.get('avg_followers', 0):,.2f}\n")
            f.write(f"Median Followers:              {results.get('median_followers', 0):,.2f}\n")
            f.write(f"Average Engagement Rate:       {results.get('avg_engagement_rate', 0):.4f}%\n")
            f.write(f"Median Engagement Rate:        {results.get('median_engagement_rate', 0):.4f}%\n")
            f.write("-" * 60 + "\n\n")
            
            f.write("--- CATEGORY DISTRIBUTION ---\n")
            for cat, count in results.get('profiles_per_category', {}).items():
                f.write(f"  {cat}: {count}\n")
                
            f.write("=" * 60 + "\n")
        logger.info("Report saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save validation report: {str(e)}", exc_info=True)

def run_validation(input_path: str, report_dir: str = 'reports') -> dict:
    """Load processed data, run validation, print and save report.
    Returns validation results dict."""
    logger.info(f"Running validation on {input_path}")
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        logger.error(f"Failed to read input file {input_path}: {str(e)}", exc_info=True)
        return {}
        
    results = validate_dataset(df)
    print_validation_report(results)
    
    report_path = os.path.join(report_dir, 'validation_report.txt')
    save_validation_report(results, report_path)
    
    return results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Validate processed dataset")
    parser.add_argument('--input', type=str, required=True, help="Path to processed CSV file")
    parser.add_argument('--report-dir', type=str, default='reports', help="Directory to save report")
    
    args = parser.parse_args()
    run_validation(args.input, args.report_dir)

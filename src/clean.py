"""
Data Cleaning Module for Instagram Influencer Analytics.
"""

import pandas as pd
import logging
import os
import unicodedata

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'cleaning.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_raw_data(filepath: str) -> pd.DataFrame:
    """Load raw CSV data."""
    logger.info(f"Loading raw data from {filepath}")
    return pd.read_csv(filepath)

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate usernames, keeping the first occurrence. Log how many removed."""
    initial_count = len(df)
    if 'username' in df.columns:
        df_cleaned = df.drop_duplicates(subset=['username'], keep='first').copy()
    else:
        df_cleaned = df.drop_duplicates().copy()
    removed = initial_count - len(df_cleaned)
    logger.info(f"Removed {removed} duplicate accounts.")
    return df_cleaned

def remove_private_accounts(df: pd.DataFrame) -> pd.DataFrame:
    """Remove private accounts. Log how many removed."""
    if 'is_private' not in df.columns:
        logger.warning("'is_private' column missing. Skipping private account removal.")
        return df
    
    initial_count = len(df)
    df_cleaned = df[~df['is_private'].isin([True, 'True', 'true', 1, '1'])].copy()
    removed = initial_count - len(df_cleaned)
    logger.info(f"Removed {removed} private accounts.")
    return df_cleaned

def filter_by_followers(df: pd.DataFrame, max_followers: int = 1_000_000) -> pd.DataFrame:
    """Remove accounts with >= 1M followers. Log how many removed."""
    if 'followers' not in df.columns:
        return df
        
    initial_count = len(df)
    df['followers'] = pd.to_numeric(df['followers'], errors='coerce').fillna(0)
    df_cleaned = df[df['followers'] < max_followers].copy()
    removed = initial_count - len(df_cleaned)
    logger.info(f"Removed {removed} accounts with {max_followers:,} or more followers.")
    return df_cleaned

def clean_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace, normalize unicode in text fields."""
    logger.info("Cleaning text fields...")
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].apply(lambda x: unicodedata.normalize('NFKC', str(x)).strip() if pd.notnull(x) else x)
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values with appropriate defaults:
    - contact_details: 'Not publicly available'
    - followers: 0 (and flag for review)
    - name: username as fallback
    - Other text fields: empty string
    - Numeric fields: 0
    """
    logger.info("Handling missing values...")
    
    if 'contact_details' in df.columns:
        df['contact_details'] = df['contact_details'].fillna('Not publicly available')
        
    if 'followers' in df.columns:
        missing_followers = df['followers'].isnull().sum()
        if missing_followers > 0:
            logger.warning(f"Found {missing_followers} accounts missing followers count. Filling with 0.")
            df['followers'] = df['followers'].fillna(0)
            
    if 'name' in df.columns and 'username' in df.columns:
        df['name'] = df['name'].fillna(df['username'])
        df.loc[df['name'] == '', 'name'] = df.loc[df['name'] == '', 'username']
        
    # Other text fields
    text_cols = df.select_dtypes(include=['object', 'string']).columns
    for col in text_cols:
        df[col] = df[col].fillna('')
        
    # Numeric fields
    num_cols = df.select_dtypes(include=['number']).columns
    for col in num_cols:
        if col != 'followers':
            df[col] = df[col].fillna(0)
            
    return df

def validate_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure followers, avg_likes, avg_comments are numeric. Convert if needed."""
    logger.info("Validating data types...")
    num_cols = ['followers', 'avg_likes_last_10', 'avg_comments_last_10']
    
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

def run_cleaning(input_path: str, output_dir: str = 'data/processed') -> str:
    """Run full cleaning pipeline. Returns output filepath.
    Steps: load -> remove_duplicates -> remove_private -> filter_followers -> clean_text -> handle_missing -> validate_types -> save
    """
    logger.info("Starting cleaning pipeline.")
    os.makedirs(output_dir, exist_ok=True)
    
    df = load_raw_data(input_path)
    df = remove_duplicates(df)
    df = remove_private_accounts(df)
    df = filter_by_followers(df)
    df = clean_text_fields(df)
    df = handle_missing_values(df)
    df = validate_data_types(df)
    
    output_path = os.path.join(output_dir, 'cleaned_profiles.csv')
    df.to_csv(output_path, index=False)
    logger.info(f"Cleaning complete. Saved cleaned data to {output_path}")
    
    return output_path

if __name__ == '__main__':
    run_cleaning('data/raw/raw_profiles.csv')

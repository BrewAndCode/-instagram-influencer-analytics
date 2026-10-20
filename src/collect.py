import os
import re
import json
import time
import logging
from datetime import datetime
import itertools
from typing import List, Dict, Optional, Any

import pandas as pd
import instaloader

# Ensure necessary directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('data/raw', exist_ok=True)

# Configure logging
logger = logging.getLogger('collection_logger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console Handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# File Handler
fh = logging.FileHandler('logs/collection.log')
fh.setFormatter(formatter)
logger.addHandler(fh)


def _extract_contact_info(bio: Any) -> str:
    """Extract email and phone number from text using regex."""
    if bio is None or pd.isna(bio) or not str(bio).strip() or str(bio).lower() == 'nan':
        return 'Not publicly available'
    
    bio_str = str(bio)
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\+?\d[\d -]{8,12}\d'
    
    emails = re.findall(email_pattern, bio_str)
    phones = re.findall(phone_pattern, bio_str)
    
    contacts = []
    if emails:
        contacts.extend(emails)
    if phones:
        contacts.extend(phones)
        
    if contacts:
        return ', '.join(contacts)
    return 'Not publicly available'


def collect_single_profile(username: str, loader: Optional[instaloader.Instaloader] = None, delay: float = 5.0) -> Dict[str, Any]:
    """Collect data for a single Instagram profile. Returns dict with raw schema fields."""
    if loader is None:
        loader = instaloader.Instaloader()
        
    time.sleep(delay)
    
    # Initialize default result dict matching raw schema
    result = {
        'profile_url': f'https://www.instagram.com/{username}/',
        'name': None,
        'username': username,
        'followers': None,
        'following': None,
        'bio': None,
        'is_private': None,
        'is_verified': None,
        'media_count': None,
        'avg_likes_last_10': None,
        'avg_comments_last_10': None,
        'post_dates_json': json.dumps([]),
        'hashtags_json': json.dumps([]),
        'contact_details': 'Not publicly available',
        'data_source': 'instagram_public',
        'collection_date': datetime.now().isoformat(),
        'collection_errors': None
    }
    
    max_retries = 3
    retry_delay = delay
    
    for attempt in range(max_retries):
        try:
            profile = instaloader.Profile.from_username(loader.context, username)
            
            result['name'] = profile.full_name
            result['followers'] = profile.followers
            result['following'] = profile.followees
            result['bio'] = profile.biography
            result['is_private'] = profile.is_private
            result['is_verified'] = profile.is_verified
            result['media_count'] = profile.mediacount
            
            result['contact_details'] = _extract_contact_info(profile.biography)
            
            if profile.is_private:
                error_msg = f"Profile {username} is private."
                logger.warning(error_msg)
                result['collection_errors'] = error_msg
                return result

            # Fetch last 10 posts
            likes = []
            comments = []
            dates = []
            all_hashtags = set()
            
            posts = itertools.islice(profile.get_posts(), 10)
            for post in posts:
                likes.append(post.likes)
                comments.append(post.comments)
                dates.append(post.date_utc.isoformat())
                if post.caption_hashtags:
                    all_hashtags.update(post.caption_hashtags)
            
            if likes:
                result['avg_likes_last_10'] = sum(likes) / len(likes)
            if comments:
                result['avg_comments_last_10'] = sum(comments) / len(comments)
                
            result['post_dates_json'] = json.dumps(dates)
            result['hashtags_json'] = json.dumps(list(all_hashtags))
            
            logger.info(f"Successfully collected profile: {username}")
            break
            
        except instaloader.exceptions.ProfileNotExistsException:
            error_msg = f"Profile {username} does not exist or was deleted."
            logger.error(error_msg)
            result['collection_errors'] = error_msg
            break
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                logger.warning(f"Error fetching {username}: {error_msg}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"Failed to fetch {username} after {max_retries} attempts: {error_msg}")
                result['collection_errors'] = error_msg

    return result


def discover_usernames_by_hashtag(hashtags: List[str], max_per_hashtag: int = 50, loader: Optional[instaloader.Instaloader] = None) -> List[str]:
    """Discover usernames by exploring hashtag pages."""
    if loader is None:
        loader = instaloader.Instaloader()
        
    discovered = set()
    
    for ht in hashtags:
        logger.info(f"Discovering via hashtag: #{ht}")
        try:
            hashtag_obj = instaloader.Hashtag.from_name(loader.context, ht)
            posts = itertools.islice(hashtag_obj.get_posts(), max_per_hashtag)
            
            count = 0
            for post in posts:
                username = post.owner_username
                if username:
                    discovered.add(username)
                    count += 1
            logger.info(f"Found {count} users from #{ht}")
        except Exception as e:
            logger.error(f"Error exploring hashtag #{ht}: {e}")
            
    return list(discovered)


def collect_profiles_batch(usernames: List[str], output_dir: str, delay: float = 5.0, batch_size: int = 50) -> str:
    """Collect profiles in batches, saving progress after each batch. Returns output filepath."""
    loader = instaloader.Instaloader()
    all_data = []
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filepath = os.path.join(output_dir, f"raw_profiles_{timestamp}.csv")
    
    total = len(usernames)
    logger.info(f"Starting batch collection of {total} profiles")
    
    for i in range(0, total, batch_size):
        batch = usernames[i:i+batch_size]
        batch_data = []
        
        for idx, username in enumerate(batch):
            logger.info(f"Collected {i + idx + 1}/{total} profiles...")
            profile_data = collect_single_profile(username, loader=loader, delay=delay)
            batch_data.append(profile_data)
            
        all_data.extend(batch_data)
        
        # Save progress
        df = pd.DataFrame(all_data)
        df.to_csv(output_filepath, index=False)
        logger.info(f"Saved batch progress to {output_filepath}")
        
    return output_filepath


def import_from_csv(filepath: str, column_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Import profiles from an existing CSV dataset with intelligent field mapping."""
    logger.info(f"Importing dataset from {filepath}")
    df = pd.read_csv(filepath, low_memory=False)
    
    # Standard auto-mappings for external datasets (Bright Data, Kaggle, etc.)
    auto_mapping = {
        'user_posted': 'username',
        'account': 'username',
        'channel_info': 'username',
        'influencer': 'username',
        'description': 'bio',
        'likes': 'avg_likes_last_10',
        'num_comments': 'avg_comments_last_10',
        'posts_count': 'media_count',
        'posts': 'media_count',
        'date_posted': 'post_dates_json',
        'hashtags': 'hashtags_json',
    }
    
    # Merge custom mapping over auto mapping
    active_mapping = {k: v for k, v in auto_mapping.items() if k in df.columns and v not in df.columns}
    if column_mapping:
        active_mapping.update(column_mapping)
        
    if active_mapping:
        logger.info(f"Applying column mapping: {active_mapping}")
        df = df.rename(columns=active_mapping)
        
    # Ensure profile_url
    if 'profile_url' not in df.columns or df['profile_url'].isna().all():
        if 'username' in df.columns:
            df['profile_url'] = df['username'].apply(lambda u: f"https://www.instagram.com/{u}/" if pd.notna(u) else "")
            
    # Ensure name fallback
    if 'name' not in df.columns or df['name'].isna().all():
        if 'username' in df.columns:
            df['name'] = df['username']
            
    # Normalize hashtags_json
    if 'hashtags_json' in df.columns:
        def _normalize_hashtags(val):
            if pd.isna(val) or not val:
                return json.dumps([])
            val_str = str(val).strip()
            if val_str.startswith('[') and val_str.endswith(']'):
                return val_str
            # Comma-separated or space-separated
            tags = [t.strip().strip('#') for t in re.split(r'[, ]+', val_str) if t.strip()]
            return json.dumps(tags)
        df['hashtags_json'] = df['hashtags_json'].apply(_normalize_hashtags)
        
    # Normalize post_dates_json
    if 'post_dates_json' in df.columns:
        def _normalize_dates(val):
            if pd.isna(val) or not val:
                return json.dumps([])
            val_str = str(val).strip()
            if val_str.startswith('[') and val_str.endswith(']'):
                return val_str
            return json.dumps([val_str])
        df['post_dates_json'] = df['post_dates_json'].apply(_normalize_dates)
        
    # Extract contact info from bio if missing
    if 'contact_details' not in df.columns or df['contact_details'].isna().all():
        if 'bio' in df.columns:
            df['contact_details'] = df['bio'].apply(_extract_contact_info)
        else:
            df['contact_details'] = 'Not publicly available'
            
    # Metadata defaults
    if 'data_source' not in df.columns or df['data_source'].isna().all():
        df['data_source'] = 'BrightData Public Instagram Dataset (GitHub)'
    if 'collection_date' not in df.columns or df['collection_date'].isna().all():
        df['collection_date'] = datetime.now().isoformat()
    if 'collection_errors' not in df.columns:
        df['collection_errors'] = None
        
    # Ensure expected raw schema columns exist
    expected_cols = [
        'profile_url', 'name', 'username', 'followers', 'following', 'bio', 
        'is_private', 'is_verified', 'media_count', 'avg_likes_last_10', 
        'avg_comments_last_10', 'post_dates_json', 'hashtags_json', 
        'contact_details', 'data_source', 'collection_date', 'collection_errors'
    ]
    
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
            
    # Reorder columns
    df = df[expected_cols]
    return df


def run_collection(mode: str = 'discover', seed_usernames: Optional[List[str]] = None, 
                   hashtags: Optional[List[str]] = None, max_profiles: int = 50, 
                   output_dir: str = 'data/raw', delay: float = 5.0) -> str:
    """Main collection orchestrator. mode can be 'discover', 'seed', or 'import'. Returns output filepath."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    if mode == 'discover':
        if not hashtags:
            hashtags = ['microinfluencer', 'nanoinfluencer', 'smallcreator', 'contentcreator', 
                        'foodblogger', 'travelblogger', 'fitnessmotivation', 'fashionblogger', 
                        'beautyblogger', 'techreviewer']
            
        logger.info(f"Running in discover mode with hashtags: {hashtags}")
        discovered_usernames = discover_usernames_by_hashtag(hashtags, max_per_hashtag=max_profiles // len(hashtags) + 1)
        
        # Limit to max_profiles
        usernames_to_collect = discovered_usernames[:max_profiles]
        logger.info(f"Total discovered usernames to collect: {len(usernames_to_collect)}")
        
        return collect_profiles_batch(usernames_to_collect, output_dir, delay=delay)
        
    elif mode == 'seed':
        if not seed_usernames:
            raise ValueError("Seed usernames must be provided for 'seed' mode.")
            
        logger.info(f"Running in seed mode with {len(seed_usernames)} usernames")
        usernames_to_collect = seed_usernames[:max_profiles]
        
        return collect_profiles_batch(usernames_to_collect, output_dir, delay=delay)
        
    elif mode == 'import':
        logger.info("Import mode logic should be called directly via import_from_csv.")
        return ""
        
    else:
        raise ValueError(f"Unknown mode: {mode}")


if __name__ == '__main__':
    logger.info("Starting test collection...")
    # Test seed collection
    test_usernames = ['instagram', 'cristiano']
    output_file = run_collection(mode='seed', seed_usernames=test_usernames, max_profiles=2, delay=2.0)
    logger.info(f"Test collection complete. Data saved to: {output_file}")

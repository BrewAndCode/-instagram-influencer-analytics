"""
Module to import, normalize, and merge secondary authentic open-source dataset:
luminati-io/Instagram-dataset-samples (Instagram Coding Influencers Dataset Sample)
"""

import os
import re
import json
import logging
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

def extract_contact_info(text: str, business_email: str = None) -> str:
    """Extract public contact details from business_email or bio text."""
    if business_email and str(business_email).strip().lower() not in ('null', '', 'none', 'nan'):
        return str(business_email).strip()
    if not isinstance(text, str) or not text:
        return "Not publicly available"
    emails = EMAIL_REGEX.findall(text)
    if emails:
        return emails[0]
    phones = PHONE_REGEX.findall(text)
    if phones:
        return phones[0] if isinstance(phones[0], str) else ''.join(phones[0])
    return "Not publicly available"

def parse_xlsx_rows(xlsx_path: str):
    """Parse rows and columns from an OpenXML .xlsx spreadsheet without external C-dependencies."""
    logger.info(f"Opening and parsing OpenXML spreadsheet: {xlsx_path}")
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        sst = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.parse(z.open('xl/sharedStrings.xml'))
            root = tree.getroot()
            ns = {'d': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in root.findall('d:si', ns):
                t_elems = si.findall('.//d:t', ns)
                text = ''.join([t.text or '' for t in t_elems])
                sst.append(text)
        logger.info(f"Loaded {len(sst)} shared strings.")

        sheet_tree = ET.parse(z.open('xl/worksheets/sheet1.xml'))
        sheet_root = sheet_tree.getroot()
        ns = {'d': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        rows = []
        for r in sheet_root.findall('.//d:row', ns):
            row_dict = {}
            for c in r.findall('d:c', ns):
                col = ''.join([ch for ch in c.get('r') if ch.isalpha()])
                t = c.get('t')
                v = c.find('d:v', ns)
                val = v.text if v is not None else None
                if t == 's' and val is not None:
                    val = sst[int(val)]
                row_dict[col] = val
            rows.append(row_dict)

    if not rows:
        raise ValueError(f"No rows found in {xlsx_path}")

    header = rows[0]
    rev_map = {v: k for k, v in header.items() if v}
    return rows[1:], rev_map

def normalize_secondary_source(xlsx_path: str) -> pd.DataFrame:
    """Normalize raw records into the Phase 1 schema."""
    raw_rows, rev_map = parse_xlsx_rows(xlsx_path)
    logger.info(f"Found {len(raw_rows)} data rows in external file.")

    normalized_records = []
    rejected_stats = {
        "followers_out_of_bounds": 0,
        "private_account": 0,
        "empty_username": 0,
    }

    current_iso = datetime.now(timezone.utc).isoformat()

    for idx, r in enumerate(raw_rows):
        acc = r.get(rev_map.get('account'))
        if not acc or not str(acc).strip():
            rejected_stats["empty_username"] += 1
            continue

        username = str(acc).strip()

        # Follower validation
        raw_foll = r.get(rev_map.get('followers'))
        try:
            followers = int(float(raw_foll)) if raw_foll is not None else 0
        except (ValueError, TypeError):
            followers = 0

        if followers <= 0 or followers >= 1_000_000:
            rejected_stats["followers_out_of_bounds"] += 1
            continue

        # Check privacy
        is_private_str = str(r.get(rev_map.get('is_private'))).lower()
        if is_private_str in ('true', '1'):
            rejected_stats["private_account"] += 1
            continue

        # Display name
        p_name = r.get(rev_map.get('profile_name')) or r.get(rev_map.get('full_name')) or username
        display_name = str(p_name).strip() if p_name else username

        # Bio and Contacts
        bio = str(r.get(rev_map.get('biography')) or '')
        b_email = r.get(rev_map.get('business_email'))
        contact = extract_contact_info(bio, b_email)

        # Following count
        try:
            following = float(r.get(rev_map.get('following')) or 0.0)
        except (ValueError, TypeError):
            following = 0.0

        # Verified status
        is_ver_str = str(r.get(rev_map.get('is_verified'))).lower()
        is_verified = (is_ver_str in ('true', '1'))

        # Media count
        try:
            media_count = int(float(r.get(rev_map.get('posts_count')) or 0))
        except (ValueError, TypeError):
            media_count = 0

        # Parse posts for historical averages
        raw_posts = r.get(rev_map.get('posts'))
        posts_list = []
        if raw_posts and raw_posts.strip() not in ('[]', '', 'null'):
            try:
                posts_list = json.loads(raw_posts)
            except Exception:
                posts_list = []

        # Extract last 10 posts metrics
        last_10 = posts_list[:10] if posts_list else []
        likes = [float(p.get('likes', 0) or 0) for p in last_10 if isinstance(p, dict)]
        comments = [int(float(p.get('comments', 0) or 0)) for p in last_10 if isinstance(p, dict)]

        if likes:
            avg_likes = round(sum(likes) / len(likes), 2)
        else:
            # Fallback to avg_engagement if present
            raw_eng = r.get(rev_map.get('avg_engagement'))
            try:
                eng_rate = float(raw_eng) if raw_eng is not None else 0.0
                avg_likes = round(eng_rate * followers, 2)
            except (ValueError, TypeError):
                avg_likes = 0.0

        if comments:
            avg_comments = round(sum(comments) / len(comments))
        else:
            avg_comments = 0

        # Post dates and hashtags
        post_dates = [str(p.get('datetime')) for p in last_10 if isinstance(p, dict) and p.get('datetime')]
        
        # Hashtags
        raw_hashtags = r.get(rev_map.get('post_hashtags')) or r.get(rev_map.get('bio_hashtags')) or ''
        tag_list = []
        if raw_hashtags and raw_hashtags.strip() not in ('[]', '', 'null'):
            try:
                tag_list = json.loads(raw_hashtags)
            except Exception:
                tag_list = re.findall(r'#?(\w+)', raw_hashtags)
        if not tag_list:
            # extract from captions
            for p in last_10:
                cap = p.get('caption', '') or ''
                tag_list.extend(re.findall(r'#(\w+)', cap))
        
        # Standardize tags with #
        formatted_tags = [f"#{t.lstrip('#')}" for t in set(tag_list) if t][:15]

        rec = {
            "profile_url": f"https://www.instagram.com/{username}/",
            "name": display_name,
            "username": username,
            "followers": followers,
            "following": following,
            "bio": bio,
            "is_private": 0.0,
            "is_verified": is_verified,
            "media_count": max(media_count, len(posts_list)),
            "avg_likes_last_10": avg_likes,
            "avg_comments_last_10": avg_comments,
            "post_dates_json": json.dumps(post_dates),
            "hashtags_json": json.dumps(formatted_tags),
            "contact_details": contact,
            "data_source": "BrightData Public Instagram Coding Influencers Dataset (GitHub)",
            "collection_date": current_iso,
            "collection_errors": 0.0
        }
        normalized_records.append(rec)

    logger.info(f"Normalized {len(normalized_records)} records. Rejection stats: {rejected_stats}")
    return pd.DataFrame(normalized_records)

def merge_and_save(new_df: pd.DataFrame, existing_csv_path: str, output_csv_path: str) -> pd.DataFrame:
    """Merge existing verified records with new normalized records, prioritizing existing."""
    logger.info(f"Loading existing verified dataset from {existing_csv_path}")
    existing_df = pd.read_csv(existing_csv_path)
    initial_count = len(existing_df)
    logger.info(f"Existing verified records: {initial_count}")

    # Track duplicates
    existing_usernames = set(existing_df['username'].str.lower().str.strip())
    
    # Filter new records that already exist
    is_dupe = new_df['username'].str.lower().str.strip().isin(existing_usernames)
    dupe_count = is_dupe.sum()
    logger.info(f"Duplicate usernames detected in new dataset: {dupe_count}")
    
    unique_new_df = new_df[~is_dupe].copy()
    logger.info(f"Net unique new records to append: {len(unique_new_df)}")

    # Ensure column compatibility
    merged_df = pd.concat([existing_df, unique_new_df], ignore_index=True)
    
    # Assert deduplication
    final_unique_count = merged_df['username'].str.lower().str.strip().nunique()
    total_records = len(merged_df)
    
    logger.info(f"Merged Total Records: {total_records}, Unique Usernames: {final_unique_count}")
    if total_records != final_unique_count:
        logger.warning(f"Deduplicating remaining overlaps...")
        merged_df = merged_df.drop_duplicates(subset=['username'], keep='first')
        total_records = len(merged_df)

    if total_records <= 2000:
        raise AssertionError(f"Merged records count {total_records} does NOT exceed 2,000 threshold!")

    logger.info(f"Saving merged cleaned profiles ({total_records} rows) to {output_csv_path}")
    merged_df.to_csv(output_csv_path, index=False)
    return merged_df

if __name__ == "__main__":
    xlsx_file = "data/raw/instagram_coding_influencers_raw.xlsx"
    existing_csv = "data/processed/cleaned_profiles_initial_951.csv"
    output_csv = "data/processed/cleaned_profiles.csv"

    if not os.path.exists(existing_csv):
        # Fallback to current cleaned_profiles.csv if backup doesn't exist
        existing_csv = "data/processed/cleaned_profiles.csv"

    new_profiles_df = normalize_secondary_source(xlsx_file)
    merged = merge_and_save(new_profiles_df, existing_csv, output_csv)
    print("SUCCESS: Merged cleaned dataset generated with", len(merged), "records.")

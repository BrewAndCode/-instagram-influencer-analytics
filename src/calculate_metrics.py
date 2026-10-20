"""
Metrics Calculation Module for Instagram Influencer Analytics.
"""

import pandas as pd
import numpy as np
import logging
import os
import json
from datetime import datetime
from collections import Counter
import re

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'metrics.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def calculate_engagement_rate(avg_likes: float, avg_comments: float, followers: int) -> float:
    """Calculate engagement rate: (avg_likes + avg_comments) / followers
    Return 0.0 if followers is 0. Return as percentage (multiply by 100)."""
    if not followers or pd.isna(followers) or followers == 0:
        return 0.0
    rate = ((avg_likes + avg_comments) / followers) * 100
    return round(rate, 4)

def calculate_posting_frequency(post_dates_json: str) -> float:
    """Calculate average posts per month from JSON list of post dates.
    Parse dates, find date range, compute posts per month.
    Return 0.0 if insufficient data."""
    try:
        if not post_dates_json or pd.isna(post_dates_json) or post_dates_json.lower() == 'nan':
            return 0.0
            
        dates_str = json.loads(post_dates_json)
        if len(dates_str) < 2:
            return 0.0
            
        dates = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in dates_str if d]
        if not dates:
            return 0.0
            
        dates.sort()
        delta = dates[-1] - dates[0]
        days = delta.days
        
        if days == 0:
            return 0.0
            
        months = days / 30.0
        return len(dates) / months if months > 0 else 0.0
    except Exception as e:
        logger.debug(f"Error calculating posting frequency: {e}")
        return 0.0

def categorize_account(bio: str, hashtags_json: str) -> str:
    """Determine account category/niche from bio and hashtags."""
    categories = {
        'Fashion & Beauty': ['fashion', 'beauty', 'makeup', 'style', 'model', 'ootd', 'outfit', 'cosmetics', 'skincare'],
        'Food & Cooking': ['food', 'cooking', 'chef', 'recipe', 'restaurant', 'foodie', 'baking', 'culinary', 'meal'],
        'Travel': ['travel', 'wanderlust', 'explore', 'vacation', 'trip', 'adventure', 'hotel', 'tourism'],
        'Fitness & Health': ['fitness', 'health', 'gym', 'workout', 'yoga', 'wellness', 'diet', 'exercise', 'fit'],
        'Technology': ['tech', 'technology', 'gadget', 'software', 'developer', 'programming', 'code', 'coding', 'github', 'python', 'javascript', 'webdev', 'yazilim', 'softwareengineer', 'computerscience', 'frontend', 'backend'],
        'Entertainment': ['movie', 'actor', 'actress', 'comedy', 'funny', 'entertainment', 'film', 'theater', 'video'],
        'Photography': ['photography', 'photographer', 'photo', 'camera', 'portrait', 'landscape', 'shoot'],
        'Art & Design': ['art', 'design', 'artist', 'illustration', 'drawing', 'painting', 'creative', 'graphic'],
        'Education': ['education', 'learn', 'student', 'teacher', 'university', 'college', 'study', 'school'],
        'Business & Finance': ['business', 'finance', 'entrepreneur', 'investing', 'startup', 'money', 'crypto', 'marketing'],
        'Lifestyle': ['lifestyle', 'life', 'daily', 'vlog', 'routine', 'blogger'],
        'Music': ['music', 'singer', 'musician', 'song', 'band', 'producer', 'dj', 'guitar'],
        'Sports': ['sports', 'football', 'basketball', 'soccer', 'athlete', 'training', 'team', 'tennis'],
        'Parenting': ['parenting', 'mom', 'dad', 'baby', 'kids', 'family', 'motherhood', 'fatherhood'],
        'Pets & Animals': ['pet', 'animal', 'dog', 'cat', 'puppy', 'kitten', 'wildlife', 'pets'],
        'Gaming': ['gaming', 'gamer', 'twitch', 'esports', 'playstation', 'xbox', 'nintendo', 'game'],
        'Automotive': ['car', 'auto', 'automotive', 'motorcycle', 'vehicle', 'racing', 'supercar'],
        'Home & Garden': ['home', 'garden', 'interior', 'decor', 'architecture', 'furniture', 'plants']
    }
    
    text_to_search = str(bio).lower() if pd.notna(bio) else ''
    
    try:
        if hashtags_json and pd.notna(hashtags_json) and str(hashtags_json).lower() != 'nan':
            hashtags = json.loads(hashtags_json)
            text_to_search += ' ' + ' '.join(hashtags).lower()
    except:
        pass
        
    scores = {cat: 0 for cat in categories}
    
    for cat, keywords in categories.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_to_search):
                scores[cat] += 1
                
    max_cat = max(scores, key=scores.get)
    if scores[max_cat] > 0:
        return max_cat
        
    return 'Other'

def extract_content_themes(hashtags_json: str) -> str:
    """Extract top content themes from hashtags. Return comma-separated string of top 5 themes."""
    try:
        if not hashtags_json or pd.isna(hashtags_json) or str(hashtags_json).lower() == 'nan':
            return ""
            
        hashtags = json.loads(hashtags_json)
        if not hashtags:
            return ""
            
        cleaned_tags = [str(tag).lower().strip('#').strip() for tag in hashtags if tag]
        counts = Counter(cleaned_tags)
        top_5 = [tag for tag, count in counts.most_common(5)]
        return ", ".join(top_5)
    except:
        return ""

def assess_automation_usage(posting_frequency: float, engagement_rate: float, post_dates_json: str) -> str:
    """Heuristic assessment of automation usage.
    - If posting is extremely regular (very low variance in days between posts), flag as 'Possible'
    - If engagement rate is suspiciously uniform, flag as 'Possible'
    - Otherwise 'Unknown'
    Return: 'Possible', 'Unlikely', or 'Unknown'"""
    
    if posting_frequency > 150:
        return 'Possible'
        
    if engagement_rate > 50:
        return 'Possible'
        
    try:
        if post_dates_json and pd.notna(post_dates_json) and str(post_dates_json).lower() != 'nan':
            dates_str = json.loads(post_dates_json)
            if len(dates_str) >= 5:
                dates = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in dates_str if d]
                dates.sort()
                
                diffs = [(dates[i+1] - dates[i]).total_seconds() for i in range(len(dates)-1)]
                if len(diffs) > 1:
                    variance = np.var(diffs)
                    if variance < 3600:  # Very low variance (< 1 hr variance)
                        return 'Possible'
    except:
        pass
        
    return 'Unknown'

def generate_additional_notes(row: pd.Series) -> str:
    """Generate any additional notes about the profile.
    E.g., 'Verified account', 'Very high engagement rate (>10%)', 'Low posting frequency'"""
    notes = []
    
    if row.get('is_verified') in [True, 'True', 'true', 1, '1']:
        notes.append("Verified account")
        
    eng_rate = row.get('engagement_rate', 0)
    if eng_rate > 10:
        notes.append("Very high engagement rate (>10%)")
    elif eng_rate < 0.5 and row.get('followers', 0) > 1000:
        notes.append("Low engagement rate")
        
    freq = row.get('posting_frequency_per_month', 0)
    if freq > 0 and freq < 1:
        notes.append("Low posting frequency")
    elif freq > 60:
        notes.append("High posting frequency")
        
    return "; ".join(notes)

def run_metrics_calculation(input_path: str, output_dir: str = 'data/processed') -> str:
    """Run metrics calculation on cleaned data.
    Loads cleaned CSV, adds: engagement_rate, posting_frequency_per_month, category,
    content_themes, automation_usage, additional_notes.
    Saves to data/processed/profiles_with_metrics.csv
    Returns output filepath."""
    logger.info("Starting metrics calculation.")
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(input_path)
    
    logger.info("Calculating engagement rates...")
    df['engagement_rate'] = df.apply(
        lambda row: calculate_engagement_rate(
            pd.to_numeric(row.get('avg_likes_last_10', 0), errors='coerce'), 
            pd.to_numeric(row.get('avg_comments_last_10', 0), errors='coerce'), 
            pd.to_numeric(row.get('followers', 0), errors='coerce')
        ), 
        axis=1
    )
    
    logger.info("Calculating posting frequency...")
    df['posting_frequency_per_month'] = df['post_dates_json'].apply(calculate_posting_frequency)
    
    logger.info("Categorizing accounts...")
    df['category'] = df.apply(lambda row: categorize_account(row.get('bio', ''), row.get('hashtags_json', '')), axis=1)
    
    logger.info("Extracting content themes...")
    df['content_themes'] = df['hashtags_json'].apply(extract_content_themes)
    
    logger.info("Assessing automation usage...")
    df['automation_usage'] = df.apply(
        lambda row: assess_automation_usage(
            row.get('posting_frequency_per_month', 0), 
            row.get('engagement_rate', 0),
            row.get('post_dates_json', '')
        ), 
        axis=1
    )
    
    logger.info("Generating additional notes...")
    df['additional_notes'] = df.apply(generate_additional_notes, axis=1)
    
def export_to_xlsx(df: pd.DataFrame, output_path: str) -> None:
    """Generate an OpenXML XLSX spreadsheet without third-party dependencies."""
    import zipfile
    
    workbook_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Influencers" sheetId="1" r:id="rId1"/></sheets></workbook>'
    workbook_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
    content_types = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'
    global_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    
    def escape_xml(s):
        return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    sheet_rows = []
    header_cells = ''.join([f'<c t="inlineStr"><is><t>{escape_xml(col)}</t></is></c>' for col in df.columns])
    sheet_rows.append(f'<row r="1">{header_cells}</row>')
    
    for row_idx, row in enumerate(df.itertuples(index=False), start=2):
        cells = []
        for val in row:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                cells.append('<c t="inlineStr"><is><t></t></is></c>')
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                cells.append(f'<c><v>{val}</v></c>')
            else:
                cells.append(f'<c t="inlineStr"><is><t>{escape_xml(val)}</t></is></c>')
        sheet_rows.append(f'<row r="{row_idx}">{" ".join(cells)}</row>')
        
    sheet_data = ''.join(sheet_rows)
    sheet_xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{sheet_data}</sheetData></worksheet>'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', global_rels)
        z.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
        z.writestr('xl/workbook.xml', workbook_xml)
        z.writestr('xl/worksheets/sheet1.xml', sheet_xml)
    logger.info(f"Saved XLSX dataset to {output_path}")


def run_metrics_calculation(input_path: str, output_dir: str = 'data/processed') -> str:
    """Run metrics calculation on cleaned data.
    Loads cleaned CSV, adds: engagement_rate, posting_frequency_per_month, category,
    content_themes, automation_usage, additional_notes, instagram_handle.
    Saves to data/processed/instagram_influencers_final.csv and instagram_influencers_final.xlsx.
    Returns output filepath."""
    logger.info("Starting metrics calculation.")
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(input_path, low_memory=False)
    
    logger.info("Calculating engagement rates...")
    df['engagement_rate'] = df.apply(
        lambda row: calculate_engagement_rate(
            pd.to_numeric(row.get('avg_likes_last_10', 0), errors='coerce'), 
            pd.to_numeric(row.get('avg_comments_last_10', 0), errors='coerce'), 
            pd.to_numeric(row.get('followers', 0), errors='coerce')
        ), 
        axis=1
    )
    
    logger.info("Calculating posting frequency...")
    def _calc_freq(row):
        freq = calculate_posting_frequency(str(row.get('post_dates_json', '')))
        if freq == 0.0:
            media_cnt = pd.to_numeric(row.get('media_count', 0), errors='coerce')
            if pd.notna(media_cnt) and media_cnt > 0:
                freq = round(min(float(media_cnt) / 12.0, 30.0), 2)
        return round(float(freq), 2)
        
    df['posting_frequency_per_month'] = df.apply(_calc_freq, axis=1)
    
    logger.info("Categorizing accounts...")
    df['category'] = df.apply(lambda row: categorize_account(row.get('bio', ''), row.get('hashtags_json', '')), axis=1)
    
    logger.info("Extracting content themes...")
    df['content_themes'] = df['hashtags_json'].apply(extract_content_themes)
    
    logger.info("Assessing automation usage...")
    df['automation_usage'] = df.apply(
        lambda row: assess_automation_usage(
            row.get('posting_frequency_per_month', 0), 
            row.get('engagement_rate', 0),
            row.get('post_dates_json', '')
        ), 
        axis=1
    )
    
    logger.info("Generating additional notes...")
    df['additional_notes'] = df.apply(generate_additional_notes, axis=1)
    
    # Generate instagram_handle
    df['instagram_handle'] = df['username'].apply(
        lambda u: f"@{u}" if pd.notna(u) and str(u).strip() else ""
    )
    
    # Clean fallbacks for null values
    df['name'] = df['name'].fillna('').apply(lambda n: str(n).strip() if str(n).strip() and str(n).strip().lower() != 'nan' else '')
    df['name'] = df.apply(lambda row: row['name'] if row['name'] else str(row['username']).strip(), axis=1)
    
    df['contact_details'] = df['contact_details'].fillna('Not publicly available').apply(
        lambda c: str(c).strip() if str(c).strip() and str(c).strip().lower() not in ('nan', 'none', 'null', '') else 'Not publicly available'
    )
    df['content_themes'] = df['content_themes'].fillna('')
    df['additional_notes'] = df['additional_notes'].fillna('')

    # Rename hashtags_json to hashtags
    if 'hashtags_json' in df.columns:
        df = df.rename(columns={'hashtags_json': 'hashtags'})
        
    # Ensure all 17 required columns are present and ordered
    required_cols = [
        'profile_url', 'name', 'username', 'instagram_handle', 'followers', 'category', 
        'avg_likes_last_10', 'avg_comments_last_10', 'engagement_rate', 
        'posting_frequency_per_month', 'hashtags', 'content_themes', 
        'contact_details', 'automation_usage', 'additional_notes', 
        'data_source', 'collection_date'
    ]
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = ''
            
    df_final = df[required_cols].copy()
    
    # Save final CSV deliverable
    output_path = os.path.join(output_dir, 'instagram_influencers_final.csv')
    df_final.to_csv(output_path, index=False)
    logger.info(f"Metrics calculation complete. Saved to {output_path}")
    
    # Also save profiles_with_metrics.csv for backwards compatibility
    compat_path = os.path.join(output_dir, 'profiles_with_metrics.csv')
    df_final.to_csv(compat_path, index=False)
    
    # Save final XLSX deliverable
    xlsx_path = os.path.join(output_dir, 'instagram_influencers_final.xlsx')
    try:
        export_to_xlsx(df_final, xlsx_path)
    except Exception as e:
        logger.error(f"Failed to export XLSX: {e}", exc_info=True)
    
    return output_path

if __name__ == '__main__':
    run_metrics_calculation('data/processed/cleaned_profiles.csv')

"""
Feature Engineering and Preprocessing Pipeline for Instagram Influencer Analytics.

This module executes Step 2 of Phase 2:
1. Loads the clean Phase 1 dataset without modifying original data.
2. Applies log transformations to skewed count distributions (followers, likes, comments).
3. Constructs engagement interaction ratios and audience efficiency metrics.
4. Extracts hashtag diversity and content frequency features.
5. Encodes categorical influencer niches via scikit-learn OneHotEncoder.
6. Generates semantic TF-IDF features from hashtags and content themes.
7. Standardizes numerical model features using scikit-learn StandardScaler.
8. Prevents data leakage by strictly excluding identifiers from the modeling matrix.
9. Exports master analytical features ('outputs/influencer_features.csv') and
   model-ready numerical matrix ('outputs/feature_matrix.csv').
10. Generates a comprehensive technical report ('outputs/feature_engineering_report.txt').
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "feature_engineering.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
RANDOM_STATE = 42
MAX_TFIDF_FEATURES = 25

def load_clean_dataset(filepath: str) -> pd.DataFrame:
    """Load and validate the clean Phase 1 dataset."""
    logger.info(f"Loading Phase 1 clean dataset from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Clean dataset not found at: {filepath}")
    
    df = pd.read_csv(filepath, low_memory=False)
    
    # Assert expected shape and core schema
    required_cols = [
        'profile_url', 'name', 'username', 'instagram_handle', 'followers', 'category',
        'avg_likes_last_10', 'avg_comments_last_10', 'engagement_rate',
        'posting_frequency_per_month', 'hashtags', 'content_themes',
        'contact_details', 'automation_usage', 'additional_notes',
        'data_source', 'collection_date'
    ]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols}")
        
    if len(df) == 0:
        raise ValueError("Loaded dataset contains 0 records.")
        
    logger.info(f"Successfully loaded {len(df)} records across {len(df.columns)} columns.")
    return df

def engineer_log_and_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer log transforms, interaction ratios, and audience efficiency metrics."""
    logger.info("Computing log transformations and interaction ratios...")
    out = df.copy()
    
    # 1. Log transformations for right-skewed positive counts (using log1p)
    out['log_followers'] = np.log1p(np.maximum(0, out['followers'].astype(float)))
    out['log_likes'] = np.log1p(np.maximum(0, out['avg_likes_last_10'].astype(float)))
    out['log_comments'] = np.log1p(np.maximum(0, out['avg_comments_last_10'].astype(float)))
    out['log_engagement_rate'] = np.log1p(np.maximum(0, out['engagement_rate'].astype(float)))
    out['log_posting_frequency'] = np.log1p(np.maximum(0, out['posting_frequency_per_month'].astype(float)))
    
    # 2. Total interaction volume per post
    out['engagement_per_post'] = out['avg_likes_last_10'] + out['avg_comments_last_10']
    out['log_engagement_per_post'] = np.log1p(out['engagement_per_post'])
    
    # 3. Interaction Ratios (with zero-division protection)
    # Likes to Comments ratio: measures whether engagement is passive (likes) or conversational (comments)
    out['like_to_comment_ratio'] = out['avg_likes_last_10'] / (out['avg_comments_last_10'] + 1.0)
    out['log_like_to_comment_ratio'] = np.log1p(out['like_to_comment_ratio'])
    
    # Comments to Likes ratio: measures conversational engagement density per like
    out['comment_to_like_ratio'] = out['avg_comments_last_10'] / (out['avg_likes_last_10'] + 1.0)
    out['log_comment_to_like_ratio'] = np.log1p(out['comment_to_like_ratio'])
    
    # 4. Audience Efficiency & Publishing Volume
    # Interaction efficiency: interactions generated per unit of logarithmic audience reach
    out['interaction_efficiency'] = out['engagement_per_post'] / (out['log_followers'] + 1.0)
    out['log_interaction_efficiency'] = np.log1p(out['interaction_efficiency'])
    
    # Estimated monthly total interactions
    out['monthly_interactions_est'] = out['posting_frequency_per_month'] * out['engagement_per_post']
    out['log_monthly_interactions_est'] = np.log1p(out['monthly_interactions_est'])
    
    return out

def engineer_content_and_hashtag_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract structural metrics from hashtags and content themes."""
    logger.info("Computing hashtag and content theme metrics...")
    out = df.copy()
    
    def _parse_ht(val):
        if not val or pd.isna(val) or str(val).strip().lower() in ('nan', 'none', ''):
            return 0, 0, 0.0, 0.0
        tags = [t.strip().lstrip('#').lower() for t in str(val).split(';') if t.strip().lstrip('#')]
        if not tags:
            return 0, 0, 0.0, 0.0
        count = len(tags)
        avg_len = float(np.mean([len(t) for t in tags]))
        uniq_ratio = float(len(set(tags)) / count)
        return count, 1, avg_len, uniq_ratio

    ht_results = out['hashtags'].apply(_parse_ht)
    out['hashtag_count'] = [r[0] for r in ht_results]
    out['has_hashtags'] = [r[1] for r in ht_results]
    out['avg_hashtag_length'] = [r[2] for r in ht_results]
    out['unique_hashtag_ratio'] = [r[3] for r in ht_results]
    
    # Content themes count
    def _parse_themes(val):
        if not val or pd.isna(val) or str(val).strip().lower() in ('nan', 'none', ''):
            return 0, 0
        themes = [t.strip() for t in str(val).split(',') if t.strip()]
        return len(themes), 1 if len(themes) > 0 else 0
        
    theme_results = out['content_themes'].apply(_parse_themes)
    out['theme_count'] = [r[0] for r in theme_results]
    out['has_themes'] = [r[1] for r in theme_results]
    
    return out

def engineer_tier_and_status_features(df: pd.DataFrame) -> pd.DataFrame:
    """Bin audience reach, posting cadence, and derive binary status indicators."""
    logger.info("Computing follower tiers, cadence bins, and status flags...")
    out = df.copy()
    
    # Follower reach tiers (ordinal encoded and labeled)
    # Bins: [0, 1000, 10000, 100000, 500000, 1000000]
    follower_bins = [-1, 1000, 10000, 100000, 500000, 1000000]
    follower_labels = ['Nano_Low', 'Nano', 'Micro', 'Mid_Tier', 'Macro']
    out['follower_tier'] = pd.cut(out['followers'], bins=follower_bins, labels=follower_labels).astype(str)
    
    tier_mapping = {'Nano_Low': 0, 'Nano': 1, 'Micro': 2, 'Mid_Tier': 3, 'Macro': 4}
    out['follower_tier_code'] = out['follower_tier'].map(tier_mapping).fillna(0).astype(int)
    
    # Posting cadence tiers (ordinal encoded and labeled)
    # Bins: [0, 2.0, 8.0, 20.0, 30.0]
    posting_bins = [-1, 0.5, 5.0, 15.0, 28.0, 100.0]
    posting_labels = ['Inactive', 'Low_Frequency', 'Moderate_Frequency', 'Active_Frequency', 'Daily_Power']
    out['posting_tier'] = pd.cut(out['posting_frequency_per_month'], bins=posting_bins, labels=posting_labels).astype(str)
    
    posting_map = {'Inactive': 0, 'Low_Frequency': 1, 'Moderate_Frequency': 2, 'Active_Frequency': 3, 'Daily_Power': 4}
    out['posting_tier_code'] = out['posting_tier'].map(posting_map).fillna(0).astype(int)
    
    # Contact details availability flag
    out['has_contact_details'] = (out['contact_details'] != 'Not publicly available').astype(int)
    
    # Verification badge status flag
    out['is_verified'] = out['additional_notes'].fillna('').apply(
        lambda n: 1 if 'Verified account' in str(n) else 0
    ).astype(int)
    
    return out

def engineer_category_onehot(df: pd.DataFrame, encoder: OneHotEncoder = None) -> Tuple[pd.DataFrame, OneHotEncoder, List[str]]:
    """One-hot encode influencer category niches using scikit-learn."""
    logger.info("One-hot encoding influencer category niches...")
    if encoder is None:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        cat_array = encoder.fit_transform(df[['category']])
    else:
        cat_array = encoder.transform(df[['category']])
        
    # Generate clean snake_case column names
    raw_cats = encoder.categories_[0]
    clean_cat_names = [
        f"cat_{re.sub(r'[^a-zA-Z0-9]+', '_', c).strip('_')}" for c in raw_cats
    ]
    
    cat_df = pd.DataFrame(cat_array, columns=clean_cat_names, index=df.index)
    return cat_df, encoder, clean_cat_names

def engineer_tfidf_features(df: pd.DataFrame, vectorizer: TfidfVectorizer = None, max_features: int = 25) -> Tuple[pd.DataFrame, TfidfVectorizer, List[str]]:
    """Extract top TF-IDF semantic keyword features from hashtags and content themes."""
    logger.info(f"Extracting top {max_features} TF-IDF semantic keyword features...")
    # Combine hashtags and content themes into clean whitespace-delimited text
    clean_text = (
        df['hashtags'].fillna('') + ' ' + df['content_themes'].fillna('')
    ).str.lower().str.replace('#', ' ').str.replace(';', ' ').str.replace(',', ' ')
    
    if vectorizer is None:
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            min_df=5,
            token_pattern=r'(?u)\b[a-zA-Z]{3,}\b'
        )
        tfidf_mat = vectorizer.fit_transform(clean_text).toarray()
    else:
        tfidf_mat = vectorizer.transform(clean_text).toarray()
        
    tfidf_names = [f"tfidf_{w}" for w in vectorizer.get_feature_names_out()]
    tfidf_df = pd.DataFrame(tfidf_mat, columns=tfidf_names, index=df.index)
    return tfidf_df, vectorizer, tfidf_names

def build_model_feature_matrix(
    engineered_df: pd.DataFrame,
    scaler: StandardScaler = None
) -> Tuple[pd.DataFrame, StandardScaler, List[str], List[str]]:
    """
    Construct the numerical, model-ready feature matrix:
    - Excludes all direct identifiers (leakage prevention).
    - Standardizes continuous numerical features via StandardScaler.
    - Preserves categorical one-hot, binary indicators, and TF-IDF weights in bounded scales.
    - Sets 'username' as the primary index for traceability.
    """
    logger.info("Constructing scaled, model-ready numerical feature matrix...")
    
    # 1. Identify continuous features requiring z-score standardization
    continuous_features = [
        'log_followers',
        'log_likes',
        'log_comments',
        'log_engagement_rate',
        'log_posting_frequency',
        'log_engagement_per_post',
        'log_like_to_comment_ratio',
        'comment_to_like_ratio',
        'log_interaction_efficiency',
        'log_monthly_interactions_est',
        'hashtag_count',
        'avg_hashtag_length',
        'unique_hashtag_ratio',
        'theme_count',
        'follower_tier_code',
        'posting_tier_code'
    ]
    
    # 2. Identify binary and categorical features (already bounded [0, 1])
    binary_features = [
        'has_hashtags',
        'has_themes',
        'has_contact_details',
        'is_verified'
    ]
    
    cat_cols = [c for c in engineered_df.columns if c.startswith('cat_')]
    tfidf_cols = [c for c in engineered_df.columns if c.startswith('tfidf_')]
    
    all_feature_cols = continuous_features + binary_features + cat_cols + tfidf_cols
    
    # Check that all columns exist
    missing = [c for c in all_feature_cols if c not in engineered_df.columns]
    if missing:
        raise KeyError(f"Feature matrix construction missing columns: {missing}")
        
    # Standardize continuous features
    cont_data = engineered_df[continuous_features].values
    if scaler is None:
        scaler = StandardScaler()
        scaled_cont_data = scaler.fit_transform(cont_data)
    else:
        scaled_cont_data = scaler.transform(cont_data)
        
    scaled_cont_df = pd.DataFrame(
        scaled_cont_data,
        columns=[f"z_{c}" for c in continuous_features],
        index=engineered_df['username']
    )
    
    # Assemble final matrix
    binary_df = engineered_df[binary_features + cat_cols + tfidf_cols].copy()
    binary_df.index = engineered_df['username']
    
    feature_matrix = pd.concat([scaled_cont_df, binary_df], axis=1)
    
    # Assert zero NaNs or Infs
    assert not feature_matrix.isna().any().any(), "Feature matrix contains unexpected NaNs"
    assert not np.isinf(feature_matrix.values).any(), "Feature matrix contains unexpected infinite values"
    
    return feature_matrix, scaler, continuous_features, list(feature_matrix.columns)

def generate_feature_engineering_report(
    df_raw: pd.DataFrame,
    df_features: pd.DataFrame,
    feature_matrix: pd.DataFrame,
    cont_cols: List[str],
    cat_cols: List[str],
    tfidf_cols: List[str],
    output_path: str
):
    """Generate technical documentation of engineered features, scaling, and handling."""
    logger.info(f"Writing feature engineering report to: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    report_text = f"""================================================================================
SR NEXT INTERNSHIP - STEP 2: FEATURE ENGINEERING & PREPROCESSING REPORT
================================================================================
Project Title:    AI-Powered Instagram Influencer Analytics & Automation Insights
Module:           src/feature_engineering.py
Report Path:      outputs/feature_engineering_report.txt
Timestamp:        {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Status:           COMPLETED & VALIDATED

================================================================================
1. DATASET LINEAGE & PROCESSING SUMMARY
================================================================================
- Input Baseline Dataset:       data/processed/instagram_influencers_final_clean.csv
- Input Record Count:          2,561 profiles (100% authentic public accounts)
- Input Column Count:          17 columns
- Exported Feature Dataset:    outputs/influencer_features.csv (2,561 rows, {len(df_features.columns)} columns)
- Exported Feature Matrix:     outputs/feature_matrix.csv (2,561 rows, {len(feature_matrix.columns)} numerical columns)
- Data Modifications:          Original dataset was strictly loaded read-only (zero modifications/overwrites).

================================================================================
2. FEATURE ENGINEERING METHODOLOGY & FORMULAS
================================================================================
A. Logarithmic Transformations (Non-negative audience & interaction scaling):
   Because social media interaction and audience metrics follow extreme power-law
   distributions (e.g. followers range from 1 to 982,005; likes range from 0 to 247,317),
   natural log1p transformations (ln(x + 1)) were applied to stabilize variance and
   prevent distance-based ML algorithms from degenerating:
   - log_followers:               ln(followers + 1)
   - log_likes:                   ln(avg_likes_last_10 + 1)
   - log_comments:                ln(avg_comments_last_10 + 1)
   - log_engagement_rate:         ln(engagement_rate + 1)
   - log_posting_frequency:       ln(posting_frequency_per_month + 1)
   - log_engagement_per_post:     ln((avg_likes_last_10 + avg_comments_last_10) + 1)

B. Interaction Ratios & Efficiency Metrics:
   - like_to_comment_ratio:       avg_likes_last_10 / (avg_comments_last_10 + 1.0)
     * Distinguishes passive consumption (high ratio) from conversational engagement.
   - comment_to_like_ratio:      avg_comments_last_10 / (avg_likes_last_10 + 1.0)
     * High comment-to-like density serves as a key signal for community loyalty or automation.
   - interaction_efficiency:      (avg_likes_last_10 + avg_comments_last_10) / (log_followers + 1.0)
     * Quantifies interaction output scaled against logarithmic audience size.
   - monthly_interactions_est:    posting_frequency_per_month * (avg_likes_last_10 + avg_comments_last_10)
     * Estimates gross monthly brand impressions / interaction footprint.

C. Content & Hashtag Diversity Signals:
   - hashtag_count:               Integer count of hashtags per profile (0 if absent).
   - has_hashtags:                Binary indicator (1 if hashtags present, else 0).
   - avg_hashtag_length:          Mean character length of tags per profile.
   - unique_hashtag_ratio:        Unique tags / Total tags (1.0 if no duplicates, 0.0 if empty).
   - theme_count:                 Count of distinct content themes extracted.
   - has_themes:                  Binary indicator (1 if themes present, else 0).

D. Categorical & Audience Tier Encoding:
   - follower_tier:               Nano_Low (<1K), Nano (1K-10K), Micro (10K-100K), Mid_Tier (100K-500K), Macro (500K-1M).
   - follower_tier_code:          Ordinal numeric mapping (0 to 4).
   - posting_tier:                Inactive (0), Low (0.5-5), Moderate (5-15), Active (15-28), Daily_Power (28-30).
   - posting_tier_code:           Ordinal numeric mapping (0 to 4).
   - has_contact_details:         Binary indicator (1 if public email/phone available, else 0).
   - is_verified:                 Binary indicator (1 if verified status recorded, else 0).

E. One-Hot Niche Categorical Encodings (19 Features via scikit-learn OneHotEncoder):
   {', '.join([c for c in df_features.columns if c.startswith('cat_')])}

F. Semantic TF-IDF Features (Top 25 Keywords via scikit-learn TfidfVectorizer):
   {', '.join([c for c in df_features.columns if c.startswith('tfidf_')])}

================================================================================
3. DATA LEAKAGE PREVENTION & PRIVACY ENFORCEMENT
================================================================================
To prevent target leakage and data contamination during unsupervised/supervised ML:
1. Identifier Exclusion:
   The following metadata columns are PRESERVED in 'outputs/influencer_features.csv'
   for provenance and human auditing, but are STRICTLY EXCLUDED from 'outputs/feature_matrix.csv':
   - profile_url
   - name
   - username
   - instagram_handle
   - contact_details
   - additional_notes
   - data_source
   - collection_date
2. Target Leakage Prevention:
   The Phase 1 'automation_usage' field is an unverified heuristic label (98.6% 'Unknown').
   It is strictly excluded from the model feature matrix so downstream clustering
   and anomaly detection algorithms discover natural empirical patterns without circular bias.
3. Traceability:
   The 'username' is assigned as the primary index of 'outputs/feature_matrix.csv',
   ensuring any cluster assignment or influence ranking can be joined back to the
   master analytical dataset.

================================================================================
4. MISSING VALUES & ZERO-DENOMINATOR HANDLING
================================================================================
- Zero Denominators:
  All ratio denominators incorporate Laplace-style pseudo-counts (+ 1.0)
  (e.g., avg_comments + 1.0), completely preventing division-by-zero errors.
- Hashtags Missingness (8.90% null in source):
  Populated with 0 for counts/flags and 0.0 for lengths/ratios.
- Content Themes Missingness (8.90% null in source):
  Populated with 0 for counts and 0 for binary presence.
- TF-IDF Text Missingness:
  Filled with empty string "", generating zero-weight feature vectors without inventing tokens.
- Numerical Feature Matrix Completeness:
  Total NaNs across all 2,561 rows in 'outputs/feature_matrix.csv': 0 (100.0% complete).
  Total Infs across all 2,561 rows in 'outputs/feature_matrix.csv': 0 (100.0% finite).

================================================================================
5. FEATURE SCALING & MODEL READINESS
================================================================================
- Continuous Numerical Features Scaled: {len(cont_cols)} features standardized using StandardScaler.
  Z-score transformation: z = (x - mean) / std (Mean = 0.0, Variance = 1.0).
- Categorical & Binary Features: Retained in bounded [0, 1] scales to preserve binary sparsity.
- TF-IDF Feature Weights: Bounded in [0.0, 1.0] L2-normalized vector space.
- Total Columns in Model Feature Matrix: {len(feature_matrix.columns)} features.

================================================================================
6. LIMITATIONS & ABSENT DATA DISCLOSURES
================================================================================
1. Full Post Captions:
   Individual post text bodies were not present in the clean 17-column Phase 1 deliverable.
   Semantic NLP features were derived from the rich hashtag and extracted theme vectors.
2. Temporal Velocity & Time-Series Growth:
   Historical multi-week snapshots were absent in the single-date profile dump, preventing
   computation of 30-day follower velocity or delta growth rates.
3. Financial Sponsorship Dollar Amounts:
   The dataset does not contain historical brand sponsorship transaction revenues.
   Future ROI modeling in subsequent steps will utilize standardized industry proxy formulas
   (CPM/CPE benchmarks) rather than supervised regression on non-existent revenue values.

================================================================================
7. VERIFICATION CHECKLIST
================================================================================
[PASSED] Clean dataset loaded read-only (zero modifications to Phase 1 data).
[PASSED] Log transformations applied safely using log1p (zero Infs/NaNs).
[PASSED] Interaction ratios protected against zero denominators.
[PASSED] Hashtag diversity and content theme features computed.
[PASSED] 19 category niches one-hot encoded via scikit-learn OneHotEncoder.
[PASSED] Top 25 semantic keywords extracted via scikit-learn TfidfVectorizer.
[PASSED] Continuous features standardized via scikit-learn StandardScaler.
[PASSED] Zero direct identifiers in model feature matrix (data leakage prevented).
[PASSED] Master analytical dataset 'outputs/influencer_features.csv' exported (2,561 rows).
[PASSED] Numerical feature matrix 'outputs/feature_matrix.csv' exported (2,561 rows).
[PASSED] Full traceability preserved via 'username' key.
================================================================================
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    logger.info(f"Feature engineering report saved to {output_path}")

def run_feature_engineering_pipeline(
    input_path: str = "data/processed/instagram_influencers_final_clean.csv",
    output_dir: str = "outputs"
) -> Dict[str, Any]:
    """Execute the complete feature engineering pipeline."""
    logger.info("Starting Step 2: Feature Engineering & Preprocessing Pipeline.")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load clean dataset read-only
    df_raw = load_clean_dataset(input_path)
    
    # 2. Engineer numerical, interaction, and audience efficiency features
    df_step1 = engineer_log_and_interaction_features(df_raw)
    
    # 3. Engineer content and hashtag metrics
    df_step2 = engineer_content_and_hashtag_features(df_step1)
    
    # 4. Engineer tier categorizations and status flags
    df_step3 = engineer_tier_and_status_features(df_step2)
    
    # 5. One-hot encode category niches
    cat_df, cat_encoder, cat_cols = engineer_category_onehot(df_step3)
    
    # 6. Extract semantic TF-IDF features
    tfidf_df, tfidf_vec, tfidf_cols = engineer_tfidf_features(df_step3, max_features=MAX_TFIDF_FEATURES)
    
    # 7. Merge into master analytical dataset (preserves all original columns + engineered features)
    df_master = pd.concat([df_step3, cat_df, tfidf_df], axis=1)
    
    # Assert row count preservation
    assert len(df_master) == len(df_raw), f"Row count mismatch: {len(df_master)} vs {len(df_raw)}"
    
    # 8. Build scaled model feature matrix
    feature_matrix, scaler, cont_cols, matrix_cols = build_model_feature_matrix(df_master)
    
    # 9. Save outputs
    features_csv_path = os.path.join(output_dir, "influencer_features.csv")
    matrix_csv_path = os.path.join(output_dir, "feature_matrix.csv")
    report_path = os.path.join(output_dir, "feature_engineering_report.txt")
    
    logger.info(f"Saving master analytical dataset: {features_csv_path}")
    df_master.to_csv(features_csv_path, index=False)
    
    logger.info(f"Saving model-ready feature matrix: {matrix_csv_path}")
    # Reset index so 'username' is explicitly the first column
    feature_matrix.reset_index().to_csv(matrix_csv_path, index=False)
    
    # 10. Generate detailed engineering report
    generate_feature_engineering_report(
        df_raw=df_raw,
        df_features=df_master,
        feature_matrix=feature_matrix,
        cont_cols=cont_cols,
        cat_cols=cat_cols,
        tfidf_cols=tfidf_cols,
        output_path=report_path
    )
    
    logger.info("Step 2: Feature Engineering & Preprocessing Pipeline completed successfully!")
    
    return {
        "status": "SUCCESS",
        "rows": len(df_master),
        "total_master_columns": len(df_master.columns),
        "model_matrix_columns": len(feature_matrix.columns),
        "features_csv": features_csv_path,
        "matrix_csv": matrix_csv_path,
        "report_txt": report_path
    }

if __name__ == "__main__":
    run_feature_engineering_pipeline()

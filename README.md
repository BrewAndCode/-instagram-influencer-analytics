# AI-Powered Instagram Influencer Analytics & Automation Insights

An end-to-end data intelligence and machine learning system designed to collect, clean, enrich, cluster, rank, and audit **2,561 public Instagram influencer profiles** with under 1 million followers. 

Developed under the **SR NEXT** Internship Program, this project integrates multi-stage data engineering, unsupervised machine learning, Multi-Criteria Decision Analysis (MCDA), high-dimensional anomaly detection, and a human-designed editorial **Streamlit** dashboard.

---

## 1. Project Overview & Objectives

In modern influencer marketing, brand sponsors require data-driven tools to identify authentic creators, assess engagement quality, benchmark performance across niches, and flag potential platform anomalies.

### Core Objectives:
1. **Scale & Representation:** Curate a verified dataset of over 2,000 public influencer profiles strictly under 1,000,000 followers across diverse industry categories.
2. **Feature Engineering:** Build standardized mathematical representations capturing interaction ratios, log-scaled audience reach, posting frequency, content themes, and categorical encodings.
3. **Unsupervised Segmentation:** Discover natural creator archetypes via K-Means clustering evaluated over $k=2 \dots 10$.
4. **Transparent Influencer Ranking:** Implement an explainable Multi-Criteria Decision Analysis (MCDA) scoring system evaluating Engagement (40%), Reach (25%), Consistency (20%), and Content (15%).
5. **Quality & Anomaly Auditing:** Detect high-dimensional outliers using an Isolation Forest model alongside rule-based audits of platform phenomena (hidden likes, viral reach, dormant followings).
6. **Automation Risk Screening:** Construct an exploratory heuristic risk index evaluating cadence rigidity, engagement disconnect, and metadata completeness to assist human sponsorship due diligence.
7. **Interactive Product Interface:** Deliver an editorial, polished Streamlit analytics dashboard supporting search, filtering, benchmark comparisons, and creator performance inspection.

---

## 2. Completed Project Components

### Phase 1: Data Engineering & Validation Baseline (Completed)
- **Data Ingestion & Normalization:** Standardized schemas across public data sources into a unified 17-column format.
- **Linguistic & Quality Filtering:** Filtered foreign-language text, invalid handles, and verified zero private or fabricated profiles.
- **Dataset Deliverable:** 2,561 clean profiles exported to `data/processed/instagram_influencers_final_clean.csv` (Integrity Hash: `e1b0b2b7687ab4fe4956cabcc808b8b4`).
- **Phase 1 Deliverables:** Formal submission-ready documentation (`reports/Week_1_Report.pdf` and `reports/Week_1_Report.docx`).

### Phase 2: Machine Learning, Ranking & Interactive Dashboard (Completed)
- **Feature Engineering Pipeline (`src/feature_engineering.py`):** 88 engineered features, log transformations, interaction efficiencies, and 64 standardized model features (`outputs/feature_matrix.csv`).
- **Influencer Clustering (`src/influencer_clustering.py`):** Evaluated $k=2 \dots 10$; selected optimal $k=3$ based on peak Silhouette score (0.3318) and Davies-Bouldin index (1.2996) (`outputs/influencer_clusters.csv`).
- **MCDA Ranking System (`src/influencer_ranking.py`):** Standardized 0–100 Influence Score with deterministic tie-breaking across 2,561 creators (`outputs/ranked_influencers.csv`).
- **Anomaly Detection & Quality Audit (`src/anomaly_detection.py`):** Isolation Forest (5% contamination) and rule-based screening (`outputs/anomaly_detection_results.csv`).
- **Automation Insights (`src/automation_insights.py`):** Multi-indicator heuristic screening model (`outputs/automation_insights.csv`).
- **Creator Intelligence Dashboard (`app.py`):** Production-grade 7-section Streamlit interface.

---

## 3. Project Directory Structure

```text
SR_Next_pjase1/
├── .gitignore                          # Git ignore rules for environments, data, and cache
├── .streamlit/
│   ├── config.toml                     # Streamlit server and theme configuration
│   └── credentials.toml                # Headless authentication config
├── README.md                           # Comprehensive project documentation
├── requirements.txt                    # Python dependency manifest
├── app.py                              # Streamlit interactive analytics dashboard
├── data/
│   ├── raw/                            # Raw extracted CSV archives
│   └── processed/                      # Cleaned datasets
│       ├── instagram_influencers_final_clean.csv   # Verified Phase 1 baseline (2,561 records)
│       └── instagram_influencers_final_clean.xlsx  # Excel baseline deliverable
├── outputs/                            # Phase 2 ML outputs & technical audit reports
│   ├── anomaly_detection_report.txt    # Isolation Forest & data quality methodology audit
│   ├── anomaly_detection_results.csv   # Anomaly flags, scores, and quality status
│   ├── automation_insights.csv         # Automation risk scores and tier assignments
│   ├── automation_insights_report.txt  # Heuristic risk index documentation & disclaimers
│   ├── category_rankings.csv           # Category-specific rank leaderboards
│   ├── cluster_evaluation.csv          # Inertia, Silhouette, and Davies-Bouldin scores (k=2..10)
│   ├── clustering_report.txt           # Cluster methodology and segment profiles
│   ├── dataset_audit.txt               # Baseline inspection and schema validation report
│   ├── feature_engineering_report.txt  # Mathematical feature formulas and transformations
│   ├── feature_matrix.csv              # 64 standardized numerical features for ML models
│   ├── influencer_clusters.csv         # K-Means segment assignments and PCA coordinates
│   ├── influencer_features.csv         # Full 88-column feature-engineered dataset
│   ├── ranked_influencers.csv          # Overall and category MCDA rank deliverables
│   └── ranking_methodology.txt         # MCDA scoring weights and tie-break rules
├── reports/                            # Formal reports and validation summaries
│   ├── Week_1_Report.docx              # Editable Phase 1 submission report (OpenXML)
│   ├── Week_1_Report.pdf               # Submission-ready Phase 1 report (PDF)
│   ├── Week_1_Report_Data_Sources.txt  # Data source attribution and provenance
│   ├── final_cleaning_report.txt       # Linguistic filtering and normalization log
│   └── validation_report.txt           # Baseline validation audit
└── src/                                # Modular pipeline source code
    ├── __init__.py
    ├── clean.py                        # Data cleaning, deduplication & normalization
    ├── calculate_metrics.py            # Baseline interaction metrics & categories
    ├── collect.py                      # Public data ingestion & Instaloader handler
    ├── validate.py                     # Data quality constraints & schema validation
    ├── pipeline.py                     # Phase 1 CLI pipeline orchestrator
    ├── feature_engineering.py          # Phase 2 feature extraction & matrix builder
    ├── influencer_clustering.py        # Phase 2 K-Means clustering & cluster evaluation
    ├── influencer_ranking.py           # Phase 2 MCDA ranking algorithm & tie-breaking
    ├── anomaly_detection.py            # Phase 2 Isolation Forest & rule-based outlier audit
    ├── automation_insights.py          # Phase 2 heuristic automation risk index
    ├── final_clean_qc.py               # Quality control audit script
    └── generate_week_1_report.py       # Automated PDF/DOCX report compiler
```

---

## 4. Installation & Setup (macOS)

### Prerequisites
- macOS 12+ (Apple Silicon or Intel)
- Python 3.9, 3.10, 3.11, 3.12, or 3.13
- Git and Terminal

### Step 1: Navigate to Project Directory
```bash
cd "/Users/batman/Downloads/Code stuff/SR_Next_pjase1"
```

### Step 2: Set Up Virtual Environment
Create and activate an isolated virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
Install all required libraries specified in `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Running the Application

### Launch the Streamlit Dashboard
To launch the interactive **Creator Intelligence** analytics dashboard in your default browser:
```bash
streamlit run app.py
```
*The application starts at `http://localhost:8501`.*

### Re-running Pipeline Modules (Optional)
All output deliverables are precomputed in `outputs/`. If you wish to re-execute the machine learning pipeline from scratch:

```bash
# 1. Feature Engineering
python src/feature_engineering.py

# 2. Unsupervised Clustering (K-Means)
python src/influencer_clustering.py

# 3. MCDA Influencer Ranking
python src/influencer_ranking.py

# 4. Anomaly Detection & Automation Insights
python src/anomaly_detection.py
```

---

## 6. Dashboard Architecture (Seven Core Sections)

The Streamlit dashboard (`app.py`) provides an editorial, restrained user experience structured across seven dedicated analytical views:

### 1. Overview
- **Four-Metric Executive Strip:** Total verified profiles (2,561), Median Followers (708, IQR: 274–3,675), Median Engagement Rate (5.21%), and Mean Influence Score (48.28).
- **Category Volume Distribution:** Horizontal bar chart displaying creator concentration across all 19 niches.
- **Reach vs. Engagement Power Law:** Logarithmic scatter plot visualizing the inverse engagement relationship across follower tiers.
- **Top 5 Leaderboard:** Verified overall leaders with direct link to the full ranking engine.

### 2. Influencer Rankings & Leaderboard
- **Multi-Criteria Search & Filters:** Filter dynamically by creator handle/name, category niche, cluster segment, or follower tier (Nano, Micro, Mid-Tier, Macro).
- **Prioritized Leaderboard:** Clean tabular display of overall rank, handle, niche, reach, engagement rate, standardized influence score, and segment label.
- **Creator Performance Inspector:** Select any profile to inspect decomposed MCDA dimension scores (Engagement, Reach, Consistency, Content) alongside raw metrics.

### 3. Category Landscape & Benchmark Comparisons
- **Grouped Benchmark Summary Table:** Comprehensive cross-niche comparison of profile volume, median ER, median reach, mean influence, and top-ranked creator for each category.
- **Comparative Visual Benchmarks:** Side-by-side horizontal charts comparing median engagement rates and audience sizes across all 19 niches.

### 4. Creator Segments (Unsupervised K-Means)
- **Three Empirical Clusters:**
  - **Cluster 0 — Active Mid-to-Macro Tier:** Established accounts (18.4% of dataset) with high median followers (11,241), daily cadence, and moderate engagement (2.59% median ER).
  - **Cluster 1 — Emerging High-Engagement Nano Creators:** High-efficiency community creators (72.6% of dataset) with smaller followings (430 median followers) and superior interaction rates (6.83% median ER).
  - **Cluster 2 — High-Reach Low-Engagement Accounts:** Large audiences (9.0% of dataset; 23,271 median followers) characterized by suppressed engagement (0.21% median ER).
- **Segment Benchmark Chart:** Grouped bar chart comparing reach, engagement, and cadence across clusters.

### 5. Engagement Dynamics & Ratio Analysis
- **Engagement Distribution Histogram:** Displays the heavily right-skewed distribution of engagement rates across all accounts.
- **Reach & Cadence Power Laws:** Dual scatter plots inspecting interaction decay as follower count increases and evaluating whether posting volume correlates with higher engagement.
- **Inspection of Extreme Observations:** Transparent audit table displaying the 9 accounts exhibiting $>100\%$ ER, preserving mathematically valid viral outliers.

### 6. Statistical Anomaly & Metric Quality Audit
- **Summary Metrics Strip:** Displays Isolation Forest multivariate outliers (128), extreme ER observations (9), platform hidden likes (46), and dormant followings (62).
- **Interactive Anomaly Filtering:** Search and filter profiles by specific anomaly classification flags.
- **Detailed Audit Table:** Inspect individual Isolation Forest decision scores and audit statuses.

### 7. Heuristic Automation Risk Screening
- **Risk Tier Distribution:** Visual breakdown across Low Risk (1,958; 76.5%), Moderate Risk (347; 13.5%), High Risk (193; 7.5%), and Elevated Audit Required (63; 2.5%).
- **Component Indicator Architecture:** Explanatory card detailing the four heuristic indicators (Cadence, Disconnect, Asymmetry, Metadata).
- **Due Diligence Review Table:** Searchable table highlighting primary risk drivers to assist sponsor vetting.

---

## 7. Analytical & Machine Learning Methodology

### A. Engagement Rate Formula
Engagement rate is calculated based on the standard interaction-to-follower ratio:
$$\text{Engagement Rate (\%)} = \left( \frac{\text{Avg Likes} + \text{Avg Comments}}{\text{Followers}} \right) \times 100$$

### B. K-Means Clustering & Model Selection
- **Feature Set:** 64 standardized continuous features (log-transformed reach, interaction ratios, posting cadence, hashtag counts, and one-hot categorical features). Identifiers (`username`, `name`, `profile_url`) were strictly excluded.
- **Evaluation ($k=2 \dots 10$):** $k=3$ was selected based on the elbow inertia curve, peak multi-segment Silhouette Score ($0.3318$), and lowest Davies-Bouldin Index ($1.2996$).
- **Reproducibility:** Seed fixed at `random_state=42` with `n_init=20`.

### C. Multi-Criteria Ranking Architecture (MCDA)
Creators are evaluated across four standardized dimensions $[0–100]$:
$$\text{Influence Score} = 0.40 \times \text{Engagement} + 0.25 \times \text{Reach} + 0.20 \times \text{Cadence} + 0.15 \times \text{Content}$$

**Deterministic Tie-Breaking:**  
Ties in Influence Score are broken deterministically by:
$$\text{Engagement Score} \rightarrow \text{Reach Score} \rightarrow \text{Cadence Score} \rightarrow \text{Content Score} \rightarrow \text{Followers} \rightarrow \text{Username (A–Z)}$$

### D. Isolation Forest Anomaly Detection
- **Configuration:** `n_estimators=100`, `contamination=0.05`, `random_state=42`.
- **Evaluated Features (9):** `log_followers`, `log_likes`, `log_comments`, `log_engagement_rate`, `log_posting_frequency`, `like_to_comment_ratio`, `comment_to_like_ratio`, `interaction_efficiency`, `hashtag_count`.
- **Flagged Profiles:** 128 multivariate outliers (5.00% of dataset).

### E. Heuristic Automation Risk Index
Synthesizes four behavioral signals into a standardized screening index $[0–100]$:
$$\text{Automation Risk Index} = 0.25 \times \text{Cadence} + 0.30 \times \text{Disconnect} + 0.25 \times \text{Asymmetry} + 0.20 \times \text{Metadata}$$

---

## 8. Methodological Limitations & Ethical Safeguards

1. **Statistical Outlier $\ne$ Fraud or Artificial Engagement:**  
   High engagement rates ($>100\%$) occur legitimately when Instagram's Reels or Explore recommendation algorithms serve content to large non-follower audiences. Such profiles represent viral reach, not data corruption or fraud.
2. **Heuristic Screening $\ne$ Calibrated Probability:**  
   The Automation Risk Index is an exploratory risk-screening tool designed to flag profiles for human due diligence. It does **not** represent a calibrated Bayesian probability of bot usage. Neutral language (*"Review Recommended"*) is used to prevent unjustified reputational harm.
3. **Absence of Ground Truth:**  
   Public Instagram metadata does not contain verified ground-truth labels for automated bot accounts. Consequently, no supervised machine learning classifier was trained on speculative labels.
4. **Public Data Compliance:**  
   All data was obtained from publicly accessible archives. Unauthenticated live scraping, CAPTCHA bypass, and credential stuffing were strictly avoided in compliance with platform terms of service.

---

## 9. Data Schema Reference (17 Columns)

| # | Column Name | Type | Description |
|---|---|---|---|
| 1 | `profile_url` | String | Canonical URL of the Instagram profile |
| 2 | `name` | String | Account display name |
| 3 | `username` | String | Unique Instagram handle |
| 4 | `instagram_handle` | String | Formatted handle (`@<username>`) |
| 5 | `followers` | Integer | Follower count (strictly $< 1,000,000$) |
| 6 | `category` | String | Inferred industry niche (19 categories) |
| 7 | `avg_likes_last_10` | Float | Average likes across recent post sample |
| 8 | `avg_comments_last_10` | Integer | Average comments across recent post sample |
| 9 | `engagement_rate` | Float | $(Likes + Comments) / Followers \times 100$ |
| 10 | `posting_frequency_per_month` | Float | Estimated monthly post cadence |
| 11 | `hashtags` | String | Formatted hashtag tokens (`#tag1; #tag2`) |
| 12 | `content_themes` | String | Extracted conceptual content topics |
| 13 | `contact_details` | String | Public email/phone or `"Not publicly available"` |
| 14 | `automation_usage` | String | Baseline heuristic indicator |
| 15 | `additional_notes` | String | Quality control status notes |
| 16 | `data_source` | String | Verified archive provenance identifier |
| 17 | `collection_date` | String | Ingestion timestamp (ISO format) |

---

## 10. Verification & Quality Assurance Summary

The project has passed comprehensive quality assurance validation:
- **Baseline Dataset Integrity:** `data/processed/instagram_influencers_final_clean.csv` verified unmodified (MD5: `e1b0b2b7687ab4fe4956cabcc808b8b4`).
- **Codebase Health:** 100% test pass rate across unit test simulations and headless `AppTest` browser suites.
- **Zero Exposed Secrets:** 0 credentials, tokens, or private keys present.
- **Complete Dependencies:** `requirements.txt` specifies all direct libraries needed for clean reproduction.

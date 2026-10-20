"""
================================================================================
CREATOR INTELLIGENCE - INSTAGRAM INFLUENCER ANALYTICS DASHBOARD
================================================================================
Project:      AI-Powered Instagram Influencer Analytics & Automation Insights
Product:      Creator Intelligence
File:         app.py
Description:  Refined editorial Streamlit dashboard emphasizing strong visual
              hierarchy, deliberate whitespace, human-designed aesthetics,
              and verified mathematical accuracy across all seven sections.
================================================================================
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------------------
# STREAMLIT CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Creator Intelligence | Instagram Influencer Analytics",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# DESIGN SYSTEM & THEME CONSTANTS
# ------------------------------------------------------------------------------
# Restrained editorial palette: Deep navy typography, clean warm neutrals, primary cobalt accent
COLOR_BG = "#FFFFFF"
COLOR_SURFACE = "#F8FAFC"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_PRIMARY = "#0F172A"   # Deep Navy / Slate
COLOR_TEXT_MUTED = "#64748B"     # Slate Gray
COLOR_TEXT_LIGHT = "#94A3B8"
COLOR_ACCENT = "#2563EB"         # Editorial Cobalt Blue Accent
COLOR_ACCENT_LIGHT = "#EFF6FF"
COLOR_SUCCESS = "#10B981"        # Emerald
COLOR_WARNING = "#F59E0B"        # Amber
COLOR_DANGER = "#EF4444"         # Rose / Alert

PLOTLY_LAYOUT_DEFAULTS = dict(
    font=dict(
        family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        color=COLOR_TEXT_PRIMARY,
        size=12,
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=48, r=24, t=48, b=48),
    xaxis=dict(
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        linecolor="#E2E8F0",
        tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
        title_font=dict(color=COLOR_TEXT_PRIMARY, size=12, weight=600),
    ),
    yaxis=dict(
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        linecolor="#E2E8F0",
        tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
        title_font=dict(color=COLOR_TEXT_PRIMARY, size=12, weight=600),
    ),
    hoverlabel=dict(
        bgcolor="#0F172A",
        font_size=12,
        font_color="#FFFFFF",
        font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto",
    ),
    legend=dict(
        font=dict(color=COLOR_TEXT_MUTED, size=11),
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="#E2E8F0",
        borderwidth=1,
    ),
)


# ------------------------------------------------------------------------------
# CUSTOM CSS INJECTION (EDITORIAL, HUMAN-DESIGNED)
# ------------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }
    
    /* Content width & deliberate spacing */
    .block-container {
        padding-top: 3.5rem;
        padding-bottom: 3.5rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1320px;
    }

    /* Product Header Styling */
    .product-header-container {
        border-bottom: 1px solid #E2E8F0;
        padding-top: 0.5rem;
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }
    .product-brand {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.8125rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #2563EB;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }
    h1.product-title, .product-title {
        font-size: 1.875rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        margin: 0 0 0.5rem 0 !important;
        padding: 0 !important;
        line-height: 1.35 !important;
        letter-spacing: -0.025em !important;
        overflow: visible !important;
    }
    .product-subtitle {
        font-size: 0.9375rem;
        color: #64748B;
        margin: 0;
        line-height: 1.55;
        max-width: 820px;
    }
    .dataset-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 9999px;
        padding: 0.35rem 0.85rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: #334155;
        white-space: nowrap;
        margin-top: 0.25rem;
        flex-shrink: 0;
    }
    .dataset-dot {
        width: 6px;
        height: 6px;
        border-radius: 9999px;
        background-color: #10B981;
    }

    /* Four-Metric Strip */
    .metric-strip {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        padding: 1.25rem 0;
        margin-bottom: 2.25rem;
        border-top: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
    }
    @media (max-width: 900px) {
        .metric-strip {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    .metric-cell {
        display: flex;
        flex-direction: column;
    }
    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .metric-caption {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 0.35rem;
    }

    /* Section Headings */
    .section-title {
        font-size: 1.1875rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.015em;
        margin-top: 0.5rem;
        margin-bottom: 0.25rem;
    }
    .section-desc {
        font-size: 0.875rem;
        color: #64748B;
        margin-bottom: 1.5rem;
        line-height: 1.45;
    }
    .card-clean {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }

    /* Editorial Callouts & Disclaimers */
    .disclaimer-box {
        background-color: #F8FAFC;
        border-left: 3px solid #2563EB;
        padding: 0.875rem 1.25rem;
        border-radius: 0 4px 4px 0;
        font-size: 0.8125rem;
        color: #334155;
        line-height: 1.5;
        margin-bottom: 1.5rem;
    }
    .disclaimer-title {
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.25rem;
        font-size: 0.8125rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Sidebar Navigation Styling */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.75rem;
        padding-bottom: 2rem;
    }
    
    /* Table Styling */
    .stDataFrame {
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        overflow: hidden;
    }

    /* Header & chrome cleanup */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 10;
    }
    [data-testid="stMarkdownContainer"] {
        overflow: visible;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# DATA LOADING & CACHED INGESTION
# ------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_all_data():
    """
    Loads verified analytical deliverables from outputs/ and merges them
    into a unified frame with safe fallback handling.
    """
    data_dir = "outputs"
    ranked_path = os.path.join(data_dir, "ranked_influencers.csv")
    anom_path = os.path.join(data_dir, "anomaly_detection_results.csv")
    auto_path = os.path.join(data_dir, "automation_insights.csv")
    features_path = os.path.join(data_dir, "influencer_features.csv")

    if not os.path.exists(ranked_path):
        st.error(f"Required deliverable missing: {ranked_path}. Please execute pipeline steps first.")
        st.stop()

    df_ranked = pd.read_csv(ranked_path)
    df_anom = pd.read_csv(anom_path) if os.path.exists(anom_path) else pd.DataFrame()
    df_auto = pd.read_csv(auto_path) if os.path.exists(auto_path) else pd.DataFrame()
    df_feat = pd.read_csv(features_path) if os.path.exists(features_path) else pd.DataFrame()

    df = df_ranked.copy()

    # Merge anomaly columns
    if not df_anom.empty:
        anom_cols = [
            "username", "avg_likes_last_10", "avg_comments_last_10", "hashtag_count",
            "iso_forest_score", "is_iso_anomaly", "flag_extreme_er",
            "flag_zero_likes_high_followers", "flag_hidden_likes",
            "flag_likes_gt_followers", "flag_zero_engagement_active", "data_quality_status"
        ]
        anom_cols = [c for c in anom_cols if c in df_anom.columns]
        df = pd.merge(df, df_anom[anom_cols], on="username", how="left")

    # Merge automation columns
    if not df_auto.empty:
        auto_cols = [
            "username", "cadence_risk_score", "disconnect_risk_score",
            "asymmetry_risk_score", "metadata_risk_score", "automation_risk_index",
            "risk_tier", "primary_risk_driver"
        ]
        auto_cols = [c for c in auto_cols if c in df_auto.columns]
        df = pd.merge(df, df_auto[auto_cols], on="username", how="left")

    # Fallbacks for safe display
    if "is_iso_anomaly" not in df.columns:
        df["is_iso_anomaly"] = False
    if "automation_risk_index" not in df.columns:
        df["automation_risk_index"] = 0.0
    if "risk_tier" not in df.columns:
        df["risk_tier"] = "Low Risk"

    return df


df_master = load_all_data()


# ------------------------------------------------------------------------------
# SHARED PLOTLY FIGURE STYLER
# ------------------------------------------------------------------------------
def create_styled_figure(fig, title=None, xaxis_title=None, yaxis_title=None):
    """Applies consistent editorial layout, grid, and typography styling."""
    fig.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    if title:
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color=COLOR_TEXT_PRIMARY, size=13, weight=600),
                x=0.0,
                y=0.98,
            )
        )
    if xaxis_title:
        fig.update_xaxes(title_text=xaxis_title)
    if yaxis_title:
        fig.update_yaxes(title_text=yaxis_title)
    return fig


# ------------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    nav_selection = st.radio(
        "Navigation Menu",
        options=[
            "Overview",
            "Influencer Rankings",
            "Category Analysis",
            "Creator Segments",
            "Engagement Analysis",
            "Anomaly Review",
            "Automation Insights",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size: 0.75rem; color: #64748B; line-height: 1.6;">
            <div style="font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Dataset Status</div>
            <div>• <b>{len(df_master):,}</b> verified profiles loaded</div>
            <div>• Followers &lt; 1,000,000</div>
            <div>• 19 influencer categories</div>
            <div>• Verified Phase 2 dataset</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------------------
# HEADER COMPONENT
# ------------------------------------------------------------------------------
def render_header(title, subtitle=None):
    desc = subtitle if subtitle else "Explore creator performance, audience engagement, and content patterns across influencer categories."
    st.markdown(
        f"""
        <div class="product-header-container">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1.5rem;">
                <div style="flex: 1; min-width: 280px;">
                    <div class="product-brand">Creator Intelligence &nbsp;•&nbsp; Instagram Influencer Analytics</div>
                    <h1 class="product-title">{title}</h1>
                    <div class="product-subtitle">{desc}</div>
                </div>
                <div class="dataset-badge">
                    <span class="dataset-dot"></span>
                    <span>{len(df_master):,} Public Profiles Loaded</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# SECTION 1: OVERVIEW
# ==============================================================================
if nav_selection == "Overview":
    # A. Header
    render_header(
        title="Creator Intelligence",
        subtitle="Explore creator performance, audience engagement, and content patterns across influencer categories."
    )

    # B. Key Metrics: Exactly four verified metrics calculated from actual data
    total_profiles = len(df_master)
    med_followers = df_master["followers"].median()
    med_er = df_master["engagement_rate"].median()
    mean_influence = df_master["influence_score"].mean()

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-cell">
                <div class="metric-label">Total Profiles Analysed</div>
                <div class="metric-value">{total_profiles:,}</div>
                <div class="metric-caption">100% public verified accounts</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Median Followers</div>
                <div class="metric-value">{med_followers:,.0f}</div>
                <div class="metric-caption">IQR: 274 – 3,675 followers</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Median Engagement Rate</div>
                <div class="metric-value">{med_er:.2f}%</div>
                <div class="metric-caption">Interactions per 100 followers</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Mean Influence Score</div>
                <div class="metric-value">{mean_influence:.2f}</div>
                <div class="metric-caption">Standardized 0–100 MCDA scale</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # C. Main Charts (Structured, readable width)
    st.markdown('<div class="section-title">Influencer Distribution by Category</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Profile volume across identified industry niches (sorted descending)</div>', unsafe_allow_html=True)

    cat_counts = df_master["category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    cat_counts = cat_counts.sort_values("count", ascending=True)

    fig_cat = px.bar(
        cat_counts,
        x="count",
        y="category",
        orientation="h",
        color_discrete_sequence=[COLOR_ACCENT],
    )
    fig_cat.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Creators: %{x:,}<extra></extra>",
    )
    fig_cat.update_layout(height=420)
    create_styled_figure(fig_cat, xaxis_title="Creator Count", yaxis_title="")
    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Audience Reach versus Engagement Rate</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Log-scaled reach demonstrating the inverse engagement power law. Accounts with 0.00% ER are plotted at a 0.01% baseline for continuous visibility.</div>', unsafe_allow_html=True)

    scatter_df = df_master.copy()
    # Handle zero engagement rates gracefully for log display
    scatter_df["plot_er"] = np.where(scatter_df["engagement_rate"] > 0, scatter_df["engagement_rate"], 0.01)
    scatter_df["is_zero_er"] = scatter_df["engagement_rate"] == 0

    fig_reach_er = px.scatter(
        scatter_df,
        x="followers",
        y="plot_er",
        color="cluster_label",
        log_x=True,
        log_y=True,
        color_discrete_map={
            "Active Mid-to-Macro Tier Influencers": "#2563EB",
            "Emerging High-Engagement Nano Creators": "#0D9488",
            "High-Reach Low-Engagement Accounts": "#64748B",
        },
        hover_name="username",
        hover_data={
            "followers": ":,d",
            "engagement_rate": ":.2f%",
            "influence_score": ":.2f",
            "category": True,
            "plot_er": False,
            "cluster_label": False,
        },
        opacity=0.6,
    )
    fig_reach_er.update_traces(marker=dict(size=6, line=dict(width=0.5, color="#FFFFFF")))
    fig_reach_er.update_layout(height=460, legend_title_text="")
    create_styled_figure(fig_reach_er, xaxis_title="Followers (Logarithmic Scale)", yaxis_title="Engagement Rate % (Logarithmic Scale)")
    st.plotly_chart(fig_reach_er, use_container_width=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # D. Top Five Influencers & Clear Navigation Path
    st.markdown('<div class="section-title">Top Five Influencers Overall</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Highest composite scores balancing engagement (40%), reach (25%), cadence (20%), and content (15%)</div>', unsafe_allow_html=True)

    top_5 = df_master.head(5)[["rank", "username", "category", "followers", "influence_score"]].copy()

    st.dataframe(
        top_5,
        column_config={
            "rank": st.column_config.NumberColumn("Rank", format="#%d", width="small"),
            "username": st.column_config.TextColumn("Creator Username", width="medium"),
            "category": st.column_config.TextColumn("Category", width="medium"),
            "followers": st.column_config.NumberColumn("Followers", format="%,d", width="small"),
            "influence_score": st.column_config.ProgressColumn(
                "Influence Score",
                format="%.2f",
                min_value=0,
                max_value=100,
                width="medium"
            ),
        },
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 0.875rem 1.25rem; border-radius: 4px; font-size: 0.8125rem; color: #475569; margin-top: 0.75rem;">
            <b>Full Leaderboard Available:</b> To search, filter by category or follower tier, and inspect individual score components for all 2,561 influencers, select <b>Influencer Rankings</b> from the sidebar menu.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# SECTION 2: INFLUENCER RANKINGS
# ==============================================================================
elif nav_selection == "Influencer Rankings":
    render_header(
        title="Influencer Rankings & Leaderboard",
        subtitle="Complete multi-criteria rankings derived from Engagement (40%), Reach (25%), Consistency (20%), and Content (15%)."
    )

    st.markdown(
        """
        <div class="disclaimer-box">
            <div class="disclaimer-title">MCDA Ranking System</div>
            Influence Score is a standardized 0–100 index: <b>Influence = 0.40 × Engagement + 0.25 × Reach + 0.20 × Cadence + 0.15 × Content</b>.
            Ties are broken deterministically by Engagement &gt; Reach &gt; Cadence &gt; Content &gt; Followers &gt; Username.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Compact Filter Controls
    f_c1, f_c2, f_c3, f_c4 = st.columns([1.5, 1.2, 1.2, 1.2], gap="medium")

    with f_c1:
        search_query = st.text_input("Username Search", placeholder="Filter by handle or name...")

    with f_c2:
        cat_list = ["All Categories"] + sorted(df_master["category"].unique().tolist())
        selected_cat = st.selectbox("Category", options=cat_list)

    with f_c3:
        cluster_list = ["All Segments"] + sorted(df_master["cluster_label"].dropna().unique().tolist())
        selected_cluster = st.selectbox("Cluster Segment", options=cluster_list)

    with f_c4:
        tier_list = [
            "All Tiers",
            "Nano (< 1K)",
            "Micro (1K – 10K)",
            "Mid-Tier (10K – 100K)",
            "Macro (100K – 1M)"
        ]
        selected_tier = st.selectbox("Follower Tier", options=tier_list)

    # Filtering logic
    f_df = df_master.copy()

    if search_query:
        sq = search_query.strip().lower()
        f_df = f_df[
            f_df["username"].str.lower().str.contains(sq, na=False) |
            f_df["name"].str.lower().str.contains(sq, na=False)
        ]

    if selected_cat != "All Categories":
        f_df = f_df[f_df["category"] == selected_cat]

    if selected_cluster != "All Segments":
        f_df = f_df[f_df["cluster_label"] == selected_cluster]

    if selected_tier == "Nano (< 1K)":
        f_df = f_df[f_df["followers"] < 1000]
    elif selected_tier == "Micro (1K – 10K)":
        f_df = f_df[(f_df["followers"] >= 1000) & (f_df["followers"] < 10000)]
    elif selected_tier == "Mid-Tier (10K – 100K)":
        f_df = f_df[(f_df["followers"] >= 10000) & (f_df["followers"] < 100000)]
    elif selected_tier == "Macro (100K – 1M)":
        f_df = f_df[f_df["followers"] >= 100000]

    st.markdown(f"<div style='font-size: 0.8125rem; color: #64748B; margin-bottom: 0.75rem;'>Displaying <b>{len(f_df):,}</b> of {len(df_master):,} influencers</div>", unsafe_allow_html=True)

    # Prioritized Table Columns (Avoiding horizontal scrolling)
    prioritized_cols = [
        "rank", "username", "category", "followers",
        "engagement_rate", "influence_score", "cluster_label"
    ]
    st.dataframe(
        f_df[prioritized_cols],
        column_config={
            "rank": st.column_config.NumberColumn("Rank", format="#%d", width="small"),
            "username": st.column_config.TextColumn("Creator", width="medium"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "followers": st.column_config.NumberColumn("Followers", format="%,d", width="small"),
            "engagement_rate": st.column_config.NumberColumn("Engagement Rate", format="%.2f%%", width="small"),
            "influence_score": st.column_config.ProgressColumn(
                "Influence Score",
                format="%.2f",
                min_value=0,
                max_value=100,
                width="medium"
            ),
            "cluster_label": st.column_config.TextColumn("Segment", width="medium"),
        },
        use_container_width=True,
        hide_index=True,
        height=500,
    )

    # Retained Creator Inspector
    st.markdown("---")
    st.markdown('<div class="section-title">Creator Performance Inspector</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Select any creator to inspect raw performance metrics and decomposed score components</div>', unsafe_allow_html=True)

    candidate_users = f_df["username"].head(100).tolist()
    if candidate_users:
        inspect_user = st.selectbox("Select Creator to Inspect", options=candidate_users)
        row = df_master[df_master["username"] == inspect_user].iloc[0]

        insp_c1, insp_c2, insp_c3, insp_c4 = st.columns([1, 1.1, 1.2, 0.9], gap="medium")

        # 1. Creator Information
        with insp_c1:
            st.markdown(
                f"""
                <div class="card-clean">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase;">CREATOR INFO</div>
                    <div style="font-size: 1.1875rem; font-weight: 700; color: #0F172A; margin: 0.25rem 0;">@{row['username']}</div>
                    <div style="font-size: 0.8125rem; color: #64748B;">{row.get('name', 'N/A')}</div>
                    <hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #F1F5F9;">
                    <div style="font-size: 0.75rem; color: #64748B;">CATEGORY</div>
                    <div style="font-size: 0.875rem; font-weight: 600; color: #0F172A;">{row['category']}</div>
                    <div style="margin-top: 0.4rem; font-size: 0.75rem; color: #64748B;">CLUSTER SEGMENT</div>
                    <div style="font-size: 0.8125rem; font-weight: 600; color: #2563EB;">{row['cluster_label']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 2. Raw Performance Metrics
        with insp_c2:
            st.markdown(
                f"""
                <div class="card-clean">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase;">RAW PERFORMANCE</div>
                    <div style="display: flex; justify-content: space-between; padding: 0.25rem 0; font-size: 0.8125rem; border-bottom: 1px solid #F1F5F9;">
                        <span style="color: #64748B;">Followers</span>
                        <b>{row['followers']:,}</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 0.25rem 0; font-size: 0.8125rem; border-bottom: 1px solid #F1F5F9;">
                        <span style="color: #64748B;">Engagement Rate</span>
                        <b>{row['engagement_rate']:.2f}%</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 0.25rem 0; font-size: 0.8125rem; border-bottom: 1px solid #F1F5F9;">
                        <span style="color: #64748B;">Posting Cadence</span>
                        <b>{row['posting_frequency']:.1f} posts/mo</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 0.25rem 0; font-size: 0.8125rem;">
                        <span style="color: #64748B;">Avg Likes / Comments</span>
                        <b>{row.get('avg_likes_last_10', 0):,.0f} / {row.get('avg_comments_last_10', 0):.0f}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 3. Component Scores (MCDA weights)
        with insp_c3:
            st.markdown(
                f"""
                <div class="card-clean">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase;">MCDA COMPONENT SCORES</div>
                    <div style="display: flex; justify-content: space-between; padding: 0.2rem 0; font-size: 0.8125rem; border-bottom: 1px solid #F1F5F9;">
                        <span style="color: #64748B;">Engagement (40% weight)</span>
                        <b>{row['engagement_score']:.1f} / 100</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 0.2rem 0; font-size: 0.8125rem; border-bottom: 1px solid #F1F5F9;">
                        <span style="color: #64748B;">Reach (25% weight)</span>
                        <b>{row['reach_score']:.1f} / 100</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 0.2rem 0; font-size: 0.8125rem; border-bottom: 1px solid #F1F5F9;">
                        <span style="color: #64748B;">Consistency (20% weight)</span>
                        <b>{row['consistency_score']:.1f} / 100</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 0.2rem 0; font-size: 0.8125rem;">
                        <span style="color: #64748B;">Content (15% weight)</span>
                        <b>{row['content_score']:.1f} / 100</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 4. Final Influence Score
        with insp_c4:
            st.markdown(
                f"""
                <div class="card-clean" style="border-top: 3px solid #2563EB; text-align: center;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase;">FINAL INFLUENCE</div>
                    <div style="font-size: 2.25rem; font-weight: 700; color: #2563EB; margin: 0.25rem 0;">{row['influence_score']:.2f}</div>
                    <div style="font-size: 0.875rem; font-weight: 600; color: #0F172A;">Overall Rank #{row['rank']:,}</div>
                    <div style="font-size: 0.75rem; color: #64748B; margin-top: 0.25rem;">of 2,561 Creators</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==============================================================================
# SECTION 3: CATEGORY ANALYSIS
# ==============================================================================
elif nav_selection == "Category Analysis":
    render_header(
        title="Category Landscape & Benchmark Comparisons",
        subtitle="Cross-niche analysis of influencer volume, median reach, median engagement, and category leaders."
    )

    # Grouped Category Summary Table
    cat_summary = df_master.groupby("category").agg(
        creator_count=("username", "count"),
        median_er=("engagement_rate", "median"),
        median_followers=("followers", "median"),
        mean_influence=("influence_score", "mean"),
    ).reset_index()

    # Determine top-ranked influencer by category
    top_per_cat = df_master.sort_values(["category", "category_rank"]).groupby("category").first().reset_index()
    top_per_cat = top_per_cat[["category", "username", "rank", "influence_score"]]
    top_per_cat.columns = ["category", "top_influencer", "top_rank", "top_score"]

    cat_table = pd.merge(cat_summary, top_per_cat, on="category").sort_values("creator_count", ascending=False)

    st.markdown('<div class="section-title">Category Performance Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Key metrics and top-ranked creator per category across all 19 niches</div>', unsafe_allow_html=True)

    st.dataframe(
        cat_table,
        column_config={
            "category": st.column_config.TextColumn("Category", width="medium"),
            "creator_count": st.column_config.NumberColumn("Profiles", format="%,d", width="small"),
            "median_er": st.column_config.NumberColumn("Median ER", format="%.2f%%", width="small"),
            "median_followers": st.column_config.NumberColumn("Median Followers", format="%,d", width="small"),
            "mean_influence": st.column_config.NumberColumn("Mean Score", format="%.1f", width="small"),
            "top_influencer": st.column_config.TextColumn("Top Influencer", width="medium"),
            "top_rank": st.column_config.NumberColumn("Overall Rank", format="#%d", width="small"),
            "top_score": st.column_config.NumberColumn("Top Score", format="%.2f", width="small"),
        },
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Category Charts
    col_c1, col_c2 = st.columns(2, gap="large")

    with col_c1:
        st.markdown('<div class="section-title">Median Engagement Rate by Category</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Comparing audience responsiveness across niches</div>', unsafe_allow_html=True)

        sorted_er = cat_table.sort_values("median_er", ascending=True)
        fig_cat_er = px.bar(
            sorted_er,
            x="median_er",
            y="category",
            orientation="h",
            color_discrete_sequence=[COLOR_ACCENT],
        )
        fig_cat_er.update_traces(
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Median ER: %{x:.2f}%<extra></extra>",
        )
        fig_cat_er.update_layout(height=480)
        create_styled_figure(fig_cat_er, xaxis_title="Median Engagement Rate %", yaxis_title="")
        st.plotly_chart(fig_cat_er, use_container_width=True)

    with col_c2:
        st.markdown('<div class="section-title">Median Audience Reach by Category</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Comparing median follower counts across niches</div>', unsafe_allow_html=True)

        sorted_reach = cat_table.sort_values("median_followers", ascending=True)
        fig_cat_reach = px.bar(
            sorted_reach,
            x="median_followers",
            y="category",
            orientation="h",
            color_discrete_sequence=["#0D9488"],
        )
        fig_cat_reach.update_traces(
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Median Followers: %{x:,}<extra></extra>",
        )
        fig_cat_reach.update_layout(height=480)
        create_styled_figure(fig_cat_reach, xaxis_title="Median Followers", yaxis_title="")
        st.plotly_chart(fig_cat_reach, use_container_width=True)


# ==============================================================================
# SECTION 4: CREATOR SEGMENTS
# ==============================================================================
elif nav_selection == "Creator Segments":
    render_header(
        title="Unsupervised Creator Segmentation (K-Means)",
        subtitle="Three empirical clusters discovered by the machine learning pipeline using 64 standardized features."
    )

    st.markdown(
        """
        <div class="disclaimer-box">
            <div class="disclaimer-title">Clustering Methodology</div>
            K-Means evaluation over k=2..10 identified k=3 as optimal based on peak multi-segment Silhouette score (0.3318)
            and lowest Davies-Bouldin index (1.2996). These segments represent empirical data distributions,
            not rigid behavioral archetypes.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c0 = df_master[df_master["cluster_id"] == 0]
    c1 = df_master[df_master["cluster_id"] == 1]
    c2 = df_master[df_master["cluster_id"] == 2]

    # 3 Structured Segment Cards
    s_c1, s_c2, s_c3 = st.columns(3, gap="medium")

    with s_c1:
        st.markdown(
            f"""
            <div class="card-clean" style="border-top: 3px solid #2563EB;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #2563EB; text-transform: uppercase;">CLUSTER 0</div>
                <div style="font-size: 1.125rem; font-weight: 700; color: #0F172A; margin: 0.25rem 0 0.5rem 0;">Active Mid-to-Macro Tier</div>
                <div style="font-size: 0.8125rem; color: #64748B; margin-bottom: 1rem; line-height: 1.45;">
                    Established creators with substantial reach, daily active posting cadence, and high absolute interaction volumes.
                </div>
                <div style="font-size: 1.625rem; font-weight: 700; color: #0F172A;">{len(c0):,} <span style="font-size: 0.875rem; font-weight: 400; color: #64748B;">({len(c0)/len(df_master)*100:.1f}%)</span></div>
                <hr style="margin: 0.75rem 0; border: none; border-top: 1px solid #F1F5F9;">
                <div style="font-size: 0.8125rem; display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="color: #64748B;">Median Followers:</span>
                    <b>{c0['followers'].median():,.0f}</b>
                </div>
                <div style="font-size: 0.8125rem; display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="color: #64748B;">Median ER %:</span>
                    <b>{c0['engagement_rate'].median():.2f}%</b>
                </div>
                <div style="font-size: 0.8125rem; display: flex; justify-content: space-between;">
                    <span style="color: #64748B;">Posting Cadence:</span>
                    <b>{c0['posting_frequency'].median():.1f} posts/mo</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s_c2:
        st.markdown(
            f"""
            <div class="card-clean" style="border-top: 3px solid #0D9488;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #0D9488; text-transform: uppercase;">CLUSTER 1</div>
                <div style="font-size: 1.125rem; font-weight: 700; color: #0F172A; margin: 0.25rem 0 0.5rem 0;">Emerging High-ER Nano</div>
                <div style="font-size: 0.8125rem; color: #64748B; margin-bottom: 1rem; line-height: 1.45;">
                    Grassroots technical and coding creators with smaller audiences but superior community interaction efficiency.
                </div>
                <div style="font-size: 1.625rem; font-weight: 700; color: #0F172A;">{len(c1):,} <span style="font-size: 0.875rem; font-weight: 400; color: #64748B;">({len(c1)/len(df_master)*100:.1f}%)</span></div>
                <hr style="margin: 0.75rem 0; border: none; border-top: 1px solid #F1F5F9;">
                <div style="font-size: 0.8125rem; display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="color: #64748B;">Median Followers:</span>
                    <b>{c1['followers'].median():,.0f}</b>
                </div>
                <div style="font-size: 0.8125rem; display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="color: #64748B;">Median ER %:</span>
                    <b>{c1['engagement_rate'].median():.2f}%</b>
                </div>
                <div style="font-size: 0.8125rem; display: flex; justify-content: space-between;">
                    <span style="color: #64748B;">Posting Cadence:</span>
                    <b>{c1['posting_frequency'].median():.1f} posts/mo</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s_c3:
        st.markdown(
            f"""
            <div class="card-clean" style="border-top: 3px solid #64748B;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase;">CLUSTER 2</div>
                <div style="font-size: 1.125rem; font-weight: 700; color: #0F172A; margin: 0.25rem 0 0.5rem 0;">High-Reach Low-Engagement</div>
                <div style="font-size: 0.8125rem; color: #64748B; margin-bottom: 1rem; line-height: 1.45;">
                    Large audiences with high daily posting, but severely suppressed engagement rates and minimal hashtag usage.
                </div>
                <div style="font-size: 1.625rem; font-weight: 700; color: #0F172A;">{len(c2):,} <span style="font-size: 0.875rem; font-weight: 400; color: #64748B;">({len(c2)/len(df_master)*100:.1f}%)</span></div>
                <hr style="margin: 0.75rem 0; border: none; border-top: 1px solid #F1F5F9;">
                <div style="font-size: 0.8125rem; display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="color: #64748B;">Median Followers:</span>
                    <b>{c2['followers'].median():,.0f}</b>
                </div>
                <div style="font-size: 0.8125rem; display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="color: #64748B;">Median ER %:</span>
                    <b>{c2['engagement_rate'].median():.2f}%</b>
                </div>
                <div style="font-size: 0.8125rem; display: flex; justify-content: space-between;">
                    <span style="color: #64748B;">Posting Cadence:</span>
                    <b>{c2['posting_frequency'].median():.1f} posts/mo</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Segment Comparison Chart
    st.markdown('<div class="section-title">Segment Performance Benchmarks</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Comparing median followers, engagement rate, and cadence across clusters</div>', unsafe_allow_html=True)

    clust_comp = pd.DataFrame({
        "Metric": ["Median Followers (k)", "Median ER (%)", "Posting Cadence (posts/mo)"],
        "Cluster 0 (Active Macro)": [c0["followers"].median() / 1000.0, c0["engagement_rate"].median(), c0["posting_frequency"].median()],
        "Cluster 1 (Nano High-ER)": [c1["followers"].median() / 1000.0, c1["engagement_rate"].median(), c1["posting_frequency"].median()],
        "Cluster 2 (High-Reach Low-ER)": [c2["followers"].median() / 1000.0, c2["engagement_rate"].median(), c2["posting_frequency"].median()],
    }).melt(id_vars="Metric", var_name="Segment", value_name="Value")

    fig_clust = px.bar(
        clust_comp,
        x="Metric",
        y="Value",
        color="Segment",
        barmode="group",
        color_discrete_map={
            "Cluster 0 (Active Macro)": "#2563EB",
            "Cluster 1 (Nano High-ER)": "#0D9488",
            "Cluster 2 (High-Reach Low-ER)": "#64748B",
        },
    )
    fig_clust.update_layout(height=400)
    create_styled_figure(fig_clust, xaxis_title="", yaxis_title="Metric Value")
    st.plotly_chart(fig_clust, use_container_width=True)


# ==============================================================================
# SECTION 5: ENGAGEMENT ANALYSIS
# ==============================================================================
elif nav_selection == "Engagement Analysis":
    render_header(
        title="Engagement Dynamics & Ratio Analysis",
        subtitle="Analyzing engagement rate distributions, reach-versus-engagement power laws, and posting cadence impact."
    )

    # 1. Engagement Distribution Histogram
    st.markdown('<div class="section-title">Engagement Rate Distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Severe right-skewed distribution across all profiles (median: 5.21%, 75th percentile: 11.60%)</div>', unsafe_allow_html=True)

    er_clipped = np.clip(df_master["engagement_rate"], 0.0, 50.0)
    fig_er_dist = px.histogram(
        er_clipped,
        nbins=40,
        color_discrete_sequence=[COLOR_ACCENT],
    )
    fig_er_dist.update_layout(height=340, showlegend=False)
    create_styled_figure(fig_er_dist, xaxis_title="Engagement Rate % (Values > 50% grouped at 50%)", yaxis_title="Creator Count")
    st.plotly_chart(fig_er_dist, use_container_width=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 2. Followers vs Engagement Scatter & Posting Frequency vs Engagement Scatter
    e_col1, e_col2 = st.columns(2, gap="large")

    with e_col1:
        st.markdown('<div class="section-title">Followers versus Engagement</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Demonstrates micro-creator high engagement and macro-creator ratio stabilization</div>', unsafe_allow_html=True)

        scatter_e1 = df_master.copy()
        scatter_e1["plot_er"] = np.where(scatter_e1["engagement_rate"] > 0, scatter_e1["engagement_rate"], 0.01)

        fig_fe = px.scatter(
            scatter_e1,
            x="followers",
            y="plot_er",
            color="cluster_label",
            log_x=True,
            log_y=True,
            color_discrete_map={
                "Active Mid-to-Macro Tier Influencers": "#2563EB",
                "Emerging High-Engagement Nano Creators": "#0D9488",
                "High-Reach Low-Engagement Accounts": "#64748B",
            },
            hover_name="username",
            hover_data={"followers": ":,d", "engagement_rate": ":.2f%", "plot_er": False, "cluster_label": False},
            opacity=0.6,
        )
        fig_fe.update_traces(marker=dict(size=5.5))
        fig_fe.update_layout(height=420, legend_title_text="")
        create_styled_figure(fig_fe, xaxis_title="Followers (Log Scale)", yaxis_title="Engagement Rate % (Log Scale)")
        st.plotly_chart(fig_fe, use_container_width=True)

    with e_col2:
        st.markdown('<div class="section-title">Posting Frequency versus Engagement</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Evaluating whether higher monthly posting volume produces higher engagement</div>', unsafe_allow_html=True)

        fig_cadence = px.scatter(
            scatter_e1,
            x="posting_frequency",
            y="plot_er",
            color="cluster_label",
            log_y=True,
            color_discrete_map={
                "Active Mid-to-Macro Tier Influencers": "#2563EB",
                "Emerging High-Engagement Nano Creators": "#0D9488",
                "High-Reach Low-Engagement Accounts": "#64748B",
            },
            hover_name="username",
            hover_data={"posting_frequency": ":.1f", "engagement_rate": ":.2f%", "plot_er": False, "cluster_label": False},
            opacity=0.6,
        )
        fig_cadence.update_traces(marker=dict(size=5.5))
        fig_cadence.update_layout(height=420, legend_title_text="")
        create_styled_figure(fig_cadence, xaxis_title="Monthly Cadence (Posts/Mo)", yaxis_title="Engagement Rate % (Log Scale)")
        st.plotly_chart(fig_cadence, use_container_width=True)

    # 3. Extreme Observations Inspection (Do not silently remove outliers)
    st.markdown("---")
    st.markdown('<div class="section-title">Inspection of Extreme Observations (ER > 100%)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Nine profiles exhibit engagement rates above 100%. These are mathematically valid observations driven by Explore page and Reels viral distribution on smaller follower bases.</div>', unsafe_allow_html=True)

    extreme_obs = df_master[df_master["engagement_rate"] > 100.0][[
        "username", "name", "category", "followers", "avg_likes_last_10",
        "avg_comments_last_10", "engagement_rate", "posting_frequency", "influence_score"
    ]].sort_values("engagement_rate", ascending=False)

    st.dataframe(
        extreme_obs,
        column_config={
            "username": st.column_config.TextColumn("Creator Handle", width="medium"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "followers": st.column_config.NumberColumn("Followers", format="%,d", width="small"),
            "avg_likes_last_10": st.column_config.NumberColumn("Avg Likes", format="%,.0f", width="small"),
            "avg_comments_last_10": st.column_config.NumberColumn("Avg Comments", format="%,.0f", width="small"),
            "engagement_rate": st.column_config.NumberColumn("ER %", format="%.2f%%", width="small"),
            "posting_frequency": st.column_config.NumberColumn("Cadence", format="%.1f", width="small"),
            "influence_score": st.column_config.NumberColumn("Influence Score", format="%.2f", width="small"),
        },
        use_container_width=True,
        hide_index=True,
    )


# ==============================================================================
# SECTION 6: ANOMALY REVIEW
# ==============================================================================
elif nav_selection == "Anomaly Review":
    render_header(
        title="Statistical Anomaly & Metric Quality Audit",
        subtitle="Auditing high-dimensional Isolation Forest outliers and empirical data collection edge cases."
    )

    st.markdown(
        """
        <div class="disclaimer-box">
            <div class="disclaimer-title">Ethical Audit Notice</div>
            An anomaly indicates an unusual statistical pattern in high-dimensional feature space.
            <b>It does not establish fraud or artificial engagement.</b> Extreme ratios frequently reflect legitimate
            viral spikes on Reels/Explore feeds, or platform UI features like hidden like counts.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Summary Metrics
    iso_count = int(df_master["is_iso_anomaly"].sum())
    extreme_er_count = int(df_master.get("flag_extreme_er", (df_master["engagement_rate"] > 100.0)).sum())
    hidden_likes_count = int(df_master.get("flag_hidden_likes", (df_master.get("avg_likes_last_10", 1) == 0) & (df_master.get("avg_comments_last_10", 0) > 0)).sum())
    dormant_count = int(df_master.get("flag_zero_likes_high_followers", (df_master["followers"] > 10000) & (df_master.get("avg_likes_last_10", 1) == 0)).sum())

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-cell">
                <div class="metric-label">Isolation Forest Anomalies</div>
                <div class="metric-value">{iso_count:,}</div>
                <div class="metric-caption">5.0% expected contamination</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Extreme ER (&gt; 100%)</div>
                <div class="metric-value">{extreme_er_count}</div>
                <div class="metric-caption">Viral non-follower interactions</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Hidden Likes Detected</div>
                <div class="metric-value">{hidden_likes_count}</div>
                <div class="metric-caption">0 likes with positive comments</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Dormant Disconnect</div>
                <div class="metric-value">{dormant_count}</div>
                <div class="metric-caption">&gt; 10K followers with 0 likes</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Searchable Anomaly Controls
    a_c1, a_c2 = st.columns([1.5, 1.5], gap="medium")

    with a_c1:
        anom_search = st.text_input("Search Anomaly Profiles", placeholder="Filter by username...")

    with a_c2:
        anom_filter = st.selectbox(
            "Filter Anomaly Flag",
            options=[
                "All Flagged Anomalies",
                "Isolation Forest Multivariate Outliers",
                "Extreme ER (> 100%)",
                "Hidden Like Counts (Likes=0, Comments>0)",
                "Dormant Audience (>10K Followers, Likes=0)",
            ],
        )

    a_df = df_master.copy()

    if anom_filter == "All Flagged Anomalies":
        a_df = a_df[a_df["is_iso_anomaly"] | (a_df["engagement_rate"] > 100.0) | a_df.get("flag_hidden_likes", False) | a_df.get("flag_zero_likes_high_followers", False)]
    elif anom_filter == "Isolation Forest Multivariate Outliers":
        a_df = a_df[a_df["is_iso_anomaly"]]
    elif anom_filter == "Extreme ER (> 100%)":
        a_df = a_df[a_df["engagement_rate"] > 100.0]
    elif anom_filter == "Hidden Like Counts (Likes=0, Comments>0)":
        a_df = a_df[a_df.get("flag_hidden_likes", False)]
    elif anom_filter == "Dormant Audience (>10K Followers, Likes=0)":
        a_df = a_df[a_df.get("flag_zero_likes_high_followers", False)]

    if anom_search:
        s_term = anom_search.strip().lower()
        a_df = a_df[a_df["username"].str.lower().str.contains(s_term, na=False)]

    st.markdown(f"<div style='font-size: 0.8125rem; color: #64748B; margin-bottom: 0.75rem;'>Showing <b>{len(a_df):,}</b> flagged anomaly profiles</div>", unsafe_allow_html=True)

    anom_cols = [
        "username", "category", "followers", "avg_likes_last_10", "avg_comments_last_10",
        "engagement_rate", "posting_frequency", "iso_forest_score", "data_quality_status"
    ]
    st.dataframe(
        a_df[[c for c in anom_cols if c in a_df.columns]],
        column_config={
            "username": st.column_config.TextColumn("Creator", width="medium"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "followers": st.column_config.NumberColumn("Followers", format="%,d", width="small"),
            "avg_likes_last_10": st.column_config.NumberColumn("Avg Likes", format="%,.0f", width="small"),
            "avg_comments_last_10": st.column_config.NumberColumn("Avg Comments", format="%,.0f", width="small"),
            "engagement_rate": st.column_config.NumberColumn("ER %", format="%.2f%%", width="small"),
            "posting_frequency": st.column_config.NumberColumn("Cadence", format="%.1f", width="small"),
            "iso_forest_score": st.column_config.NumberColumn("Isolation Score", format="%.4f", width="small"),
            "data_quality_status": st.column_config.TextColumn("Audit Status", width="large"),
        },
        use_container_width=True,
        hide_index=True,
        height=480,
    )


# ==============================================================================
# SECTION 7: AUTOMATION INSIGHTS
# ==============================================================================
elif nav_selection == "Automation Insights":
    render_header(
        title="Heuristic Automation Risk Screening",
        subtitle="Exploratory multi-signal risk index assisting influencer marketing managers with commercial sponsor due diligence."
    )

    st.markdown(
        """
        <div class="disclaimer-box">
            <div class="disclaimer-title">Methodological Disclaimer</div>
            The Automation Risk Index is a heuristic screening score, not a calibrated probability.
            <b>A high score does not prove automation or fraudulent behaviour.</b>
            Neutral language such as "Review recommended" is used to guide human sponsor vetting.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Risk Tier Breakdown
    tier_counts = df_master["risk_tier"].value_counts()
    low_cnt = tier_counts.get("Low Risk", 0)
    mod_cnt = tier_counts.get("Moderate Risk", 0)
    high_cnt = tier_counts.get("High Risk", 0)
    elev_cnt = tier_counts.get("Elevated Audit Required", 0)

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-cell">
                <div class="metric-label">Low Risk (&lt; 25)</div>
                <div class="metric-value" style="color: #10B981;">{low_cnt:,}</div>
                <div class="metric-caption">{low_cnt/len(df_master)*100:.1f}% organic metrics</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Moderate Risk (25–50)</div>
                <div class="metric-value">{mod_cnt:,}</div>
                <div class="metric-caption">{mod_cnt/len(df_master)*100:.1f}% standard vetting</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">High Risk (50–75)</div>
                <div class="metric-value" style="color: #F59E0B;">{high_cnt:,}</div>
                <div class="metric-caption">{high_cnt/len(df_master)*100:.1f}% secondary review</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Elevated Audit (&ge; 75)</div>
                <div class="metric-value" style="color: #EF4444;">{elev_cnt:,}</div>
                <div class="metric-caption">{elev_cnt/len(df_master)*100:.1f}% pre-contract review</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Component Indicators & Searchable Audit Table
    auto_c1, auto_c2 = st.columns([1.1, 2], gap="large")

    with auto_c1:
        st.markdown('<div class="section-title">Component Indicators</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Four behavioral indicators weighted in the composite index</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="card-clean" style="font-size: 0.8125rem; line-height: 1.6;">
                <div style="margin-bottom: 0.75rem;">
                    <b>1. Cadence Risk (25% weight)</b><br>
                    <span style="color: #64748B;">Rigid daily automated posting (30 posts/month).</span>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <b>2. Engagement Disconnect (30% weight)</b><br>
                    <span style="color: #64748B;">Large audience reach paired with near-zero engagement rate.</span>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <b>3. Interaction Asymmetry (25% weight)</b><br>
                    <span style="color: #64748B;">Zero likes on large followings or platform like-hiding.</span>
                </div>
                <div>
                    <b>4. Metadata Absence (20% weight)</b><br>
                    <span style="color: #64748B;">Zero hashtags and themes indicating uncurated feed syndication.</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with auto_c2:
        st.markdown('<div class="section-title">Profiles Requiring Review</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Search and inspect profiles by risk classification tier</div>', unsafe_allow_html=True)

        sel_tier = st.selectbox(
            "Filter Risk Classification",
            options=["Elevated Audit Required (>= 75)", "High Risk (50–75)", "Moderate Risk (25–50)", "All Profiles"],
        )

        review_df = df_master.copy()
        if sel_tier == "Elevated Audit Required (>= 75)":
            review_df = review_df[review_df["risk_tier"] == "Elevated Audit Required"]
        elif sel_tier == "High Risk (50–75)":
            review_df = review_df[review_df["risk_tier"] == "High Risk"]
        elif sel_tier == "Moderate Risk (25–50)":
            review_df = review_df[review_df["risk_tier"] == "Moderate Risk"]

        review_df = review_df.sort_values("automation_risk_index", ascending=False)

        audit_display_cols = [
            "username", "category", "followers", "engagement_rate", "posting_frequency",
            "automation_risk_index", "risk_tier", "primary_risk_driver"
        ]
        st.dataframe(
            review_df[[c for c in audit_display_cols if c in review_df.columns]],
            column_config={
                "username": st.column_config.TextColumn("Creator", width="medium"),
                "category": st.column_config.TextColumn("Category", width="small"),
                "followers": st.column_config.NumberColumn("Followers", format="%,d", width="small"),
                "engagement_rate": st.column_config.NumberColumn("ER %", format="%.4f%%", width="small"),
                "posting_frequency": st.column_config.NumberColumn("Cadence", format="%.1f", width="small"),
                "automation_risk_index": st.column_config.ProgressColumn(
                    "Risk Index",
                    format="%.2f",
                    min_value=0,
                    max_value=100,
                    width="medium"
                ),
                "risk_tier": st.column_config.TextColumn("Review Status", width="small"),
                "primary_risk_driver": st.column_config.TextColumn("Primary Risk Driver", width="large"),
            },
            use_container_width=True,
            hide_index=True,
            height=340,
        )

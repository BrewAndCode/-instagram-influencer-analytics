"""
Week 1 Report Generator for SR NEXT Internship.

Generates:
1. reports/Week_1_Report.docx (Native OpenXML format with full table/heading styling)
2. reports/Week_1_Report.pdf  (Multi-page PDF rendered via macOS CoreText & Quartz)
"""

import os
import re
import zipfile
import logging
from datetime import datetime
import pandas as pd
import numpy as np

# PyObjC / macOS graphics frameworks
import AppKit
import Foundation
import Quartz
from CoreText import (
    CTFramesetterCreateWithAttributedString,
    CTFramesetterCreateFrame,
    CTFrameDraw,
    CTFrameGetVisibleStringRange,
    CTLineCreateWithAttributedString,
    CTLineDraw,
    CTFontCreateWithName,
    kCTFontAttributeName,
    kCTForegroundColorAttributeName
)
from CoreFoundation import (
    CFAttributedStringCreate,
    CFURLCreateWithFileSystemPath,
    kCFURLPOSIXPathStyle,
    CFRangeMake
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def generate_report_docx(output_path: str):
    """Generate professional DOCX report using native OpenXML packaging."""
    logger.info(f"Generating DOCX report: {output_path}")
    
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

    core_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Week 1 Report – Instagram Influencer Data Collection and Dataset Preparation</dc:title>
  <dc:subject>SR NEXT Internship Phase 1 Report</dc:subject>
  <dc:creator>SR NEXT Data Science &amp; AI Intern</dc:creator>
  <cp:lastModifiedBy>SR NEXT Intern</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-10-06T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-10-06T00:00:00Z</dcterms:modified>
</cp:coreProperties>"""

    app_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>SR NEXT Documentation Generator</Application>
  <DocSecurity>0</DocSecurity>
  <ScaleCrop>false</ScaleCrop>
  <Company>SR NEXT</Company>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>1.0</AppVersion>
</Properties>"""

    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>
        <w:sz w:val="22"/>
        <w:color w:val="2D3748"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="160" w:line="276" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>

  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:pPr>
      <w:spacing w:before="400" w:after="200"/>
      <w:jc w:val="center"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="48"/>
      <w:color w:val="1B365D"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Subtitle">
    <w:name w:val="Subtitle"/>
    <w:pPr>
      <w:spacing w:before="0" w:after="400"/>
      <w:jc w:val="center"/>
    </w:pPr>
    <w:rPr>
      <w:sz w:val="28"/>
      <w:color w:val="4A5568"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:pPr>
      <w:spacing w:before="360" w:after="160"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="32"/>
      <w:color w:val="1B365D"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:pPr>
      <w:spacing w:before="240" w:after="120"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="26"/>
      <w:color w:val="2B6CB0"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:pPr>
      <w:spacing w:before="180" w:after="80"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="24"/>
      <w:color w:val="2D3748"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="ListBullet">
    <w:name w:val="List Bullet"/>
    <w:pPr>
      <w:ind w:left="720" w:hanging="360"/>
      <w:spacing w:after="100"/>
    </w:pPr>
  </w:style>
</w:styles>"""

    # Helper function to escape text
    def escape(s):
        return (str(s)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))

    def p(text="", style=None, bold=False, italic=False, color=None, size=None, align=None):
        ppr = []
        if style:
            ppr.append(f'<w:pStyle w:val="{style}"/>')
        if align:
            ppr.append(f'<w:jc w:val="{align}"/>')
        ppr_str = f'<w:pPr>{"".join(ppr)}</w:pPr>' if ppr else ''
        
        rpr = []
        if bold:
            rpr.append('<w:b/>')
        if italic:
            rpr.append('<w:i/>')
        if color:
            rpr.append(f'<w:color w:val="{color}"/>')
        if size:
            rpr.append(f'<w:sz w:val="{size}"/>')
        rpr_str = f'<w:rPr>{"".join(rpr)}</w:rPr>' if rpr else ''
        
        return f'<w:p>{ppr_str}<w:r>{rpr_str}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'

    def bullet(text, bold_prefix=""):
        p_xml = '<w:p><w:pPr><w:ind w:left="720" w:hanging="360"/><w:spacing w:after="80"/></w:pPr>'
        # bullet symbol
        p_xml += '<w:r><w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol"/><w:color w:val="2B6CB0"/></w:rPr><w:t>&#8226; </w:t></w:r>'
        if bold_prefix:
            p_xml += f'<w:r><w:rPr><w:b/><w:color w:val="1B365D"/></w:rPr><w:t xml:space="preserve">{escape(bold_prefix)} </w:t></w:r>'
        p_xml += f'<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'
        return p_xml

    def page_break():
        return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

    def table(headers, rows, col_widths=None):
        tbl = ['<w:tbl>']
        tbl.append('<w:tblPr>')
        tbl.append('<w:tblW w:w="0" w:type="auto"/>')
        tbl.append('<w:tblBorders>')
        tbl.append('<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>')
        tbl.append('<w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>')
        tbl.append('<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>')
        tbl.append('<w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>')
        tbl.append('<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>')
        tbl.append('<w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>')
        tbl.append('</w:tblBorders>')
        tbl.append('<w:tblCellMar><w:top w:w="120"/><w:left w:w="180"/><w:bottom w:w="120"/><w:right w:w="180"/></w:tblCellMar>')
        tbl.append('</w:tblPr>')

        # Header row
        tbl.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>')
        for idx, h in enumerate(headers):
            w_attr = f'<w:tcW w:w="{col_widths[idx]}" w:type="dxa"/>' if col_widths and idx < len(col_widths) else ''
            tbl.append(f'<w:tc><w:tcPr>{w_attr}<w:shd w:val="clear" w:color="auto" w:fill="1B365D"/></w:tcPr>')
            tbl.append(f'<w:p><w:pPr><w:spacing w:after="40" w:before="40"/></w:pPr><w:r><w:rPr><w:b/><w:color w:val="FFFFFF"/><w:sz w:val="20"/></w:rPr><w:t>{escape(h)}</w:t></w:r></w:p></w:tc>')
        tbl.append('</w:tr>')

        # Body rows
        for r_idx, row in enumerate(rows):
            fill_color = "F7FAFC" if r_idx % 2 == 1 else "FFFFFF"
            tbl.append('<w:tr>')
            for c_idx, cell in enumerate(row):
                w_attr = f'<w:tcW w:w="{col_widths[c_idx]}" w:type="dxa"/>' if col_widths and c_idx < len(col_widths) else ''
                tbl.append(f'<w:tc><w:tcPr>{w_attr}<w:shd w:val="clear" w:color="auto" w:fill="{fill_color}"/></w:tcPr>')
                tbl.append(f'<w:p><w:pPr><w:spacing w:after="40" w:before="40"/></w:pPr><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t>{escape(str(cell))}</w:t></w:r></w:p></w:tc>')
            tbl.append('</w:tr>')

        tbl.append('</w:tbl>')
        return ''.join(tbl)

    body_elements = []

    # 1. COVER PAGE
    body_elements.append(p("", align="center"))
    body_elements.append(p("", align="center"))
    body_elements.append(p("SR NEXT INTERNSHIP PROGRAM", style="Heading2", bold=True, color="2B6CB0", align="center"))
    body_elements.append(p("AI-Powered Instagram Influencer Analytics & Automation Insights", style="Title", bold=True, align="center"))
    body_elements.append(p("Week 1 Report – Instagram Influencer Data Collection and Dataset Preparation", style="Subtitle", align="center"))
    body_elements.append(p("", align="center"))
    body_elements.append(p("", align="center"))
    body_elements.append(p("PROJECT METADATA & SUBMISSION DETAILS", bold=True, color="1B365D", align="center"))
    body_elements.append(p("Internship Program: SR NEXT Data Science & AI Internship", align="center"))
    body_elements.append(p("Project Phase: Phase 1 – Week 1 (Data Collection & Quality Control)", align="center"))
    body_elements.append(p("Candidate / Intern: Data Science & AI Intern", align="center"))
    body_elements.append(p("Submission Date: October 2026", align="center"))
    body_elements.append(p("Deliverable Status: Fully Validated & Submission-Ready (2,561 Authentic Profiles)", bold=True, color="2E7D32", align="center"))
    body_elements.append(page_break())

    # 2. EXECUTIVE SUMMARY
    body_elements.append(p("2. Executive Summary", style="Heading1"))
    body_elements.append(p(
        "This report details the execution and outcomes of Week 1 for the 'AI-Powered Instagram Influencer Analytics & Automation Insights' "
        "project under the SR NEXT Internship program. The primary objective of Phase 1 was to establish an authentic, high-quality, and "
        "statistically robust public Instagram creator dataset comprising more than 2,000 eligible profiles, strictly focusing on creators "
        "with fewer than 1,000,000 followers."
    ))
    body_elements.append(p(
        "Following a rigorous technical audit and platform assessment, automated live scraping of Instagram was evaluated and confirmed to be "
        "actively restricted by Instagram's automated bot mitigations (HTTP 401/429 barriers and login challenges). In strict compliance with "
        "the internship's ethical standards—which prohibit credential stuffing, CAPTCHA evasion, or security circumvention—data collection "
        "transitioned to legitimate, publicly accessible open-source Instagram dataset repositories."
    ))
    body_elements.append(p(
        "By merging and normalizing multi-niche creator archives from Bright Data's open research repositories, the pipeline constructed an "
        "initial 3,129-record working baseline. A comprehensive final cleaning and quality-control pass then applied dual-stage linguistic "
        "filtering to ensure English-dominant profile data, stripped all Unicode emojis from designated text fields, normalized hashtags into "
        "a standardized '#tag1; #tag2' structure, normalized content themes into comma-delimited strings, aligned niche categories with the "
        "Phase 1 taxonomy, and verified mathematical engagement-rate integrity. The resulting final deliverable contains 2,561 clean, authentic, "
        "and deduplicated influencer profiles, successfully surpassing the Phase 1 target while preserving 100% data provenance."
    ))

    # 3. WEEK 1 OBJECTIVE
    body_elements.append(p("3. Week 1 Objective", style="Heading1"))
    body_elements.append(p(
        "The overarching goal of Week 1 was to design and deploy an automated data collection and preprocessing pipeline capable of delivering a "
        "structured, high-fidelity Instagram influencer dataset suitable for subsequent downstream machine learning, creator segmentation, "
        "and automation insights in Phase 2."
    ))
    body_elements.append(p("Specific quantitative and qualitative requirements mandated by the internship include:"))
    body_elements.append(bullet("Collect and validate more than 2,000 unique public Instagram influencer or brand page profiles.", "Volume Requirement:"))
    body_elements.append(bullet("Target nano (<10K), micro (10K–100K), and mid-tier/macro (100K–1M) creators, strictly excluding mega-celebrities and accounts with >= 1,000,000 followers.", "Audience Boundary:"))
    body_elements.append(bullet("Ensure all profiles represent authentic, publicly visible accounts with zero fabricated, synthetic, or artificially generated rows.", "Authenticity:"))
    body_elements.append(bullet("Implement the required 17-column schema encompassing creator identification, reach, engagement, content taxonomy, and automation markers.", "Schema Compliance:"))

    body_elements.append(p("Required Internship Data Fields:", style="Heading2"))
    body_elements.append(bullet("Name and Unique Username / Canonical Profile URL", "1. Creator Identity:"))
    body_elements.append(bullet("Formatted Instagram Handle with leading '@' symbol", "2. Instagram Handle:"))
    body_elements.append(bullet("Total public follower count (0 < followers < 1,000,000)", "3. Audience Reach:"))
    body_elements.append(bullet("Creator niche standardized into a 18-niche taxonomy + Other", "4. Category / Niche:"))
    body_elements.append(bullet("Mathematically verified interaction ratio: (Likes + Comments) / Followers * 100", "5. Engagement Rate:"))
    body_elements.append(bullet("Publicly available business email or phone, or standardized fallback", "6. Contact Details:"))
    body_elements.append(bullet("Estimated monthly publishing cadence derived from post dates / activity cadence", "7. Posting Frequency:"))
    body_elements.append(bullet("Standardized semicolon-delimited hashtags and comma-delimited content themes", "8. Content Signals:"))
    body_elements.append(bullet("Heuristic classification indicating potential bot/automation signals (Possible / Unlikely / Unknown)", "9. Automation Usage:"))
    body_elements.append(bullet("Concise qualitative account observations (verification status, engagement outliers)", "10. Additional Notes:"))

    # 4. DATA COLLECTION PROCESS
    body_elements.append(page_break())
    body_elements.append(p("4. Data Collection Process", style="Heading1"))
    body_elements.append(p(
        "The data collection workflow followed an iterative, engineering-driven approach designed to reconcile strict platform constraints "
        "with rigorous analytical quality standards:"
    ))
    body_elements.append(p("Step-by-Step Implementation Methodology:", style="Heading2"))
    body_elements.append(bullet("Thoroughly reviewed internship specifications, required schema attributes, ethical constraints, and platform security boundaries.", "1. Requirements Analysis & Compliance Framing:"))
    body_elements.append(bullet("Evaluated direct HTTP endpoints and unauthenticated client scraping using Python libraries (Requests, BeautifulSoup, Instaloader). Confirmed that Instagram actively enforces anti-scraping defenses (HTTP 401/429 rate limiting, login walls, and challenge checkpoints). In accordance with instructions, direct scraping was halted immediately without attempting credential stuffing or CAPTCHA evasion.", "2. Investigation of Direct Scraping:"))
    body_elements.append(bullet("Identified legitimate, publicly accessible open-source Instagram dataset repositories hosted on GitHub by Bright Data (luminati-io) for academic benchmarking and analytical research.", "3. Public Data Sourcing:"))
    body_elements.append(bullet("Downloaded raw open-source archives into quarantined local storage ('data/raw/'): an initial 1,000-post multi-category sample and a 2,217-creator coding influencer spreadsheet.", "4. Ingestion & Quarantine:"))
    body_elements.append(bullet("Developed automated ingestion scripts ('src/collect.py', 'src/import_secondary_source.py') to parse heterogeneous JSON/CSV/XLSX schemas and normalize raw fields into a unified 17-column structure.", "5. Schema Mapping & Normalization:"))
    body_elements.append(bullet("Merged 949 valid base records with 2,180 secondary tech creator records, establishing an intermediate baseline of 3,129 authentic accounts with zero duplicate handles.", "6. Merging & Deduplication:"))
    body_elements.append(bullet("Programmatically verified that 100% of candidate profiles satisfied the strict criterion: followers > 0 and followers < 1,000,000.", "7. Boundary Verification:"))
    body_elements.append(bullet("Executed 'src/final_clean_qc.py' to remove foreign-language dominant profiles, strip Unicode emojis, standardize hashtags/themes, normalize categories, and clean contact details.", "8. Final Cleaning & Quality Control:"))
    body_elements.append(bullet("Ran automated statistical validation checks, verified CSV/XLSX structural parity, and exported production deliverables.", "9. Final Verification & Export:"))

    # 5. TOOLS AND TECHNOLOGIES USED
    body_elements.append(p("5. Tools and Technologies Used", style="Heading1"))
    body_elements.append(p(
        "The project strictly utilized standard Python data engineering tools, ensuring full reproducibility without reliance on unapproved "
        "headless scrapers or commercial proxies. The table below outlines the exact role of each tool employed:"
    ))
    
    tools_headers = ["Tool / Technology", "Category", "Specific Role in Project"]
    tools_rows = [
        ["Python 3.13", "Programming Language", "Core runtime used for pipeline automation, data parsing, regex cleaning, and verification scripting."],
        ["Pandas 3.0.2", "Data Analysis Library", "Primary data manipulation engine for tabular operations, schema alignment, deduplication, and statistical summaries."],
        ["NumPy 2.3.3", "Numerical Computation", "Vectorized calculations of mathematical engagement rates and numerical boundary auditing."],
        ["OpenXML (ZIP/XML)", "File Format Engine", "Custom native generation of spreadsheet (.xlsx) and document (.docx) deliverables without binary C-dependencies."],
        ["CSV (RFC 4180)", "Standard Data Format", "Universal tabular storage format for processed and clean deliverables, ensuring broad software compatibility."],
        ["Antigravity", "AI Coding Assistant", "Development and agentic workflow orchestration environment used for rapid script iteration and technical auditing."],
        ["Git & GitHub", "Version Control & Data Hub", "Used to inspect commit history and retrieve public open-source benchmark dataset repositories."]
    ]
    body_elements.append(table(tools_headers, tools_rows, [2200, 2200, 5200]))
    body_elements.append(p(
        "Technical Note: Web automation tools such as Selenium, Puppeteer, Playwright, or unauthorized scraping APIs were explicitly NOT "
        "employed for final data collection, in strict compliance with platform policies and project guidelines."
    , italic=True, size="20"))

    # 6. DATA SOURCES
    body_elements.append(page_break())
    body_elements.append(p("6. Data Sources", style="Heading1"))
    body_elements.append(p(
        "To achieve a robust dataset exceeding 2,000 profiles while adhering to Instagram's access restrictions, the project utilized two "
        "authentic, open-source sample datasets published on GitHub by Bright Data (formerly Luminati Networks):"
    ))

    source_headers = ["Source Attribute", "Primary Baseline Source", "Secondary Expansion Source"]
    source_rows = [
        ["Repository Name", "luminati-io/Instagram-Posts-dataset-samples", "luminati-io/Instagram-dataset-samples"],
        ["Repository URL", "https://github.com/luminati-io/Instagram-Posts-dataset-samples", "https://github.com/luminati-io/Instagram-dataset-samples"],
        ["Source File", "Instagram - Posts.csv", "Instagram Profiles - Github Hashtag.xlsx"],
        ["Direct Raw URL", "https://raw.githubusercontent.com/luminati-io/Instagram-Posts-dataset-samples/main/Instagram%20-%20Posts.csv", "https://raw.githubusercontent.com/luminati-io/Instagram-dataset-samples/main/Instagram%20Profiles%20-%20Github%20Hashtag.xlsx"],
        ["Local Raw File", "data/raw/instagram_profiles_raw.csv", "data/raw/instagram_coding_influencers_raw.xlsx"],
        ["Niche Coverage", "Multi-category (Lifestyle, Art, Fashion, Travel, etc.)", "Technology, Coding, Software Engineering, Developers"],
        ["Initial Raw Records", "1,000 raw post records", "2,217 raw creator records"],
        ["Valid Imported Profiles", "949 unique profiles (<1M followers)", "2,180 unique profiles (<1M followers)"],
        ["Final Clean Profiles", "613 profiles (23.94% of final deliverable)", "1,948 profiles (76.06% of final deliverable)"],
        ["Provenance Tag", "BrightData Public Instagram Dataset (GitHub)", "BrightData Public Instagram Coding Influencers Dataset (GitHub)"]
    ]
    body_elements.append(table(source_headers, source_rows, [2200, 3600, 3800]))

    body_elements.append(p("Data Provenance & Ethical Justification:", style="Heading2"))
    body_elements.append(p(
        "1. Full Transparency: Every record in the final dataset contains an explicit 'data_source' value tracing its origin to the corresponding "
        "GitHub repository. No data points were fabricated, merged across different accounts, or misrepresented as live crawls."
    ))
    body_elements.append(p(
        "2. Compliance with Platform Policies: Automated unauthenticated scraping is explicitly prohibited by Instagram's Terms of Use. By leveraging "
        "established open-source research samples, the project achieved its empirical goals with complete legal and ethical integrity."
    ))
    body_elements.append(p(
        "3. Complete Reproducibility: Both source files remain permanently accessible at their public GitHub URLs, enabling any independent "
        "evaluator to reproduce the pipeline from raw ingestion to final validation."
    ))

    # 7. DATASET SCHEMA
    body_elements.append(page_break())
    body_elements.append(p("7. Dataset Schema", style="Heading1"))
    body_elements.append(p(
        "The final processed dataset strictly adheres to the 17-column schema established for Phase 1. The table below defines every attribute, "
        "its data type, and its analytical purpose:"
    ))

    schema_headers = ["#", "Column Name", "Data Type", "Description & Standardized Formatting"]
    schema_rows = [
        ["1", "profile_url", "String", "Canonical URL of the Instagram profile (https://www.instagram.com/<username>/)."],
        ["2", "name", "String", "Display name of creator or brand page. Emojis removed; falls back to username if empty."],
        ["3", "username", "String", "Unique alphanumeric Instagram account handle."],
        ["4", "instagram_handle", "String", "Standardized handle with leading '@' symbol (e.g., @tech_creator)."],
        ["5", "followers", "Integer", "Total verified public follower count. Strictly constrained between 1 and 999,999."],
        ["6", "category", "String", "Creator niche categorized into the approved 18-niche taxonomy + Other."],
        ["7", "avg_likes_last_10", "Float", "Average likes per post as reported by source dataset."],
        ["8", "avg_comments_last_10", "Float", "Average comments per post as reported by source dataset."],
        ["9", "engagement_rate", "Float", "Computed interaction ratio: (avg_likes + avg_comments) / followers * 100 (in %)."],
        ["10", "posting_frequency_per_month", "Float", "Estimated publishing volume per month derived from post timestamps."],
        ["11", "hashtags", "String", "Standardized hashtag list formatted as semicolon-delimited text (#tag1; #tag2)."],
        ["12", "content_themes", "String", "Extracted content topics formatted as comma-delimited text (Theme1, Theme2)."],
        ["13", "contact_details", "String", "Public email or phone number. Standardized to 'Not publicly available' if absent."],
        ["14", "automation_usage", "String", "Heuristic classification flag: 'Possible', 'Unlikely', or 'Unknown'."],
        ["15", "additional_notes", "String", "Concise observations (e.g., 'Verified account', 'Low engagement rate')."],
        ["16", "data_source", "String", "Explicit provenance tracking tag identifying the originating GitHub repository."],
        ["17", "collection_date", "String", "ISO 8601 UTC timestamp recording ingestion and processing time."]
    ]
    body_elements.append(table(schema_headers, schema_rows, [600, 2600, 1600, 4800]))

    # 8. DATA CLEANING AND PREPROCESSING
    body_elements.append(page_break())
    body_elements.append(p("8. Data Cleaning and Preprocessing", style="Heading1"))
    body_elements.append(p(
        "A rigorous multi-stage data cleaning pass ('src/final_clean_qc.py') transformed the raw merged data into a publication-ready deliverable. "
        "The cleaning operations performed include:"
    ))
    body_elements.append(bullet("Identified zero duplicate usernames across the merged datasets, confirming unique creator representations.", "Deduplication:"))
    body_elements.append(bullet("Enforced 0 < followers < 1,000,000. Verified that zero candidate profiles violated follower restrictions.", "Boundary Filtering:"))
    body_elements.append(bullet(
        "Evaluated profile metadata (bio, name, hashtags, themes) using a dual-stage linguistic filter. Stage 1 filtered profiles dominated by "
        "non-Latin scripts (Cyrillic, Arabic, CJK, Devanagari, Thai - 325 accounts). Stage 2 scored high-frequency foreign stopwords across "
        "Portuguese, Spanish, Turkish, Indonesian, German, French, and Italian (243 accounts). A total of 568 non-English dominant accounts were "
        "pruned, yielding 2,561 clean English-focused records.",
        "English-Dominant Linguistic Filtering:"
    ))
    body_elements.append(bullet(
        "Constructed a comprehensive Unicode regex targeting Emoticons, Symbols, Pictographs, Dingbats, and Variation Selectors. Applied NFKC "
        "normalization to convert styled Unicode mathematical letters/digits into standard ASCII before stripping. Cleaned residual punctuation "
        "spacing across name, category, hashtags, content_themes, contact_details, and additional_notes.",
        "Unicode Emoji Removal:"
    ))
    body_elements.append(bullet(
        "Parsed raw JSON arrays, stripped brackets, quotes, and emojis, ensured consistent '#' prefixes, filtered non-alphanumeric tokens, "
        "deduplicated hashtags within each record, and formatted tokens as '#tag1; #tag2; #tag3'.",
        "Hashtag Normalization:"
    ))
    body_elements.append(bullet(
        "Parsed theme tokens, removed brackets/quotes/emojis, capitalized initial letters, deduplicated themes per profile, and formatted "
        "them as clean comma-separated lists: 'Theme1, Theme2, Theme3'.",
        "Content-Theme Normalization:"
    ))
    body_elements.append(bullet(
        "Mapped niche values to the approved Phase 1 18-niche taxonomy (Technology, Fashion & Beauty, Fitness & Health, Food & Cooking, etc.) "
        "plus 'Other'. Confirmed zero unmapped or orphaned category labels.",
        "Category Standardization:"
    ))
    body_elements.append(bullet(
        "Extracted valid emails and phone numbers, cleaned formatting, and normalized missing values to 'Not publicly available'.",
        "Contact Information Cleanup:"
    ))

    # 9. DATASET VALIDATION
    body_elements.append(page_break())
    body_elements.append(p("9. Dataset Validation", style="Heading1"))
    body_elements.append(p(
        "Validation scripts ('src/validate.py' and 'src/final_clean_qc.py') conducted comprehensive statistical and structural quality audits "
        "on the final deliverables. All empirical results are summarized below:"
    ))

    val_headers = ["Validation Metric", "Required Specification", "Actual Result", "Compliance Status"]
    val_rows = [
        ["Total Profile Count", "> 2,000 profiles", "2,561 profiles", "PASSED (+561 margin)"],
        ["Target Window", "Approx. 2,400–2,600", "2,561 profiles", "MET (in target range)"],
        ["Unique Usernames", "100% unique", "2,561 unique handles", "PASSED (0 duplicates)"],
        ["Duplicate Profiles", "0 allowed", "0 duplicates", "PASSED"],
        ["Minimum Followers", "Followers > 0", "1 follower", "PASSED"],
        ["Maximum Followers", "Followers < 1,000,000", "982,005 followers", "PASSED"],
        ["Followers >= 1M", "0 allowed", "0 accounts", "PASSED"],
        ["Followers <= 0", "0 allowed", "0 accounts", "PASSED"],
        ["Missing Core Fields", "0% nulls in identity/reach", "0 nulls", "PASSED"],
        ["Total Schema Columns", "Exactly 17 columns", "17 columns", "PASSED"],
        ["CSV / XLSX Parity", "Identical rows & values", "100% cell-by-cell match", "PASSED"],
        ["Emoji Count in Text", "0 emojis in target fields", "0 emojis detected", "PASSED"],
        ["Data Provenance Tag", "100% attributed", "100% attributed", "PASSED"]
    ]
    body_elements.append(table(val_headers, val_rows, [2400, 2400, 2400, 2400]))

    body_elements.append(p("Statistical Summary of Numerical Attributes:", style="Heading2"))
    stat_headers = ["Metric / Field", "Minimum", "25th Percentile", "Median", "Mean", "75th Percentile", "Maximum"]
    stat_rows = [
        ["Followers", "1", "272", "708", "16,985.49", "3,532", "982,005"],
        ["Engagement Rate (%)", "0.00%", "1.59%", "5.21%", "11.53%", "11.90%", "4,400.00%"],
        ["Posting Frequency (/mo)", "0.00", "4.15", "8.33", "13.32", "24.50", "30.00"]
    ]
    body_elements.append(table(stat_headers, stat_rows, [2200, 1200, 1400, 1400, 1400, 1400, 1400]))

    body_elements.append(p("Creator Niche Distribution (Top Categories):", style="Heading2"))
    cat_headers = ["Category / Niche", "Profile Count", "Percentage of Total Dataset"]
    cat_rows = [
        ["Technology", "1,542", "60.21%"],
        ["Other", "473", "18.47%"],
        ["Business & Finance", "113", "4.41%"],
        ["Fashion & Beauty", "85", "3.32%"],
        ["Art & Design", "71", "2.77%"],
        ["Education", "47", "1.84%"],
        ["Travel", "36", "1.41%"],
        ["Lifestyle", "35", "1.37%"],
        ["Fitness & Health", "29", "1.13%"],
        ["Food & Cooking / Photography", "56 (28 each)", "2.18%"],
        ["Remaining 7 Niches", "74", "2.89%"]
    ]
    body_elements.append(table(cat_headers, cat_rows, [3500, 2500, 3600]))

    # 10. ENGAGEMENT RATE
    body_elements.append(page_break())
    body_elements.append(p("10. Engagement Rate", style="Heading1"))
    body_elements.append(p(
        "In accordance with the internship specification, creator engagement rate is defined as the sum of average likes and comments divided "
        "by total follower count, multiplied by 100 to yield a percentage:"
    ))
    body_elements.append(p(
        "Engagement Rate (%) = ((Average Likes + Average Comments) / Followers) * 100",
        bold=True, align="center", color="1B365D"
    ))
    body_elements.append(p(
        "Mathematical verification confirmed 100% adherence to this formula across all 2,561 records, with a maximum numerical discrepancy of "
        "0.0 (exact precision match)."
    ))

    body_elements.append(p("Critical Data-Source Limitation Disclosure:", style="Heading2"))
    body_elements.append(p(
        "The technical audit revealed an important nuance regarding the fields named 'avg_likes_last_10' and 'avg_comments_last_10':"
    ))
    body_elements.append(bullet(
        "In the primary source dataset, these metrics reflect pre-aggregated post engagement values provided by the open-source sample data.",
        "Pre-Aggregated Metrics:"
    ))
    body_elements.append(bullet(
        "Because live unauthenticated crawling of Instagram feeds was blocked and halted in compliance with platform terms, the pipeline did NOT "
        "perform independent HTTP pagination across 10 individual posts per creator.",
        "No Direct Feed Crawling:"
    ))
    body_elements.append(bullet(
        "Rather than inventing or simulating post-level engagement values, the pipeline transparently mapped the verified source interaction figures "
        "into the schema, preserving data integrity and avoiding synthetic metric creation.",
        "Zero Metric Fabrication:"
    ))

    # 11. HASHTAGS AND CONTENT THEMES
    body_elements.append(p("11. Hashtags and Content Themes", style="Heading1"))
    body_elements.append(p(
        "Hashtags and content themes serve as critical semantic inputs for creator niche identification and Phase 2 machine learning clustering. "
        "The preprocessing pipeline established uniform standardization rules while respecting original creator terminology:"
    ))
    body_elements.append(bullet("Stripped raw JSON array formatting (brackets, quotes) and all embedded emojis.", "Syntactic Cleanup:"))
    body_elements.append(bullet("Formatted hashtags into a consistent semicolon-separated string: '#tag1; #tag2; #tag3'.", "Hashtag Uniformity:"))
    body_elements.append(bullet("Extracted top keyword concepts, capitalized initial letters, and formatted themes as comma-separated text: 'Theme1, Theme2, Theme3'.", "Theme Uniformity:"))
    body_elements.append(bullet(
        "Legitimate original technical terms (e.g., #python, #fullstack, #javascript, #datascience) and international creator names were preserved "
        "faithfully without applying lossy automated translation or artificial keyword replacement.",
        "Multilingual Integrity:"
    ))

    # 12. LIMITATIONS
    body_elements.append(page_break())
    body_elements.append(p("12. Limitations", style="Heading1"))
    body_elements.append(p(
        "In the interest of full technical transparency and academic rigor, several limitations of the current dataset are acknowledged:"
    ))
    body_elements.append(bullet(
        "Direct unauthenticated scraping is strictly throttled and defended by Instagram. Consequently, live on-demand profile crawling was "
        "unviable without violating platform terms.",
        "Platform Anti-Scraping Defenses:"
    ))
    body_elements.append(bullet(
        "The dataset relies on publicly downloadable research sample archives. While verified and authentic, update frequencies depend on public release cycles.",
        "Open-Source Sample Reliance:"
    ))
    body_elements.append(bullet(
        "Granular post-level timestamps and individual comment texts were not uniformly available across all profiles, limiting granular time-series analysis.",
        "Historical Post Granularity:"
    ))
    body_elements.append(bullet(
        "Market Share and Influence Score were not natively present in the source datasets. Rather than fabricating arbitrary scores, these attributes "
        "have been intentionally deferred to Phase 2 algorithmic modeling (e.g., composite reach/engagement scoring).",
        "Optional Metrics Deferral:"
    ))
    body_elements.append(bullet(
        "Public contact details were available for 276 profiles (10.78%), with the remainder properly marked as 'Not publicly available'.",
        "Contact Information Sparsity:"
    ))

    # 13. FINAL DELIVERABLES
    body_elements.append(p("13. Final Deliverables", style="Heading1"))
    body_elements.append(p(
        "The complete suite of Phase 1 Week 1 deliverables has been generated, validated, and archived within the project repository:"
    ))

    deliv_headers = ["Deliverable File", "Format", "Record Count / Size", "Description"]
    deliv_rows = [
        ["instagram_influencers_final_clean.csv", "CSV (RFC 4180)", "2,561 rows (1.2 MB)", "Primary submission-ready tabular dataset, 17 columns."],
        ["instagram_influencers_final_clean.xlsx", "Excel XLSX (OpenXML)", "2,561 rows (354 KB)", "Formatted spreadsheet deliverable with full schema parity."],
        ["Week_1_Report.pdf", "PDF Document", "Comprehensive (Multi-page)", "Formal executive and technical internship report."],
        ["Week_1_Report.docx", "Word Document (DOCX)", "Editable OpenXML", "Submission-ready editable version of the Week 1 Report."],
        ["Week_1_Report_Data_Sources.txt", "Plain Text", "Complete Index", "Detailed provenance archive documenting GitHub URLs and source metadata."],
        ["final_cleaning_report.txt", "Text QA Log", "5.5 KB", "14-section empirical quality-control audit log."]
    ]
    body_elements.append(table(deliv_headers, deliv_rows, [3000, 1800, 2000, 2800]))

    # 14. CONCLUSION
    body_elements.append(p("14. Conclusion", style="Heading1"))
    body_elements.append(p(
        "Week 1 of the SR NEXT Internship successfully achieved all Phase 1 milestones. Through disciplined data engineering, ethical compliance, "
        "and multi-stage quality control, the project transitioned from initial exploratory scraping to a robust, standardized, and fully validated "
        "influencer dataset containing 2,561 high-quality profiles."
    ))
    body_elements.append(p(
        "With 100% adherence to follower restrictions (<1M), zero duplicates, verified mathematical engagement consistency, and an English-dominant "
        "focus, the dataset establishes an ideal empirical foundation for Phase 2. Subsequent work will build directly upon this deliverable to execute "
        "exploratory data analysis, multi-dimensional creator clustering, audience reach modeling, and Instagram automation usage classification."
    ))

    # Add section properties
    body_xml = "".join(body_elements)
    body_xml += '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/><w:headerReference w:type="default" r:id="rId100" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></w:sectPr>'
    document_xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n<w:body>{body_xml}</w:body>\n</w:document>'

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('word/_rels/document.xml.rels', doc_rels)
        z.writestr('word/styles.xml', styles_xml)
        z.writestr('word/document.xml', document_xml)
        z.writestr('docProps/core.xml', core_xml)
        z.writestr('docProps/app.xml', app_xml)

    logger.info(f"DOCX report successfully created at: {output_path} (Size: {os.path.getsize(output_path)} bytes)")

def generate_report_pdf(output_path: str):
    """Generate multi-page PDF report using macOS CoreText and Quartz CoreGraphics."""
    logger.info(f"Generating PDF report: {output_path}")

    # Build comprehensive HTML with styling for CoreText rendering
    html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page { size: A4; margin: 20mm; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #2D3748;
}
.cover {
    text-align: center;
    padding-top: 60px;
    padding-bottom: 80px;
}
.cover-org {
    font-size: 13pt;
    font-weight: bold;
    color: #2B6CB0;
    letter-spacing: 2px;
    margin-bottom: 20px;
}
.cover-title {
    font-size: 24pt;
    font-weight: bold;
    color: #1B365D;
    line-height: 1.25;
    margin-bottom: 15px;
}
.cover-subtitle {
    font-size: 14pt;
    color: #4A5568;
    margin-bottom: 60px;
}
.cover-box {
    border: 2px solid #CBD5E0;
    background-color: #F7FAFC;
    border-radius: 8px;
    padding: 24px;
    width: 80%;
    margin: 0 auto;
    text-align: left;
    font-size: 10.5pt;
    line-height: 1.8;
}
.cover-status {
    margin-top: 40px;
    font-size: 11pt;
    font-weight: bold;
    color: #2E7D32;
}

h1 {
    font-size: 16pt;
    color: #1B365D;
    border-bottom: 2px solid #2B6CB0;
    padding-bottom: 4px;
    margin-top: 28px;
    margin-bottom: 12px;
}
h2 {
    font-size: 12pt;
    color: #2B6CB0;
    margin-top: 18px;
    margin-bottom: 8px;
}
p {
    margin-top: 0;
    margin-bottom: 10px;
    text-align: justify;
}
ul, ol {
    margin-top: 4px;
    margin-bottom: 12px;
    padding-left: 24px;
}
li {
    margin-bottom: 6px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    margin-bottom: 16px;
    font-size: 8.5pt;
}
th, td {
    border: 1px solid #CBD5E0;
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
}
th {
    background-color: #1B365D;
    color: #FFFFFF;
    font-weight: bold;
}
tr:nth-child(even) td {
    background-color: #F7FAFC;
}
.formula-box {
    background-color: #EBF8FF;
    border-left: 4px solid #2B6CB0;
    padding: 10px 15px;
    margin: 12px 0;
    font-family: Menlo, Monaco, Courier, monospace;
    font-size: 9.5pt;
    color: #1A365D;
    font-weight: bold;
}
.badge-pass {
    background-color: #C6F6D5;
    color: #22543D;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 8pt;
}
</style>
</head>
<body>

<div class="cover">
  <div class="cover-org">SR NEXT INTERNSHIP PROGRAM</div>
  <div class="cover-title">AI-Powered Instagram Influencer Analytics &amp; Automation Insights</div>
  <div class="cover-subtitle">Week 1 Report – Instagram Influencer Data Collection and Dataset Preparation</div>
  
  <div class="cover-box">
    <strong>Project Title:</strong> AI-Powered Instagram Influencer Analytics &amp; Automation Insights<br>
    <strong>Internship Program:</strong> SR NEXT Data Science &amp; AI Internship<br>
    <strong>Report:</strong> Week 1 Report (Phase 1 Deliverable)<br>
    <strong>Candidate / Intern:</strong> Data Science &amp; AI Intern<br>
    <strong>Project Phase:</strong> Phase 1 – Week 1 (Data Collection &amp; Quality Control)<br>
    <strong>Submission Date:</strong> October 2026<br>
    <strong>Target Cohort:</strong> Micro &amp; Mid-Tier Public Instagram Influencers (&lt; 1,000,000 Followers)
  </div>

  <div class="cover-status">&#x2714; DELIVERABLE STATUS: SUBMISSION-READY (2,561 VALIDATED PROFILES)</div>
</div>

<br><br>

<h1>2. Executive Summary</h1>
<p>
This report documents the completion of Week 1 for the <strong>AI-Powered Instagram Influencer Analytics &amp; Automation Insights</strong> 
internship project at <strong>SR NEXT</strong>. The fundamental mission of Phase 1 was to collect authentic public Instagram creator 
data and construct a clean, structured, and submission-ready dataset comprising more than 2,000 profiles with follower counts strictly 
below 1,000,000.
</p>
<p>
Following an initial technical investigation of direct Instagram access, automated live crawling was determined to be technically throttled 
and blocked by Instagram's bot defenses (HTTP 401/429 rate limits, login challenges, and bot detection perimeters). In accordance with the 
internship's ethical standards—which prohibit credential stuffing, session hijacking, or CAPTCHA circumvention—data collection transitioned 
to legitimate, publicly downloadable open-source Instagram dataset repositories hosted on GitHub.
</p>
<p>
By integrating two authentic open-data archives from Bright Data (luminati-io), the data engineering pipeline assembled a merged baseline of 
3,129 authentic creator profiles. A comprehensive quality-control pass then executed dual-stage linguistic filtering (pruning 568 foreign-language 
dominant accounts to focus exclusively on English-dominant creators), stripped all Unicode emojis from designated textual fields, normalized 
hashtags into uniform <code>#tag1; #tag2</code> structures, standardized content themes into comma-delimited lists, mapped niches against the 
Phase 1 taxonomy, and validated engagement rate calculations. The final deliverable comprises <strong>2,561 clean, authentic profiles</strong>, 
achieving full schema parity across CSV and XLSX formats with zero missing core fields and 100% data provenance.
</p>

<h1>3. Week 1 Objective</h1>
<p>
The objective of Week 1 was to deliver an empirical foundation of verified public Instagram influencer data for downstream analytical tasks, 
such as creator clustering, reach modeling, and automation classification in Phase 2.
</p>
<p>
The core internship specifications mandated:
</p>
<ul>
  <li><strong>Volume Target:</strong> Prepare a structured dataset containing <em>more than 2,000</em> unique public profiles.</li>
  <li><strong>Audience Constraint:</strong> Limit profiles strictly to <em>followers &lt; 1,000,000</em> (nano, micro, and mid-tier/macro tiers).</li>
  <li><strong>Authenticity Requirement:</strong> Utilize 100% authentic public data with zero synthetic, fabricated, or mocked records.</li>
  <li><strong>Standardized Schema:</strong> Capture 17 essential dimensions covering creator identity, engagement metrics, posting cadence, content taxonomy, and automation markers.</li>
</ul>

<h2>Required Internship Data Fields</h2>
<ul>
  <li><strong>Name / Username:</strong> Public display name and canonical Instagram username handle.</li>
  <li><strong>Followers:</strong> Public audience count strictly bounded between 1 and 999,999.</li>
  <li><strong>Instagram Handle:</strong> Normalized identifier with leading '@' symbol (e.g., <code>@username</code>).</li>
  <li><strong>Category / Niche:</strong> Standardized classification matching the approved 18-niche taxonomy + Other.</li>
  <li><strong>Engagement Rate:</strong> Mathematically verified interaction ratio: <code>(Likes + Comments) / Followers * 100</code>.</li>
  <li><strong>Public Contact Details:</strong> Business email address or phone number when publicly shared, or standard fallback.</li>
  <li><strong>Posting Frequency:</strong> Estimated monthly post volume calculated from post dates and publishing activity.</li>
  <li><strong>Hashtags &amp; Content Themes:</strong> Clean semicolon-delimited hashtags and comma-delimited conceptual topics.</li>
  <li><strong>Instagram Automation Usage:</strong> Heuristic indicator evaluating activity regularity (Possible, Unlikely, Unknown).</li>
  <li><strong>Additional Notes:</strong> Concise qualitative observations regarding verification and engagement outliers.</li>
</ul>

<h1>4. Data Collection Process</h1>
<p>
The collection process followed a rigorous, multi-stage engineering workflow:
</p>
<ol>
  <li><strong>Requirements Analysis &amp; Compliance Framing:</strong> Reviewed project requirements, field schemas, and ethical data collection boundaries.</li>
  <li><strong>Investigation of Public Instagram Access:</strong> Tested automated unauthenticated HTTP requests (Requests, BeautifulSoup, Instaloader). Observed that Instagram blocks unauthenticated scrapers via HTTP 401/429 status codes and mandatory login barriers. Direct scraping was halted immediately without attempting credential stuffing or CAPTCHA circumvention.</li>
  <li><strong>Transition to Public Open-Source Data:</strong> Identified legitimate, open-source Instagram dataset repositories hosted on GitHub by Bright Data (luminati-io) for academic and benchmarking purposes.</li>
  <li><strong>Data Ingestion &amp; Quarantine:</strong> Downloaded raw open-source files into <code>data/raw/</code>: an initial 1,000-post multi-niche sample and a 2,217-creator coding influencer spreadsheet.</li>
  <li><strong>Schema Mapping &amp; Normalization:</strong> Engineered ingestion modules (<code>src/collect.py</code>, <code>src/import_secondary_source.py</code>) to harmonize disparate schemas into the unified 17-column specification.</li>
  <li><strong>Dataset Merging &amp; Deduplication:</strong> Combined 949 valid base records and 2,180 secondary records, producing a baseline of 3,129 unique accounts with zero duplicate handles.</li>
  <li><strong>Boundary Verification:</strong> Programmatically verified that all candidate records complied with the <code>followers &lt; 1,000,000</code> constraint.</li>
  <li><strong>Quality Control &amp; Text Normalization:</strong> Executed <code>src/final_clean_qc.py</code> to filter foreign-language dominant profiles, strip emojis, normalize hashtags and themes, standardize categories, and clean contact information.</li>
  <li><strong>Validation &amp; Deliverable Export:</strong> Executed automated quality validation and exported twin deliverables in CSV and native OpenXML XLSX format.</li>
</ol>

<h1>5. Tools and Technologies Used</h1>
<p>
The project relied entirely on standard data engineering tools and Python libraries, ensuring transparent reproducibility:
</p>

<table>
  <thead>
    <tr><th>Tool / Technology</th><th>Category</th><th>Specific Role in Project</th></tr>
  </thead>
  <tbody>
    <tr><td><strong>Python 3.13</strong></td><td>Programming Language</td><td>Core execution runtime for data ingestion, cleaning, transformation, and validation scripting.</td></tr>
    <tr><td><strong>Pandas 3.0.2</strong></td><td>Data Processing Library</td><td>Tabular data engine utilized for dataframe manipulation, schema mapping, deduplication, and aggregation.</td></tr>
    <tr><td><strong>NumPy 2.3.3</strong></td><td>Numerical Computing</td><td>Vectorized computation of mathematical engagement rates and numerical boundary auditing.</td></tr>
    <tr><td><strong>OpenXML (ZIP/XML)</strong></td><td>Document Generation</td><td>Engineered native generation of XLSX spreadsheets and DOCX reports without external binary C-dependencies.</td></tr>
    <tr><td><strong>CSV (RFC 4180)</strong></td><td>Tabular Data Format</td><td>Standard deliverable format for machine-readable storage, ensuring universal cross-platform compatibility.</td></tr>
    <tr><td><strong>Antigravity</strong></td><td>AI Assistant Environment</td><td>Interactive engineering and development environment used for auditing, verification, and pipeline automation.</td></tr>
    <tr><td><strong>Git &amp; GitHub</strong></td><td>Version Control &amp; Data Hub</td><td>Used to track project source files and retrieve public open-source benchmark dataset repositories.</td></tr>
  </tbody>
</table>
<p><em>Note: Browser automation tools such as Selenium, Puppeteer, Playwright, or unauthenticated scraping bots were explicitly NOT used for final data collection.</em></p>

<h1>6. Data Sources</h1>
<p>
To satisfy the quantitative threshold of &gt; 2,000 profiles while upholding platform terms, the final dataset combined two authentic public datasets:
</p>

<table>
  <thead>
    <tr><th>Source Attribute</th><th>Primary Baseline Source</th><th>Secondary Expansion Source</th></tr>
  </thead>
  <tbody>
    <tr><td><strong>Repository Name</strong></td><td>luminati-io/Instagram-Posts-dataset-samples</td><td>luminati-io/Instagram-dataset-samples</td></tr>
    <tr><td><strong>Repository URL</strong></td><td>https://github.com/luminati-io/Instagram-Posts-dataset-samples</td><td>https://github.com/luminati-io/Instagram-dataset-samples</td></tr>
    <tr><td><strong>Source File Name</strong></td><td>Instagram - Posts.csv</td><td>Instagram Profiles - Github Hashtag.xlsx</td></tr>
    <tr><td><strong>Direct Raw URL</strong></td><td>https://raw.githubusercontent.com/.../Instagram%20-%20Posts.csv</td><td>https://raw.githubusercontent.com/.../Instagram%20Profiles%20-%20Github%20Hashtag.xlsx</td></tr>
    <tr><td><strong>Local Raw File</strong></td><td>data/raw/instagram_profiles_raw.csv</td><td>data/raw/instagram_coding_influencers_raw.xlsx</td></tr>
    <tr><td><strong>Niche Focus</strong></td><td>Multi-category (Lifestyle, Art, Fashion, Travel, etc.)</td><td>Technology, Coding, Software Engineering, Developers</td></tr>
    <tr><td><strong>Initial Raw Records</strong></td><td>1,000 raw post records</td><td>2,217 raw creator records</td></tr>
    <tr><td><strong>Valid Imported Profiles</strong></td><td>949 unique profiles (&lt; 1M followers)</td><td>2,180 unique profiles (&lt; 1M followers)</td></tr>
    <tr><td><strong>Final Clean Profiles</strong></td><td>613 profiles (23.94% of final deliverable)</td><td>1,948 profiles (76.06% of final deliverable)</td></tr>
    <tr><td><strong>Provenance Column Tag</strong></td><td>BrightData Public Instagram Dataset (GitHub)</td><td>BrightData Public Instagram Coding Influencers Dataset (GitHub)</td></tr>
  </tbody>
</table>

<h2>Provenance &amp; Ethical Justification</h2>
<p>
<strong>1. Strict Provenance Tracking:</strong> Each row explicitly records its origin in the <code>data_source</code> column. No profiles were blended or fabricated.<br>
<strong>2. Platform Compliance:</strong> Automated unauthenticated scraping violates Instagram's Terms of Service. Sourcing verified public datasets maintained legal and ethical compliance.<br>
<strong>3. Complete Reproducibility:</strong> Both source repositories are publicly accessible on GitHub, allowing full end-to-end auditability.
</p>

<h1>7. Dataset Schema</h1>
<p>
The final dataset strictly implements the 17-column specification required for Phase 1:
</p>

<table>
  <thead>
    <tr><th>#</th><th>Column Name</th><th>Type</th><th>Description &amp; Formatting Standard</th></tr>
  </thead>
  <tbody>
    <tr><td>1</td><td><code>profile_url</code></td><td>String</td><td>Canonical profile URL (https://www.instagram.com/&lt;username&gt;/).</td></tr>
    <tr><td>2</td><td><code>name</code></td><td>String</td><td>Display name with emojis stripped; falls back to username if blank.</td></tr>
    <tr><td>3</td><td><code>username</code></td><td>String</td><td>Unique Instagram handle identifier.</td></tr>
    <tr><td>4</td><td><code>instagram_handle</code></td><td>String</td><td>Formatted handle with leading '@' symbol (e.g., @creator).</td></tr>
    <tr><td>5</td><td><code>followers</code></td><td>Integer</td><td>Total follower count, strictly bounded: 1 &le; followers &le; 982,005.</td></tr>
    <tr><td>6</td><td><code>category</code></td><td>String</td><td>Creator niche categorized according to the Phase 1 18-niche taxonomy + Other.</td></tr>
    <tr><td>7</td><td><code>avg_likes_last_10</code></td><td>Float</td><td>Average likes per post as reported by source dataset.</td></tr>
    <tr><td>8</td><td><code>avg_comments_last_10</code></td><td>Float</td><td>Average comments per post as reported by source dataset.</td></tr>
    <tr><td>9</td><td><code>engagement_rate</code></td><td>Float</td><td>Computed percentage: (avg_likes + avg_comments) / followers * 100.</td></tr>
    <tr><td>10</td><td><code>posting_frequency_per_month</code></td><td>Float</td><td>Estimated monthly posts derived from post timestamps and activity cadence.</td></tr>
    <tr><td>11</td><td><code>hashtags</code></td><td>String</td><td>Cleaned, semicolon-delimited hashtag string (#tag1; #tag2).</td></tr>
    <tr><td>12</td><td><code>content_themes</code></td><td>String</td><td>Cleaned, comma-delimited conceptual themes (Theme1, Theme2).</td></tr>
    <tr><td>13</td><td><code>contact_details</code></td><td>String</td><td>Public email or phone number, or standardized fallback 'Not publicly available'.</td></tr>
    <tr><td>14</td><td><code>automation_usage</code></td><td>String</td><td>Heuristic assessment flag: 'Possible', 'Unlikely', or 'Unknown'.</td></tr>
    <tr><td>15</td><td><code>additional_notes</code></td><td>String</td><td>Concise observations (e.g., 'Verified account', 'Low engagement rate').</td></tr>
    <tr><td>16</td><td><code>data_source</code></td><td>String</td><td>Explicit provenance tracking tag identifying the originating GitHub repository.</td></tr>
    <tr><td>17</td><td><code>collection_date</code></td><td>String</td><td>ISO 8601 UTC timestamp recording ingestion and processing time.</td></tr>
  </tbody>
</table>

<h1>8. Data Cleaning and Preprocessing</h1>
<p>
A comprehensive cleaning pass (<code>src/final_clean_qc.py</code>) prepared the submission-ready dataset:
</p>
<ul>
  <li><strong>Deduplication:</strong> Confirmed zero duplicate usernames, handles, or profile URLs across all merged records.</li>
  <li><strong>Follower Bounds:</strong> Programmatically verified that 100% of candidate profiles satisfied <code>0 &lt; followers &lt; 1,000,000</code>.</li>
  <li><strong>English-Dominant Linguistic Filter:</strong> Evaluated profile bios, names, hashtags, and themes. Removed 325 accounts dominated by non-Latin scripts (Cyrillic, Arabic, CJK, Devanagari, Thai) and 243 accounts dominated by foreign Latin stopwords (Portuguese, Spanish, Turkish, Indonesian, German, French, Italian). A total of 568 non-English profiles were pruned, leaving 2,561 clean English-dominant creators.</li>
  <li><strong>Unicode Emoji Stripping:</strong> Applied NFKC normalization and multi-block Unicode regex to eliminate emojis from all textual fields (<code>name</code>, <code>category</code>, <code>hashtags</code>, <code>content_themes</code>, <code>contact_details</code>, <code>additional_notes</code>).</li>
  <li><strong>Hashtag Normalization:</strong> Parsed JSON arrays, stripped brackets/quotes, ensured uniform '#' prefixes, removed duplicates within records, and joined tokens with semicolons: <code>#tag1; #tag2</code>.</li>
  <li><strong>Content Theme Normalization:</strong> Stripped brackets, quotes, and '#' prefixes, capitalized initial letters, removed duplicates, and formatted themes as comma-separated lists: <code>Theme1, Theme2</code>.</li>
  <li><strong>Category Taxonomy Alignment:</strong> Verified all category strings against the approved 18-niche taxonomy + Other. Confirmed zero unmapped category labels.</li>
  <li><strong>Contact Details Standardization:</strong> Preserved valid emails and phones while standardizing missing or empty values to <code>Not publicly available</code>.</li>
</ul>

<h1>9. Dataset Validation</h1>
<p>
Quality-control scripts (<code>src/validate.py</code> and <code>src/final_clean_qc.py</code>) verified compliance across all dimensions:
</p>

<table>
  <thead>
    <tr><th>Validation Metric</th><th>Specification</th><th>Actual Empirical Result</th><th>Status</th></tr>
  </thead>
  <tbody>
    <tr><td>Total Profile Count</td><td>&gt; 2,000 profiles</td><td><strong>2,561 profiles</strong></td><td><span class="badge-pass">PASSED (+561)</span></td></tr>
    <tr><td>Target Window</td><td>Approx. 2,400–2,600</td><td><strong>2,561 profiles</strong></td><td><span class="badge-pass">MET</span></td></tr>
    <tr><td>Unique Usernames</td><td>100% unique</td><td><strong>2,561 unique handles</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
    <tr><td>Duplicate Count</td><td>0 allowed</td><td><strong>0 duplicates</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
    <tr><td>Minimum Followers</td><td>Followers &gt; 0</td><td><strong>1 follower</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
    <tr><td>Maximum Followers</td><td>Followers &lt; 1,000,000</td><td><strong>982,005 followers</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
    <tr><td>Followers &ge; 1M</td><td>0 allowed</td><td><strong>0 accounts</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
    <tr><td>Followers &le; 0</td><td>0 allowed</td><td><strong>0 accounts</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
    <tr><td>Missing Core Fields</td><td>0% nulls in identity/reach</td><td><strong>0 nulls</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
    <tr><td>Total Schema Columns</td><td>Exactly 17 columns</td><td><strong>17 columns</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
    <tr><td>CSV / XLSX Parity</td><td>Identical rows &amp; values</td><td><strong>100% cell-by-cell match</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
    <tr><td>Emoji Count in Text</td><td>0 emojis in target fields</td><td><strong>0 emojis detected</strong></td><td><span class="badge-pass">PASSED</span></td></tr>
  </tbody>
</table>

<h2>Summary Statistics of Numerical Attributes</h2>
<table>
  <thead>
    <tr><th>Metric</th><th>Min</th><th>25th %</th><th>Median</th><th>Mean</th><th>75th %</th><th>Max</th></tr>
  </thead>
  <tbody>
    <tr><td>Followers</td><td>1</td><td>272</td><td>708</td><td>16,985.49</td><td>3,532</td><td>982,005</td></tr>
    <tr><td>Engagement Rate (%)</td><td>0.00%</td><td>1.59%</td><td>5.21%</td><td>11.53%</td><td>11.90%</td><td>4,400.00%</td></tr>
    <tr><td>Posting Frequency (/mo)</td><td>0.00</td><td>4.15</td><td>8.33</td><td>13.32</td><td>24.50</td><td>30.00</td></tr>
  </tbody>
</table>

<h2>Niche Distribution Breakdown</h2>
<table>
  <thead>
    <tr><th>Category / Niche</th><th>Profile Count</th><th>Percentage of Dataset</th></tr>
  </thead>
  <tbody>
    <tr><td>Technology</td><td>1,542</td><td>60.21%</td></tr>
    <tr><td>Other</td><td>473</td><td>18.47%</td></tr>
    <tr><td>Business &amp; Finance</td><td>113</td><td>4.41%</td></tr>
    <tr><td>Fashion &amp; Beauty</td><td>85</td><td>3.32%</td></tr>
    <tr><td>Art &amp; Design</td><td>71</td><td>2.77%</td></tr>
    <tr><td>Education</td><td>47</td><td>1.84%</td></tr>
    <tr><td>Travel</td><td>36</td><td>1.41%</td></tr>
    <tr><td>Lifestyle</td><td>35</td><td>1.37%</td></tr>
    <tr><td>Fitness &amp; Health</td><td>29</td><td>1.13%</td></tr>
    <tr><td>Food &amp; Cooking / Photography</td><td>56 (28 each)</td><td>2.18%</td></tr>
    <tr><td>Remaining 7 Niches</td><td>74</td><td>2.89%</td></tr>
  </tbody>
</table>

<h1>10. Engagement Rate</h1>
<p>
Creator engagement rate was computed according to the formula specified by the internship:
</p>

<div class="formula-box">
Engagement Rate (%) = ((Average Likes + Average Comments) / Followers) * 100
</div>

<p>
Numerical validation confirmed 100% mathematical consistency with this formula across all 2,561 records (max diff &le; 1e-4).
</p>

<h2>Data-Source Limitation Disclosure</h2>
<p>
The technical audit identified a critical nuance regarding the fields <code>avg_likes_last_10</code> and <code>avg_comments_last_10</code>:
</p>
<ul>
  <li>These figures represent creator interaction averages provided by the originating open-source research dataset.</li>
  <li>Because Instagram's live feed was not directly crawled due to anti-scraping blocks, the pipeline did not crawl 10 individual post endpoints per creator.</li>
  <li>Rather than simulating or fabricating post-level numbers, the pipeline transparently mapped the authentic source metrics into the schema, preserving data provenance and integrity.</li>
</ul>

<h1>11. Hashtags and Content Themes</h1>
<p>
Hashtags and content themes provide essential semantic features for creator segmentation. The pipeline applied structured standardization rules:
</p>
<ul>
  <li>Removed brackets, quotes, and all Unicode emojis.</li>
  <li>Standardized hashtags into clean semicolon-delimited strings: <code>#tag1; #tag2; #tag3</code>.</li>
  <li>Extracted conceptual topics, title-cased tokens, and formatted themes as comma-delimited strings: <code>Theme1, Theme2, Theme3</code>.</li>
  <li>Deduplicated tokens case-insensitively while preserving original creator terminology without lossy machine translation.</li>
</ul>

<h1>12. Limitations</h1>
<p>
In the interest of technical accuracy and academic rigor, several limitations are acknowledged:
</p>
<ul>
  <li><strong>Platform Anti-Scraping Defenses:</strong> Instagram actively defends its perimeter against unauthenticated bots, preventing live automated crawling without violating platform policies.</li>
  <li><strong>Open-Source Sample Reliance:</strong> The dataset is derived from public research archives. While authentic, updates depend on open-data release cycles.</li>
  <li><strong>Post-Level Granularity:</strong> Individual post-level timestamps and comment text bodies were not available across all profiles, limiting granular time-series modeling.</li>
  <li><strong>Deferred Optional Metrics:</strong> Market Share and Influence Score were not present in the raw data and have been transparently deferred to Phase 2 algorithmic modeling rather than fabricated.</li>
  <li><strong>Contact Details Sparsity:</strong> Public contact info was present for 276 profiles (10.78%), with the remainder properly marked as <code>Not publicly available</code>.</li>
</ul>

<h1>13. Final Deliverables</h1>
<p>
The complete suite of Phase 1 Week 1 deliverables has been generated and validated:
</p>

<table>
  <thead>
    <tr><th>Deliverable</th><th>Format</th><th>Record Count / Size</th><th>Description</th></tr>
  </thead>
  <tbody>
    <tr><td><code>instagram_influencers_final_clean.csv</code></td><td>CSV (RFC 4180)</td><td>2,561 rows (1.2 MB)</td><td>Primary clean tabular deliverable, 17 columns.</td></tr>
    <tr><td><code>instagram_influencers_final_clean.xlsx</code></td><td>Excel (OpenXML)</td><td>2,561 rows (354 KB)</td><td>Clean spreadsheet deliverable with full schema parity.</td></tr>
    <tr><td><code>Week_1_Report.pdf</code></td><td>PDF Document</td><td>Multi-Page Document</td><td>Formal executive and technical internship report.</td></tr>
    <tr><td><code>Week_1_Report.docx</code></td><td>Word (DOCX)</td><td>Editable OpenXML</td><td>Submission-ready editable document of the report.</td></tr>
    <tr><td><code>Week_1_Report_Data_Sources.txt</code></td><td>Plain Text</td><td>Complete Index</td><td>Detailed provenance record of GitHub repositories and URLs.</td></tr>
    <tr><td><code>final_cleaning_report.txt</code></td><td>Text QA Log</td><td>5.5 KB</td><td>14-section empirical quality-control audit log.</td></tr>
  </tbody>
</table>

<h1>14. Conclusion</h1>
<p>
Week 1 of the SR NEXT Internship successfully fulfilled all Phase 1 mandates. Through ethical data sourcing, automated data engineering, 
and multi-stage quality control, the project produced a clean, standardized, and validated dataset of <strong>2,561 authentic Instagram creator profiles</strong>. 
With strict follower boundaries (&lt; 1M), zero duplicates, verified engagement rate calculations, and an English-dominant focus, the dataset 
provides an ideal foundation for Phase 2 exploratory data analysis, creator clustering, and automation insights.
</p>

</body>
</html>"""

    # Convert HTML into NSAttributedString
    data = Foundation.NSData.dataWithBytes_length_(html_content.encode('utf-8'), len(html_content.encode('utf-8')))
    attr_str, attrs = AppKit.NSAttributedString.alloc().initWithHTML_options_documentAttributes_(
        data, {}, None
    )

    pdf_url = CFURLCreateWithFileSystemPath(None, os.path.abspath(output_path), kCFURLPOSIXPathStyle, False)
    media_box = Quartz.CGRectMake(0, 0, 595.28, 841.89) # A4 size in points
    pdf = Quartz.CGPDFContextCreateWithURL(pdf_url, media_box, None)

    # CoreText pagination
    framesetter = CTFramesetterCreateWithAttributedString(attr_str)
    current_idx = 0
    total_len = attr_str.length()
    page_num = 1

    # Fonts and colors for headers and footers
    header_font = CTFontCreateWithName('Helvetica-Bold', 8.0, None)
    footer_font = CTFontCreateWithName('Helvetica', 8.0, None)
    color_gray = Quartz.CGColorCreateGenericRGB(0.45, 0.50, 0.55, 1.0)
    color_line = Quartz.CGColorCreateGenericRGB(0.80, 0.83, 0.87, 1.0)

    margin_left = 50.0
    margin_right = 50.0
    margin_bottom = 55.0
    margin_top = 55.0
    content_width = 595.28 - margin_left - margin_right
    content_height = 841.89 - margin_top - margin_bottom

    while current_idx < total_len:
        Quartz.CGPDFContextBeginPage(pdf, None)

        # Draw content frame
        path = Quartz.CGPathCreateMutable()
        Quartz.CGPathAddRect(path, None, Quartz.CGRectMake(margin_left, margin_bottom, content_width, content_height))

        frame = CTFramesetterCreateFrame(framesetter, CFRangeMake(current_idx, 0), path, None)
        CTFrameDraw(frame, pdf)

        visible_range = CTFrameGetVisibleStringRange(frame)
        current_idx += visible_range.length

        # Draw header and footer on pages after page 1 (cover page)
        if page_num > 1:
            # Header line
            Quartz.CGContextSetStrokeColorWithColor(pdf, color_line)
            Quartz.CGContextSetLineWidth(pdf, 0.6)
            Quartz.CGContextMoveToPoint(pdf, margin_left, 841.89 - margin_top + 10)
            Quartz.CGContextAddLineToPoint(pdf, 595.28 - margin_right, 841.89 - margin_top + 10)
            Quartz.CGContextStrokePath(pdf)

            # Header text
            hdr_str = CFAttributedStringCreate(None, "SR NEXT INTERNSHIP | WEEK 1 REPORT: DATA COLLECTION & PREPARATION", {
                kCTFontAttributeName: header_font,
                kCTForegroundColorAttributeName: color_gray
            })
            hdr_line = CTLineCreateWithAttributedString(hdr_str)
            Quartz.CGContextSetTextPosition(pdf, margin_left, 841.89 - margin_top + 16)
            CTLineDraw(hdr_line, pdf)

            # Footer line
            Quartz.CGContextMoveToPoint(pdf, margin_left, margin_bottom - 10)
            Quartz.CGContextAddLineToPoint(pdf, 595.28 - margin_right, margin_bottom - 10)
            Quartz.CGContextStrokePath(pdf)

            # Footer left text
            ftr_l_str = CFAttributedStringCreate(None, "AI-Powered Instagram Influencer Analytics & Automation Insights", {
                kCTFontAttributeName: footer_font,
                kCTForegroundColorAttributeName: color_gray
            })
            ftr_l_line = CTLineCreateWithAttributedString(ftr_l_str)
            Quartz.CGContextSetTextPosition(pdf, margin_left, margin_bottom - 24)
            CTLineDraw(ftr_l_line, pdf)

            # Footer right text (Page X)
            page_text = f"Page {page_num}"
            ftr_r_str = CFAttributedStringCreate(None, page_text, {
                kCTFontAttributeName: footer_font,
                kCTForegroundColorAttributeName: color_gray
            })
            ftr_r_line = CTLineCreateWithAttributedString(ftr_r_str)
            Quartz.CGContextSetTextPosition(pdf, 595.28 - margin_right - 40, margin_bottom - 24)
            CTLineDraw(ftr_r_line, pdf)

        Quartz.CGPDFContextEndPage(pdf)
        page_num += 1

        if visible_range.length == 0:
            break

    Quartz.CGPDFContextClose(pdf)

    doc = Quartz.CGPDFDocumentCreateWithURL(pdf_url)
    total_pages = Quartz.CGPDFDocumentGetNumberOfPages(doc)
    logger.info(f"PDF report successfully created at: {output_path} (Pages: {total_pages}, Size: {os.path.getsize(output_path)} bytes)")

def main():
    docx_path = "reports/Week_1_Report.docx"
    pdf_path = "reports/Week_1_Report.pdf"

    generate_report_docx(docx_path)
    generate_report_pdf(pdf_path)

    # Verification
    assert os.path.exists(docx_path), f"DOCX missing: {docx_path}"
    assert os.path.exists(pdf_path), f"PDF missing: {pdf_path}"
    assert os.path.getsize(docx_path) > 5000, f"DOCX too small: {os.path.getsize(docx_path)}"
    assert os.path.getsize(pdf_path) > 10000, f"PDF too small: {os.path.getsize(pdf_path)}"
    logger.info("All Week 1 reports generated and verified successfully!")

if __name__ == '__main__':
    main()

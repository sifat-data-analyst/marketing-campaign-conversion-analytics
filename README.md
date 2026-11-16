# Marketing Campaign & Conversion Analytics

**End-to-End Marketing Analytics | Python | Statistics | SQL Server | Power BI**

A business-focused marketing analytics project that evaluates campaign performance, channel efficiency, lead quality, and conversion outcomes using Python, statistical analysis, SQL Server, and Power BI.

> **Dataset Notice:** This project uses synthetic educational data representing a fictional business. Results are not real-company performance or industry benchmarks.

---

## 1. Project Overview

Marketing teams need to understand which campaigns and channels generate stronger results, how efficiently advertising budgets are used, and which leads show higher conversion potential.

This project analyzes 120 marketing campaigns across five channels over the period January 2023 to December 2025.

The workflow combines data validation, KPI analysis, statistical testing, SQL-based business analysis, and interactive Power BI dashboards to turn raw marketing data into actionable business insights.

## 2. Business Objectives

- Evaluate marketing spend and attributed revenue.
- Compare channel-level ROAS, CTR, CPC, and conversion performance.
- Identify high-performing campaigns.
- Analyze monthly marketing performance.
- Understand lead-score patterns and conversion behavior.
- Validate KPI calculations and financial reconciliation.
- Present findings through interactive dashboards and business recommendations.

## 3. Tools & Technologies

| Tool | Purpose |
|---|---|
| Python | Data auditing, cleaning checks, KPI analysis |
| Pandas & NumPy | Data processing and calculations |
| SciPy / Statistics | Statistical hypothesis testing |
| SQL Server | Data validation, joins, aggregations, business queries |
| Power BI | Interactive dashboards and DAX measures |
| Power Query | Data preparation |
| DAX | Business metrics and analytical calculations |
| PowerShell | Project workflow and file management |

## 4. Dataset Overview

The project uses four synthetic source datasets.

| Dataset | Records |
|---|---:|
| Campaigns | 120 |
| Daily Spend | 11,240 |
| Leads | 261,684 |
| Conversions | 39,696 |
| **Total** | **312,740** |

Dataset characteristics:
- Version: 1.0.0
- Date range: January 2023 – December 2025
- Generation seed: 2025090503
- Attribution: Last-touch
- Personally identifiable information: None

## 5. Key Performance Indicators

| KPI | Result |
|---|---:|
| Total Campaigns | 120 |
| Impressions | 436.84M |
| Clicks | 7.10M |
| Marketing Spend | $4.52M |
| Attributed Revenue | $21.56M |
| Leads | 261.68K |
| Conversions | 39.70K |
| CTR | 1.63% |
| CPC | $0.64 |
| Lead-to-Conversion Rate | 15.17% |
| Cost per Conversion | $113.94 |
| ROAS | 4.77x |

**Important:** ROAS represents attributed revenue divided by recorded media spend. It is not profit or ROI.

## 6. Power BI Dashboard

The Power BI report contains three analytical pages.

### Page 1 — Executive Overview
- Marketing performance KPI cards
- Monthly Spend vs Revenue
- Channel-wise ROAS
- Top 5 Campaigns by Revenue
- Conversion Type Distribution

### Page 2 — Campaign & Channel Analysis
- Campaign Spend vs Revenue
- Revenue Contribution by Channel
- Top 10 Campaigns by ROAS
- Monthly Revenue Trend by Channel

### Page 3 — Lead & Conversion Performance
- Lead and conversion performance KPIs
- Lead Conversion Rate by Score Band
- Leads vs Conversions by Lead Source
- Channel and Lead Source slicers

**Power BI File:**  
`02_Power_BI/Project_5_Marketing_Campaign_Conversion_Analytics.pbix`

## 7. Key Business Insights

### Channel Performance

| Channel | Attributed Revenue | ROAS |
|---|---:|---:|
| Affiliate | $5.61M | 6.54x |
| Paid Search | $5.44M | 6.06x |
| Paid Social | $4.69M | 4.76x |
| Display | $3.73M | 3.91x |
| Video | $2.09M | 2.52x |

Key findings:

- Affiliate generated the highest attributed revenue and channel-level ROAS.
- Paid Search achieved the highest CTR at 3.49%.
- Video recorded the lowest channel-level ROAS.
- Paid Social had the highest recorded spend.

### Lead Quality

Observed conversion rates by lead-score band:

| Lead Score | Conversion Rate |
|---|---:|
| 01–20 | 7.11% |
| 21–40 | 11.14% |
| 41–60 | 15.09% |
| 61–80 | 19.31% |
| 81–100 | 23.13% |

Higher lead-score bands showed higher observed conversion rates. This is an association, not proof of causation.

### Business Recommendations

1. Evaluate affiliate and paid search campaigns for carefully controlled scaling opportunities.
2. Investigate video campaign targeting, creative performance, and conversion funnels.
3. Review paid social campaigns to identify opportunities for improved spending efficiency.
4. Consider lead scores when prioritizing follow-up, subject to further validation.
5. Evaluate revenue, ROAS, conversion volume, and acquisition cost together before making budget decisions.

More details: [Business Insights & Recommendations](BUSINESS_INSIGHTS.md)

## 8. Statistical Analysis

Campaign-level channel comparisons use:

- Kruskal-Wallis tests
- Pairwise Mann-Whitney tests
- Holm adjustment for multiple comparisons

| Metric | Kruskal-Wallis p-value |
|---|---:|
| ROAS | 7.4844e-15 |
| CTR | 9.03091e-24 |
| CPC | 9.03091e-24 |

The results indicate differences in campaign-level metric distributions across channels. Statistical significance does not establish causation.

## 9. SQL Analysis

Nine SQL scripts cover:

1. Domain Validation
2. Date Consistency
3. Financial Reconciliation
4. KPI Analysis
5. Campaign Performance
6. Channel Performance
7. Monthly Performance
8. Conversion Analysis
9. Final Quality Audit

SQL reports are stored in:

`08_SQL_Analysis/Reports/`

## 10. Data Quality & Validation

The KPI and calculation quality audit produced:

| Validation | Result |
|---|---:|
| Checks Passed | 74 |
| Checks Failed | 0 |
| KPI Formula Mismatches | 0 |
| Financial Reconciliation | PASS |

Campaign, channel, and monthly spend and revenue totals reconciled with their source data.

## 11. Project Documentation

| File | Description |
|---|---|
| `BUSINESS_INSIGHTS.md` | Business findings and recommendations |
| `DATA_DICTIONARY.md` | Dataset and field reference |
| `METHODOLOGY.md` | Analysis workflow and technical methodology |
| `LIMITATIONS.md` | Dataset limitations and analytical considerations |
| `LICENSE.txt` | Dataset license information |
| `project5_audit_report.txt` | Data audit results |
| `project5_kpi_quality_check_report.txt` | KPI validation results |
| `project5_marketing_analysis_report.txt` | Marketing performance summary |
| `project5_statistics_analysis_report.txt` | Statistical analysis results |

## 12. Limitations & Analytical Considerations

- The dataset is synthetic and represents a fictional business.
- Last-touch attribution is used; channel performance does not establish incremental impact.
- ROAS is not profit or ROI.
- Offline and view-through conversions are excluded.
- December 2025 is partial and should not be treated as a complete month.
- Monthly leads use lead creation month, while conversions and revenue use conversion month.
- Lead source and campaign channel are separate fields.
- Statistical differences do not prove causation.
- Campaigns may differ in objectives, budgets, and dates.

## 13. Dataset License & Reproducibility

Dataset version: 1.0.0  
Generation seed: 2025090503

See `LICENSE.txt` for license terms. The dataset is synthetic educational data and does not represent real business outcomes.

---

## Project Summary

**Domain:** Marketing Analytics  
**Analysis Type:** Descriptive, Diagnostic, Statistical  
**Tools:** Python, Statistics, SQL Server, Power BI  
**Dataset:** Synthetic Marketing Campaign Data  
**Reporting Period:** 2023–2025

This project demonstrates an end-to-end analytical workflow, from data validation and KPI reconciliation to statistical investigation, SQL analysis, interactive reporting, and evidence-based business recommendations.


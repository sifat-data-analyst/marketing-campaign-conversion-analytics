# Business Insights & Recommendations
## Marketing Campaign & Conversion Analytics

## 1. Executive Summary

This project analyzes 120 marketing campaigns across five channels using a synthetic dataset covering January 2023 to December 2025.

Key results:
- Total Marketing Spend: $4,523,050.02
- Attributed Revenue: $21,561,839.01
- Total Leads: 261,684
- Total Conversions: 39,696
- Overall ROAS: 4.77x
- Lead-to-Conversion Rate: 15.17%
- Cost per Conversion: $113.94

## 2. Channel Performance Insights

| Channel | Spend | Revenue | ROAS | CTR |
|---|---:|---:|---:|---:|
| Affiliate | $857,835.07 | $5,610,700.73 | 6.54x | 2.50% |
| Paid Search | $897,091.53 | $5,439,329.35 | 6.06x | 3.49% |
| Paid Social | $984,731.88 | $4,690,137.28 | 4.76x | 1.79% |
| Display | $955,297.00 | $3,734,117.43 | 3.91x | 0.60% |
| Video | $828,094.54 | $2,087,554.22 | 2.52x | 0.89% |

### Insight 1: Affiliate Leads Revenue and ROAS

Affiliate generated the highest attributed revenue ($5.61M) and the highest overall channel ROAS (6.54x).

Recommendation:
Evaluate opportunities to scale affiliate campaigns while monitoring incremental performance, conversion quality, and actual profitability.

### Insight 2: Paid Search Leads Click Engagement

Paid Search achieved the highest channel CTR (3.49%) and a ROAS of 6.06x.

Recommendation:
Review successful search campaigns, keyword performance, and landing-page effectiveness to identify further optimization opportunities.

### Insight 3: Video Has the Lowest ROAS

Video recorded the lowest channel ROAS (2.52x) and attributed revenue ($2.09M).

Recommendation:
Review audience targeting, creative performance, and conversion funnel quality before making budget decisions.

### Insight 4: Paid Social Has the Highest Spend

Paid Social recorded the highest channel spend ($984,731.88), but did not generate the highest attributed revenue.

Recommendation:
Evaluate campaign-level efficiency and identify opportunities to improve spending effectiveness.

## 3. Campaign-Level Insights

Top five campaigns by attributed revenue:

| Campaign ID | Channel | Revenue | ROAS |
|---|---|---:|---:|
| CMP0060 | Affiliate | $417,738.92 | 6.70x |
| CMP0050 | Affiliate | $388,919.88 | 11.04x |
| CMP0021 | Paid Search | $380,892.89 | 5.34x |
| CMP0061 | Paid Search | $369,829.93 | 7.56x |
| CMP0081 | Paid Search | $361,820.39 | 8.41x |

Recommendation:
Investigate high-performing campaigns to identify potentially reusable strategies. Revenue and ROAS should be evaluated together because the highest-revenue campaign is not necessarily the most efficient.

## 4. Lead Quality Insights

Lead conversion rates by lead score band:

| Lead Score | Conversion Rate |
|---|---:|
| 01–20 | 7.11% |
| 21–40 | 11.14% |
| 41–60 | 15.09% |
| 61–80 | 19.31% |
| 81–100 | 23.13% |

Insight:
Higher lead-score bands show progressively higher observed conversion rates.

Recommendation:
Consider prioritizing follow-up for higher-scoring leads. Validate scoring thresholds using new or out-of-sample data before operational adoption.

This relationship is observational and does not establish causation.

## 5. Statistical Evidence

Campaign-level channel comparisons:

| Metric | Kruskal-Wallis H | p-value | Effect Size |
|---|---:|---:|---:|
| ROAS | 72.2813 | 7.4844e-15 | 0.5938 |
| CTR | 114.2479 | 9.03091e-24 | 0.9587 |
| CPC | 114.2479 | 9.03091e-24 | 0.9587 |

Statistical methods:
- Kruskal-Wallis tests for campaign-level differences across channels.
- Pairwise Mann-Whitney tests with Holm adjustment for multiple comparisons.

Interpretation:
The results provide evidence of differences in campaign-level metric distributions across channels. Statistical significance does not establish that channel selection caused the observed outcomes.

## 6. Business Recommendations

1. Evaluate affiliate and paid search campaigns for carefully controlled scaling opportunities.
2. Investigate video campaigns for targeting, creative, and funnel improvements.
3. Review paid social spending at campaign level to identify efficiency opportunities.
4. Use lead scores as a prioritization signal, subject to further validation.
5. Monitor revenue, ROAS, conversion volume, and cost efficiency together rather than relying on a single KPI.
6. Evaluate actual profit using additional business costs before making profitability claims.

## 7. Important Limitations

- Dataset is synthetic and does not represent real-company performance.
- Attribution follows a last-touch model.
- ROAS is attributed revenue divided by recorded media spend; it is not profit or ROI.
- December 2025 is partial and should not be compared with complete months without adjustment.
- Monthly leads use lead creation month, while conversions and revenue use conversion month.
- Lead source and campaign channel are separate fields.
- Statistical differences do not prove causation.
- Campaigns may differ in budget, objectives, dates, and other factors.

## 8. Data Quality Evidence

KPI and calculation quality audit:
- Checks passed: 74
- Checks failed: 0
- Campaign, channel, and monthly spend reconciliation: PASS
- Campaign, channel, and monthly revenue reconciliation: PASS
- KPI formula mismatches: 0

All reported findings are based on the existing project analysis outputs.

---
Project: Marketing Campaign & Conversion Analytics
Tools: Python, Statistics, SQL Server, Power BI
Dataset: Synthetic

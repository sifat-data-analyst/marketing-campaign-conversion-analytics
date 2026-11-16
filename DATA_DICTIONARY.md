# Data Dictionary
## Marketing Campaign & Conversion Analytics

### Dataset Information

| Property | Value |
|---|---|
| Dataset Version | 1.0.0 |
| Source Type | Synthetic |
| Coverage | 2023-01-01 to 2025-12-31 |
| Attribution Model | Last-touch |
| Total Records | 312,740 |
| PII | None |

## 1. Dataset Overview

| Dataset | Records | Grain |
|---|---:|---|
| Campaigns | 120 | One row per campaign |
| Daily Spend | 11,240 | One row per campaign active date |
| Leads | 261,684 | One row per lead |
| Conversions | 39,696 | One row per converted lead |

## 2. Campaigns

Grain: One row per campaign.

| Column | Type | Nullable | Description |
|---|---|---|---|
| campaign_id | Text | No | Unique campaign identifier |
| campaign_name | Text | No | Campaign display name |
| channel | Text | No | Marketing channel associated with the campaign |
| objective | Text | No | Campaign objective: awareness, lead generation, or acquisition |
| start_date | Date | No | Campaign start date |
| end_date | Date | No | Campaign end date |
| budget | Decimal | No | Planned campaign budget |

## 3. Daily Spend

Grain: One row per campaign active date.

| Column | Type | Nullable | Description |
|---|---|---|---|
| spend_id | Text | No | Unique spend record identifier |
| campaign_id | Text | No | Associated campaign identifier |
| spend_date | Date | No | Date of advertising delivery |
| impressions | Integer | No | Number of recorded ad impressions |
| clicks | Integer | No | Number of recorded ad clicks |
| spend | Decimal | No | Recorded media advertising cost |

## 4. Leads

Grain: One row per lead.

| Column | Type | Nullable | Description |
|---|---|---|---|
| lead_id | Text | No | Unique lead identifier |
| campaign_id | Text | No | Associated campaign identifier |
| created_at | Date | No | Lead creation date |
| lead_source | Text | No | Lead source classification |
| lead_score | Integer | No | Lead qualification score from 1 to 100 |

**Important:** `lead_source` and `campaigns.channel` are separate fields and should not automatically be treated as interchangeable.

## 5. Conversions

Grain: One row per converted lead.

| Column | Type | Nullable | Description |
|---|---|---|---|
| conversion_id | Text | No | Unique conversion identifier |
| lead_id | Text | No | Associated lead identifier |
| converted_at | Date | No | Conversion date |
| conversion_type | Text | No | Conversion category: trial or purchase |
| revenue | Decimal | No | Revenue attributed to the conversion |

A trial conversion has zero recorded revenue in this dataset.

## 6. Data Relationships

| Parent Dataset | Child Dataset | Key | Relationship |
|---|---|---|---|
| Campaigns | Daily Spend | campaign_id | One-to-Many |
| Campaigns | Leads | campaign_id | One-to-Many |
| Leads | Conversions | lead_id | One-to-One |

All conversions map to valid leads in the validated dataset.

## 7. Important KPI Definitions

| KPI | Definition |
|---|---|
| CTR | Total Clicks / Total Impressions |
| CPC | Total Spend / Total Clicks |
| Lead-to-Conversion Rate | Total Conversions / Unique Leads |
| Cost per Conversion | Total Spend / Total Conversions |
| ROAS | Attributed Revenue / Total Spend |
| Budget Utilization | Total Spend / Campaign Budget |

These definitions describe the calculations used in the project.

## 8. Analytical Considerations

- The dataset is synthetic educational data.
- Attribution follows a last-touch model.
- ROAS is not profit or ROI.
- Offline and view-through conversions are excluded.
- December 2025 is partial.
- Monthly leads use lead creation date.
- Monthly conversions and revenue use conversion date.
- Monthly ratios are not cohort-based.
- Lead source and campaign channel are separate fields.
- Statistical differences do not establish causation.
- No personally identifiable information is included.

## 9. Data Quality

The project KPI quality audit reported:

- 74 checks passed.
- 0 checks failed.
- No KPI formula mismatches.
- Campaign, channel, and monthly financial totals reconciled with source data.

---

Project: Marketing Campaign & Conversion Analytics  
Documentation: Data Dictionary  
Dataset Version: 1.0.0

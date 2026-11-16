# Project Methodology
## Marketing Campaign & Conversion Analytics

## 1. Project Approach

This project follows a structured analytics workflow to evaluate marketing campaign performance, advertising efficiency, lead quality, and conversion outcomes.

The workflow combines Python-based validation and analysis, statistical testing, SQL-based business analysis, and interactive Power BI reporting.

## 2. Data Preparation and Validation

Four synthetic datasets were used:

- Campaigns: 120 records
- Daily Spend: 11,240 records
- Leads: 261,684 records
- Conversions: 39,696 records

Validation included:

- Record counts and dataset structure.
- Unique identifier checks.
- Primary and foreign key relationships.
- Missing and invalid values.
- Date consistency.
- Financial reconciliation.
- KPI calculation consistency.

The Python audit and KPI quality checks reported 51 audit checks and 74 KPI checks passed, with no warnings, failures, or KPI formula mismatches in their respective reports.

## 3. Python Analysis

Python was used for:

- Dataset auditing and validation.
- Campaign-level performance analysis.
- Channel-level performance analysis.
- Monthly performance analysis.
- KPI calculations.
- Statistical analysis.
- Exporting analytical reports and CSV outputs.

Libraries included pandas, NumPy, SciPy, and related Python analytical tools.

## 4. KPI Calculations

| KPI | Calculation |
|---|---|
| CTR | Clicks / Impressions |
| CPC | Advertising Spend / Clicks |
| Lead-to-Conversion Rate | Conversions / Unique Leads |
| Cost per Conversion | Advertising Spend / Conversions |
| ROAS | Attributed Revenue / Advertising Spend |
| Budget Utilization | Advertising Spend / Campaign Budget |

Percentages are presented as ratios multiplied by 100.

ROAS measures attributed revenue relative to advertising spend. It does not represent profit or ROI.

## 5. Statistical Analysis

Campaign-level performance distributions were compared using the Kruskal-Wallis test.

Pairwise Mann-Whitney U tests with Holm adjustment were used for follow-up comparisons.

Effect size was also evaluated using epsilon-squared where applicable.

Lead score distributions across lead sources were examined using the Kruskal-Wallis test.

Statistical findings are interpreted as evidence of distribution differences, not proof of causality.

## 6. SQL Server Analysis

The datasets were imported into SQL Server.

The analysis included:

- Domain validation.
- Date consistency checks.
- Financial reconciliation.
- KPI analysis.
- Campaign performance.
- Channel performance.
- Monthly performance.
- Conversion analysis.
- Final quality audit.

Primary and foreign key relationships were established and validated.

## 7. Power BI Reporting

Power BI was used to build an interactive report with three pages:

### Page 1: Executive Overview
Provides an overall view of marketing performance through KPI cards and summary charts.

### Page 2: Campaign & Channel Analysis
Compares campaign and channel performance, advertising efficiency, and attributed revenue.

### Page 3: Lead & Conversion Performance
Examines lead quality, conversion behavior, and performance by lead source using interactive slicers.

DAX measures were used for KPI calculations, and a DateTable supported time-based analysis.

## 8. Quality Assurance

The project used independent validation across Python and SQL Server.

Key checks included:

- Record and relationship validation.
- Financial reconciliation.
- KPI consistency between source data and analytical outputs.
- Zero orphan conversion records.
- Power BI refresh verification.

The reported KPI quality audit passed all 74 checks.

## 9. Analytical Boundaries

- The data is synthetic and represents a fictional business.
- Attribution follows a last-touch model.
- Offline and view-through conversions are excluded.
- December 2025 is partial.
- Monthly leads and conversions use different date bases.
- Monthly conversion rates are not cohort-based.
- Statistical differences do not establish causality.

---

Project: Marketing Campaign & Conversion Analytics  
Documentation: Methodology

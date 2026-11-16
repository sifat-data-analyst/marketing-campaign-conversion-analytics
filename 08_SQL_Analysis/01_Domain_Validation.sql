-- ============================================================
-- PROJECT 5: MARKETING CAMPAIGN & CONVERSION ANALYTICS
-- Script: 01_Domain_Validation.sql
-- Purpose: Validate business rules across all source tables
-- Database: Project_5_Marketing_Analytics
-- ============================================================

USE Project_5_Marketing_Analytics;
GO

-- 1. Negative Impressions
SELECT 'Negative Impressions' AS CheckName,
COUNT_BIG(*) AS ErrorRows
FROM dbo.Daily_Spend
WHERE impressions < 0

UNION ALL

-- 2. Negative Clicks
SELECT 'Negative Clicks', COUNT_BIG(*)
FROM dbo.Daily_Spend
WHERE clicks < 0

UNION ALL

-- 3. Clicks Greater Than Impressions
SELECT 'Clicks Greater Than Impressions', COUNT_BIG(*)
FROM dbo.Daily_Spend
WHERE clicks > impressions

UNION ALL

-- 4. Negative Spend
SELECT 'Negative Spend', COUNT_BIG(*)
FROM dbo.Daily_Spend
WHERE spend < 0

UNION ALL

-- 5. Negative Campaign Budget
SELECT 'Negative Budget', COUNT_BIG(*)
FROM dbo.Campaigns
WHERE budget < 0

UNION ALL

-- 6. Negative Revenue
SELECT 'Negative Revenue', COUNT_BIG(*)
FROM dbo.Conversions
WHERE revenue < 0

UNION ALL

-- 7. Invalid Lead Score
SELECT 'Invalid Lead Score', COUNT_BIG(*)
FROM dbo.Leads
WHERE lead_score < 1 OR lead_score > 100

UNION ALL

-- 8. Invalid Campaign Dates
SELECT 'Invalid Campaign Dates', COUNT_BIG(*)
FROM dbo.Campaigns
WHERE end_date < start_date;
GO

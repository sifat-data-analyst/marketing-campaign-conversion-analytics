-- ============================================================
-- PROJECT 5: MARKETING CAMPAIGN & CONVERSION ANALYTICS
-- Script: 02_Date_Consistency.sql
-- Purpose: Validate date relationships across source tables
-- Database: Project_5_Marketing_Analytics
-- ============================================================

USE Project_5_Marketing_Analytics;
GO

-- 1. Spend Outside Campaign Dates
SELECT
'Spend Outside Campaign Dates' AS CheckName,
COUNT_BIG(*) AS ErrorRows
FROM dbo.Daily_Spend d
INNER JOIN dbo.Campaigns c
ON d.campaign_id = c.campaign_id
WHERE d.spend_date < c.start_date
OR d.spend_date > c.end_date

UNION ALL

-- 2. Leads Outside Campaign Dates
SELECT
'Leads Outside Campaign Dates',
COUNT_BIG(*)
FROM dbo.Leads l
INNER JOIN dbo.Campaigns c
ON l.campaign_id = c.campaign_id
WHERE l.created_at < c.start_date
OR l.created_at > c.end_date

UNION ALL

-- 3. Conversion Before Lead Creation
SELECT
'Conversion Before Lead Creation',
COUNT_BIG(*)
FROM dbo.Conversions v
INNER JOIN dbo.Leads l
ON v.lead_id = l.lead_id
WHERE v.converted_at < l.created_at;
GO

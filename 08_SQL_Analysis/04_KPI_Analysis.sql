-- ============================================================
-- PROJECT 5: MARKETING CAMPAIGN & CONVERSION ANALYTICS
-- Script: 04_KPI_Analysis.sql
-- Purpose: Calculate and validate core marketing KPIs
-- Database: Project_5_Marketing_Analytics
-- ============================================================

USE Project_5_Marketing_Analytics;
GO

-- 1. Overall Marketing KPI Summary

WITH MarketingTotals AS
(
    SELECT
        SUM(impressions) AS TotalImpressions,
        SUM(clicks) AS TotalClicks,
        SUM(spend) AS TotalSpend
    FROM dbo.Daily_Spend
),
LeadTotals AS
(
    SELECT COUNT_BIG(*) AS TotalLeads
    FROM dbo.Leads
),
ConversionTotals AS
(
    SELECT
        COUNT_BIG(*) AS TotalConversions,
        SUM(revenue) AS TotalRevenue
    FROM dbo.Conversions
)
SELECT
    m.TotalImpressions,
    m.TotalClicks,
    m.TotalSpend,
    l.TotalLeads,
    c.TotalConversions,
    c.TotalRevenue,

    CAST(
        m.TotalClicks * 100.0 /
        NULLIF(m.TotalImpressions, 0)
        AS DECIMAL(10,4)
    ) AS CTR_Percent,

    CAST(
        m.TotalSpend /
        NULLIF(m.TotalClicks, 0)
        AS DECIMAL(18,4)
    ) AS CPC,

    CAST(
        c.TotalConversions * 100.0 /
        NULLIF(l.TotalLeads, 0)
        AS DECIMAL(10,4)
    ) AS Lead_Conversion_Rate_Percent,

    CAST(
        m.TotalSpend /
        NULLIF(c.TotalConversions, 0)
        AS DECIMAL(18,4)
    ) AS Cost_Per_Conversion,

    CAST(
        c.TotalRevenue /
        NULLIF(m.TotalSpend, 0)
        AS DECIMAL(18,4)
    ) AS ROAS

FROM MarketingTotals m
CROSS JOIN LeadTotals l
CROSS JOIN ConversionTotals c;
GO

-- 2. KPI Validation Against Python Results

WITH KPI AS
(
    SELECT
        SUM(impressions) AS TotalImpressions,
        SUM(clicks) AS TotalClicks,
        SUM(spend) AS TotalSpend
    FROM dbo.Daily_Spend
),
Leads AS
(
    SELECT COUNT_BIG(*) AS TotalLeads
    FROM dbo.Leads
),
Conversions AS
(
    SELECT
        COUNT_BIG(*) AS TotalConversions,
        SUM(revenue) AS TotalRevenue
    FROM dbo.Conversions
),
Calculated AS
(
    SELECT
        CAST(k.TotalClicks * 100.0 /
            NULLIF(k.TotalImpressions, 0)
            AS DECIMAL(10,4)) AS CTR,

        CAST(k.TotalSpend /
            NULLIF(k.TotalClicks, 0)
            AS DECIMAL(18,4)) AS CPC,

        CAST(c.TotalConversions * 100.0 /
            NULLIF(l.TotalLeads, 0)
            AS DECIMAL(10,4)) AS ConversionRate,

        CAST(k.TotalSpend /
            NULLIF(c.TotalConversions, 0)
            AS DECIMAL(18,4)) AS CostPerConversion,

        CAST(c.TotalRevenue /
            NULLIF(k.TotalSpend, 0)
            AS DECIMAL(18,4)) AS ROAS

    FROM KPI k
    CROSS JOIN Leads l
    CROSS JOIN Conversions c
)
SELECT
    MetricName,
    ExpectedValue,
    ActualValue,
    CAST(ActualValue - ExpectedValue AS DECIMAL(18,4))
        AS Difference,
    CASE
        WHEN ABS(ActualValue - ExpectedValue) < 0.01
        THEN 'PASS'
        ELSE 'CHECK'
    END AS ValidationStatus
FROM Calculated
CROSS APPLY
(
    VALUES
        ('CTR_Percent', 1.6258, CTR),
        ('CPC', 0.6368, CPC),
        ('Lead_Conversion_Rate_Percent', 15.1694, ConversionRate),
        ('Cost_Per_Conversion', 113.9422, CostPerConversion),
        ('ROAS', 4.7671, ROAS)
) V(MetricName, ExpectedValue, ActualValue);
GO
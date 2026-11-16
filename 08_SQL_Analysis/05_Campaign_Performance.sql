-- ============================================================
-- PROJECT 5: MARKETING CAMPAIGN & CONVERSION ANALYTICS
-- Script: 05_Campaign_Performance.sql
-- Purpose: Comprehensive campaign-level performance analysis
-- ============================================================

USE Project_5_Marketing_Analytics;
GO

-- 1. Campaign Performance Summary
-- Aggregate each fact table separately to avoid join fan-out.

WITH SpendSummary AS
(
    SELECT
        campaign_id,
        SUM(impressions) AS TotalImpressions,
        SUM(clicks) AS TotalClicks,
        SUM(spend) AS TotalSpend
    FROM dbo.Daily_Spend
    GROUP BY campaign_id
),
LeadSummary AS
(
    SELECT
        campaign_id,
        COUNT_BIG(*) AS TotalLeads
    FROM dbo.Leads
    GROUP BY campaign_id
),
ConversionSummary AS
(
    SELECT
        l.campaign_id,
        COUNT_BIG(*) AS TotalConversions,
        SUM(cv.revenue) AS TotalRevenue
    FROM dbo.Leads l
    INNER JOIN dbo.Conversions cv
        ON l.lead_id = cv.lead_id
    GROUP BY l.campaign_id
),
CampaignResults AS
(
    SELECT
        c.campaign_id,
        c.campaign_name,
        c.channel,
        c.objective,
        c.budget,

        COALESCE(s.TotalImpressions, 0) AS TotalImpressions,
        COALESCE(s.TotalClicks, 0) AS TotalClicks,
        COALESCE(s.TotalSpend, 0) AS TotalSpend,
        COALESCE(l.TotalLeads, 0) AS TotalLeads,
        COALESCE(v.TotalConversions, 0) AS TotalConversions,
        COALESCE(v.TotalRevenue, 0) AS TotalRevenue

    FROM dbo.Campaigns c
    LEFT JOIN SpendSummary s
        ON c.campaign_id = s.campaign_id
    LEFT JOIN LeadSummary l
        ON c.campaign_id = l.campaign_id
    LEFT JOIN ConversionSummary v
        ON c.campaign_id = v.campaign_id
)
SELECT
    campaign_id,
    campaign_name,
    channel,
    objective,
    budget,
    TotalSpend,
    CAST(budget - TotalSpend AS DECIMAL(18,2))
        AS BudgetRemaining,

    CAST(TotalSpend * 100.0 /
        NULLIF(budget, 0) AS DECIMAL(10,2))
        AS BudgetUtilizationPercent,

    TotalImpressions,
    TotalClicks,

    CAST(TotalClicks * 100.0 /
        NULLIF(TotalImpressions, 0)
        AS DECIMAL(10,4)) AS CTR_Percent,

    CAST(TotalSpend /
        NULLIF(TotalClicks, 0)
        AS DECIMAL(18,4)) AS CPC,

    TotalLeads,
    TotalConversions,

    CAST(TotalConversions * 100.0 /
        NULLIF(TotalLeads, 0)
        AS DECIMAL(10,4)) AS ConversionRatePercent,

    TotalRevenue,

    CAST(TotalSpend /
        NULLIF(TotalConversions, 0)
        AS DECIMAL(18,4)) AS CostPerConversion,

    CAST(TotalRevenue /
        NULLIF(TotalSpend, 0)
        AS DECIMAL(18,4)) AS ROAS

FROM CampaignResults
ORDER BY TotalRevenue DESC, campaign_id;
GO

-- 2. Top 10 Campaigns by ROAS
-- Exclude campaigns with zero spend.

WITH SpendSummary AS
(
    SELECT campaign_id, SUM(spend) AS TotalSpend
    FROM dbo.Daily_Spend
    GROUP BY campaign_id
),
RevenueSummary AS
(
    SELECT
        l.campaign_id,
        SUM(cv.revenue) AS TotalRevenue
    FROM dbo.Leads l
    INNER JOIN dbo.Conversions cv
        ON l.lead_id = cv.lead_id
    GROUP BY l.campaign_id
)
SELECT TOP 10
    c.campaign_id,
    c.campaign_name,
    c.channel,
    s.TotalSpend,
    COALESCE(r.TotalRevenue, 0) AS TotalRevenue,
    CAST(
        COALESCE(r.TotalRevenue, 0) /
        NULLIF(s.TotalSpend, 0)
        AS DECIMAL(18,4)
    ) AS ROAS
FROM dbo.Campaigns c
INNER JOIN SpendSummary s
    ON c.campaign_id = s.campaign_id
LEFT JOIN RevenueSummary r
    ON c.campaign_id = r.campaign_id
WHERE s.TotalSpend > 0
ORDER BY ROAS DESC, c.campaign_id;
GO

-- 3. Bottom 10 Campaigns by ROAS
-- Only campaigns with positive spend are included.

WITH SpendSummary AS
(
    SELECT campaign_id, SUM(spend) AS TotalSpend
    FROM dbo.Daily_Spend
    GROUP BY campaign_id
),
RevenueSummary AS
(
    SELECT
        l.campaign_id,
        SUM(cv.revenue) AS TotalRevenue
    FROM dbo.Leads l
    INNER JOIN dbo.Conversions cv
        ON l.lead_id = cv.lead_id
    GROUP BY l.campaign_id
)
SELECT TOP 10
    c.campaign_id,
    c.campaign_name,
    c.channel,
    s.TotalSpend,
    COALESCE(r.TotalRevenue, 0) AS TotalRevenue,
    CAST(
        COALESCE(r.TotalRevenue, 0) /
        NULLIF(s.TotalSpend, 0)
        AS DECIMAL(18,4)
    ) AS ROAS
FROM dbo.Campaigns c
INNER JOIN SpendSummary s
    ON c.campaign_id = s.campaign_id
LEFT JOIN RevenueSummary r
    ON c.campaign_id = r.campaign_id
WHERE s.TotalSpend > 0
ORDER BY ROAS ASC, c.campaign_id;
GO
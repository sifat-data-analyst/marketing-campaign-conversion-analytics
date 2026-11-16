USE Project_5_Marketing_Analytics;
GO

SET NOCOUNT ON;

-- PROJECT 5: CHANNEL PERFORMANCE ANALYSIS

-- 1. Aggregate spend separately
WITH SpendAgg AS
(
    SELECT
        c.channel,
        COUNT(DISTINCT s.campaign_id) AS ActiveCampaigns,
        SUM(s.impressions) AS TotalImpressions,
        SUM(s.clicks) AS TotalClicks,
        SUM(s.spend) AS TotalSpend
    FROM dbo.Daily_Spend s
    INNER JOIN dbo.Campaigns c
        ON s.campaign_id = c.campaign_id
    GROUP BY c.channel
),

-- 2. Aggregate leads separately
LeadAgg AS
(
    SELECT
        c.channel,
        COUNT(*) AS TotalLeads
    FROM dbo.Leads l
    INNER JOIN dbo.Campaigns c
        ON l.campaign_id = c.campaign_id
    GROUP BY c.channel
),

-- 3. Aggregate conversions and revenue separately
ConversionAgg AS
(
    SELECT
        c.channel,
        COUNT(*) AS TotalConversions,
        SUM(cv.revenue) AS TotalRevenue
    FROM dbo.Conversions cv
    INNER JOIN dbo.Leads l
        ON cv.lead_id = l.lead_id
    INNER JOIN dbo.Campaigns c
        ON l.campaign_id = c.campaign_id
    GROUP BY c.channel
)

-- 4. Final channel performance
SELECT
    s.channel,
    s.ActiveCampaigns,
    s.TotalImpressions,
    s.TotalClicks,

    CAST(
        100.0 * s.TotalClicks /
        NULLIF(s.TotalImpressions, 0)
        AS DECIMAL(10,4)
    ) AS CTR_Percent,

    CAST(
        s.TotalSpend /
        NULLIF(s.TotalClicks, 0)
        AS DECIMAL(18,4)
    ) AS CPC,

    CAST(s.TotalSpend AS DECIMAL(18,2)) AS TotalSpend,

    COALESCE(l.TotalLeads, 0) AS TotalLeads,

    COALESCE(cv.TotalConversions, 0) AS TotalConversions,

    CAST(
        100.0 * COALESCE(cv.TotalConversions, 0) /
        NULLIF(l.TotalLeads, 0)
        AS DECIMAL(10,4)
    ) AS LeadConversionRate_Percent,

    CAST(
        s.TotalSpend /
        NULLIF(cv.TotalConversions, 0)
        AS DECIMAL(18,4)
    ) AS CostPerConversion,

    CAST(
        COALESCE(cv.TotalRevenue, 0)
        AS DECIMAL(18,2)
    ) AS TotalAttributedRevenue,

    CAST(
        cv.TotalRevenue /
        NULLIF(s.TotalSpend, 0)
        AS DECIMAL(18,4)
    ) AS ROAS

FROM SpendAgg s

LEFT JOIN LeadAgg l
    ON s.channel = l.channel

LEFT JOIN ConversionAgg cv
    ON s.channel = cv.channel

ORDER BY TotalAttributedRevenue DESC;

GO

-- 5. Channel ranking by ROAS
WITH SpendAgg AS
(
    SELECT
        c.channel,
        SUM(s.spend) AS TotalSpend
    FROM dbo.Daily_Spend s
    INNER JOIN dbo.Campaigns c
        ON s.campaign_id = c.campaign_id
    GROUP BY c.channel
),

RevenueAgg AS
(
    SELECT
        c.channel,
        SUM(cv.revenue) AS TotalRevenue
    FROM dbo.Conversions cv
    INNER JOIN dbo.Leads l
        ON cv.lead_id = l.lead_id
    INNER JOIN dbo.Campaigns c
        ON l.campaign_id = c.campaign_id
    GROUP BY c.channel
)

SELECT
    s.channel,
    CAST(s.TotalSpend AS DECIMAL(18,2)) AS TotalSpend,
    CAST(COALESCE(r.TotalRevenue, 0) AS DECIMAL(18,2))
        AS TotalRevenue,

    CAST(
        r.TotalRevenue /
        NULLIF(s.TotalSpend, 0)
        AS DECIMAL(18,4)
    ) AS ROAS

FROM SpendAgg s
LEFT JOIN RevenueAgg r
    ON s.channel = r.channel

ORDER BY ROAS DESC;

GO
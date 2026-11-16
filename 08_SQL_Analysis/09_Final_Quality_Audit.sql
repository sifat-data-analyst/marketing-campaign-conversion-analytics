USE Project_5_Marketing_Analytics;
GO

SET NOCOUNT ON;

PRINT '======================================';
PRINT 'PROJECT 5 - FINAL SQL QUALITY AUDIT';
PRINT '======================================';

-- 1. TABLE ROW COUNT AND UNIQUE ID AUDIT

SELECT
    'Campaigns' AS TableName,
    COUNT(*) AS TotalRows,
    COUNT(DISTINCT campaign_id) AS UniqueIDs
FROM dbo.Campaigns

UNION ALL

SELECT
    'Daily_Spend',
    COUNT(*),
    COUNT(DISTINCT spend_id)
FROM dbo.Daily_Spend

UNION ALL

SELECT
    'Leads',
    COUNT(*),
    COUNT(DISTINCT lead_id)
FROM dbo.Leads

UNION ALL

SELECT
    'Conversions',
    COUNT(*),
    COUNT(DISTINCT conversion_id)
FROM dbo.Conversions;

-- 2. NULL VALUE AUDIT

SELECT
    'Campaigns' AS TableName,
    COUNT(*) AS RowsWithNulls
FROM dbo.Campaigns
WHERE campaign_id IS NULL
   OR campaign_name IS NULL
   OR channel IS NULL
   OR objective IS NULL
   OR start_date IS NULL
   OR end_date IS NULL
   OR budget IS NULL

UNION ALL

SELECT
    'Daily_Spend',
    COUNT(*)
FROM dbo.Daily_Spend
WHERE spend_id IS NULL
   OR campaign_id IS NULL
   OR spend_date IS NULL
   OR impressions IS NULL
   OR clicks IS NULL
   OR spend IS NULL

UNION ALL

SELECT
    'Leads',
    COUNT(*)
FROM dbo.Leads
WHERE lead_id IS NULL
   OR campaign_id IS NULL
   OR created_at IS NULL
   OR lead_source IS NULL
   OR lead_score IS NULL

UNION ALL

SELECT
    'Conversions',
    COUNT(*)
FROM dbo.Conversions
WHERE conversion_id IS NULL
   OR lead_id IS NULL
   OR converted_at IS NULL
   OR conversion_type IS NULL
   OR revenue IS NULL;

-- 3. DUPLICATE PRIMARY KEY AUDIT

SELECT
    'Campaigns' AS TableName,
    COUNT(*) AS DuplicateGroups
FROM
(
    SELECT campaign_id
    FROM dbo.Campaigns
    GROUP BY campaign_id
    HAVING COUNT(*) > 1
) AS D

UNION ALL

SELECT
    'Daily_Spend',
    COUNT(*)
FROM
(
    SELECT spend_id
    FROM dbo.Daily_Spend
    GROUP BY spend_id
    HAVING COUNT(*) > 1
) AS D

UNION ALL

SELECT
    'Leads',
    COUNT(*)
FROM
(
    SELECT lead_id
    FROM dbo.Leads
    GROUP BY lead_id
    HAVING COUNT(*) > 1
) AS D

UNION ALL

SELECT
    'Conversions',
    COUNT(*)
FROM
(
    SELECT conversion_id
    FROM dbo.Conversions
    GROUP BY conversion_id
    HAVING COUNT(*) > 1
) AS D;

-- 4. FOREIGN KEY RELATIONSHIP AUDIT

SELECT
    'Daily_Spend -> Campaigns' AS RelationshipName,
    COUNT(*) AS OrphanRows
FROM dbo.Daily_Spend s
LEFT JOIN dbo.Campaigns c
    ON s.campaign_id = c.campaign_id
WHERE c.campaign_id IS NULL

UNION ALL

SELECT
    'Leads -> Campaigns',
    COUNT(*)
FROM dbo.Leads l
LEFT JOIN dbo.Campaigns c
    ON l.campaign_id = c.campaign_id
WHERE c.campaign_id IS NULL

UNION ALL

SELECT
    'Conversions -> Leads',
    COUNT(*)
FROM dbo.Conversions cv
LEFT JOIN dbo.Leads l
    ON cv.lead_id = l.lead_id
WHERE l.lead_id IS NULL;

-- 5. FINANCIAL KPI RECONCILIATION

WITH SpendData AS
(
    SELECT
        SUM(impressions) AS TotalImpressions,
        SUM(clicks) AS TotalClicks,
        SUM(spend) AS TotalSpend
    FROM dbo.Daily_Spend
),

LeadData AS
(
    SELECT COUNT(*) AS TotalLeads
    FROM dbo.Leads
),

ConversionData AS
(
    SELECT
        COUNT(*) AS TotalConversions,
        SUM(revenue) AS TotalRevenue
    FROM dbo.Conversions
)

SELECT
    s.TotalImpressions,
    s.TotalClicks,
    s.TotalSpend,
    l.TotalLeads,
    c.TotalConversions,
    c.TotalRevenue,

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

    CAST(
        100.0 * c.TotalConversions /
        NULLIF(l.TotalLeads, 0)
        AS DECIMAL(10,4)
    ) AS ConversionRate_Percent,

    CAST(
        s.TotalSpend /
        NULLIF(c.TotalConversions, 0)
        AS DECIMAL(18,4)
    ) AS CostPerConversion,

    CAST(
        c.TotalRevenue /
        NULLIF(s.TotalSpend, 0)
        AS DECIMAL(18,4)
    ) AS ROAS

FROM SpendData s
CROSS JOIN LeadData l
CROSS JOIN ConversionData c;

GO

PRINT 'FINAL SQL QUALITY AUDIT COMPLETED';
GO
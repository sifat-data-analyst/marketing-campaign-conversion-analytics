USE Project_5_Marketing_Analytics;
GO

SET NOCOUNT ON;

-- PROJECT 5: CONVERSION ANALYSIS

-- 1. Overall Conversion Summary
SELECT
    COUNT(*) AS TotalConversions,
    COUNT(DISTINCT lead_id) AS UniqueConvertedLeads,
    SUM(revenue) AS TotalAttributedRevenue,
    AVG(revenue) AS AverageRevenuePerConversion,
    MIN(revenue) AS MinimumConversionRevenue,
    MAX(revenue) AS MaximumConversionRevenue
FROM dbo.Conversions;

GO

-- 2. Conversion Type Performance
SELECT
    conversion_type,
    COUNT(*) AS TotalConversions,
    SUM(revenue) AS TotalRevenue,
    AVG(revenue) AS AverageRevenue,
    CAST(
        100.0 * COUNT(*) /
        NULLIF((SELECT COUNT(*) FROM dbo.Conversions), 0)
        AS DECIMAL(10,4)
    ) AS ConversionShare_Percent
FROM dbo.Conversions
GROUP BY conversion_type
ORDER BY TotalRevenue DESC;

GO

-- 3. Lead Score and Conversion Analysis
SELECT
    CASE
        WHEN l.lead_score BETWEEN 1 AND 20 THEN '01-20'
        WHEN l.lead_score BETWEEN 21 AND 40 THEN '21-40'
        WHEN l.lead_score BETWEEN 41 AND 60 THEN '41-60'
        WHEN l.lead_score BETWEEN 61 AND 80 THEN '61-80'
        WHEN l.lead_score BETWEEN 81 AND 100 THEN '81-100'
    END AS LeadScoreRange,

    COUNT(*) AS ConvertedLeads,
    SUM(cv.revenue) AS TotalRevenue,
    AVG(cv.revenue) AS AverageRevenue

FROM dbo.Conversions cv
INNER JOIN dbo.Leads l
    ON cv.lead_id = l.lead_id

GROUP BY
    CASE
        WHEN l.lead_score BETWEEN 1 AND 20 THEN '01-20'
        WHEN l.lead_score BETWEEN 21 AND 40 THEN '21-40'
        WHEN l.lead_score BETWEEN 41 AND 60 THEN '41-60'
        WHEN l.lead_score BETWEEN 61 AND 80 THEN '61-80'
        WHEN l.lead_score BETWEEN 81 AND 100 THEN '81-100'
    END

ORDER BY LeadScoreRange;

GO

-- 4. Lead Score Conversion Rate
SELECT
    CASE
        WHEN l.lead_score BETWEEN 1 AND 20 THEN '01-20'
        WHEN l.lead_score BETWEEN 21 AND 40 THEN '21-40'
        WHEN l.lead_score BETWEEN 41 AND 60 THEN '41-60'
        WHEN l.lead_score BETWEEN 61 AND 80 THEN '61-80'
        WHEN l.lead_score BETWEEN 81 AND 100 THEN '81-100'
    END AS LeadScoreRange,

    COUNT(*) AS TotalLeads,
    COUNT(cv.conversion_id) AS ConvertedLeads,

    CAST(
        100.0 * COUNT(cv.conversion_id) /
        NULLIF(COUNT(*), 0)
        AS DECIMAL(10,4)
    ) AS ConversionRate_Percent

FROM dbo.Leads l
LEFT JOIN dbo.Conversions cv
    ON l.lead_id = cv.lead_id

GROUP BY
    CASE
        WHEN l.lead_score BETWEEN 1 AND 20 THEN '01-20'
        WHEN l.lead_score BETWEEN 21 AND 40 THEN '21-40'
        WHEN l.lead_score BETWEEN 41 AND 60 THEN '41-60'
        WHEN l.lead_score BETWEEN 61 AND 80 THEN '61-80'
        WHEN l.lead_score BETWEEN 81 AND 100 THEN '81-100'
    END

ORDER BY LeadScoreRange;

GO
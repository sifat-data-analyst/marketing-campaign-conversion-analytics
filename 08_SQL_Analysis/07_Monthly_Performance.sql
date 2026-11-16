USE Project_5_Marketing_Analytics;
GO

SET NOCOUNT ON;

-- PROJECT 5: MONTHLY PERFORMANCE ANALYSIS

-- 1. Monthly Spend and Traffic
WITH SpendMonthly AS
(
    SELECT
        YEAR(spend_date) AS [Year],
        MONTH(spend_date) AS [Month],
        SUM(impressions) AS TotalImpressions,
        SUM(clicks) AS TotalClicks,
        SUM(spend) AS TotalSpend
    FROM dbo.Daily_Spend
    GROUP BY
        YEAR(spend_date),
        MONTH(spend_date)
),

-- 2. Monthly Leads
LeadMonthly AS
(
    SELECT
        YEAR(created_at) AS [Year],
        MONTH(created_at) AS [Month],
        COUNT(*) AS TotalLeads
    FROM dbo.Leads
    GROUP BY
        YEAR(created_at),
        MONTH(created_at)
),

-- 3. Monthly Conversions and Revenue
ConversionMonthly AS
(
    SELECT
        YEAR(cv.converted_at) AS [Year],
        MONTH(cv.converted_at) AS [Month],
        COUNT(*) AS TotalConversions,
        SUM(cv.revenue) AS TotalRevenue
    FROM dbo.Conversions cv
    GROUP BY
        YEAR(cv.converted_at),
        MONTH(cv.converted_at)
),

-- 4. Combine monthly metrics
MonthlyPerformance AS
(
    SELECT
        s.[Year],
        s.[Month],
        s.TotalImpressions,
        s.TotalClicks,
        s.TotalSpend,
        COALESCE(l.TotalLeads, 0) AS TotalLeads,
        COALESCE(c.TotalConversions, 0) AS TotalConversions,
        COALESCE(c.TotalRevenue, 0) AS TotalRevenue
    FROM SpendMonthly s
    LEFT JOIN LeadMonthly l
        ON s.[Year] = l.[Year]
        AND s.[Month] = l.[Month]
    LEFT JOIN ConversionMonthly c
        ON s.[Year] = c.[Year]
        AND s.[Month] = c.[Month]
)

SELECT
    [Year],
    [Month],
    CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2))
        AS YearMonth,

    TotalImpressions,
    TotalClicks,

    CAST(
        100.0 * TotalClicks /
        NULLIF(TotalImpressions, 0)
        AS DECIMAL(10,4)
    ) AS CTR_Percent,

    CAST(TotalSpend AS DECIMAL(18,2)) AS TotalSpend,

    CAST(
        TotalSpend / NULLIF(TotalClicks, 0)
        AS DECIMAL(18,4)
    ) AS CPC,

    TotalLeads,
    TotalConversions,

    CAST(
        100.0 * TotalConversions /
        NULLIF(TotalLeads, 0)
        AS DECIMAL(10,4)
    ) AS LeadConversionRate_Percent,

    CAST(TotalRevenue AS DECIMAL(18,2)) AS TotalRevenue,

    CAST(
        TotalSpend / NULLIF(TotalConversions, 0)
        AS DECIMAL(18,4)
    ) AS CostPerConversion,

    CAST(
        TotalRevenue / NULLIF(TotalSpend, 0)
        AS DECIMAL(18,4)
    ) AS ROAS

FROM MonthlyPerformance
ORDER BY [Year], [Month];

GO
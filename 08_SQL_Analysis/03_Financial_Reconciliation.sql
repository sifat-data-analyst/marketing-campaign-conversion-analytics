-- ============================================================
-- PROJECT 5: MARKETING CAMPAIGN & CONVERSION ANALYTICS
-- Script: 03_Financial_Reconciliation.sql
-- Purpose: Reconcile campaign budget, actual spend and revenue
-- Database: Project_5_Marketing_Analytics
-- ============================================================

USE Project_5_Marketing_Analytics;
GO

-- 1. Overall Financial Summary
SELECT
CAST(SUM(c.budget) AS DECIMAL(18,2)) AS TotalCampaignBudget,
CAST((SELECT SUM(spend)
FROM dbo.Daily_Spend) AS DECIMAL(18,2)) AS TotalActualSpend,
CAST((SELECT SUM(revenue)
FROM dbo.Conversions) AS DECIMAL(18,2)) AS TotalAttributedRevenue,
(SELECT COUNT_BIG(*)
FROM dbo.Leads) AS TotalLeads,
(SELECT COUNT_BIG(*)
FROM dbo.Conversions) AS TotalConversions
FROM dbo.Campaigns c;
GO

-- 2. Campaign-Level Budget vs Actual Spend
SELECT
c.campaign_id,
c.campaign_name,
c.budget,
COALESCE(SUM(d.spend), 0) AS ActualSpend,
CAST(
c.budget - COALESCE(SUM(d.spend), 0)
AS DECIMAL(18,2)
) AS BudgetRemaining,
CAST(
COALESCE(SUM(d.spend), 0) * 100.0
/ NULLIF(c.budget, 0)
AS DECIMAL(18,2)
) AS BudgetUtilizationPercent
FROM dbo.Campaigns c
LEFT JOIN dbo.Daily_Spend d
ON c.campaign_id = d.campaign_id
GROUP BY
c.campaign_id,
c.campaign_name,
c.budget
ORDER BY ActualSpend DESC;
GO

-- 3. Financial Reconciliation Totals
SELECT
(SELECT SUM(spend)
FROM dbo.Daily_Spend) AS SpendTotal,
(SELECT SUM(spend)
FROM dbo.Daily_Spend) -
(SELECT SUM(actual_spend)
FROM (
SELECT campaign_id, SUM(spend) AS actual_spend
FROM dbo.Daily_Spend
GROUP BY campaign_id
) x) AS SpendReconciliationDifference,
(SELECT SUM(revenue)
FROM dbo.Conversions) AS RevenueTotal;
GO

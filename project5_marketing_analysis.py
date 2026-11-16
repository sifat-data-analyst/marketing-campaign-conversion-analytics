"""Project 5 marketing performance analysis. Reads raw CSVs only; does not modify them."""
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent
def load(name, **kwargs):
    p = BASE / name
    if not p.exists():
        raise FileNotFoundError(f"Missing {name}. Put this script beside the four source CSV files.")
    return pd.read_csv(p, **kwargs)

campaigns = load("campaigns.csv", parse_dates=["start_date", "end_date"])
spend = load("daily_spend.csv", parse_dates=["spend_date"])
leads = load("leads.csv", parse_dates=["created_at"])
conversions = load("conversions.csv", parse_dates=["converted_at"])

# Aggregate each source to campaign grain before joining, preventing row multiplication.
s = spend.groupby("campaign_id", as_index=False).agg(
    impressions=("impressions","sum"), clicks=("clicks","sum"),
    spend=("spend","sum"), spend_days=("spend_date","nunique"))
l = leads.groupby("campaign_id", as_index=False).agg(
    leads=("lead_id","nunique"), average_lead_score=("lead_score","mean"))
lead_keys = leads[["lead_id","campaign_id"]]
cv = conversions.merge(lead_keys, on="lead_id", how="left", validate="one_to_one")
v = cv.groupby("campaign_id", as_index=False).agg(
    conversions=("conversion_id","nunique"), attributed_revenue=("revenue","sum"),
    trial_conversions=("conversion_type",lambda x:(x=="trial").sum()),
    purchase_conversions=("conversion_type",lambda x:(x=="purchase").sum()))

cp = campaigns.merge(s,on="campaign_id",how="left",validate="one_to_one").merge(
    l,on="campaign_id",how="left",validate="one_to_one").merge(
    v,on="campaign_id",how="left",validate="one_to_one")
for c in ["impressions","clicks","spend","spend_days","leads","conversions",
          "attributed_revenue","trial_conversions","purchase_conversions"]:
    cp[c] = cp[c].fillna(0)
def div(a,b):
    return np.where(b > 0, a / b, np.nan)
cp["ctr_pct"] = div(cp.clicks,cp.impressions)*100
cp["cpc"] = div(cp.spend,cp.clicks)
cp["lead_to_conversion_pct"] = div(cp.conversions,cp.leads)*100
cp["cost_per_conversion"] = div(cp.spend,cp.conversions)
cp["roas"] = div(cp.attributed_revenue,cp.spend)
cp["budget_used_pct"] = div(cp.spend,cp.budget)*100
cp["revenue_minus_ad_spend"] = cp.attributed_revenue-cp.spend

ch = cp.groupby("channel",as_index=False).agg(
    campaigns=("campaign_id","nunique"), impressions=("impressions","sum"),
    clicks=("clicks","sum"), spend=("spend","sum"), leads=("leads","sum"),
    conversions=("conversions","sum"), attributed_revenue=("attributed_revenue","sum"),
    budget=("budget","sum"))
ch["ctr_pct"] = div(ch.clicks,ch.impressions)*100
ch["cpc"] = div(ch.spend,ch.clicks)
ch["lead_to_conversion_pct"] = div(ch.conversions,ch.leads)*100
ch["cost_per_conversion"] = div(ch.spend,ch.conversions)
ch["roas"] = div(ch.attributed_revenue,ch.spend)
ch["budget_used_pct"] = div(ch.spend,ch.budget)*100
ch["revenue_minus_ad_spend"] = ch.attributed_revenue-ch.spend

# Monthly tables use each event's own date; they are not lead-cohort conversion rates.
sm = spend.assign(month=spend.spend_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(
    impressions=("impressions","sum"),clicks=("clicks","sum"),spend=("spend","sum"))
lm = leads.assign(month=leads.created_at.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(
    leads=("lead_id","nunique"))
vm = conversions.assign(month=conversions.converted_at.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(
    conversions=("conversion_id","nunique"),attributed_revenue=("revenue","sum"))
mo = sm.merge(lm,on="month",how="outer").merge(vm,on="month",how="outer").sort_values("month")
for c in ["impressions","clicks","spend","leads","conversions","attributed_revenue"]:
    mo[c]=mo[c].fillna(0)
mo["ctr_pct"]=div(mo.clicks,mo.impressions)*100
mo["cpc"]=div(mo.spend,mo.clicks)
mo["lead_to_conversion_pct"]=div(mo.conversions,mo.leads)*100
mo["cost_per_conversion"]=div(mo.spend,mo.conversions)
mo["roas"]=div(mo.attributed_revenue,mo.spend)

for df in [cp,ch,mo]:
    for c in df.columns:
        if c in ["ctr_pct","lead_to_conversion_pct","budget_used_pct","average_lead_score","roas"]:
            df[c]=df[c].round(2)
        elif c in ["spend","budget","attributed_revenue","cpc","cost_per_conversion","revenue_minus_ad_spend"]:
            df[c]=df[c].round(2)

cp.to_csv(BASE/"campaign_performance.csv",index=False)
ch.to_csv(BASE/"channel_performance.csv",index=False)
mo.to_csv(BASE/"monthly_performance.csv",index=False)

spend_total=float(spend.spend.sum())
revenue_total=float(conversions.revenue.sum())
impressions_total=int(spend.impressions.sum())
clicks_total=int(spend.clicks.sum())
leads_total=int(leads.lead_id.nunique())
conversions_total=int(conversions.conversion_id.nunique())
report=[
"PROJECT 5 — MARKETING PERFORMANCE ANALYSIS",
"Dataset is SYNTHETIC. Do not present results as real-company outcomes.",
"Original source CSVs were read only and were not modified.","",
"OVERALL DESCRIPTIVE METRICS",
f"Campaigns: {campaigns.campaign_id.nunique():,}",
f"Impressions: {impressions_total:,}",f"Clicks: {clicks_total:,}",
f"Spend: {spend_total:,.2f}",f"Leads: {leads_total:,}",
f"Conversions: {conversions_total:,}",f"Attributed revenue: {revenue_total:,.2f}",
f"CTR: {clicks_total/impressions_total*100:.2f}%" if impressions_total else "CTR: N/A",
f"CPC: {spend_total/clicks_total:.2f}" if clicks_total else "CPC: N/A",
f"Overall lead-to-conversion rate: {conversions_total/leads_total*100:.2f}%" if leads_total else "Overall lead-to-conversion rate: N/A",
f"Cost per conversion: {spend_total/conversions_total:.2f}" if conversions_total else "Cost per conversion: N/A",
f"ROAS: {revenue_total/spend_total:.2f}x" if spend_total else "ROAS: N/A","",
"INTERPRETATION NOTES",
"- ROAS is attributed revenue divided by recorded media spend; it is not profit or ROI.",
"- Overall lead-to-conversion rate is total conversions divided by unique leads, not a cohort-based rate.",
"- Monthly leads use creation date; conversions/revenue use conversion date. Treat monthly rates cautiously.",
"- Channel is taken from campaigns.channel; leads.lead_source is a separate field.",
"- Rankings are descriptive and do not prove a channel caused an outcome.","",
"CHANNEL SUMMARY — sorted by attributed revenue"]
for _,r in ch.sort_values("attributed_revenue",ascending=False).iterrows():
    report.append(f"{r.channel}: spend={r.spend:,.2f}; leads={int(r.leads):,}; conversions={int(r.conversions):,}; revenue={r.attributed_revenue:,.2f}; CTR={r.ctr_pct:.2f}%; ROAS={r.roas:.2f}x")
report += ["","TOP 5 CAMPAIGNS BY ATTRIBUTED REVENUE"]
for _,r in cp.sort_values("attributed_revenue",ascending=False).head(5).iterrows():
    report.append(f"{r.campaign_id} | {r.campaign_name} | channel={r.channel} | spend={r.spend:,.2f} | conversions={int(r.conversions):,} | revenue={r.attributed_revenue:,.2f} | ROAS={r.roas:.2f}x")
report += ["","OUTPUT FILES","campaign_performance.csv","channel_performance.csv","monthly_performance.csv","project5_marketing_analysis_report.txt"]
out=BASE/"project5_marketing_analysis_report.txt"
out.write_text("\n".join(report)+"\n",encoding="utf-8")
print("\n".join(report))
print(f"\nReport saved to: {out}")
print("Three analysis CSV files saved beside the source files.")

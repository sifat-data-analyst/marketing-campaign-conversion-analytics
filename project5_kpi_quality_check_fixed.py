from pathlib import Path
import math
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent
REPORT = BASE / "project5_kpi_quality_check_report.txt"
FILES = {
    "campaigns": BASE / "campaigns.csv",
    "daily_spend": BASE / "daily_spend.csv",
    "leads": BASE / "leads.csv",
    "conversions": BASE / "conversions.csv",
    "campaign_output": BASE / "campaign_performance.csv",
    "channel_output": BASE / "channel_performance.csv",
    "monthly_output": BASE / "monthly_performance.csv",
}
checks = []
notes = []

def check(name, ok, detail=""):
    checks.append((name, bool(ok)))
    notes.append(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

def compare(actual, expected, key, col, label, atol=0.03):
    if key not in actual or key not in expected or col not in actual or col not in expected:
        check(label, False, "Required key/column missing.")
        return
    a, e = actual[[key, col]].copy(), expected[[key, col]].copy()
    a[key], e[key] = a[key].astype(str), e[key].astype(str)
    m = a.merge(e, on=key, how="outer", suffixes=("_a", "_e"), indicator=True)
    if not (m["_merge"] == "both").all():
        check(label, False, "Rows/keys differ.")
        return
    x, y = pd.to_numeric(m[f"{col}_a"], errors="coerce"), pd.to_numeric(m[f"{col}_e"], errors="coerce")
    matched = np.isclose(x.fillna(0), y.fillna(0), atol=atol, rtol=1e-7) | (x.isna() & y.isna())
    check(label, matched.all(), f"Mismatches={int((~matched).sum())}; tolerance ±{atol}")

def div(a, b):
    a, b = pd.to_numeric(a, errors="coerce"), pd.to_numeric(b, errors="coerce")
    return a.div(b.where(b.ne(0)))

def main():
    for name, p in FILES.items():
        check(f"File exists: {name}", p.is_file(), p.name)
    missing = [p.name for p in FILES.values() if not p.is_file()]
    if missing:
        REPORT.write_text("Missing required files: " + ", ".join(missing), encoding="utf-8")
        print("Missing required files:", ", ".join(missing))
        raise SystemExit(2)

    campaigns = pd.read_csv(FILES["campaigns"], parse_dates=["start_date", "end_date"])
    spend = pd.read_csv(FILES["daily_spend"], parse_dates=["spend_date"])
    leads = pd.read_csv(FILES["leads"], parse_dates=["created_at"])
    conv = pd.read_csv(FILES["conversions"], parse_dates=["converted_at"])
    co = pd.read_csv(FILES["campaign_output"])
    cho = pd.read_csv(FILES["channel_output"])
    mo = pd.read_csv(FILES["monthly_output"])

    check("Campaign source has 120 rows", len(campaigns) == 120, f"Rows={len(campaigns)}")
    for name, df, idcol in [
        ("campaign", campaigns, "campaign_id"), ("spend", spend, "spend_id"),
        ("lead", leads, "lead_id"), ("conversion", conv, "conversion_id")
    ]:
        check(f"{name.title()} IDs unique", df[idcol].is_unique,
              f"Rows={len(df)}; unique={df[idcol].nunique()}")
    check("Spend campaign foreign keys valid", spend.campaign_id.isin(campaigns.campaign_id).all(),
          f"Invalid={int((~spend.campaign_id.isin(campaigns.campaign_id)).sum())}")
    check("Lead campaign foreign keys valid", leads.campaign_id.isin(campaigns.campaign_id).all(),
          f"Invalid={int((~leads.campaign_id.isin(campaigns.campaign_id)).sum())}")
    lk = leads[["lead_id", "campaign_id", "created_at"]]
    cj = conv.merge(lk, on="lead_id", how="left", validate="one_to_one", indicator=True)
    check("All conversions map to a lead", (cj["_merge"] == "both").all(),
          f"Unmatched={int((cj['_merge'] != 'both').sum())}")
    check("Conversion types are trial/purchase", conv.conversion_type.isin(["trial", "purchase"]).all(),
          f"Types={sorted(conv.conversion_type.dropna().astype(str).unique())}")

    # Rebuild campaign-level metrics from source files independently.
    sb = spend.groupby("campaign_id", as_index=False).agg(
        impressions=("impressions", "sum"), clicks=("clicks", "sum"),
        spend=("spend", "sum"), spend_days=("spend_date", "nunique"))
    lb = leads.groupby("campaign_id", as_index=False).agg(
        leads=("lead_id", "nunique"), average_lead_score=("lead_score", "mean"))
    cb = cj.groupby("campaign_id", as_index=False).agg(
        conversions=("conversion_id", "nunique"), attributed_revenue=("revenue", "sum"),
        trial_conversions=("conversion_type", lambda s: int((s == "trial").sum())),
        purchase_conversions=("conversion_type", lambda s: int((s == "purchase").sum())))
    ec = campaigns.merge(sb, on="campaign_id", how="left", validate="one_to_one")
    ec = ec.merge(lb, on="campaign_id", how="left", validate="one_to_one")
    ec = ec.merge(cb, on="campaign_id", how="left", validate="one_to_one")
    for c in ["impressions", "clicks", "spend", "spend_days", "leads", "conversions",
              "attributed_revenue", "trial_conversions", "purchase_conversions", "average_lead_score"]:
        ec[c] = ec[c].fillna(0)
    ec["ctr_pct"] = div(ec.clicks, ec.impressions) * 100
    ec["cpc"] = div(ec.spend, ec.clicks)
    ec["lead_to_conversion_pct"] = div(ec.conversions, ec.leads) * 100
    ec["cost_per_conversion"] = div(ec.spend, ec.conversions)
    ec["roas"] = div(ec.attributed_revenue, ec.spend)
    ec["budget_used_pct"] = div(ec.spend, ec.budget) * 100
    ec["revenue_minus_ad_spend"] = ec.attributed_revenue - ec.spend

    check("Campaign output has 120 rows", len(co) == 120, f"Rows={len(co)}")
    check("Campaign output IDs unique", "campaign_id" in co and co.campaign_id.is_unique)
    for c in ["impressions", "clicks", "spend", "spend_days", "leads", "conversions",
              "attributed_revenue", "trial_conversions", "purchase_conversions", "average_lead_score",
              "ctr_pct", "cpc", "lead_to_conversion_pct", "cost_per_conversion", "roas",
              "budget_used_pct", "revenue_minus_ad_spend"]:
        compare(co, ec, "campaign_id", c, f"Campaign value/formula: {c}")

    # Rebuild channel-level totals and KPIs.
    ech = ec.groupby("channel", as_index=False).agg(
        campaigns=("campaign_id", "nunique"), impressions=("impressions", "sum"),
        clicks=("clicks", "sum"), spend=("spend", "sum"), leads=("leads", "sum"),
        conversions=("conversions", "sum"), attributed_revenue=("attributed_revenue", "sum"),
        budget=("budget", "sum"))
    ech["ctr_pct"] = div(ech.clicks, ech.impressions) * 100
    ech["cpc"] = div(ech.spend, ech.clicks)
    ech["lead_to_conversion_pct"] = div(ech.conversions, ech.leads) * 100
    ech["cost_per_conversion"] = div(ech.spend, ech.conversions)
    ech["roas"] = div(ech.attributed_revenue, ech.spend)
    ech["budget_used_pct"] = div(ech.spend, ech.budget) * 100
    ech["revenue_minus_ad_spend"] = ech.attributed_revenue - ech.spend
    check("Channel output has 5 rows", len(cho) == 5, f"Rows={len(cho)}")
    for c in ["campaigns", "impressions", "clicks", "spend", "leads", "conversions",
              "attributed_revenue", "budget", "ctr_pct", "cpc", "lead_to_conversion_pct",
              "cost_per_conversion", "roas", "budget_used_pct", "revenue_minus_ad_spend"]:
        compare(cho, ech, "channel", c, f"Channel value/formula: {c}")

    # Rebuild monthly metrics: spend date, lead creation date, conversion date.
    sm = spend.assign(month=spend.spend_date.dt.to_period("M").astype(str)).groupby("month", as_index=False).agg(
        impressions=("impressions", "sum"), clicks=("clicks", "sum"), spend=("spend", "sum"))
    lm = leads.assign(month=leads.created_at.dt.to_period("M").astype(str)).groupby("month", as_index=False).agg(
        leads=("lead_id", "nunique"))
    cj["month"] = cj.converted_at.dt.to_period("M").astype(str)
    cm = cj.groupby("month", as_index=False).agg(
        conversions=("conversion_id", "nunique"), attributed_revenue=("revenue", "sum"))
    em = sm.merge(lm, on="month", how="outer").merge(cm, on="month", how="outer")
    for c in ["impressions", "clicks", "spend", "leads", "conversions", "attributed_revenue"]:
        em[c] = em[c].fillna(0)
    em["ctr_pct"] = div(em.clicks, em.impressions) * 100
    em["cpc"] = div(em.spend, em.clicks)
    em["lead_to_conversion_pct"] = div(em.conversions, em.leads) * 100
    em["cost_per_conversion"] = div(em.spend, em.conversions)
    em["roas"] = div(em.attributed_revenue, em.spend) 
    check("Monthly output has 36 rows", len(mo) == 36, f"Rows={len(mo)}")
    for c in ["impressions", "clicks", "spend", "leads", "conversions", "attributed_revenue",
              "ctr_pct", "cpc", "lead_to_conversion_pct", "cost_per_conversion", "roas"]:
        compare(mo, em, "month", c, f"Monthly value/formula: {c}")

    # Reconciliation across raw sources and outputs.
    source_spend, source_revenue = float(spend.spend.sum()), float(conv.revenue.sum())
    for label, df, col, target in [
        ("Campaign spend reconciles", co, "spend", source_spend),
        ("Channel spend reconciles", cho, "spend", source_spend),
        ("Monthly spend reconciles", mo, "spend", source_spend),
        ("Campaign revenue reconciles", co, "attributed_revenue", source_revenue),
        ("Channel revenue reconciles", cho, "attributed_revenue", source_revenue),
        ("Monthly revenue reconciles", mo, "attributed_revenue", source_revenue),
    ]:
        total = float(pd.to_numeric(df[col], errors="coerce").sum())
        check(label, math.isclose(total, target, abs_tol=0.03, rel_tol=1e-7),
              f"Output={total:.2f}; source={target:.2f}")

    for name, df in [("Campaign", co), ("Channel", cho), ("Monthly", mo)]:
        cols = [c for c in ["ctr_pct", "cpc", "lead_to_conversion_pct", "cost_per_conversion",
                            "roas", "budget_used_pct"] if c in df.columns]
        has_inf = any(np.isinf(pd.to_numeric(df[c], errors="coerce").to_numpy(dtype=float)).any() for c in cols)
        check(f"{name} KPIs contain no infinity values", not has_inf)
    check("Source spend is non-negative", (pd.to_numeric(spend.spend, errors="coerce") >= 0).all())
    check("Source revenue is non-negative", (pd.to_numeric(conv.revenue, errors="coerce") >= 0).all())

    over_budget = int((pd.to_numeric(co.budget_used_pct, errors="coerce") > 100).sum()) if "budget_used_pct" in co else 0
    notes.extend([
        f"[INFO] Campaigns with spend above budget: {over_budget}. This is an observation, not automatically an error.",
        "[INFO] revenue_minus_ad_spend is NOT profit or net income.",
        "[INFO] ROAS is attributed revenue / recorded media spend; it is NOT profit or ROI.",
        "[INFO] Monthly leads use lead creation month; conversions/revenue use conversion month. Monthly ratios are not cohort-based.",
        "[INFO] Dataset is synthetic; portfolio findings must not be presented as real-company outcomes."
    ])
    passed = sum(1 for _, ok in checks if ok)
    failed = len(checks) - passed
    report = "\n".join([
        "PROJECT 5 — KPI & CALCULATION QUALITY CHECK",
        f"Folder: {BASE}",
        "Source CSVs are read-only; this script does not modify any CSV data.",
        f"Checks passed: {passed}",
        f"Checks failed: {failed}",
        "", "DETAILS", *notes, "",
        "RESULT: " + ("ALL TESTED CHECKS PASSED." if failed == 0 else "FAILURES FOUND — review FAIL items before continuing.")
    ])
    REPORT.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nReport saved: {REPORT.name}")
    if failed:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

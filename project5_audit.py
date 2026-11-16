from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent
FILES = {
    "campaigns": "campaigns.csv",
    "daily_spend": "daily_spend.csv",
    "leads": "leads.csv",
    "conversions": "conversions.csv",
}
IDS = {"campaigns": "campaign_id", "daily_spend": "spend_id",
       "leads": "lead_id", "conversions": "conversion_id"}
DATES = {"campaigns": ["start_date", "end_date"],
         "daily_spend": ["spend_date"], "leads": ["created_at"],
         "conversions": ["converted_at"]}
START, END = pd.Timestamp("2023-01-01"), pd.Timestamp("2025-12-31")
lines = ["PROJECT 5 — COMPREHENSIVE DATA QUALITY AUDIT",
         f"Folder: {BASE}", "Dataset is synthetic. Raw CSV files are not modified.", ""]
flags = []

def add(level, area, message):
    line = f"[{level}] {area}: {message}"
    lines.append(line)
    if level in ("WARNING", "FAIL"):
        flags.append(line)

missing = [f for f in FILES.values() if not (BASE / f).exists()]
if missing:
    for f in missing:
        add("FAIL", "FILE", f"Missing required file: {f}")
else:
    data = {name: pd.read_csv(BASE / filename) for name, filename in FILES.items()}
    for name, df in data.items():
        lines.append(f"--- {FILES[name]} ---")
        add("INFO", "STRUCTURE", f"{len(df)} rows; {len(df.columns)} columns; columns={list(df.columns)}")
        nulls = int(df.isna().sum().sum())
        add("PASS" if nulls == 0 else "WARNING", "MISSING", f"{name}: {nulls} null cells")
        blanks = sum(int(df[c].astype("string").str.strip().eq("").sum())
                     for c in df.select_dtypes(include=["object", "string"]).columns)
        add("PASS" if blanks == 0 else "WARNING", "BLANK TEXT", f"{name}: {blanks} blank/whitespace cells")
        dup_rows = int(df.duplicated().sum())
        add("PASS" if dup_rows == 0 else "WARNING", "DUPLICATE ROWS", f"{name}: {dup_rows}")
        idc = IDS[name]
        if idc in df:
            dup_ids = int(df[idc].duplicated().sum())
            add("PASS" if dup_ids == 0 else "FAIL", "UNIQUE ID", f"{name}.{idc}: {dup_ids} duplicate IDs")
        lines.append("")

    c, s, l, v = (data[k].copy() for k in ("campaigns", "daily_spend", "leads", "conversions"))
    for name, df in (("campaigns", c), ("daily_spend", s), ("leads", l), ("conversions", v)):
        for col in DATES[name]:
            parsed = pd.to_datetime(df[col], errors="coerce")
            invalid = int(parsed.isna().sum())
            add("PASS" if invalid == 0 else "FAIL", "DATE PARSING", f"{name}.{col}: {invalid} invalid dates")
            outside = int((parsed.notna() & ((parsed < START) | (parsed > END))).sum())
            add("PASS" if outside == 0 else "WARNING", "DATE COVERAGE",
                f"{name}.{col}: {outside} dates outside {START.date()} to {END.date()}")
            df[col] = parsed

    reversed_dates = int((c.end_date < c.start_date).sum())
    add("PASS" if reversed_dates == 0 else "FAIL", "CAMPAIGN DATES",
        f"end_date before start_date: {reversed_dates}")

    campaign_ids = set(c.campaign_id.dropna())
    lead_ids = set(l.lead_id.dropna())
    fk_checks = [
        ("daily_spend campaign IDs missing from campaigns", int((~s.campaign_id.isin(campaign_ids)).sum())),
        ("lead campaign IDs missing from campaigns", int((~l.campaign_id.isin(campaign_ids)).sum())),
        ("conversion lead IDs missing from leads", int((~v.lead_id.isin(lead_ids)).sum())),
    ]
    for label, count in fk_checks:
        add("PASS" if count == 0 else "FAIL", "FOREIGN KEY", f"{label}: {count}")

    repeated_conversion_leads = int(v.lead_id.duplicated().sum())
    add("PASS" if repeated_conversion_leads == 0 else "WARNING", "RELATIONSHIP",
        f"Repeated lead_id in conversions (dictionary says one-to-one): {repeated_conversion_leads}")
    repeated_spend_dates = int(s.duplicated(["campaign_id", "spend_date"]).sum())
    add("PASS" if repeated_spend_dates == 0 else "WARNING", "GRAIN",
        f"Repeated campaign_id + spend_date pairs: {repeated_spend_dates}")

    campaign_dates = c[["campaign_id", "start_date", "end_date"]].drop_duplicates("campaign_id")
    sx = s.merge(campaign_dates, on="campaign_id", how="left")
    bad_spend_dates = int((sx.spend_date.notna() & sx.start_date.notna() & sx.end_date.notna() &
        ((sx.spend_date < sx.start_date) | (sx.spend_date > sx.end_date))).sum())
    add("PASS" if bad_spend_dates == 0 else "WARNING", "BUSINESS RULE",
        f"Spend dates outside campaign active dates: {bad_spend_dates}")
    lx = l.merge(campaign_dates, on="campaign_id", how="left")
    bad_lead_dates = int((lx.created_at.notna() & lx.start_date.notna() & lx.end_date.notna() &
        ((lx.created_at < lx.start_date) | (lx.created_at > lx.end_date))).sum())
    add("PASS" if bad_lead_dates == 0 else "WARNING", "BUSINESS RULE",
        f"Lead dates outside campaign active dates: {bad_lead_dates}")
    vx = v.merge(l[["lead_id", "created_at"]], on="lead_id", how="left")
    bad_conversion_order = int((vx.converted_at.notna() & vx.created_at.notna() &
        (vx.converted_at < vx.created_at)).sum())
    add("PASS" if bad_conversion_order == 0 else "WARNING", "BUSINESS RULE",
        f"Conversion before lead creation: {bad_conversion_order}")

    numeric = [
        ("campaigns", c, "budget"), ("daily_spend", s, "impressions"),
        ("daily_spend", s, "clicks"), ("daily_spend", s, "spend"),
        ("leads", l, "lead_score"), ("conversions", v, "revenue")]
    for name, df, col in numeric:
        vals = pd.to_numeric(df[col], errors="coerce")
        unparsable = int((vals.isna() & df[col].notna()).sum())
        negative = int((vals < 0).sum())
        add("PASS" if unparsable == 0 else "FAIL", "NUMERIC FORMAT",
            f"{name}.{col}: {unparsable} non-numeric values")
        add("PASS" if negative == 0 else "WARNING", "NEGATIVE VALUES",
            f"{name}.{col}: {negative} negative values")

    clicks_gt = int((pd.to_numeric(s.clicks, errors="coerce") >
                     pd.to_numeric(s.impressions, errors="coerce")).sum())
    add("PASS" if clicks_gt == 0 else "WARNING", "BUSINESS RULE",
        f"Rows where clicks exceed impressions: {clicks_gt}")
    bad_scores = int((~pd.to_numeric(l.lead_score, errors="coerce").between(1, 100)).sum())
    add("PASS" if bad_scores == 0 else "WARNING", "BUSINESS RULE",
        f"Lead scores outside documented 1–100 range: {bad_scores}")
    objectives = set(c.objective.dropna().astype(str).str.strip().str.lower())
    unexpected_obj = sorted(objectives - {"awareness", "lead_gen", "acquisition"})
    add("PASS" if not unexpected_obj else "WARNING", "CATEGORY",
        f"Unexpected objectives: {unexpected_obj or 'None'}")
    types = set(v.conversion_type.dropna().astype(str).str.strip().str.lower())
    unexpected_types = sorted(types - {"trial", "purchase"})
    add("PASS" if not unexpected_types else "WARNING", "CATEGORY",
        f"Unexpected conversion types: {unexpected_types or 'None'}")

    lines.append("")
    lines.append("--- DESCRIPTIVE TOTALS (not performance conclusions) ---")
    lines.append(f"Campaign rows: {len(c)}")
    lines.append(f"Daily spend rows: {len(s)}")
    lines.append(f"Lead rows: {len(l)}")
    lines.append(f"Conversion rows: {len(v)}")
    lines.append(f"Total spend: {pd.to_numeric(s.spend, errors='coerce').sum():,.2f}")
    lines.append(f"Total attributed revenue: {pd.to_numeric(v.revenue, errors='coerce').sum():,.2f}")

lines.extend(["", "--- SUMMARY ---"])
lines.append(f"PASS checks: {sum(x.startswith('[PASS]') for x in lines)}")
lines.append(f"WARNING checks: {sum(x.startswith('[WARNING]') for x in lines)}")
lines.append(f"FAIL checks: {sum(x.startswith('[FAIL]') for x in lines)}")
lines.append("Warnings require review; they do not automatically mean the data is wrong.")
lines.append("Raw CSV files were not edited.")
lines.append("")
lines.append("--- ITEMS TO REVIEW ---")
lines.extend(flags if flags else ["No WARNING or FAIL checks raised."])

out = BASE / "project5_audit_report.txt"
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print(f"\nReport saved to: {out}")

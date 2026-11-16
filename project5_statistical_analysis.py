from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE_DIR = Path(__file__).resolve().parent

CAMPAIGNS_FILE = BASE_DIR / "campaigns.csv"
SPEND_FILE = BASE_DIR / "daily_spend.csv"
LEADS_FILE = BASE_DIR / "leads.csv"
CONVERSIONS_FILE = BASE_DIR / "conversions.csv"

OUTPUT_CHANNEL = BASE_DIR / "project5_statistics_channel_summary.csv"
OUTPUT_PAIRWISE = BASE_DIR / "project5_statistics_pairwise_tests.csv"
OUTPUT_LEADS = BASE_DIR / "project5_statistics_lead_source.csv"
OUTPUT_REPORT = BASE_DIR / "project5_statistics_analysis_report.txt"


def safe_divide(numerator, denominator):
    if denominator == 0:
        return np.nan
    return numerator / denominator


def main():
    print("=" * 65)
    print("PROJECT 5 — STATISTICAL ANALYSIS")
    print("=" * 65)

    # Load source files without modifying them
    campaigns = pd.read_csv(CAMPAIGNS_FILE)
    spend = pd.read_csv(SPEND_FILE)
    leads = pd.read_csv(LEADS_FILE)
    conversions = pd.read_csv(CONVERSIONS_FILE)

    # Basic data preparation
    for col in ["start_date", "end_date"]:
        campaigns[col] = pd.to_datetime(campaigns[col], errors="coerce")

    spend["spend_date"] = pd.to_datetime(
        spend["spend_date"], errors="coerce"
    )
    leads["created_at"] = pd.to_datetime(
        leads["created_at"], errors="coerce"
    )
    conversions["converted_at"] = pd.to_datetime(
        conversions["converted_at"], errors="coerce"
    )

    # Aggregate spend and engagement by campaign
    spend_summary = spend.groupby("campaign_id").agg(
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        spend=("spend", "sum"),
        spend_days=("spend_date", "nunique"),
    ).reset_index()

    # Aggregate leads by campaign
    lead_summary = leads.groupby("campaign_id").agg(
        leads=("lead_id", "nunique"),
        average_lead_score=("lead_score", "mean"),
    ).reset_index()

    # Map each conversion to its campaign through the lead table
    lead_campaign = leads[["lead_id", "campaign_id"]].drop_duplicates()

    conversion_map = conversions.merge(
        lead_campaign,
        on="lead_id",
        how="left",
        validate="many_to_one",
    )

    conversion_summary = conversion_map.groupby("campaign_id").agg(
        conversions=("conversion_id", "nunique"),
        attributed_revenue=("revenue", "sum"),
    ).reset_index()

    # Build one row per campaign
    summary = campaigns.merge(
        spend_summary, on="campaign_id", how="left"
    )
    summary = summary.merge(
        lead_summary, on="campaign_id", how="left"
    )
    summary = summary.merge(
        conversion_summary, on="campaign_id", how="left"
    )

    count_columns = [
        "impressions", "clicks", "spend", "spend_days",
        "leads", "conversions", "attributed_revenue"
    ]
    for col in count_columns:
        summary[col] = summary[col].fillna(0)

    summary["ctr_pct"] = (
        summary["clicks"] / summary["impressions"].replace(0, np.nan)
    ) * 100

    summary["cpc"] = (
        summary["spend"] / summary["clicks"].replace(0, np.nan)
    )

    summary["lead_to_conversion_pct"] = (
        summary["conversions"] / summary["leads"].replace(0, np.nan)
    ) * 100

    summary["cost_per_conversion"] = (
        summary["spend"] / summary["conversions"].replace(0, np.nan)
    )

    summary["roas"] = (
        summary["attributed_revenue"] /
        summary["spend"].replace(0, np.nan)
    )

    # Channel-level descriptive statistics
    channel_summary = summary.groupby("channel").agg(
        campaigns=("campaign_id", "nunique"),
        total_spend=("spend", "sum"),
        total_impressions=("impressions", "sum"),
        total_clicks=("clicks", "sum"),
        total_leads=("leads", "sum"),
        total_conversions=("conversions", "sum"),
        attributed_revenue=("attributed_revenue", "sum"),
        mean_campaign_ctr_pct=("ctr_pct", "mean"),
        median_campaign_ctr_pct=("ctr_pct", "median"),
        mean_campaign_roas=("roas", "mean"),
        median_campaign_roas=("roas", "median"),
        mean_campaign_cpc=("cpc", "mean"),
        median_campaign_cpc=("cpc", "median"),
    ).reset_index()

    channel_summary["overall_ctr_pct"] = (
        channel_summary["total_clicks"] /
        channel_summary["total_impressions"].replace(0, np.nan)
    ) * 100

    channel_summary["overall_roas"] = (
        channel_summary["attributed_revenue"] /
        channel_summary["total_spend"].replace(0, np.nan)
    )

    channel_summary.to_csv(OUTPUT_CHANNEL, index=False)

    # Kruskal-Wallis tests compare campaign-level distributions
    # across channels. Campaigns, not individual clicks, are the units.
    test_metrics = ["roas", "ctr_pct", "cpc"]
    test_results = []
    pairwise_results = []

    for metric in test_metrics:
        groups = []
        group_names = []

        for channel, group in summary.groupby("channel"):
            values = group[metric].replace(
                [np.inf, -np.inf], np.nan
            ).dropna()

            if len(values) >= 2:
                groups.append(values.to_numpy())
                group_names.append(channel)

        if len(groups) < 2:
            test_results.append(
                f"{metric}: Insufficient groups for statistical testing."
            )
            continue

        h_stat, p_value = stats.kruskal(*groups)
        total_n = sum(len(group) for group in groups)
        number_groups = len(groups)

        # Epsilon-squared effect size estimate
        effect_size = (
            (h_stat - number_groups + 1) /
            (total_n - number_groups)
            if total_n > number_groups else np.nan
        )
        effect_size = max(0.0, effect_size) if np.isfinite(effect_size) else np.nan

        test_results.append(
            f"{metric}: Kruskal-Wallis H={h_stat:.4f}, "
            f"p-value={p_value:.6g}, "
            f"epsilon-squared={effect_size:.4f}, "
            f"campaigns tested={total_n}"
        )

        # Pairwise Mann-Whitney tests, followed by Holm correction
        raw_pairs = []

        for i in range(len(group_names)):
            for j in range(i + 1, len(group_names)):
                name_a = group_names[i]
                name_b = group_names[j]
                values_a = groups[i]
                values_b = groups[j]

                u_stat, pair_p = stats.mannwhitneyu(
                    values_a,
                    values_b,
                    alternative="two-sided",
                )

                raw_pairs.append({
                    "metric": metric,
                    "channel_a": name_a,
                    "channel_b": name_b,
                    "n_a": len(values_a),
                    "n_b": len(values_b),
                    "median_a": float(np.median(values_a)),
                    "median_b": float(np.median(values_b)),
                    "u_statistic": float(u_stat),
                    "p_value": float(pair_p),
                })

        if raw_pairs:
            adjusted = multipletests(
                [item["p_value"] for item in raw_pairs],
                method="holm",
            )

            for idx, item in enumerate(raw_pairs):
                item["holm_adjusted_p_value"] = float(adjusted[1][idx])
                item["significant_at_0_05"] = bool(adjusted[0][idx])
                pairwise_results.append(item)

    pd.DataFrame(pairwise_results).to_csv(
        OUTPUT_PAIRWISE, index=False
    )

    # Lead-source descriptive summary
    lead_source_summary = leads.groupby("lead_source").agg(
        leads=("lead_id", "nunique"),
        mean_lead_score=("lead_score", "mean"),
        median_lead_score=("lead_score", "median"),
        lead_score_std=("lead_score", "std"),
    ).reset_index()

    converted_leads = conversion_map[
        ["lead_id", "conversion_id"]
    ].drop_duplicates()["lead_id"].unique()

    converted_ids = set(converted_leads)
    leads_for_source = leads.copy()
    leads_for_source["has_conversion"] = (
        leads_for_source["lead_id"].isin(converted_ids)
    )

    source_conversion = leads_for_source.groupby("lead_source").agg(
        leads=("lead_id", "nunique"),
        leads_with_conversion=("has_conversion", "sum"),
    ).reset_index()

    source_conversion["lead_conversion_pct"] = (
        source_conversion["leads_with_conversion"] /
        source_conversion["leads"].replace(0, np.nan)
    ) * 100

    lead_source_summary = lead_source_summary.merge(
        source_conversion[
            ["lead_source", "leads_with_conversion", "lead_conversion_pct"]
        ],
        on="lead_source",
        how="left",
    )

    lead_source_summary.to_csv(OUTPUT_LEADS, index=False)

    # Lead score comparison across lead sources
    lead_score_groups = []
    for source, group in leads.groupby("lead_source"):
        values = group["lead_score"].dropna().to_numpy()
        if len(values) >= 2:
            lead_score_groups.append((source, values))

    lead_score_test = "Lead score test: not enough groups to compare."
    if len(lead_score_groups) >= 2:
        h_stat, p_value = stats.kruskal(
            *[values for _, values in lead_score_groups]
        )
        lead_score_test = (
            f"Lead score by lead_source: Kruskal-Wallis "
            f"H={h_stat:.4f}, p-value={p_value:.6g}. "
            "This compares score distributions, not business causality."
        )

    # Build report
    report_lines = [
        "PROJECT 5 — STATISTICAL ANALYSIS REPORT",
        f"Project folder: {BASE_DIR}",
        "",
        "DATASET SCOPE",
        f"Campaigns analyzed: {len(summary)}",
        f"Spend records loaded: {len(spend)}",
        f"Leads loaded: {len(leads)}",
        f"Conversions loaded: {len(conversions)}",
        f"Channels analyzed: {summary['channel'].nunique()}",
        "",
        "CHANNEL DESCRIPTIVE SUMMARY",
        channel_summary.to_string(index=False),
        "",
        "STATISTICAL TESTS",
        "Kruskal-Wallis tests compare campaign-level metric distributions "
        "across channels.",
        "Pairwise Mann-Whitney tests use Holm adjustment for multiple comparisons.",
        *test_results,
        "",
        "LEAD SOURCE SUMMARY",
        lead_source_summary.to_string(index=False),
        "",
        "LEAD SCORE TEST",
        lead_score_test,
        "",
        "INTERPRETATION NOTES",
        "- A small p-value indicates evidence of distribution differences, "
        "not proof that channel caused the difference.",
        "- A non-significant result does not prove that channels are identical.",
        "- Effect size and medians should be considered alongside p-values.",
        "- Campaigns may differ in budget, objective, dates, and other factors.",
        "- ROAS is attributed revenue divided by spend; it is not profit or ROI.",
        "- This dataset is synthetic; results must not be presented as real-company outcomes.",
        "- Lead-source conversion percentages use whether a lead has any mapped "
        "conversion; they are not a causal attribution study.",
        "",
        "OUTPUT FILES",
        OUTPUT_CHANNEL.name,
        OUTPUT_PAIRWISE.name,
        OUTPUT_LEADS.name,
        OUTPUT_REPORT.name,
    ]

    OUTPUT_REPORT.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print("\nSTATISTICAL ANALYSIS COMPLETED")
    print(f"Campaigns analyzed: {len(summary)}")
    print(f"Channels analyzed: {summary['channel'].nunique()}")
    print(f"Lead sources analyzed: {leads['lead_source'].nunique()}")
    print("\nFiles created:")
    print(f"- {OUTPUT_CHANNEL.name}")
    print(f"- {OUTPUT_PAIRWISE.name}")
    print(f"- {OUTPUT_LEADS.name}")
    print(f"- {OUTPUT_REPORT.name}")
    print("\nPlease share the console output for verification.")


if __name__ == "__main__":
    main()
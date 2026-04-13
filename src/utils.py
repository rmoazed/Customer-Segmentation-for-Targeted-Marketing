"""Business summaries, simple chart export, and revenue uplift helpers."""

from __future__ import annotations
from pathlib import Path
from typing import Dict
import matplotlib.pyplot as plt
import pandas as pd


SEGMENT_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "High-Value Loyal Customers": {
        "summary": "These customers purchase recently, frequently, and spend the most.",
        "strategy": "Focus on retention, loyalty rewards, VIP perks, and personalized recommendations.",
    },
    "At-Risk Valuable Customers": {
        "summary": "These customers used to spend meaningfully, but have not purchased as recently.",
        "strategy": "Use targeted re-engagement campaigns, win-back discounts, and personalized outreach.",
    },
    "Recent Low-Value Customers": {
        "summary": "These customers purchased recently but have not yet developed strong buying habits.",
        "strategy": "Use onboarding flows, product recommendations, and second-purchase incentives.",
    },
    "Inactive Customers": {
        "summary": "These customers have not purchased recently, buy infrequently, and contribute relatively little revenue.",
        "strategy": "Use low-cost reactivation campaigns or deprioritize if acquisition cost is too high.",
    },
}


def revenue_by_segment(rfm_segmented: pd.DataFrame) -> pd.Series:
    return rfm_segmented.groupby("Segment")["Monetary"].sum().sort_values(ascending=False)


def revenue_share_pct(rfm_segmented: pd.DataFrame) -> pd.Series:
    rev = revenue_by_segment(rfm_segmented)
    return rev / rev.sum() * 100


def simulate_revenue_uplift(
    rfm_segmented: pd.DataFrame,
    segment_name: str,
    uplift_rate: float,
) -> float:
    """
    Estimate incremental revenue from improving a segment by uplift_rate.
    Example: uplift_rate=0.10 means a 10% increase.
    """
    segment_revenue = rfm_segmented.loc[
        rfm_segmented["Segment"] == segment_name, "Monetary"
    ].sum()
    return segment_revenue * uplift_rate


def save_dataframe(df: pd.DataFrame, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_bar_chart(series: pd.Series, title: str, ylabel: str, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(series.index, series.values)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Segment")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)

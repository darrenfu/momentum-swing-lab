#!/usr/bin/env python3
"""Summarize the one-month momentum screen output."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


DATA = Path("data")
RESULTS = DATA / "screen_results.csv"
TOP = DATA / "top_5pct_one_month_gainers.csv"
OUT = DATA / "analysis_summary.json"


def pct(x: float) -> float:
    return round(100 * float(x), 2)


def main() -> None:
    all_df = pd.read_csv(RESULTS)
    top = pd.read_csv(TOP)

    all_sector = all_df["sector"].value_counts(normalize=True)
    top_sector = top["sector"].value_counts(normalize=True)
    sector_lift = (
        pd.concat([top_sector.rename("top_share"), all_sector.rename("universe_share")], axis=1)
        .fillna(0)
        .assign(lift=lambda d: d["top_share"] / d["universe_share"].replace(0, pd.NA))
        .sort_values("top_share", ascending=False)
    )

    all_ind = all_df["industry"].value_counts(normalize=True)
    top_ind = top["industry"].value_counts(normalize=True)
    industry_lift = (
        pd.concat([top_ind.rename("top_share"), all_ind.rename("universe_share")], axis=1)
        .fillna(0)
        .assign(lift=lambda d: d["top_share"] / d["universe_share"].replace(0, pd.NA))
        .sort_values(["top_share", "lift"], ascending=False)
    )

    market_caps = top["market_cap"]
    dollar_vol = top["nasdaq_dollar_volume"]

    def records(frame: pd.DataFrame, n: int) -> list[dict]:
        return json.loads(frame.head(n).reset_index().to_json(orient="records"))

    summary = {
        "top_rows": int(len(top)),
        "return_cutoff_pct": pct(top["one_month_return"].min()),
        "return_median_pct": pct(top["one_month_return"].median()),
        "return_mean_pct": pct(top["one_month_return"].mean()),
        "return_max_pct": pct(top["one_month_return"].max()),
        "market_cap_median_bil": round(float(market_caps.median()) / 1e9, 2),
        "market_cap_lt_5b_count": int((market_caps < 5e9).sum()),
        "market_cap_lt_10b_count": int((market_caps < 10e9).sum()),
        "dollar_volume_median_mil": round(float(dollar_vol.median()) / 1e6, 1),
        "sector_counts": top["sector"].value_counts(dropna=False).to_dict(),
        "sector_lift": records(
            sector_lift.assign(
                top_share_pct=lambda d: (100 * d["top_share"]).round(2),
                universe_share_pct=lambda d: (100 * d["universe_share"]).round(2),
                lift=lambda d: d["lift"].round(2),
            )[["top_share_pct", "universe_share_pct", "lift"]],
            12,
        ),
        "top_industries": records(
            industry_lift.assign(
                top_count=top["industry"].value_counts(),
                top_share_pct=lambda d: (100 * d["top_share"]).round(2),
                universe_share_pct=lambda d: (100 * d["universe_share"]).round(2),
                lift=lambda d: d["lift"].round(2),
            )[["top_count", "top_share_pct", "universe_share_pct", "lift"]],
            25,
        ),
        "top_25": json.loads(
            top[
                [
                    "symbol",
                    "name",
                    "sector",
                    "industry",
                    "market_cap",
                    "nasdaq_dollar_volume",
                    "one_month_return",
                ]
            ]
            .head(25)
            .assign(
                market_cap_bil=lambda d: (d["market_cap"] / 1e9).round(2),
                dollar_volume_mil=lambda d: (d["nasdaq_dollar_volume"] / 1e6).round(1),
                return_pct=lambda d: (100 * d["one_month_return"]).round(2),
            )[
                [
                    "symbol",
                    "name",
                    "sector",
                    "industry",
                    "market_cap_bil",
                    "dollar_volume_mil",
                    "return_pct",
                ]
            ]
            .to_json(orient="records")
        ),
    }
    OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

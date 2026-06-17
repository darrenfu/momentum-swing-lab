#!/usr/bin/env python3
"""Verification checks for the US momentum screen."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests


DATA = Path("data")
TOP = DATA / "top_5pct_one_month_gainers.csv"
RESULTS = DATA / "screen_results.csv"
RAW_NASDAQ = DATA / "nasdaq_screener_raw.json"
OUT = DATA / "verification_report.json"


SAMPLE_SYMBOLS = [
    "HYLN",
    "APPS",
    "ARM",
    "ALAB",
    "MRVL",
    "DELL",
    "CBRL",
    "SNOW",
    "SLS",
    "BTDR",
]


def parse_money(value: object) -> float:
    text = str(value or "").strip().replace("$", "").replace(",", "").replace("%", "")
    try:
        return float(text)
    except ValueError:
        return float("nan")


def direct_yahoo_chart(symbol: str, start: str, end: str) -> dict:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        "period1": int(pd.Timestamp(start, tz="UTC").timestamp()) - 3 * 24 * 3600,
        "period2": int(pd.Timestamp(end, tz="UTC").timestamp()) + 2 * 24 * 3600,
        "interval": "1d",
        "events": "history|div|split",
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    payload = resp.json()["chart"]["result"][0]
    timestamps = payload["timestamp"]
    closes = payload["indicators"]["quote"][0]["close"]
    adj = payload["indicators"].get("adjclose", [{}])[0].get("adjclose", closes)
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(timestamps, unit="s", utc=True).date,
            "close": closes,
            "adj_close": adj,
        }
    )
    frame = frame.dropna(subset=["adj_close"])
    return {
        "start_adj_close": float(frame.loc[frame["date"] <= pd.to_datetime(start).date(), "adj_close"].iloc[-1]),
        "latest_adj_close": float(frame.loc[frame["date"] <= pd.to_datetime(end).date(), "adj_close"].iloc[-1]),
    }


def main() -> None:
    top = pd.read_csv(TOP)
    results = pd.read_csv(RESULTS)
    raw = json.loads(RAW_NASDAQ.read_text(encoding="utf-8"))
    raw_by_symbol = {row["symbol"]: row for row in raw["data"]["rows"]}

    failures: list[dict] = []

    # Verify all top names still satisfy the Nasdaq snapshot filters used by the screen.
    for _, row in top.iterrows():
        source = raw_by_symbol.get(row["symbol"])
        if not source:
            failures.append({"symbol": row["symbol"], "check": "missing_from_nasdaq_raw"})
            continue
        price = parse_money(source.get("lastsale"))
        market_cap = parse_money(source.get("marketCap"))
        volume = parse_money(source.get("volume"))
        dollar_volume = price * volume
        if price <= 3 or market_cap < 1_000_000_000 or dollar_volume < 20_000_000:
            failures.append(
                {
                    "symbol": row["symbol"],
                    "check": "filter_threshold",
                    "price": price,
                    "market_cap": market_cap,
                    "dollar_volume": dollar_volume,
                }
            )

    # Recompute the percentile cutoff from the full result set.
    cutoff = float(results["one_month_return"].quantile(0.95))
    cutoff_matches = abs(cutoff - float(top["one_month_return"].min())) < 0.002

    # Re-pull sample prices through Yahoo's chart endpoint, bypassing yfinance's dataframe code.
    samples = []
    by_symbol = top.set_index("symbol")
    for symbol in SAMPLE_SYMBOLS:
        row = by_symbol.loc[symbol]
        direct = direct_yahoo_chart(symbol, row["start_date"], row["latest_date"])
        direct_return = direct["latest_adj_close"] / direct["start_adj_close"] - 1.0
        samples.append(
            {
                "symbol": symbol,
                "csv_return": float(row["one_month_return"]),
                "direct_return": float(direct_return),
                "abs_diff": abs(float(row["one_month_return"]) - float(direct_return)),
                "csv_start": float(row["start_adj_close"]),
                "direct_start": direct["start_adj_close"],
                "csv_latest": float(row["latest_adj_close"]),
                "direct_latest": direct["latest_adj_close"],
            }
        )

    report = {
        "checked_top_rows": int(len(top)),
        "threshold_failures": failures,
        "cutoff_from_full_results": cutoff,
        "top_min_return": float(top["one_month_return"].min()),
        "cutoff_matches_top_membership": bool(cutoff_matches),
        "direct_yahoo_chart_sample": samples,
        "direct_yahoo_chart_max_abs_return_diff": max(s["abs_diff"] for s in samples),
        "status": "pass"
        if not failures
        and cutoff_matches
        and max(s["abs_diff"] for s in samples) < 1e-6
        else "review",
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

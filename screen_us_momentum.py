#!/usr/bin/env python3
"""
Screen US-listed common stocks by market cap, dollar volume, price, and 1-month return.

Data sources:
- Nasdaq screener API for current symbol snapshot, market cap, volume, sector/industry.
- Yahoo Finance via yfinance for daily adjusted close history.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
import yfinance as yf


NASDAQ_SCREENER_URL = (
    "https://api.nasdaq.com/api/screener/stocks"
    "?tableonly=true&limit=25&offset=0&download=true"
)

OUT_DIR = Path("data")
RAW_NASDAQ = OUT_DIR / "nasdaq_screener_raw.json"
FILTERED = OUT_DIR / "filtered_universe.csv"
RETURNS = OUT_DIR / "screen_results.csv"
TOP = OUT_DIR / "top_5pct_one_month_gainers.csv"
SUMMARY = OUT_DIR / "screen_summary.json"


COMMON_STOCK_HINTS = (
    "common stock",
    "ordinary shares",
    "common shares",
    "american depositary shares",
    "ads",
    "adr",
)

EXCLUDE_NAME_HINTS = (
    " etf",
    " etn",
    " fund",
    " trust",
    " warrant",
    " warrants",
    " right",
    " rights",
    " unit",
    " units",
    " preferred",
    " preference",
    " notes due",
    " senior notes",
    " bond",
    " debenture",
)

EXCLUDE_SYMBOL_SUFFIXES = (
    "W",
    "WS",
    "WT",
    "U",
    "R",
)


@dataclass(frozen=True)
class ScreenConfig:
    min_market_cap: float = 1_000_000_000
    min_dollar_volume: float = 20_000_000
    min_price: float = 3.0
    lookback_days: int = 31
    history_period: str = "2mo"
    min_history_trading_days: int = 15


def fetch_nasdaq_snapshot() -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.nasdaq.com",
        "Referer": "https://www.nasdaq.com/market-activity/stocks/screener",
    }
    resp = requests.get(NASDAQ_SCREENER_URL, headers=headers, timeout=45)
    resp.raise_for_status()
    return resp.json()


def parse_money(value: object) -> float:
    if value is None:
        return math.nan
    text = str(value).strip()
    if not text or text in {"N/A", "na", "nan", "--"}:
        return math.nan
    text = text.replace("$", "").replace(",", "").replace("%", "")
    try:
        return float(text)
    except ValueError:
        return math.nan


def normalize_symbol_for_yahoo(symbol: str) -> str:
    # Yahoo uses BRK-B/BF-B style where Nasdaq snapshot uses BRK/B or BRK.B variants.
    return symbol.strip().replace("/", "-").replace(".", "-")


def looks_like_common_equity(row: pd.Series) -> bool:
    symbol = str(row["symbol"]).upper().strip()
    name = f" {str(row.get('name', '')).lower()} "
    if row.get("assetType") not in (None, "", "Stock"):
        return False
    if bool(row.get("isEtf", False)):
        return False
    if any(hint in name for hint in EXCLUDE_NAME_HINTS):
        return False
    if symbol.endswith(EXCLUDE_SYMBOL_SUFFIXES) and not any(
        hint in name for hint in COMMON_STOCK_HINTS
    ):
        return False
    if "^" in symbol or "$" in symbol:
        return False
    return True


def snapshot_to_frame(snapshot: dict) -> pd.DataFrame:
    rows = snapshot["data"]["rows"]
    df = pd.DataFrame(rows)
    df["last_price"] = df["lastsale"].map(parse_money)
    df["market_cap"] = df["marketCap"].map(parse_money)
    df["volume"] = df["volume"].map(parse_money)
    df["dollar_volume"] = df["last_price"] * df["volume"]
    df["yf_symbol"] = df["symbol"].map(normalize_symbol_for_yahoo)
    df["is_common_equity"] = df.apply(looks_like_common_equity, axis=1)
    return df


def dedupe_symbols(df: pd.DataFrame) -> pd.DataFrame:
    # Keep the highest-dollar-volume line if Nasdaq returns duplicates.
    ordered = df.sort_values(["symbol", "dollar_volume"], ascending=[True, False])
    return ordered.drop_duplicates(subset=["symbol"], keep="first")


def filter_universe(df: pd.DataFrame, config: ScreenConfig) -> pd.DataFrame:
    filt = (
        df["is_common_equity"]
        & (df["last_price"] > config.min_price)
        & (df["market_cap"] >= config.min_market_cap)
        & (df["dollar_volume"] >= config.min_dollar_volume)
    )
    cols = [
        "symbol",
        "yf_symbol",
        "name",
        "last_price",
        "market_cap",
        "volume",
        "dollar_volume",
        "sector",
        "industry",
        "country",
        "ipoyear",
    ]
    return df.loc[filt, cols].sort_values("dollar_volume", ascending=False)


def chunked(items: list[str], size: int) -> Iterable[list[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _adj_close_frame(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        if "Adj Close" in raw.columns.get_level_values(0):
            return raw["Adj Close"]
        if "Close" in raw.columns.get_level_values(0):
            return raw["Close"]
    if "Adj Close" in raw.columns:
        return raw[["Adj Close"]].rename(columns={"Adj Close": raw.attrs.get("ticker", "UNKNOWN")})
    if "Close" in raw.columns:
        return raw[["Close"]].rename(columns={"Close": raw.attrs.get("ticker", "UNKNOWN")})
    return pd.DataFrame()


def download_history(symbols: list[str], config: ScreenConfig) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for idx, group in enumerate(chunked(symbols, 250), start=1):
        print(f"Downloading history chunk {idx}: {len(group)} symbols")
        raw = yf.download(
            " ".join(group),
            period=config.history_period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            group_by="column",
            threads=True,
        )
        close = _adj_close_frame(raw)
        if not close.empty:
            frames.append(close)
    if not frames:
        return pd.DataFrame()
    hist = pd.concat(frames, axis=1)
    hist = hist.loc[:, ~hist.columns.duplicated()]
    hist.index = pd.to_datetime(hist.index).tz_localize(None)
    return hist.sort_index()


def compute_returns(universe: pd.DataFrame, hist: pd.DataFrame, config: ScreenConfig) -> pd.DataFrame:
    latest_date = hist.dropna(how="all").index.max()
    start_target = latest_date - pd.Timedelta(days=config.lookback_days)

    rows = []
    by_yf = universe.set_index("yf_symbol", drop=False)
    for yf_symbol in universe["yf_symbol"].tolist():
        if yf_symbol not in hist.columns:
            continue
        series = hist[yf_symbol].dropna()
        series = series.loc[series.index <= latest_date]
        if len(series) < config.min_history_trading_days:
            continue
        latest_price = float(series.iloc[-1])
        latest_px_date = series.index[-1]
        prior_series = series.loc[series.index <= start_target]
        if prior_series.empty:
            continue
        start_price = float(prior_series.iloc[-1])
        start_px_date = prior_series.index[-1]
        if start_price <= 0 or latest_price <= 0:
            continue
        one_month_return = latest_price / start_price - 1.0
        meta = by_yf.loc[yf_symbol]
        rows.append(
            {
                "symbol": meta["symbol"],
                "yf_symbol": yf_symbol,
                "name": meta["name"],
                "sector": meta["sector"],
                "industry": meta["industry"],
                "country": meta["country"],
                "ipoyear": meta["ipoyear"],
                "market_cap": float(meta["market_cap"]),
                "nasdaq_last_price": float(meta["last_price"]),
                "nasdaq_volume": float(meta["volume"]),
                "nasdaq_dollar_volume": float(meta["dollar_volume"]),
                "start_date": start_px_date.date().isoformat(),
                "start_adj_close": start_price,
                "latest_date": latest_px_date.date().isoformat(),
                "latest_adj_close": latest_price,
                "one_month_return": one_month_return,
                "history_observations": int(len(series)),
            }
        )
    return pd.DataFrame(rows).sort_values("one_month_return", ascending=False)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    config = ScreenConfig()

    snapshot = fetch_nasdaq_snapshot()
    snapshot["_fetched_at_utc"] = datetime.now(timezone.utc).isoformat()
    RAW_NASDAQ.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    full = dedupe_symbols(snapshot_to_frame(snapshot))
    universe = filter_universe(full, config)
    universe.to_csv(FILTERED, index=False)

    hist = download_history(universe["yf_symbol"].tolist(), config)
    results = compute_returns(universe, hist, config)
    results.to_csv(RETURNS, index=False)

    cutoff = results["one_month_return"].quantile(0.95)
    top = results.loc[results["one_month_return"] >= cutoff].copy()
    top.to_csv(TOP, index=False)

    summary = {
        "run_date": date.today().isoformat(),
        "nasdaq_fetched_at_utc": snapshot["_fetched_at_utc"],
        "config": config.__dict__,
        "raw_rows": int(len(full)),
        "filtered_universe_rows": int(len(universe)),
        "results_with_history_rows": int(len(results)),
        "top_5pct_rows": int(len(top)),
        "return_95th_percentile_cutoff": float(cutoff),
        "latest_price_date": str(results["latest_date"].mode().iloc[0]) if not results.empty else None,
        "start_price_date_mode": str(results["start_date"].mode().iloc[0]) if not results.empty else None,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

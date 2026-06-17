#!/usr/bin/env python3
"""Prepare TradingView symbol specs for the screened ticker list."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd
import requests


DATA = Path("data")
TOP = DATA / "top_5pct_one_month_gainers.csv"
OUT = DATA / "tradingview_symbol_specs.csv"


OTHER_EXCHANGE_TO_TV = {
    "A": "AMEX",
    "N": "NYSE",
    "P": "NYSEARCA",
    "Z": "BATS",
    "V": "IEX",
}


def fetch_pipe_table(url: str) -> pd.DataFrame:
    text = requests.get(url, timeout=30).text
    lines = [line for line in text.splitlines() if not line.startswith("File Creation Time")]
    return pd.read_csv(StringIO("\n".join(lines)), sep="|")


def main() -> None:
    top = pd.read_csv(TOP)
    nasdaq = fetch_pipe_table("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt")
    other = fetch_pipe_table("https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt")

    exchange_by_symbol: dict[str, str] = {}
    for _, row in nasdaq.iterrows():
        if str(row.get("Test Issue", "N")) == "N":
            exchange_by_symbol[str(row["Symbol"])] = "NASDAQ"
    for _, row in other.iterrows():
        if str(row.get("Test Issue", "N")) == "N":
            code = str(row.get("Exchange", ""))
            exchange_by_symbol[str(row["ACT Symbol"])] = OTHER_EXCHANGE_TO_TV.get(code, code)

    rows = []
    for _, row in top.iterrows():
        symbol = str(row["symbol"])
        exchange = exchange_by_symbol.get(symbol, "")
        tv_symbol = symbol.replace(".", "-").replace("/", "-")
        rows.append(
            {
                "symbol": symbol,
                "exchange": exchange,
                "tv_spec": f"{exchange}:{tv_symbol}" if exchange else "",
                "name": row["name"],
                "screen_latest_adj_close": row["latest_adj_close"],
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()

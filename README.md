# momentum-swing-lab

Momentum and swing-trading research workspace for screening US-listed equities, analyzing short-term momentum cohorts, and keeping applied CAN SLIM study notes.

This repository is for education and research. It is not financial advice.

## Contents

- `screen_us_momentum.py` - builds a US common-stock universe from Nasdaq data and ranks names by one-month return using Yahoo Finance history.
- `analyze_screen.py` - summarizes the screen output by sector, industry, market cap, dollar volume, and top symbols.
- `verify_screen.py` - rechecks screen membership and sample returns against direct Yahoo chart data.
- `tradingview_close_check.py` - prepares TradingView symbol specs for the screened ticker list.
- `data/` - sample outputs from the momentum screen and verification pass.
- `obsidian/` - investing study notes and applied CAN SLIM learning routes.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python screen_us_momentum.py
python analyze_screen.py
python verify_screen.py
python tradingview_close_check.py
```

## Notes

The scripts use public web data sources and may need updates if those sources change their formats, rate limits, or access rules. Review all generated outputs before using them in any decision process.


# FPL Price & Fixture Tracker

A Python tool that pulls live player data from the official Fantasy
Premier League API and builds a report showing each player's price,
form, and ownership alongside their next 3 fixtures — color-coded by
difficulty, the same green-to-red scale used in the FPL app. It also
saves a daily price snapshot and flags who rose or fell in price since
the last run.

## What it does

1. **Fetches** live data from the official FPL API (players, teams, fixtures)
2. **Builds a player table** with price, form, ownership %, total points,
   and their next 3 upcoming fixtures
3. **Color-codes each fixture** by difficulty (1–5), matching the FPL app:
   dark green (very easy) → green → grey → red → dark red (very hard)
4. **Saves a daily price snapshot** to `data/price_history/`
5. **Compares today's snapshot to the most recent previous one** and
   lists every player whose price changed, on a separate sheet
6. **Outputs a formatted Excel report** with two sheets: `Players` and
   `Price Changes`

## Tech used

Python · requests · pandas · openpyxl · PyYAML

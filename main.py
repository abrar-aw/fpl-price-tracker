"""
FPL Price & Fixture Tracker
----------------------------
Fetches live player data from the official Fantasy Premier League API,
builds a report showing price, form, and ownership for every player
alongside their next few fixtures color-coded by difficulty (matching
the FPL app's green-to-red scale), and tracks day-to-day price changes
by saving a snapshot each time it runs.

Usage:
    python main.py              # fetch live data from the FPL API
    python main.py --sample     # use bundled sample data (no internet needed)
"""

import argparse
import logging
import sys

import yaml

import fpl_api
import price_tracker
import report_builder
from data_processor import build_player_dataframe, build_team_lookup, build_upcoming_fixtures_by_team

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fpl_tracker")


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="FPL Price & Fixture Tracker")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use bundled sample data instead of calling the live FPL API",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        num_fixtures = config["num_fixtures"]

        if args.sample:
            log.info("Using bundled sample data (offline mode)")
            bootstrap = fpl_api.load_sample_bootstrap("sample_data/bootstrap_sample.json")
            fixtures = fpl_api.load_sample_fixtures("sample_data/fixtures_sample.json")
        else:
            log.info("Fetching live data from the FPL API...")
            bootstrap = fpl_api.fetch_bootstrap_static()
            fixtures = fpl_api.fetch_fixtures()

        log.info(f"Loaded {len(bootstrap['elements'])} players, {len(fixtures)} fixtures")

        team_lookup = build_team_lookup(bootstrap["teams"])
        fixtures_by_team = build_upcoming_fixtures_by_team(fixtures, num_fixtures)
        player_df = build_player_dataframe(bootstrap, fixtures_by_team, team_lookup, num_fixtures)

        snapshot_path = price_tracker.save_snapshot(player_df, config["price_history_dir"])
        log.info(f"Saved today's price snapshot to {snapshot_path}")

        changes_df = price_tracker.detect_price_changes(
            player_df, config["price_history_dir"], config["min_price_change"]
        )
        if not changes_df.empty:
            log.info(f"Detected {len(changes_df)} price change(s) since last run")
        else:
            log.info("No price changes detected (or no previous snapshot to compare against)")

        report_builder.build_report(player_df, changes_df, config["output_file"], num_fixtures)
        log.info(f"Report saved to {config['output_file']}")
        log.info("Done.")

    except Exception as e:
        log.error(f"Run failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

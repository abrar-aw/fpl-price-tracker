"""
Thin wrapper around the official Fantasy Premier League API.

The FPL API is free, public, and needs no authentication:
    https://fantasy.premierleague.com/api/bootstrap-static/  -> players, teams, positions
    https://fantasy.premierleague.com/api/fixtures/           -> full fixture list + difficulty ratings
"""

import json

import requests

BASE_URL = "https://fantasy.premierleague.com/api"


def fetch_bootstrap_static() -> dict:
    """Players, teams, positions - the core FPL dataset."""
    resp = requests.get(f"{BASE_URL}/bootstrap-static/", timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_fixtures() -> list:
    """Every fixture in the season, including difficulty ratings (1-5)."""
    resp = requests.get(f"{BASE_URL}/fixtures/", timeout=15)
    resp.raise_for_status()
    return resp.json()


def load_sample_bootstrap(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def load_sample_fixtures(path: str) -> list:
    with open(path, "r") as f:
        return json.load(f)

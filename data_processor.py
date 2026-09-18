"""Transforms raw FPL API data into a clean, analysis-ready table."""

import pandas as pd

POSITION_MAP = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}


def build_team_lookup(teams: list) -> dict:
    """{team_id: short_name}, e.g. {1: 'ARS'}"""
    return {t["id"]: t["short_name"] for t in teams}


def build_upcoming_fixtures_by_team(fixtures: list, num_fixtures: int = 3) -> dict:
    """Returns {team_id: [ {opponent_id, difficulty, venue, event}, ... ]}
    with each team's next `num_fixtures` unfinished matches, in order."""
    upcoming = [f for f in fixtures if not f.get("finished") and f.get("event") is not None]
    upcoming.sort(key=lambda f: (f["event"], f.get("kickoff_time") or ""))

    by_team: dict = {}
    for f in upcoming:
        for side, opp_side, diff_key in [
            ("team_h", "team_a", "team_h_difficulty"),
            ("team_a", "team_h", "team_a_difficulty"),
        ]:
            team_id = f[side]
            by_team.setdefault(team_id, [])
            if len(by_team[team_id]) < num_fixtures:
                by_team[team_id].append(
                    {
                        "opponent_id": f[opp_side],
                        "difficulty": f[diff_key],
                        "venue": "H" if side == "team_h" else "A",
                        "event": f["event"],
                    }
                )
    return by_team


def build_player_dataframe(
    bootstrap: dict, fixtures_by_team: dict, team_lookup: dict, num_fixtures: int = 3
) -> pd.DataFrame:
    """One row per player: price, form, ownership, points, and their next
    N fixtures with opponent + difficulty (for color-coding later)."""
    rows = []
    for p in bootstrap["elements"]:
        team_id = p["team"]
        team_fixtures = fixtures_by_team.get(team_id, [])

        row = {
            "Player": p["web_name"],
            "Team": team_lookup.get(team_id, "?"),
            "Position": POSITION_MAP.get(p["element_type"], "?"),
            "Price": p["now_cost"] / 10,
            "Form": float(p["form"]) if p.get("form") else 0.0,
            "Selected By %": float(p["selected_by_percent"]) if p.get("selected_by_percent") else 0.0,
            "Total Points": p["total_points"],
            "Status": p["status"],
        }

        for i in range(num_fixtures):
            if i < len(team_fixtures):
                fx = team_fixtures[i]
                opponent = team_lookup.get(fx["opponent_id"], "?")
                row[f"Fixture {i + 1}"] = f"{opponent} ({fx['venue']})"
                row[f"Fixture {i + 1} FDR"] = fx["difficulty"]
            else:
                row[f"Fixture {i + 1}"] = ""
                row[f"Fixture {i + 1} FDR"] = None

        rows.append(row)

    df = pd.DataFrame(rows)
    return df.sort_values("Form", ascending=False).reset_index(drop=True)

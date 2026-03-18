from __future__ import annotations

import csv
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from cricket_scoring.models import DeliveryRecord, InningsState, MatchSetup, TeamRoster
from cricket_scoring.sheets import REQUIRED_COLUMNS


class LocalStoreError(Exception):
    """Raised for local scoring store errors."""


class LocalScoringStore:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or os.getenv("LOCAL_SCORING_DIR", ".local_scoring"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.latest_match_path = self.base_dir / "latest_match.json"
        self.snapshot_path = self.base_dir / "app_snapshot.json"

    def _match_csv_path(self, match_id: str) -> Path:
        return self.base_dir / f"match_{match_id}.csv"

    def set_latest_match(self, match_id: str) -> None:
        self.latest_match_path.write_text(json.dumps({"match_id": match_id}), encoding="utf-8")

    def get_latest_match(self) -> str | None:
        if not self.latest_match_path.exists():
            return None
        try:
            data = json.loads(self.latest_match_path.read_text(encoding="utf-8"))
            return data.get("match_id")
        except json.JSONDecodeError:
            return None

    def initialize_match_csv(self, match_id: str) -> Path:
        csv_path = self._match_csv_path(match_id)
        if not csv_path.exists():
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(REQUIRED_COLUMNS)
        self.set_latest_match(match_id)
        return csv_path

    def append_delivery(self, record: DeliveryRecord) -> Path:
        csv_path = self.initialize_match_csv(record.match_id)
        record_dict = asdict(record)
        row = [record_dict[key] for key in REQUIRED_COLUMNS]
        with csv_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(row)
        return csv_path

    def read_deliveries(self, match_id: str) -> list[dict[str, Any]]:
        csv_path = self._match_csv_path(match_id)
        if not csv_path.exists():
            return []
        with csv_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return list(reader)

    def get_csv_bytes(self, match_id: str) -> bytes:
        csv_path = self._match_csv_path(match_id)
        if not csv_path.exists():
            raise LocalStoreError("No local CSV file found for this match.")
        return csv_path.read_bytes()

    def snapshot_state(self, payload: dict[str, Any]) -> None:
        self.snapshot_path.write_text(json.dumps(payload), encoding="utf-8")

    def load_snapshot(self) -> dict[str, Any] | None:
        if not self.snapshot_path.exists():
            return None
        try:
            return json.loads(self.snapshot_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None


def innings_state_to_dict(state: InningsState) -> dict[str, Any]:
    return {
        "match": {
            "match_id": state.match.match_id,
            "innings_no": state.match.innings_no,
            "batting_team": {
                "name": state.match.batting_team.name,
                "players": state.match.batting_team.players,
            },
            "bowling_team": {
                "name": state.match.bowling_team.name,
                "players": state.match.bowling_team.players,
            },
        },
        "striker": state.striker,
        "non_striker": state.non_striker,
        "current_bowler": state.current_bowler,
        "over_no": state.over_no,
        "legal_balls_in_over": state.legal_balls_in_over,
        "delivery_seq": state.delivery_seq,
        "total_runs": state.total_runs,
        "total_wickets": state.total_wickets,
        "batter_runs": state.batter_runs,
        "requires_bowler_selection": state.requires_bowler_selection,
    }


def innings_state_from_dict(data: dict[str, Any]) -> InningsState:
    match_data = data["match"]
    match = MatchSetup(
        match_id=match_data["match_id"],
        innings_no=match_data["innings_no"],
        batting_team=TeamRoster(
            name=match_data["batting_team"]["name"],
            players=list(match_data["batting_team"]["players"]),
        ),
        bowling_team=TeamRoster(
            name=match_data["bowling_team"]["name"],
            players=list(match_data["bowling_team"]["players"]),
        ),
    )
    return InningsState(
        match=match,
        striker=data["striker"],
        non_striker=data["non_striker"],
        current_bowler=data.get("current_bowler"),
        over_no=int(data["over_no"]),
        legal_balls_in_over=int(data["legal_balls_in_over"]),
        delivery_seq=int(data["delivery_seq"]),
        total_runs=int(data["total_runs"]),
        total_wickets=int(data["total_wickets"]),
        batter_runs={k: int(v) for k, v in data["batter_runs"].items()},
        requires_bowler_selection=bool(data["requires_bowler_selection"]),
    )

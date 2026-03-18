from __future__ import annotations

from pathlib import Path

from cricket_scoring.local_store import LocalScoringStore, innings_state_from_dict, innings_state_to_dict
from cricket_scoring.models import DeliveryRecord, create_initial_state


def _delivery_record(match_id: str) -> DeliveryRecord:
    return DeliveryRecord(
        match_id=match_id,
        innings_no=1,
        over_no=1,
        ball_in_over_legal=1,
        delivery_seq=1,
        batting_team="Team-1",
        bowling_team="Team-2",
        striker="player-1",
        non_striker="player-2",
        bowler="player-4",
        batter_runs=1,
        extra_type="none",
        extra_runs=0,
        total_runs_on_ball=1,
        is_legal_ball=True,
        over_completed=False,
        team_total_runs=1,
        team_total_wickets=0,
        timestamp_utc="2026-03-18T00:00:00+00:00",
    )


def test_append_read_and_export_csv(tmp_path: Path):
    store = LocalScoringStore(base_dir=str(tmp_path))
    record = _delivery_record("match-1")

    csv_path = store.append_delivery(record)
    rows = store.read_deliveries("match-1")
    csv_bytes = store.get_csv_bytes("match-1")

    assert csv_path.exists()
    assert len(rows) == 1
    assert rows[0]["match_id"] == "match-1"
    assert b"match_id" in csv_bytes
    assert b"match-1" in csv_bytes


def test_snapshot_and_restore_state(tmp_path: Path):
    store = LocalScoringStore(base_dir=str(tmp_path))
    state = create_initial_state(
        batting_team_name="Team-1",
        batting_players=["player-1", "player-2", "player-3"],
        bowling_team_name="Team-2",
        bowling_players=["player-4", "player-5", "player-6"],
        striker="player-1",
        non_striker="player-2",
    )

    payload = {
        "auth_mode": "local-csv-fallback",
        "innings_state": innings_state_to_dict(state),
        "deliveries": [{"delivery_seq": 1}],
    }
    store.snapshot_state(payload)

    loaded = store.load_snapshot()
    assert loaded is not None
    assert loaded["auth_mode"] == "local-csv-fallback"

    roundtrip_state = innings_state_from_dict(loaded["innings_state"])
    assert roundtrip_state.match.match_id == state.match.match_id
    assert roundtrip_state.striker == state.striker

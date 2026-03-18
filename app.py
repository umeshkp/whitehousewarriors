from __future__ import annotations

import os
from dataclasses import asdict
from typing import Any

import streamlit as st

from cricket_scoring.auth import AUTH_MODE_GOOGLE, AUTH_MODE_LOCAL, GoogleAuthManager, credentials_from_session
from cricket_scoring.config import AppConfig
from cricket_scoring.engine import apply_delivery
from cricket_scoring.local_store import LocalScoringStore, innings_state_from_dict, innings_state_to_dict
from cricket_scoring.models import DeliveryInput, InningsState, ValidationError, create_initial_state
from cricket_scoring.sheets import GSpreadSheetsService, InMemorySheetsService, REQUIRED_COLUMNS, SheetsServiceError


def _parse_players(raw: str) -> list[str]:
    players = [line.strip() for line in raw.splitlines() if line.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for player in players:
        if player not in seen:
            seen.add(player)
            deduped.append(player)
    return deduped


def _get_state() -> InningsState | None:
    return st.session_state.get("innings_state")


def _set_state(state: InningsState | None) -> None:
    if state is None:
        st.session_state.pop("innings_state", None)
        return
    st.session_state["innings_state"] = state


def _get_local_store() -> LocalScoringStore:
    if "local_store" not in st.session_state:
        st.session_state["local_store"] = LocalScoringStore()
    return st.session_state["local_store"]


def _snapshot_app_state() -> None:
    store = _get_local_store()
    innings_state = _get_state()
    payload: dict[str, Any] = {
        "team1_name": st.session_state.get("team1_name"),
        "team2_name": st.session_state.get("team2_name"),
        "team1_players": st.session_state.get("team1_players"),
        "team2_players": st.session_state.get("team2_players"),
        "team1_players_list": st.session_state.get("team1_players_list"),
        "team2_players_list": st.session_state.get("team2_players_list"),
        "deliveries": st.session_state.get("deliveries", []),
        "auth_mode": st.session_state.get("auth_mode", AUTH_MODE_LOCAL),
        "sheet_url": st.session_state.get("sheet_url", ""),
        "sheet_ready": bool(st.session_state.get("sheet_ready", False)),
        "local_match_id": st.session_state.get("local_match_id"),
        "match_ended": bool(st.session_state.get("match_ended", False)),
        "innings_state": innings_state_to_dict(innings_state) if innings_state else None,
    }
    store.snapshot_state(payload)


def _restore_snapshot_once() -> None:
    if st.session_state.get("snapshot_restored"):
        return
    st.session_state["snapshot_restored"] = True

    snapshot = _get_local_store().load_snapshot()
    if not snapshot:
        return

    for key in (
        "team1_name",
        "team2_name",
        "team1_players",
        "team2_players",
        "team1_players_list",
        "team2_players_list",
        "deliveries",
        "sheet_url",
        "sheet_ready",
        "local_match_id",
        "match_ended",
    ):
        if key in snapshot and key not in st.session_state:
            st.session_state[key] = snapshot[key]

    if "auth_mode" in snapshot and "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = snapshot["auth_mode"]

    if snapshot.get("innings_state") and "innings_state" not in st.session_state:
        try:
            st.session_state["innings_state"] = innings_state_from_dict(snapshot["innings_state"])
        except Exception:
            pass


def _get_sheets_service(config: AppConfig):
    if os.getenv("USE_IN_MEMORY_SHEETS", "false").lower() == "true":
        if "in_memory_sheet_service" not in st.session_state:
            st.session_state["in_memory_sheet_service"] = InMemorySheetsService()
        return st.session_state["in_memory_sheet_service"]

    credentials = credentials_from_session(st.session_state)
    return GSpreadSheetsService(credentials)


def render_auth(config: AppConfig) -> str:
    st.subheader("Login")
    auth_manager = GoogleAuthManager(config)
    mode = auth_manager.render_login_controls()
    st.session_state["auth_mode"] = mode
    return mode


def render_mode_indicator(mode: str) -> None:
    if mode == AUTH_MODE_GOOGLE:
        st.info("Scoring mode: Google-authenticated")
    else:
        st.info("Scoring mode: Local CSV fallback")


def render_team_setup(mode: str) -> None:
    st.subheader("Team Setup")

    with st.form("team_setup_form"):
        col1, col2 = st.columns(2)
        with col1:
            team1_name = st.text_input("Team 1 Name", value=st.session_state.get("team1_name", "Team-1"))
            team1_players = st.text_area(
                "Team 1 Players (one per line)",
                value=st.session_state.get("team1_players", ""),
                height=180,
            )
        with col2:
            team2_name = st.text_input("Team 2 Name", value=st.session_state.get("team2_name", "Team-2"))
            team2_players = st.text_area(
                "Team 2 Players (one per line)",
                value=st.session_state.get("team2_players", ""),
                height=180,
            )

        submitted = st.form_submit_button("Save Teams")
        if submitted:
            t1 = _parse_players(team1_players)
            t2 = _parse_players(team2_players)
            if len(t1) < 2 or len(t2) < 1:
                st.error("Team 1 needs at least 2 players and Team 2 needs at least 1 player.")
                return
            st.session_state.update(
                {
                    "team1_name": team1_name.strip() or "Team-1",
                    "team2_name": team2_name.strip() or "Team-2",
                    "team1_players": "\n".join(t1),
                    "team2_players": "\n".join(t2),
                    "team1_players_list": t1,
                    "team2_players_list": t2,
                }
            )
            _snapshot_app_state()
            st.success("Teams saved.")

    team1_players = st.session_state.get("team1_players_list", [])
    team2_players = st.session_state.get("team2_players_list", [])
    if not team1_players or not team2_players:
        return

    st.markdown("### Start Innings")
    innings_col1, innings_col2 = st.columns(2)
    with innings_col1:
        batting_choice = st.selectbox("Batting Team", options=["Team 1", "Team 2"], key="batting_side")
    with innings_col2:
        bowling_choice = "Team 2" if batting_choice == "Team 1" else "Team 1"
        st.text_input("Bowling Team", value=bowling_choice, disabled=True)

    if batting_choice == "Team 1":
        batting_team_name = st.session_state["team1_name"]
        batting_players = team1_players
        bowling_team_name = st.session_state["team2_name"]
        bowling_players = team2_players
    else:
        batting_team_name = st.session_state["team2_name"]
        batting_players = team2_players
        bowling_team_name = st.session_state["team1_name"]
        bowling_players = team1_players

    striker = st.selectbox("Initial Striker", options=batting_players, key="initial_striker")
    non_striker_options = [p for p in batting_players if p != striker]
    non_striker = st.selectbox("Initial Non-Striker", options=non_striker_options, key="initial_non_striker")

    if st.button("Start Scoring", use_container_width=True):
        try:
            innings_state = create_initial_state(
                batting_team_name=batting_team_name,
                batting_players=batting_players,
                bowling_team_name=bowling_team_name,
                bowling_players=bowling_players,
                striker=striker,
                non_striker=non_striker,
            )
            _set_state(innings_state)
            st.session_state["deliveries"] = []
            st.session_state["match_ended"] = False
            if mode == AUTH_MODE_LOCAL:
                _get_local_store().initialize_match_csv(innings_state.match.match_id)
                st.session_state["local_match_id"] = innings_state.match.match_id
            _snapshot_app_state()
            st.success("Innings initialized.")
        except ValidationError as exc:
            st.error(str(exc))


def render_sheet_config(config: AppConfig, mode: str) -> None:
    if mode != AUTH_MODE_GOOGLE:
        return

    st.subheader("Google Sheet")
    sheet_url = st.text_input("Shared Google Sheet URL", value=st.session_state.get("sheet_url", config.google_sheet_url))
    st.session_state["sheet_url"] = sheet_url.strip()
    st.caption("Required columns: " + ", ".join(REQUIRED_COLUMNS))

    if st.button("Validate Sheet Access"):
        try:
            service = _get_sheets_service(config)
            if isinstance(service, InMemorySheetsService):
                service.allow_url(st.session_state["sheet_url"])
            service.validate_sheet(st.session_state["sheet_url"])
            st.session_state["sheet_ready"] = True
            _snapshot_app_state()
            st.success("Google Sheet is ready for scoring persistence.")
        except (SheetsServiceError, ValidationError) as exc:
            st.session_state["sheet_ready"] = False
            _snapshot_app_state()
            st.error(str(exc))


def render_scoreboard(state: InningsState) -> None:
    st.subheader("Live Score")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Runs", state.total_runs)
    col2.metric("Wickets", state.total_wickets)
    col3.metric("Over", f"{state.over_no}.{state.legal_balls_in_over}")
    col4.metric("Current Bowler", state.current_bowler or "Select for over")
    st.write(f"Striker: **{state.striker}** | Non-striker: **{state.non_striker}**")


def render_delivery_entry(config: AppConfig, mode: str) -> None:
    state = _get_state()
    if state is None:
        st.info("Complete team setup and start innings to begin scoring.")
        return

    render_scoreboard(state)

    if mode == AUTH_MODE_GOOGLE and not st.session_state.get("sheet_ready"):
        st.warning("Validate Google Sheet access before submitting deliveries.")
        return

    bowling_options = state.match.bowling_team.players
    batting_options = state.match.batting_team.players

    st.markdown("### Delivery Entry")
    if state.requires_bowler_selection:
        st.info("New over started. Select a bowler before submitting the next ball.")

    with st.form("delivery_form"):
        default_bowler = state.current_bowler if state.current_bowler else bowling_options[0]
        bowler = st.selectbox("Bowler", options=bowling_options, index=bowling_options.index(default_bowler))

        striker = st.selectbox("Striker", options=batting_options, index=batting_options.index(state.striker))
        non_striker_candidates = [p for p in batting_options if p != striker]
        non_striker_default = state.non_striker if state.non_striker in non_striker_candidates else non_striker_candidates[0]
        non_striker = st.selectbox(
            "Non-striker",
            options=non_striker_candidates,
            index=non_striker_candidates.index(non_striker_default),
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            batter_runs = st.number_input("Batter runs", min_value=0, max_value=6, step=1, value=0)
        with col2:
            extra_type = st.selectbox("Extra type", options=["none", "wide", "no-ball"])
        with col3:
            extra_runs = st.number_input("Extra runs", min_value=0, max_value=6, step=1, value=0)

        wicket = st.checkbox("Wicket on this ball")
        submitted = st.form_submit_button("Submit delivery", use_container_width=True)

    if not submitted:
        _render_delivery_log_and_download(mode, state)
        return

    try:
        delivery = DeliveryInput(
            striker=striker,
            non_striker=non_striker,
            bowler=bowler,
            batter_runs=int(batter_runs),
            extra_type=extra_type,
            extra_runs=int(extra_runs),
            is_wicket=wicket,
        )
        next_state, record = apply_delivery(state, delivery)

        if mode == AUTH_MODE_GOOGLE:
            sheets_service = _get_sheets_service(config)
            sheets_service.append_delivery(st.session_state["sheet_url"], record)
        else:
            _get_local_store().append_delivery(record)
            st.session_state["local_match_id"] = record.match_id

        _set_state(next_state)
        st.session_state.setdefault("deliveries", []).append(asdict(record))
        _snapshot_app_state()
        st.success("Delivery saved.")
    except (ValidationError, SheetsServiceError) as exc:
        st.error(str(exc))

    _render_delivery_log_and_download(mode, _get_state())


def _render_delivery_log_and_download(mode: str, state: InningsState | None) -> None:
    deliveries = st.session_state.get("deliveries", [])
    if deliveries:
        st.markdown("### Delivery Log")
        st.dataframe(deliveries, use_container_width=True)

    if mode != AUTH_MODE_LOCAL or not deliveries:
        return

    if not st.session_state.get("match_ended"):
        if st.button("End Match", key="end-match", use_container_width=True):
            st.session_state["match_ended"] = True
            _snapshot_app_state()
            st.rerun()
        return

    match_id = st.session_state.get("local_match_id")
    if not match_id and state:
        match_id = state.match.match_id
    if not match_id:
        return

    csv_bytes = _get_local_store().get_csv_bytes(match_id)
    st.download_button(
        "Download Scoring CSV",
        data=csv_bytes,
        file_name=f"match_{match_id}.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(page_title="Cricket Scoring", layout="wide")
    st.title("Whitehouse Warriors Cricket Scoring")

    config = AppConfig.from_env()
    startup_errors = config.validate_startup()
    if startup_errors:
        for err in startup_errors:
            st.error(err)
        st.stop()

    _restore_snapshot_once()
    mode = render_auth(config)
    render_mode_indicator(mode)
    render_team_setup(mode)
    render_sheet_config(config, mode)
    render_delivery_entry(config, mode)


if __name__ == "__main__":
    main()

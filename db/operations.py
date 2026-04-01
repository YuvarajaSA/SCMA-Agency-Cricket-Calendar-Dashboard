# db/operations.py
# ──────────────────────────────────────────────────────────────
#  All Supabase read / write operations.
#  Uses the authenticated client (RLS enforced server-side).
# ──────────────────────────────────────────────────────────────

from __future__ import annotations

import pandas as pd
import streamlit as st
from datetime import date
from postgrest.exceptions import APIError

from db.supabase_client import get_client


# ═══════════════════════════════════════════════════════════════
#  READ HELPERS  (cached for performance on large datasets)
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=60, show_spinner=False)
def load_events(gender: str | None = None, category: str | None = None) -> pd.DataFrame:
    sb = get_client()
    q  = sb.table("events").select("*").order("start_date")
    if gender:
        q = q.eq("gender", gender)
    if category:
        q = q.eq("category", category)
    df = pd.DataFrame(q.execute().data)
    if not df.empty:
        df["start_date"] = pd.to_datetime(df["start_date"])
        df["end_date"]   = pd.to_datetime(df["end_date"])
    return df


@st.cache_data(ttl=60, show_spinner=False)
def load_teams() -> pd.DataFrame:
    sb   = get_client()
    resp = sb.table("teams").select("*").execute()
    return pd.DataFrame(resp.data)


@st.cache_data(ttl=60, show_spinner=False)
def load_squad() -> pd.DataFrame:
    sb   = get_client()
    resp = sb.table("squad").select("*").order("start_date").execute()
    df   = pd.DataFrame(resp.data)
    if not df.empty:
        df["start_date"] = pd.to_datetime(df["start_date"])
        df["end_date"]   = pd.to_datetime(df["end_date"])
    return df


def search_events(query: str, year: int | None = None) -> pd.DataFrame:
    """Full-text search across event_name, country, format, category."""
    sb   = get_client()
    resp = sb.table("events").select("*").ilike("event_name", f"%{query}%").execute()
    df   = pd.DataFrame(resp.data)
    if not df.empty:
        df["start_date"] = pd.to_datetime(df["start_date"])
        df["end_date"]   = pd.to_datetime(df["end_date"])
        if year:
            df = df[
                (df["start_date"].dt.year == year) |
                (df["end_date"].dt.year   == year)
            ]
    return df


def event_names() -> list[str]:
    df = load_events()
    return df["event_name"].tolist() if not df.empty else []


def teams_for_event(event_name: str) -> list[str]:
    df = load_teams()
    if df.empty:
        return []
    return df[df["event_name"] == event_name]["team_name"].tolist()


# ═══════════════════════════════════════════════════════════════
#  WRITE HELPERS
# ═══════════════════════════════════════════════════════════════

def add_event(
    name: str,
    etype: str,
    category: str,
    fmt: str,
    start: date,
    end: date,
    country: str,
    gender: str,
    notes: str = "",
    user_id: str | None = None,
) -> tuple[bool, str]:
    sb = get_client()
    try:
        payload = {
            "event_name": name,
            "event_type": etype,
            "category":   category,
            "format":     fmt,
            "start_date": str(start),
            "end_date":   str(end),
            "country":    country,
            "gender":     gender,
            "notes":      notes,
        }
        if user_id:
            payload["created_by"] = user_id
        sb.table("events").insert(payload).execute()
        load_events.clear()
        return True, f"✅ Event **{name}** added successfully!"
    except APIError as e:
        if "unique" in str(e).lower() or "23505" in str(e):
            return False, f"Event **{name}** already exists."
        return False, f"Database error: {e}"


def update_event(event_id: int, payload: dict) -> tuple[bool, str]:
    sb = get_client()
    try:
        sb.table("events").update(payload).eq("id", event_id).execute()
        return True, "Event updated."
    except APIError as e:
        return False, str(e)


def delete_event(event_id: int) -> tuple[bool, str]:
    sb = get_client()
    try:
        sb.table("events").delete().eq("id", event_id).execute()
        return True, "Event deleted."
    except APIError as e:
        return False, str(e)


def add_team(event_name: str, team_name: str) -> tuple[bool, str]:
    sb = get_client()
    try:
        sb.table("teams").insert({
            "event_name": event_name,
            "team_name":  team_name,
        }).execute()
        load_teams.clear()
        return True, f"✅ **{team_name}** added to *{event_name}*."
    except APIError as e:
        if "unique" in str(e).lower() or "23505" in str(e):
            return False, f"**{team_name}** already in *{event_name}*."
        return False, f"Database error: {e}"


def add_teams_bulk(event_name: str, team_names: list[str]) -> tuple[int, list[str]]:
    """Insert multiple teams for one event. Returns (success_count, warnings)."""
    ok_count = 0
    warns    = []
    for t in team_names:
        t = t.strip()
        if not t:
            continue
        ok, msg = add_team(event_name, t)
        if ok:
            ok_count += 1
        else:
            warns.append(msg)
    return ok_count, warns


def add_player_to_squad(player: str, event_name: str, team: str) -> tuple[bool, str]:
    sb = get_client()
    resp = (
        sb.table("events")
        .select("*")
        .eq("event_name", event_name)
        .single()
        .execute()
    )
    ev = resp.data
    try:
        sb.table("squad").insert({
            "player_name": player.strip(),
            "event_name":  event_name,
            "event_type":  ev["event_type"],
            "category":    ev["category"],
            "format":      ev["format"],
            "start_date":  ev["start_date"],
            "end_date":    ev["end_date"],
            "team":        team,
            "gender":      ev["gender"],
            "country":     ev["country"],
        }).execute()
        load_squad.clear()
        return True, f"✅ **{player}** added to {team} / {event_name}."
    except APIError as e:
        if "unique" in str(e).lower() or "23505" in str(e):
            return False, f"**{player}** already in {team} / {event_name}."
        return False, f"Database error: {e}"


def bulk_add_players(
    players: list[str], event_name: str, team: str
) -> tuple[int, list[str]]:
    success, warns = 0, []
    for p in players:
        ok, msg = add_player_to_squad(p, event_name, team)
        if ok:
            success += 1
        else:
            warns.append(msg)
    return success, warns

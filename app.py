# app.py
# ══════════════════════════════════════════════════════════════
#  Cricket Availability Dashboard  v2
#
#  AUTH ORDER — THIS ORDER IS NON-NEGOTIABLE:
#
#    1. handle_oauth_callback()   ← must be FIRST
#       Reads ?access_token= from URL (put there by JS hash reader)
#       and calls set_session() to establish auth.
#
#    2. hydrate_session()         ← must be SECOND
#       On every Streamlit rerun st.session_state is empty.
#       This restores auth_user from the cached Supabase client.
#
#    3. is_logged_in()            ← now safe to check
#       Returns True if auth_user is in session_state.
#
#    4. Show login page OR dashboard
# ══════════════════════════════════════════════════════════════

import streamlit as st

# ── Page config — MUST be the very first Streamlit call ───────
st.set_page_config(
    page_title="Cricket Availability Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────
from config.styles import inject
inject()

# ── AUTH STEP 1: Handle OAuth callback ───────────────────────
# Exchange tokens from URL query params into a Supabase session.
# MUST run before is_logged_in() — it populates auth_user.
from db.auth import (
    handle_oauth_callback,
    hydrate_session,
    is_logged_in,
    logout,
    current_email,
    get_role,
    can_edit,
    is_admin,
)

just_logged_in = handle_oauth_callback()

# ── AUTH STEP 2: Restore session on every rerun ───────────────
# st.session_state is empty after every Streamlit rerun.
# hydrate_session() asks the cached Supabase client for its
# stored session and writes it back into session_state.
hydrate_session()

# ── AUTH STEP 3: Gate ─────────────────────────────────────────
if not is_logged_in():
    from views.login import render as login_page
    login_page()
    st.stop()

# ── Welcome toast on fresh OAuth login ───────────────────────
if just_logged_in:
    st.toast(f"👋 Welcome, {current_email()}!", icon="✅")

# ── Page imports (only after auth passes) ─────────────────────
from views import (
    dashboard, calendar_view, search,
    add_event, add_team, add_squad,
    conflicts, availability, timeline, admin,
)
from db.operations import load_events, load_teams, load_squad
from utils.conflicts import detect_event_overlaps, detect_player_conflicts

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:

    # Brand
    st.markdown("""
    <div style="padding:1.1rem 0 1.3rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                    color:#f0b429;letter-spacing:.06em;line-height:1;">
            🏏 CRICKET
        </div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:.78rem;
                    color:#8b949e;letter-spacing:.18em;margin-top:.1rem;">
            AVAILABILITY DASHBOARD
        </div>
    </div>
    """, unsafe_allow_html=True)

    # User info + role pill
    role      = get_role()
    role_cls  = {"admin":"role-admin","editor":"role-editor","viewer":"role-viewer"}.get(role, "role-viewer")
    role_icon = {"admin":"👑","editor":"✏️","viewer":"👁"}.get(role, "👁")
    email     = current_email()

    st.markdown(f"""
    <div style="background:#1c2128;border:1px solid #30363d;border-radius:10px;
                padding:.7rem .9rem;margin-bottom:1rem;">
        <div style="font-size:.7rem;color:#8b949e;overflow:hidden;
                    text-overflow:ellipsis;white-space:nowrap;
                    margin-bottom:.35rem;">{email}</div>
        <span class="role-pill {role_cls}">{role_icon} {role}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation — items shown based on role
    nav_options = [
        "📊  Dashboard",
        "📅  Calendar",
        "🔍  Search",
        "⚠️  Conflicts",
        "🧑  Availability",
        "📈  Timeline",
    ]
    if can_edit():
        nav_options += ["➕  Add Event", "🏟  Add Team", "👥  Add Squad"]
    if is_admin():
        nav_options += ["🛡  Admin"]

    page = st.radio("NAVIGATE", nav_options)

    st.markdown("---")

    # Live stats (uses cached db calls)
    events_df = load_events()
    teams_df  = load_teams()
    squad_df  = load_squad()

    total_events  = len(events_df)
    total_teams   = teams_df["team_name"].nunique() if not teams_df.empty else 0
    total_players = squad_df["player_name"].nunique() if not squad_df.empty else 0
    eo = detect_event_overlaps(events_df)
    pc = detect_player_conflicts(squad_df)

    stat_rows = "".join(
        f'<div style="background:#1c2128;border:1px solid #30363d;border-radius:8px;'
        f'padding:.45rem .85rem;display:flex;align-items:center;gap:.75rem;">'
        f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.35rem;'
        f'color:{c};min-width:1.8rem;text-align:right;">{v}</span>'
        f'<span style="font-size:.68rem;font-weight:700;letter-spacing:.07em;'
        f'text-transform:uppercase;color:#8b949e;">{l}</span></div>'
        for v, l, c in [
            (total_events,  "Events",          "#f0b429"),
            (total_teams,   "Teams",            "#3fb950"),
            (total_players, "Players",          "#58a6ff"),
            (len(eo), "Date Conflicts",   "#f85149" if eo else "#3fb950"),
            (len(pc), "Player Conflicts", "#f85149" if pc else "#3fb950"),
        ]
    )
    st.markdown(f"""
    <div style="font-size:.6rem;font-weight:800;letter-spacing:.14em;
                text-transform:uppercase;color:#8b949e;margin-bottom:.6rem;">
        QUICK STATS
    </div>
    <div style="display:flex;flex-direction:column;gap:.35rem;">
        {stat_rows}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪  Log Out", use_container_width=True, key="logout_btn"):
        logout()
        st.rerun()

    st.markdown("""
    <div style="font-size:.62rem;color:#8b949e;margin-top:.7rem;
                line-height:1.7;text-align:center;">
        Powered by <b style="color:#f0b429;">Supabase</b> + Streamlit<br>
        🔒 Internal use only
    </div>
    """, unsafe_allow_html=True)


# ── Page router ───────────────────────────────────────────────
ROUTES = {
    "📊  Dashboard":    dashboard.render,
    "📅  Calendar":     calendar_view.render,
    "🔍  Search":       search.render,
    "⚠️  Conflicts":    conflicts.render,
    "🧑  Availability": availability.render,
    "📈  Timeline":     timeline.render,
    "➕  Add Event":    add_event.render,
    "🏟  Add Team":     add_team.render,
    "👥  Add Squad":    add_squad.render,
    "🛡  Admin":        admin.render,
}

if page in ROUTES:
    ROUTES[page]()

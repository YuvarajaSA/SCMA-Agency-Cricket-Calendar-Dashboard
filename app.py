# app.py
# ══════════════════════════════════════════════════════════════
#  Cricket Availability Dashboard  v2
#  Entry point — auth gate + sidebar navigation
#
#  AUTH FLOW (correct order):
#    1. handle_oauth_callback()  ← exchange ?code= for session
#    2. hydrate_session()        ← restore session from Supabase client
#    3. is_logged_in()           ← now safe to check
#    4. Show login OR dashboard
# ══════════════════════════════════════════════════════════════

import streamlit as st

# ── Page config (MUST be first Streamlit call) ────────────────
st.set_page_config(
    page_title="Cricket Availability Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────
from config.styles import inject
inject()

# ── STEP 1: Handle OAuth callback BEFORE anything else ────────
# If Supabase redirected back with ?code=, exchange it now.
# This MUST run before is_logged_in() is checked.
from db.auth import (
    handle_oauth_callback, hydrate_session, is_logged_in,
    logout, current_email, get_role, can_edit, is_admin,
)

just_logged_in = handle_oauth_callback()

# ── STEP 2: Hydrate session from cached Supabase client ───────
# Restores session_state after every Streamlit rerun.
hydrate_session()

# ── STEP 3: Auth gate ─────────────────────────────────────────
if not is_logged_in():
    from pages.login import render as login_page
    login_page()
    st.stop()

# ── STEP 4: Show welcome toast on fresh login ─────────────────
if just_logged_in:
    st.toast(f"👋 Welcome back, {current_email()}!", icon="✅")

# ── Page modules ──────────────────────────────────────────────
from pages import (
    dashboard, calendar_view, search,
    add_event, add_team, add_squad,
    conflicts, availability, timeline, admin,
)
from db.operations import load_events, load_teams, load_squad
from utils.conflicts import detect_event_overlaps, detect_player_conflicts

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    # Brand header
    st.markdown("""
    <div style="padding:1.1rem 0 1.3rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                    color:#f0b429;letter-spacing:.06em;line-height:1;">
            🏏 CRICKET
        </div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:.8rem;
                    color:#8b949e;letter-spacing:.18em;margin-top:.1rem;">
            AVAILABILITY DASHBOARD
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Current user + role pill
    role      = get_role()
    role_cls  = {"admin":"role-admin","editor":"role-editor","viewer":"role-viewer"}.get(role,"role-viewer")
    role_icon = {"admin":"👑","editor":"✏️","viewer":"👁"}.get(role,"👁")
    email     = current_email()
    st.markdown(f"""
    <div style="background:#1c2128;border:1px solid #30363d;border-radius:10px;
                padding:.7rem .9rem;margin-bottom:1rem;">
        <div style="font-size:.72rem;color:#8b949e;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                    margin-bottom:.35rem;">{email}</div>
        <span class="role-pill {role_cls}">{role_icon} {role}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
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

    # Live quick-stats
    events_df = load_events()
    teams_df  = load_teams()
    squad_df  = load_squad()

    total_events  = len(events_df)
    total_teams   = teams_df["team_name"].nunique() if not teams_df.empty else 0
    total_players = squad_df["player_name"].nunique() if not squad_df.empty else 0
    eo = detect_event_overlaps(events_df)
    pc = detect_player_conflicts(squad_df)

    stats = [
        (total_events,  "Events",           "#f0b429"),
        (total_teams,   "Teams",             "#3fb950"),
        (total_players, "Players",           "#58a6ff"),
        (len(eo), "Date Conflicts",    "#f85149" if eo else "#3fb950"),
        (len(pc), "Player Conflicts",  "#f85149" if pc else "#3fb950"),
    ]
    rows_html = "".join(
        f'<div style="background:#1c2128;border:1px solid #30363d;border-radius:8px;'
        f'padding:.45rem .85rem;display:flex;align-items:center;gap:.75rem;">'
        f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.35rem;'
        f'color:{c};min-width:1.8rem;text-align:right;">{v}</span>'
        f'<span style="font-size:.68rem;font-weight:700;letter-spacing:.07em;'
        f'text-transform:uppercase;color:#8b949e;">{l}</span></div>'
        for v, l, c in stats
    )
    st.markdown(f"""
    <div style="font-size:.6rem;font-weight:800;letter-spacing:.14em;
                text-transform:uppercase;color:#8b949e;margin-bottom:.6rem;">
        QUICK STATS
    </div>
    <div style="display:flex;flex-direction:column;gap:.35rem;">
        {rows_html}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪  Log Out", use_container_width=True, key="logout_btn"):
        logout()
        st.rerun()

    st.markdown("""
    <div style="font-size:.62rem;color:#8b949e;margin-top:.7rem;
                line-height:1.6;text-align:center;">
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

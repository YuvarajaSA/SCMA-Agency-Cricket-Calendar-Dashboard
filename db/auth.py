# db/auth.py
# ══════════════════════════════════════════════════════════════
#  Authentication & Role Management  — FIXED v2
#
#  WHY THE OLD VERSION BROKE
#  ─────────────────────────
#  1. Supabase default OAuth uses URL HASH fragments (#access_token=…)
#     Streamlit st.query_params CANNOT read hash fragments — only ?key=val
#     So the callback silently received nothing and returned False.
#
#  2. handle_oauth_callback() was called inside login.py, but app.py
#     checked is_logged_in() BEFORE login.py loaded → callback never ran.
#
#  3. No session hydration — after every Streamlit rerun st.session_state
#     is empty and nothing restored the existing Supabase session.
#
#  THE FIX
#  ───────
#  1. Use PKCE flow → Supabase returns ?code=xxx as a query param
#     Streamlit CAN read query params → exchange code for session
#
#  2. Call handle_oauth_callback() at the very top of app.py,
#     BEFORE any is_logged_in() check
#
#  3. Add hydrate_session() — on every load try supabase.auth.get_session()
#     and restore into session_state if a valid session exists
# ══════════════════════════════════════════════════════════════

from __future__ import annotations
import streamlit as st
from db.supabase_client import get_client


# ── Internal session helpers ──────────────────────────────────

def _set_session(session) -> None:
    """Store Supabase session + user in session_state."""
    st.session_state["auth_session"] = session
    st.session_state["auth_user"]    = session.user if session else None
    # Clear cached role so it gets re-fetched for new user
    st.session_state.pop("auth_role", None)


def _clear_session() -> None:
    for k in ["auth_session", "auth_user", "auth_role"]:
        st.session_state.pop(k, None)


# ── Public read API ───────────────────────────────────────────

def current_user():
    """Return the logged-in Supabase User object, or None."""
    return st.session_state.get("auth_user")


def current_email() -> str:
    u = current_user()
    return u.email if u else ""


def is_logged_in() -> bool:
    """
    True if we have a user in session_state.
    hydrate_session() must be called before this to restore
    sessions that survived a Streamlit rerun.
    """
    return st.session_state.get("auth_user") is not None


# ── SESSION HYDRATION — call on every app load ────────────────

def hydrate_session() -> bool:
    """
    On every Streamlit rerun, st.session_state starts empty.
    Supabase-py stores tokens internally in its client object
    (which IS cached via @st.cache_resource).
    
    This function asks the cached Supabase client for its
    current session and restores it into session_state.
    
    Returns True if a valid session was found and restored.
    """
    # Already hydrated this run
    if st.session_state.get("auth_user"):
        return True

    sb = get_client()
    try:
        resp = sb.auth.get_session()
        if resp and resp.session and resp.session.user:
            _set_session(resp.session)
            return True
    except Exception:
        pass
    return False


# ── OAUTH CALLBACK — call at very top of app.py ──────────────

def handle_oauth_callback() -> bool:
    """
    Supabase PKCE flow redirects back to the app with:
        ?code=XXXX
    
    We exchange that code for a real session.
    Must be called BEFORE is_logged_in() check in app.py.
    
    Returns True if a new session was established from a code.
    """
    params = st.query_params

    # ── PKCE: exchange authorization code ────────────────────
    code = params.get("code")
    if code:
        sb = get_client()
        try:
            resp = sb.auth.exchange_code_for_session({"auth_code": code})
            if resp and resp.session:
                _set_session(resp.session)
                # Remove ?code= from the URL so it doesn't re-trigger
                st.query_params.clear()
                return True
        except Exception as e:
            # Clear bad code from URL silently
            st.query_params.clear()
        return False

    # ── Implicit fallback: direct tokens in query params ─────
    # (happens if PKCE isn't available in older supabase-py)
    access_token  = params.get("access_token")
    refresh_token = params.get("refresh_token", "")
    if access_token:
        sb = get_client()
        try:
            resp = sb.auth.set_session(access_token, refresh_token)
            if resp and resp.session:
                _set_session(resp.session)
                st.query_params.clear()
                return True
        except Exception:
            st.query_params.clear()
        return False

    return False


# ── LOGIN ─────────────────────────────────────────────────────

def login_with_password(email: str, password: str) -> tuple[bool, str]:
    sb = get_client()
    try:
        resp = sb.auth.sign_in_with_password({"email": email, "password": password})
        if resp and resp.session:
            _set_session(resp.session)
            return True, "Logged in successfully."
        return False, "Invalid credentials. Check your email and password."
    except Exception as e:
        msg = str(e)
        if "Invalid login" in msg or "invalid_credentials" in msg:
            return False, "Invalid email or password."
        if "Email not confirmed" in msg:
            return False, "Please confirm your email first — check your inbox."
        return False, f"Login error: {msg}"


def login_with_google() -> str:
    """
    Build and return the Google OAuth URL using PKCE flow.
    PKCE returns ?code= as a query param — readable by Streamlit.
    
    The returned URL should be opened in the browser via st.markdown redirect.
    """
    sb       = get_client()
    redirect = st.secrets["supabase"].get("redirect_url", "")

    try:
        resp = sb.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to":        redirect,
                "flow_type":          "pkce",       # ← KEY FIX: returns ?code= not #hash
                "query_params": {
                    "access_type": "offline",
                    "prompt":      "select_account",  # always show account picker
                },
            },
        })
        return resp.url if resp else ""
    except Exception as e:
        return ""


def logout() -> None:
    sb = get_client()
    try:
        sb.auth.sign_out()
    except Exception:
        pass
    _clear_session()


# ── ROLE MANAGEMENT ───────────────────────────────────────────

def get_role() -> str:
    """
    Return role for current user. Cached in session_state.
    Falls back to 'viewer' if no record found.
    """
    if "auth_role" in st.session_state:
        return st.session_state["auth_role"]

    u = current_user()
    if not u:
        return "viewer"

    sb = get_client()
    try:
        resp = (
            sb.table("user_roles")
            .select("role")
            .eq("user_id", u.id)
            .maybe_single()
            .execute()
        )
        role = resp.data.get("role", "viewer") if resp.data else "viewer"
    except Exception:
        role = "viewer"

    st.session_state["auth_role"] = role
    return role


def can_edit() -> bool:
    return get_role() in ("admin", "editor")


def is_admin() -> bool:
    return get_role() == "admin"


# ── USER MANAGEMENT (admin only) ─────────────────────────────

def list_users() -> list[dict]:
    sb   = get_client()
    resp = sb.table("user_roles").select("*").order("email").execute()
    return resp.data or []


def set_user_role(user_id: str, email: str, role: str) -> tuple[bool, str]:
    sb = get_client()
    try:
        sb.table("user_roles").upsert({
            "user_id": user_id,
            "email":   email,
            "role":    role,
        }).execute()
        return True, f"Role updated to '{role}' for {email}."
    except Exception as e:
        return False, str(e)

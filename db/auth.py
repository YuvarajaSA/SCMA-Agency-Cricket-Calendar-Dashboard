# db/auth.py
# ══════════════════════════════════════════════════════════════
#  Authentication — DEFINITIVE FIX
#
#  ROOT CAUSES OF PREVIOUS FAILURES
#  ──────────────────────────────────
#
#  1. PKCE flow requires code_verifier stored in the Supabase
#     client object (@st.cache_resource). On Streamlit Cloud the
#     server sleeps between the OAuth redirect and the callback —
#     the cache is cleared → verifier gone → exchange fails →
#     login loop. PKCE is unreliable for Streamlit deployments.
#
#  2. get_session() returns Optional[Session] DIRECTLY.
#     The old code did `resp.session` which is WRONG.
#     resp IS the session (or None). This broke hydration silently.
#
#  3. handle_oauth_callback() was called inside login.py, AFTER
#     app.py already ran is_logged_in() → st.stop(). The callback
#     never ran. Must be first thing in app.py.
#
#  4. Second click → 403: Supabase client holds pending PKCE state
#     from first attempt. New OAuth call conflicts → 403.
#     Fix: sign_out() before starting any new OAuth flow.
#
#  THE WORKING APPROACH
#  ─────────────────────
#  Use IMPLICIT flow (no PKCE).
#  Supabase returns: yourapp.com/#access_token=...&refresh_token=...
#  A JS snippet in login.py reads the hash and rewrites the URL
#  to: yourapp.com/?access_token=...&refresh_token=...
#  Streamlit CAN read ?query params → set_session() → done.
#  No code_verifier. No cache dependency. Works after any restart.
#
# ══════════════════════════════════════════════════════════════

from __future__ import annotations
import streamlit as st
from db.supabase_client import get_client


# ── Internal helpers ──────────────────────────────────────────

def _store_session(session) -> None:
    """Store a Supabase Session object into session_state."""
    if session is None:
        return
    st.session_state["auth_session"] = session
    st.session_state["auth_user"]    = session.user
    st.session_state.pop("auth_role",  None)   # re-fetch on next get_role()
    st.session_state.pop("auth_error", None)


def _clear_all() -> None:
    for k in ["auth_session", "auth_user", "auth_role",
              "auth_error", "oauth_in_progress"]:
        st.session_state.pop(k, None)


# ── Public read helpers ───────────────────────────────────────

def current_user():
    return st.session_state.get("auth_user")


def current_email() -> str:
    u = current_user()
    return u.email if u else ""


def is_logged_in() -> bool:
    """
    Check session_state first (fast path after hydration).
    hydrate_session() + handle_oauth_callback() must run before this.
    """
    return st.session_state.get("auth_user") is not None


# ── STEP 1: OAuth callback ────────────────────────────────────
# Called at the very top of app.py before any auth check.
# Handles tokens that arrive as query params after OAuth redirect.

def handle_oauth_callback() -> bool:
    """
    The JS hash reader in login.py converts:
        #access_token=XXX&refresh_token=YYY
    into query params:
        ?access_token=XXX&refresh_token=YYY

    We read those params and establish the session.
    Returns True if a new session was created from callback tokens.
    """
    params = st.query_params

    # ── Implicit flow: access_token in query params ────────────
    access_token  = params.get("access_token")
    refresh_token = params.get("refresh_token", "")

    if access_token:
        sb = get_client()
        try:
            # set_session(access_token: str, refresh_token: str) → AuthResponse
            resp = sb.auth.set_session(access_token, refresh_token)
            if resp and resp.session:
                _store_session(resp.session)
                # Clean tokens from the URL bar
                st.query_params.clear()
                st.session_state.pop("oauth_in_progress", None)
                return True
            else:
                st.session_state["auth_error"] = "Session could not be established."
                st.query_params.clear()
                return False
        except Exception as e:
            st.session_state["auth_error"] = f"Session error: {e}"
            st.query_params.clear()
            return False

    # ── PKCE fallback: ?code= in query params ──────────────────
    # Handles edge case where Supabase sends a code instead of tokens
    code = params.get("code")
    if code:
        sb = get_client()
        try:
            # CodeExchangeParams expects {"auth_code": code}
            from supabase_auth.types import CodeExchangeParams
            resp = sb.auth.exchange_code_for_session(
                CodeExchangeParams(auth_code=code)
            )
            if resp and resp.session:
                _store_session(resp.session)
                st.query_params.clear()
                st.session_state.pop("oauth_in_progress", None)
                return True
        except Exception:
            pass
        st.query_params.clear()
        return False

    # ── OAuth error params ─────────────────────────────────────
    error = params.get("error")
    if error:
        desc = params.get("error_description", error)
        st.session_state["auth_error"] = f"OAuth error: {desc}"
        st.query_params.clear()
        return False

    return False


# ── STEP 2: Session hydration ─────────────────────────────────
# Called right after handle_oauth_callback() in app.py.
# Restores session from Supabase client cache on every rerun.

def hydrate_session() -> bool:
    """
    st.session_state is wiped on every Streamlit rerun, but the
    Supabase client (@st.cache_resource) persists across reruns
    within the same server process.

    IMPORTANT: get_session() returns Optional[Session] DIRECTLY.
    It does NOT return an object with a .session attribute.
    """
    # Already hydrated this run — skip the network call
    if st.session_state.get("auth_user"):
        return True

    sb = get_client()
    try:
        # Returns Optional[Session] — not AuthResponse!
        session = sb.auth.get_session()
        if session and hasattr(session, "user") and session.user:
            _store_session(session)
            return True
    except Exception:
        pass
    return False


# ── Login ─────────────────────────────────────────────────────

def login_with_password(email: str, password: str) -> tuple[bool, str]:
    sb = get_client()
    try:
        resp = sb.auth.sign_in_with_password({"email": email, "password": password})
        # sign_in_with_password returns AuthResponse — has .session
        if resp and resp.session:
            _store_session(resp.session)
            return True, "Logged in."
        return False, "Invalid credentials."
    except Exception as e:
        msg = str(e)
        if "invalid_credentials" in msg or "Invalid login" in msg:
            return False, "Incorrect email or password."
        if "Email not confirmed" in msg:
            return False, "Please confirm your email address first."
        return False, f"Login failed: {msg}"


def login_with_google() -> str:
    """
    Build Google OAuth URL using IMPLICIT flow (no PKCE).

    WHY NO PKCE:
    PKCE stores a code_verifier in the cached Supabase client.
    On Streamlit Cloud the server can restart between the OAuth
    redirect and the callback, clearing @st.cache_resource and
    losing the verifier → exchange fails → login loop.

    Implicit flow returns tokens in the URL hash.
    The JS hash reader in login.py converts them to query params
    so Streamlit can read them.

    WHY sign_out() first:
    If a previous OAuth attempt left pending PKCE state in the
    Supabase client, a new sign_in_with_oauth call conflicts with
    it → 403 on second click. sign_out() clears that state.
    """
    sb = get_client()

    # Clear any stale auth state to prevent 403 on second click
    try:
        sb.auth.sign_out()
    except Exception:
        pass

    redirect = st.secrets["supabase"].get("redirect_url", "")

    try:
        resp = sb.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to":  redirect,
                "query_params": {
                    "access_type": "offline",
                    "prompt":      "select_account",
                },
            },
        })
        return resp.url if resp else ""
    except Exception as e:
        st.session_state["auth_error"] = f"OAuth init error: {e}"
        return ""


def logout() -> None:
    sb = get_client()
    try:
        sb.auth.sign_out()
    except Exception:
        pass
    _clear_all()


# ── Roles ─────────────────────────────────────────────────────

def get_role() -> str:
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


# ── User management ───────────────────────────────────────────

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

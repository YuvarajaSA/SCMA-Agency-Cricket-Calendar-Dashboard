# pages/login.py
# ══════════════════════════════════════════════════════════════
#  Login Page — Modern, professional, centered card design
#  Supports:
#    • Google OAuth (PKCE flow — works with Streamlit)
#    • Email + Password
# ══════════════════════════════════════════════════════════════

import streamlit as st
from db.auth import login_with_password, login_with_google
from db.supabase_client import get_client


def render() -> None:
    # ── Full-page background ───────────────────────────────
    st.markdown("""
    <style>
    /* Full dark gradient background on login screen */
    .stApp {
        background: radial-gradient(ellipse at 20% 50%,
            rgba(26,111,181,0.12) 0%,
            transparent 60%),
        radial-gradient(ellipse at 80% 20%,
            rgba(240,180,41,0.08) 0%,
            transparent 50%),
        #0d1117 !important;
    }
    /* Hide sidebar on login */
    section[data-testid="stSidebar"] { display: none !important; }
    /* Remove default padding */
    .main .block-container {
        padding-top: 0 !important;
        max-width: 100% !important;
    }
    /* Login card */
    .login-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 18px;
        padding: 2.8rem 2.6rem 2.4rem;
        box-shadow: 0 8px 40px rgba(0,0,0,0.5),
                    0 1px 0 rgba(255,255,255,0.04) inset;
        width: 100%;
        max-width: 440px;
        margin: 0 auto;
    }
    /* Google button override */
    .google-btn > button {
        background: #fff !important;
        color: #1f1f1f !important;
        border: 1px solid #dadce0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: .9rem !important;
        padding: .65rem 1.4rem !important;
        transition: box-shadow .15s, background .15s !important;
        width: 100% !important;
    }
    .google-btn > button:hover {
        background: #f8f9fa !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25) !important;
        transform: none !important;
    }
    /* Divider line */
    .or-divider {
        display: flex; align-items: center; gap: .9rem;
        margin: 1.4rem 0;
        font-size: .75rem; color: #8b949e;
        font-weight: 600; letter-spacing: .08em;
        text-transform: uppercase;
    }
    .or-divider::before,
    .or-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #30363d;
    }
    /* Security badge */
    .sec-badge {
        display: flex; align-items: center; justify-content: center;
        gap: .4rem; margin-top: 1.6rem;
        font-size: .72rem; color: #8b949e;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Centred layout ─────────────────────────────────────
    st.markdown("<div style='min-height:8vh'></div>", unsafe_allow_html=True)

    _, centre, _ = st.columns([1, 2, 1])

    with centre:
        # ── Card top: logo + title ─────────────────────────
        st.markdown("""
        <div class="login-card">
            <div style="text-align:center;margin-bottom:1.8rem;">
                <div style="font-size:2.8rem;line-height:1;margin-bottom:.5rem;">🏏</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2.1rem;
                            color:#f0b429;letter-spacing:.06em;line-height:1;">
                    CRICKET DASHBOARD
                </div>
                <div style="font-size:.84rem;color:#8b949e;margin-top:.4rem;
                            letter-spacing:.02em;">
                    Availability & Conflict System
                </div>
                <div style="display:inline-block;margin-top:.7rem;padding:.2rem .8rem;
                            background:rgba(248,81,73,.1);border:1px solid rgba(248,81,73,.25);
                            border-radius:20px;font-size:.68rem;font-weight:700;
                            letter-spacing:.1em;text-transform:uppercase;color:#f85149;">
                    🔒 Internal Access Only
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Google Login (PRIMARY) ─────────────────────────
        st.markdown('<div class="google-btn">', unsafe_allow_html=True)

        if st.button(
            "🔵  Continue with Google",
            use_container_width=True,
            key="btn_google_login",
        ):
            with st.spinner("Connecting to Google…"):
                url = login_with_google()
            if url:
                # Redirect via meta refresh — works on both local + deployed
                st.markdown(
                    f'<meta http-equiv="refresh" content="0;url={url}">',
                    unsafe_allow_html=True,
                )
                st.markdown(f"""
                <div style="text-align:center;margin-top:1rem;
                            font-size:.84rem;color:#8b949e;">
                    Redirecting to Google…
                    <br><a href="{url}" style="color:#58a6ff;">
                    Click here if not redirected</a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:rgba(248,81,73,.1);border:1px solid rgba(248,81,73,.3);
                            border-radius:8px;padding:.8rem 1rem;margin-top:.8rem;
                            font-size:.84rem;color:#f85149;">
                    ⚠️ Google login is not configured yet.<br>
                    <span style="color:#8b949e;">
                    Enable Google provider in Supabase → Authentication → Sign In / Providers
                    </span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Divider ────────────────────────────────────────
        st.markdown('<div class="or-divider">or</div>', unsafe_allow_html=True)

        # ── Email / Password ───────────────────────────────
        with st.expander("✉️  Sign in with Email & Password", expanded=False):
            st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

            email    = st.text_input(
                "Email", placeholder="you@yourcompany.com",
                key="li_email", label_visibility="collapsed",
            )
            password = st.text_input(
                "Password", type="password",
                placeholder="Your password",
                key="li_pass", label_visibility="collapsed",
            )

            if st.button("Log In →", use_container_width=True, key="btn_email_login"):
                if not email.strip() or not password:
                    st.error("Please enter both email and password.")
                else:
                    with st.spinner("Verifying credentials…"):
                        ok, msg = login_with_password(email.strip(), password)
                    if ok:
                        st.success("✅ Logged in! Loading dashboard…")
                        st.rerun()
                    else:
                        st.markdown(f"""
                        <div style="background:rgba(248,81,73,.1);
                                    border:1px solid rgba(248,81,73,.3);
                                    border-radius:8px;padding:.75rem 1rem;
                                    font-size:.84rem;color:#f85149;margin-top:.5rem;">
                            ❌ {msg}
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("""
            <div style="font-size:.74rem;color:#8b949e;margin-top:.8rem;
                        text-align:center;line-height:1.6;">
                New staff? Ask your admin to invite you via Supabase.<br>
                Forgot password? Contact your system administrator.
            </div>
            """, unsafe_allow_html=True)

        # ── Security footer ────────────────────────────────
        st.markdown("""
        <div class="sec-badge">
            <span>🔐</span>
            <span>Secured by Supabase Auth</span>
            <span style="color:#30363d;">·</span>
            <span>End-to-end encrypted</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Debug panel (temporary — remove in production) ────
    _show_debug_panel()


def _show_debug_panel() -> None:
    """
    Temporary debug panel to confirm session state.
    Remove or set DEBUG = False once auth is confirmed working.
    """
    DEBUG = True   # ← set to False once login works

    if not DEBUG:
        return

    with st.expander("🛠 Debug Panel — remove in production", expanded=False):
        st.markdown("**st.query_params** (what Supabase sent back):")
        st.json(dict(st.query_params))

        st.markdown("**st.session_state keys:**")
        safe_state = {
            k: str(v)[:120] for k, v in st.session_state.items()
        }
        st.json(safe_state)

        st.markdown("**Supabase get_session():**")
        try:
            sb   = get_client()
            sess = sb.auth.get_session()
            if sess and sess.session:
                st.success(f"✅ Active session found for: {sess.session.user.email}")
            else:
                st.warning("⚠️ No active session in Supabase client.")
        except Exception as e:
            st.error(f"get_session() error: {e}")

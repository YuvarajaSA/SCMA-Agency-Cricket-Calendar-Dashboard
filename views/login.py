# # pages/login.py
# # ══════════════════════════════════════════════════════════════
# #  Login Page — Modern, professional, centered card design
# #  Supports:
# #    • Google OAuth (PKCE flow — works with Streamlit)
# #    • Email + Password
# # ══════════════════════════════════════════════════════════════

# import streamlit as st
# from db.auth import login_with_password, login_with_google
# from db.supabase_client import get_client


# def render() -> None:
#     # ── Full-page background ───────────────────────────────
#     st.markdown("""
#     <style>
#     /* Full dark gradient background on login screen */
#     .stApp {
#         background: radial-gradient(ellipse at 20% 50%,
#             rgba(26,111,181,0.12) 0%,
#             transparent 60%),
#         radial-gradient(ellipse at 80% 20%,
#             rgba(240,180,41,0.08) 0%,
#             transparent 50%),
#         #0d1117 !important;
#     }
#     /* Hide sidebar on login */
#     section[data-testid="stSidebar"] { display: none !important; }
#     /* Remove default padding */
#     .main .block-container {
#         padding-top: 0 !important;
#         max-width: 100% !important;
#     }
#     /* Login card */
#     .login-card {
#         background: #161b22;
#         border: 1px solid #30363d;
#         border-radius: 18px;
#         padding: 2.8rem 2.6rem 2.4rem;
#         box-shadow: 0 8px 40px rgba(0,0,0,0.5),
#                     0 1px 0 rgba(255,255,255,0.04) inset;
#         width: 100%;
#         max-width: 440px;
#         margin: 0 auto;
#     }
#     /* Google button override */
#     .google-btn > button {
#         background: #fff !important;
#         color: #1f1f1f !important;
#         border: 1px solid #dadce0 !important;
#         border-radius: 8px !important;
#         font-weight: 600 !important;
#         font-size: .9rem !important;
#         padding: .65rem 1.4rem !important;
#         transition: box-shadow .15s, background .15s !important;
#         width: 100% !important;
#     }
#     .google-btn > button:hover {
#         background: #f8f9fa !important;
#         box-shadow: 0 2px 8px rgba(0,0,0,0.25) !important;
#         transform: none !important;
#     }
#     /* Divider line */
#     .or-divider {
#         display: flex; align-items: center; gap: .9rem;
#         margin: 1.4rem 0;
#         font-size: .75rem; color: #8b949e;
#         font-weight: 600; letter-spacing: .08em;
#         text-transform: uppercase;
#     }
#     .or-divider::before,
#     .or-divider::after {
#         content: '';
#         flex: 1;
#         height: 1px;
#         background: #30363d;
#     }
#     /* Security badge */
#     .sec-badge {
#         display: flex; align-items: center; justify-content: center;
#         gap: .4rem; margin-top: 1.6rem;
#         font-size: .72rem; color: #8b949e;
#     }
#     </style>
#     """, unsafe_allow_html=True)

#     # ── Centred layout ─────────────────────────────────────
#     st.markdown("<div style='min-height:8vh'></div>", unsafe_allow_html=True)

#     _, centre, _ = st.columns([1, 2, 1])

#     with centre:
#         # ── Card top: logo + title ─────────────────────────
#         st.markdown("""
#         <div class="login-card">
#             <div style="text-align:center;margin-bottom:1.8rem;">
#                 <div style="font-size:2.8rem;line-height:1;margin-bottom:.5rem;">🏏</div>
#                 <div style="font-family:'Bebas Neue',sans-serif;font-size:2.1rem;
#                             color:#f0b429;letter-spacing:.06em;line-height:1;">
#                     CRICKET DASHBOARD
#                 </div>
#                 <div style="font-size:.84rem;color:#8b949e;margin-top:.4rem;
#                             letter-spacing:.02em;">
#                     Availability & Conflict System
#                 </div>
#                 <div style="display:inline-block;margin-top:.7rem;padding:.2rem .8rem;
#                             background:rgba(248,81,73,.1);border:1px solid rgba(248,81,73,.25);
#                             border-radius:20px;font-size:.68rem;font-weight:700;
#                             letter-spacing:.1em;text-transform:uppercase;color:#f85149;">
#                     🔒 Internal Access Only
#                 </div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#         # ── Google Login (PRIMARY) ─────────────────────────
#         st.markdown('<div class="google-btn">', unsafe_allow_html=True)

#         if st.button(
#             "🔵  Continue with Google",
#             use_container_width=True,
#             key="btn_google_login",
#         ):
#             with st.spinner("Connecting to Google…"):
#                 url = login_with_google()
#             if url:
#                 # Redirect via meta refresh — works on both local + deployed
#                 st.markdown(
#                     f'<meta http-equiv="refresh" content="0;url={url}">',
#                     unsafe_allow_html=True,
#                 )
#                 st.markdown(f"""
#                 <div style="text-align:center;margin-top:1rem;
#                             font-size:.84rem;color:#8b949e;">
#                     Redirecting to Google…
#                     <br><a href="{url}" style="color:#58a6ff;">
#                     Click here if not redirected</a>
#                 </div>
#                 """, unsafe_allow_html=True)
#             else:
#                 st.markdown("""
#                 <div style="background:rgba(248,81,73,.1);border:1px solid rgba(248,81,73,.3);
#                             border-radius:8px;padding:.8rem 1rem;margin-top:.8rem;
#                             font-size:.84rem;color:#f85149;">
#                     ⚠️ Google login is not configured yet.<br>
#                     <span style="color:#8b949e;">
#                     Enable Google provider in Supabase → Authentication → Sign In / Providers
#                     </span>
#                 </div>
#                 """, unsafe_allow_html=True)

#         st.markdown('</div>', unsafe_allow_html=True)

#         # ── Divider ────────────────────────────────────────
#         st.markdown('<div class="or-divider">or</div>', unsafe_allow_html=True)

#         # ── Email / Password ───────────────────────────────
#         with st.expander("✉️  Sign in with Email & Password", expanded=False):
#             st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

#             email    = st.text_input(
#                 "Email", placeholder="you@yourcompany.com",
#                 key="li_email", label_visibility="collapsed",
#             )
#             password = st.text_input(
#                 "Password", type="password",
#                 placeholder="Your password",
#                 key="li_pass", label_visibility="collapsed",
#             )

#             if st.button("Log In →", use_container_width=True, key="btn_email_login"):
#                 if not email.strip() or not password:
#                     st.error("Please enter both email and password.")
#                 else:
#                     with st.spinner("Verifying credentials…"):
#                         ok, msg = login_with_password(email.strip(), password)
#                     if ok:
#                         st.success("✅ Logged in! Loading dashboard…")
#                         st.rerun()
#                     else:
#                         st.markdown(f"""
#                         <div style="background:rgba(248,81,73,.1);
#                                     border:1px solid rgba(248,81,73,.3);
#                                     border-radius:8px;padding:.75rem 1rem;
#                                     font-size:.84rem;color:#f85149;margin-top:.5rem;">
#                             ❌ {msg}
#                         </div>
#                         """, unsafe_allow_html=True)

#             st.markdown("""
#             <div style="font-size:.74rem;color:#8b949e;margin-top:.8rem;
#                         text-align:center;line-height:1.6;">
#                 New staff? Ask your admin to invite you via Supabase.<br>
#                 Forgot password? Contact your system administrator.
#             </div>
#             """, unsafe_allow_html=True)

#         # ── Security footer ────────────────────────────────
#         st.markdown("""
#         <div class="sec-badge">
#             <span>🔐</span>
#             <span>Secured by Supabase Auth</span>
#             <span style="color:#30363d;">·</span>
#             <span>End-to-end encrypted</span>
#         </div>
#         """, unsafe_allow_html=True)

#     # ── Debug panel (temporary — remove in production) ────
#     _show_debug_panel()


# def _show_debug_panel() -> None:
#     """
#     Temporary debug panel to confirm session state.
#     Remove or set DEBUG = False once auth is confirmed working.
#     """
#     DEBUG = True   # ← set to False once login works

#     if not DEBUG:
#         return

#     with st.expander("🛠 Debug Panel — remove in production", expanded=False):
#         st.markdown("**st.query_params** (what Supabase sent back):")
#         st.json(dict(st.query_params))

#         st.markdown("**st.session_state keys:**")
#         safe_state = {
#             k: str(v)[:120] for k, v in st.session_state.items()
#         }
#         st.json(safe_state)

#         st.markdown("**Supabase get_session():**")
#         try:
#             sb   = get_client()
#             sess = sb.auth.get_session()
#             if sess and sess.session:
#                 st.success(f"✅ Active session found for: {sess.session.user.email}")
#             else:
#                 st.warning("⚠️ No active session in Supabase client.")
#         except Exception as e:
#             st.error(f"get_session() error: {e}")


# pages/login.py
# ══════════════════════════════════════════════════════════════
#  Login Page
#
#  CRITICAL: The JS hash reader at the top converts
#  Supabase's implicit-flow URL hash tokens:
#    yourapp.com/#access_token=XXX&refresh_token=YYY
#  into query params that Streamlit CAN read:
#    yourapp.com/?access_token=XXX&refresh_token=YYY
#
#  This runs on EVERY page load. If no hash → does nothing.
#  If hash with access_token → rewrites URL → Streamlit reruns
#  → handle_oauth_callback() in app.py picks up the tokens.
# ══════════════════════════════════════════════════════════════

import streamlit as st
import streamlit.components.v1 as components
from db.auth import login_with_password, login_with_google
from db.supabase_client import get_client


# ══════════════════════════════════════════════════════════════
#  JS HASH READER — Must be injected before anything else
#  Reads URL hash fragment and rewrites as query params
# ══════════════════════════════════════════════════════════════

_HASH_READER_JS = """
<script>
(function() {
    const hash = window.location.hash;
    if (!hash || hash.length < 2) return;

    // Parse the hash fragment
    const params = new URLSearchParams(hash.substring(1));
    const accessToken  = params.get('access_token');
    const refreshToken = params.get('refresh_token') || '';
    const errorCode    = params.get('error');

    if (accessToken) {
        // Rewrite URL with tokens as query params (Streamlit can read these)
        const newUrl = window.location.origin
            + window.location.pathname
            + '?access_token=' + encodeURIComponent(accessToken)
            + '&refresh_token=' + encodeURIComponent(refreshToken);
        window.location.replace(newUrl);
    } else if (errorCode) {
        const desc = params.get('error_description') || errorCode;
        const newUrl = window.location.origin
            + window.location.pathname
            + '?error=' + encodeURIComponent(errorCode)
            + '&error_description=' + encodeURIComponent(desc);
        window.location.replace(newUrl);
    }
})();
</script>
"""


def render() -> None:
    # ── 1. Inject JS hash reader (MUST be first) ──────────────
    # Height=0 means no visible iframe — just runs the script
    components.html(_HASH_READER_JS, height=0, scrolling=False)

    # ── 2. Full-page styles ────────────────────────────────────
    st.markdown("""
    <style>
    /* Full-page dark gradient background */
    .stApp {
        background:
            radial-gradient(ellipse at 15% 50%,
                rgba(26,111,181,0.13) 0%, transparent 55%),
            radial-gradient(ellipse at 85% 15%,
                rgba(240,180,41,0.09) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 90%,
                rgba(63,185,80,0.06) 0%, transparent 50%),
            #0d1117 !important;
    }

    /* Hide sidebar completely on login */
    section[data-testid="stSidebar"]  { display: none !important; }
    .main .block-container {
        padding-top:    0 !important;
        padding-bottom: 0 !important;
        max-width:      100% !important;
    }

    /* Login card */
    .lc {
        background:    #161b22;
        border:        1px solid #30363d;
        border-radius: 18px;
        padding:       2.8rem 2.6rem 2.4rem;
        box-shadow:
            0 8px 48px rgba(0,0,0,0.55),
            0 1px 0   rgba(255,255,255,0.04) inset;
        width:     100%;
        max-width: 440px;
        margin:    0 auto;
    }

    /* Google button — white on dark */
    div[data-testid="stButton"].google-btn > button,
    .google-btn > button {
        background:    #ffffff !important;
        color:         #1f1f1f !important;
        border:        1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        font-weight:   600 !important;
        font-size:     .92rem !important;
        padding:       .65rem 1.4rem !important;
        letter-spacing:.01em !important;
        width:         100% !important;
    }
    .google-btn > button:hover {
        background:  #f5f5f5 !important;
        box-shadow:  0 2px 10px rgba(0,0,0,0.3) !important;
        transform:   none !important;
        opacity:     1 !important;
    }
    .google-btn > button:disabled {
        opacity: .5 !important;
        cursor:  not-allowed !important;
    }

    /* Divider */
    .or-line {
        display:     flex;
        align-items: center;
        gap:         .9rem;
        margin:      1.3rem 0;
        font-size:   .72rem;
        color:       #8b949e;
        font-weight: 700;
        letter-spacing:.1em;
        text-transform:uppercase;
    }
    .or-line::before,
    .or-line::after {
        content:    '';
        flex:       1;
        height:     1px;
        background: #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 3. Show pending redirect message if OAuth is in progress ─
    if st.session_state.get("oauth_in_progress"):
        st.markdown("""
        <div style="height:30vh"></div>
        <div style="text-align:center;">
            <div style="font-size:2rem;margin-bottom:1rem;">🔄</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;
                        color:#f0b429;letter-spacing:.06em;">
                Redirecting to Google…
            </div>
            <div style="font-size:.86rem;color:#8b949e;margin-top:.6rem;">
                Complete sign-in in the Google popup,
                then you'll be returned here automatically.
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Show a cancel option
        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        _, c, _ = st.columns([2, 1, 2])
        with c:
            if st.button("✕  Cancel", key="cancel_oauth"):
                st.session_state.pop("oauth_in_progress", None)
                st.rerun()
        return

    # ── 4. Top spacer ──────────────────────────────────────────
    st.markdown("<div style='min-height:6vh'></div>", unsafe_allow_html=True)

    # ── 5. Main card ───────────────────────────────────────────
    _, mid, _ = st.columns([1, 2, 1])

    with mid:
        # Card header
        st.markdown("""
        <div class="lc">
            <div style="text-align:center;margin-bottom:2rem;">
                <div style="font-size:3rem;line-height:1;margin-bottom:.6rem;">🏏</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;
                            color:#f0b429;letter-spacing:.06em;line-height:1;">
                    CRICKET DASHBOARD
                </div>
                <div style="font-size:.85rem;color:#8b949e;margin-top:.45rem;">
                    Availability &amp; Conflict System
                </div>
                <div style="margin-top:.8rem;">
                    <span style="display:inline-block;padding:.2rem .85rem;
                        background:rgba(248,81,73,.1);
                        border:1px solid rgba(248,81,73,.25);
                        border-radius:20px;font-size:.66rem;font-weight:800;
                        letter-spacing:.12em;text-transform:uppercase;
                        color:#f85149;">
                        🔒 Internal Staff Access Only
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Error banner ───────────────────────────────────────
        err = st.session_state.pop("auth_error", None)
        if err:
            st.markdown(f"""
            <div style="background:rgba(248,81,73,.1);border:1px solid rgba(248,81,73,.3);
                        border-radius:10px;padding:.85rem 1.1rem;margin-bottom:1rem;
                        font-size:.84rem;color:#f85149;display:flex;gap:.6rem;">
                <span>⚠️</span>
                <span>{err}</span>
            </div>
            """, unsafe_allow_html=True)

        # ── Google button (primary CTA) ────────────────────────
        st.markdown('<div class="google-btn">', unsafe_allow_html=True)

        google_disabled = st.session_state.get("oauth_in_progress", False)

        if st.button(
            "🔵  Continue with Google",
            use_container_width=True,
            key="btn_google",
            disabled=google_disabled,
        ):
            # Set flag FIRST to disable button on rerun
            st.session_state["oauth_in_progress"] = True

            url = login_with_google()

            if url:
                # meta-refresh redirect — works on all browsers/deployments
                st.markdown(
                    f'<meta http-equiv="refresh" content="0;url={url}">',
                    unsafe_allow_html=True,
                )
                st.markdown(f"""
                <div style="text-align:center;margin-top:1.2rem;
                            font-size:.84rem;color:#8b949e;">
                    Opening Google sign-in…<br>
                    <a href="{url}" target="_self"
                       style="color:#58a6ff;text-decoration:none;">
                       Click here if not redirected
                    </a>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Google not configured
                st.session_state.pop("oauth_in_progress", None)
                st.markdown("""
                <div style="background:rgba(227,179,65,.1);
                            border:1px solid rgba(227,179,65,.3);
                            border-radius:8px;padding:.85rem 1rem;
                            margin-top:.8rem;font-size:.84rem;color:#e3b341;">
                    ⚙️ Google login is not configured yet.<br>
                    <span style="color:#8b949e;font-size:.8rem;">
                    Go to Supabase → Authentication → Sign In / Providers → Google
                    </span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── OR divider ─────────────────────────────────────────
        st.markdown('<div class="or-line">or</div>', unsafe_allow_html=True)

        # ── Email / Password ───────────────────────────────────
        with st.expander("✉️  Sign in with Email & Password"):
            st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)
            email = st.text_input(
                "Email", placeholder="staff@yourcompany.com",
                key="li_email", label_visibility="collapsed",
            )
            password = st.text_input(
                "Password", type="password",
                placeholder="Your password",
                key="li_pass", label_visibility="collapsed",
            )
            if st.button("Log In →", use_container_width=True, key="btn_email"):
                if not email.strip() or not password:
                    st.error("Enter both email and password.")
                else:
                    with st.spinner("Verifying…"):
                        ok, msg = login_with_password(email.strip(), password)
                    if ok:
                        st.success("✅ Logged in!")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            st.markdown("""
            <div style="font-size:.74rem;color:#8b949e;margin-top:.8rem;
                        text-align:center;line-height:1.6;">
                First time? Ask your admin to invite you.<br>
                Forgot password? Contact your system administrator.
            </div>
            """, unsafe_allow_html=True)

        # ── Footer ─────────────────────────────────────────────
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;
                    gap:.5rem;margin-top:1.8rem;font-size:.72rem;color:#8b949e;">
            <span>🔐</span>
            <span>Secured by Supabase Auth</span>
            <span style="color:#30363d;">·</span>
            <span>Encrypted in transit</span>
        </div>
        """, unsafe_allow_html=True)

    # ── 6. Debug panel ─────────────────────────────────────────
    _debug_panel()


def _debug_panel() -> None:
    """
    Debug panel — set DEBUG=False once login is confirmed working.
    Shows query params, session state, and Supabase session status.
    """
    DEBUG = True   # ← flip to False in production

    if not DEBUG:
        return

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    with st.expander("🛠  Debug Panel — disable once working (set DEBUG=False in login.py)"):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**URL Query Params** (tokens Streamlit received):")
            qp = dict(st.query_params)
            if qp:
                # Mask tokens for display
                safe = {}
                for k, v in qp.items():
                    safe[k] = v[:12] + "…" if len(str(v)) > 12 else v
                st.json(safe)
            else:
                st.info("No query params — if you just logged in via Google and landed here, the JS hash reader may not have run yet. Try refreshing once.")

        with col2:
            st.markdown("**Session State** (auth keys only):")
            auth_keys = {
                k: (str(v)[:60] + "…" if len(str(v)) > 60 else str(v))
                for k, v in st.session_state.items()
                if k.startswith("auth_") or k == "oauth_in_progress"
            }
            st.json(auth_keys if auth_keys else {"status": "empty"})

        st.markdown("**Supabase get_session()** (what the cached client holds):")
        try:
            sb   = get_client()
            sess = sb.auth.get_session()   # Returns Optional[Session] directly
            if sess and hasattr(sess, "user") and sess.user:
                st.success(f"✅ Active session: {sess.user.email}")
                st.json({
                    "user_id":    str(sess.user.id)[:16] + "…",
                    "email":      sess.user.email,
                    "expires_at": str(getattr(sess, 'expires_at', 'unknown')),
                })
            else:
                st.warning("⚠️ No active session in Supabase client.")
                st.caption("This is expected on first visit. After Google login the session should appear here.")
        except Exception as e:
            st.error(f"get_session() raised: {e}")

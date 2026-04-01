# pages/admin.py
import streamlit as st
import pandas as pd
from db.auth import is_admin, list_users, set_user_role, current_email


def render() -> None:
    st.markdown("""
    <div class="page-header">
        <h1>ADMIN</h1>
        <p>User access management — assign and modify staff roles</p>
    </div>
    """, unsafe_allow_html=True)

    if not is_admin():
        st.markdown("""
        <div class="alert-box alert-error">
            <div class="icon">🔒</div>
            <div class="body"><div class="title">Admin Only</div>
            This page is restricted to administrators.</div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Info box ───────────────────────────────────────────
    st.markdown("""
    <div class="alert-box alert-info">
        <div class="icon">ℹ️</div>
        <div class="body">
            <div class="title">Role Permissions</div>
            <b>Admin</b> — Full access: add, edit, delete events + manage user roles<br>
            <b>Editor</b> — Can add &amp; edit events, teams, squads<br>
            <b>Viewer</b> — Read-only: calendar, search, availability check
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Current users ──────────────────────────────────────
    st.markdown('<div class="card-title">STAFF ACCESS LIST</div>', unsafe_allow_html=True)
    users = list_users()

    if not users:
        st.markdown("""
        <div class="alert-box alert-warn">
            <div class="icon">⚠️</div>
            <div class="body">No users in the role table yet. Users appear here after
            their first login. Then set their role below.</div>
        </div>""", unsafe_allow_html=True)
    else:
        # Show editable role table
        for u in users:
            uc1, uc2, uc3 = st.columns([3, 2, 1])
            with uc1:
                role_cls = {"admin":"role-admin","editor":"role-editor","viewer":"role-viewer"}.get(u["role"],"role-viewer")
                me = " (you)" if u["email"] == current_email() else ""
                st.markdown(
                    f'<div style="padding:.4rem 0;font-size:.88rem;">'
                    f'<b>{u["email"]}</b>{me}&nbsp;'
                    f'<span class="role-pill {role_cls}">{u["role"]}</span></div>',
                    unsafe_allow_html=True,
                )
            with uc2:
                new_role = st.selectbox(
                    "Role",
                    ["viewer","editor","admin"],
                    index=["viewer","editor","admin"].index(u["role"]),
                    key=f"role_{u['user_id']}",
                    label_visibility="collapsed",
                )
            with uc3:
                if st.button("Update", key=f"upd_{u['user_id']}"):
                    ok, msg = set_user_role(u["user_id"], u["email"], new_role)
                    if ok: st.success(msg)
                    else:  st.error(msg)

    # ── Role guide ─────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="card-title">HOW TO ADD NEW STAFF</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <ol style="font-size:.88rem;color:#c9d1d9;line-height:2;">
            <li>Go to your <b>Supabase Dashboard → Authentication → Users</b></li>
            <li>Click <b>Invite user</b> and enter their Gmail or work email</li>
            <li>They receive a magic-link email to set their password</li>
            <li>Once they log in, their email appears in the table above</li>
            <li>Set their role to <b>Editor</b> or <b>Admin</b> as needed</li>
        </ol>
        <div style="margin-top:.8rem;font-size:.82rem;color:#8b949e;">
            Viewers can log in immediately with no extra steps — they only see the calendar and search.
        </div>
    </div>
    """, unsafe_allow_html=True)

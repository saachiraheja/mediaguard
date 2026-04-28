import streamlit as st
import database_manager as db_mgr
import engine, styles, io, base64, zipfile
from datetime import datetime
from engine import validate_bytes, safe_open_image

st.set_page_config(page_title="MediaGuard", page_icon="🛡️", layout="wide")
styles.apply_styles()

ADMIN_PASSWORD = "MediaGuard@Admin2026"

# ── SESSION STATE ──
for key, val in {
    "role": "public", "org_id": None, "org_name": None,
    "org_data": None, "org_step": "login"
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── HEADER ──
def render_header():
    # This creates a "Top Bar" that looks like an actual Web App
    st.markdown("""
        <div style='display: flex; justify-content: space-between; align-items: center; 
                    background: white; padding: 16px 32px; border-radius: 16px; 
                    border: 1px solid #E2E8F0; margin-bottom: 40px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div style='background: #0F172A; color: white; padding: 8px; border-radius: 8px;'>🛡️</div>
                <div>
                    <h1 style='margin: 0; font-size: 20px; font-weight: 700; color: #0F172A;'>MediaGuard <span style='font-weight: 400; color: #94A3B8;'>v2.0</span></h1>
                </div>
            </div>
            <div style='display: flex; gap: 20px; font-size: 14px; font-weight: 500; color: #64748B;'>
                <span>Status: <span style='color: #10B981;'>● Active</span></span>
                <span>Forensic Node: <span style='color: #0F172A;'>Mumbai_01</span></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Now call them
styles.apply_styles()
styles.render_top_bar()
styles.how_it_works_banner()


tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Forensic Scanner",
    "📝 Request Access",
    "🔐 Organisation Portal",
    "⚙️ Admin Panel"
])

# ══════════════════════════════════════════
# TAB 1 — FORENSIC SCANNER (PUBLIC)
# ══════════════════════════════════════════
with tab1:
    styles.section_header(
        "Forensic Content Scanner",
        "Upload any image to check for IP violations and AI manipulation — no login required"
    )
    styles.info_card(
        "🔍 This scanner is publicly accessible. Upload a suspected unauthorized copy and "
        "MediaGuard will cross-reference it against the entire registered vault using "
        "four forensic algorithms, then analyse it for AI or digital manipulation."
    )

    suspected_file = st.file_uploader(
        "Upload Suspected Image",
        type=["jpg", "jpeg", "png", "avif", "webp"],
        key="public_check"
    )
    suspected_img = None
    suspected_bytes = None

    if suspected_file is not None:
        suspected_bytes = suspected_file.read()
        is_valid, file_format = validate_bytes(suspected_bytes)
        if not is_valid:
            st.error("❌ Invalid file — only genuine image files accepted (JPG, PNG, WEBP, AVIF).")
        else:
            suspected_img = safe_open_image(suspected_bytes)
            col_prev, col_info = st.columns([2, 1])
            with col_prev:
                st.image(suspected_img, caption="Uploaded image", use_container_width=True)
            with col_info:
                st.markdown(f"""
                <div style='background:#161b22; border:1px solid #30363d;
                            border-radius:10px; padding:20px; margin-top:10px;'>
                    <p style='color:#8b949e; font-size:12px; margin:0;'>FILE FORMAT</p>
                    <p style='color:#58a6ff; font-size:18px; font-weight:700; margin:4px 0 16px 0;'>{file_format.upper()}</p>
                    <p style='color:#8b949e; font-size:12px; margin:0;'>FILE NAME</p>
                    <p style='color:#e6edf3; font-size:13px; margin:4px 0 16px 0;'>{suspected_file.name}</p>
                    <p style='color:#8b949e; font-size:12px; margin:0;'>STATUS</p>
                    <p style='color:#3fb950; font-size:13px; font-weight:600; margin:4px 0 0 0;'>✓ Valid — Ready for analysis</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Run Forensic Analysis", use_container_width=True, key="analyse_public"):
        if suspected_img is None:
            st.error("Please upload a valid image first.")
        else:
            with st.spinner("Running forensic analysis — scanning vault and detecting manipulation..."):
                suspected_hashes = engine.get_hashes(suspected_bytes)
                assets = db_mgr.get_all_assets()
                ela_img, manip_score = engine.perform_ela(suspected_img)
                manip_verdict, manip_color, manip_level = engine.get_manipulation_verdict(manip_score)

            if not assets:
                st.warning("⚠️ The vault is currently empty. No registered assets to compare against.")
            else:
                results = []
                for asset in assets:
                    p, a, d = engine.compare_hashes(suspected_hashes, asset["hashes"])
                    ssim_sim = 0.0
                    if asset.get("img_data"):
                        try:
                            ssim_sim = engine.calculate_ssim(
                                suspected_bytes, base64.b64decode(asset["img_data"]))
                        except Exception:
                            pass
                    weighted = engine.calculate_weighted_similarity(
                        p, a, d, ssim_sim, has_original=bool(asset.get("img_data")))
                    results.append({
                        "asset_name": asset["asset_name"],
                        "org_name": asset["org_name"],
                        "registered_at": asset["registered_at"],
                        "p_sim": p, "a_sim": a, "d_sim": d,
                        "ssim_sim": ssim_sim, "similarity": weighted
                    })

                results.sort(key=lambda x: x["similarity"], reverse=True)
                best = results[0]
                sim = best["similarity"]
                verdict, color, risk_level, plain = engine.get_violation_verdict(sim)

                st.markdown("---")
                styles.section_header("Analysis Results")

                # Vault stats
                styles.stat_row([
                    ("Assets Scanned", str(len(assets)), "#58a6ff"),
                    ("Best Match Score", f"{sim:.1f}%", color),
                    ("Risk Level", risk_level, color),
                    ("Manipulation", manip_level, manip_color),
                ])

                st.markdown("<br>", unsafe_allow_html=True)

                # Copyright result
                st.markdown("#### 📊 Copyright Violation Assessment")
                styles.result_card(verdict, color, best['asset_name'], best['org_name'], sim)
                styles.info_card(f"📋 <b>What this means:</b> {plain}", color="#0d1f2d", border=color)

                # Metrics
                st.markdown("<br>", unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Perceptual Hash", f"{best['p_sim']:.1f}%")
                m2.metric("Average Hash", f"{best['a_sim']:.1f}%")
                m3.metric("Difference Hash", f"{best['d_sim']:.1f}%")
                m4.metric("Structural (SSIM)", f"{best['ssim_sim']:.1f}%")

                # ELA
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 🔬 AI Manipulation Detection")
                ela_col1, ela_col2 = st.columns(2)
                with ela_col1:
                    st.image(suspected_img, caption="Original upload", use_container_width=True)
                with ela_col2:
                    st.image(ela_img, caption="ELA Heatmap — brighter = more edited",
                             use_container_width=True)
                styles.manip_card(manip_verdict, manip_color, manip_score, manip_level)

                # Technical details
                with st.expander("🔬 View Full Technical Details"):
                    st.markdown(f"""
                    **Vault Scan:** {len(assets)} registered asset(s) checked

                    | Algorithm | Score | What It Examines |
                    |-----------|-------|-----------------|
                    | pHash | {best['p_sim']:.1f}% | Overall visual structure & composition |
                    | aHash | {best['a_sim']:.1f}% | Brightness & tone distribution |
                    | dHash | {best['d_sim']:.1f}% | Edge patterns & gradients |
                    | SSIM | {best['ssim_sim']:.1f}% | Pixel-level match vs stored original |

                    **Final Score:** (pHash×0.45 + aHash×0.35 + dHash×0.20) × 0.70 + SSIM × 0.30 = **{sim:.1f}%**

                    **ELA Score:** {manip_score:.2f} → {manip_level} manipulation likelihood

                    **Legal Basis:**
                    - IT Act 2000 §66 — unauthorized reproduction of digital assets
                    - BSA 2023 §63 — this report is admissible as electronic evidence
                    - Copyright Act 1957 — sports media is protected intellectual property
                    """)

                # PDF Download
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 📄 Forensic Evidence Report")
                styles.info_card(
                    "The report below is formatted as a forensic evidence document admissible "
                    "under BSA 2023 Section 63. It includes a plain English summary, technical "
                    "analysis tables, manipulation findings, and applicable legal references."
                )
                pdf_buf = engine.generate_report_pdf(
                    best, sim, risk_level, manip_verdict, manip_score, suspected_file.name)
                st.download_button(
                    "⬇️ Download Forensic Evidence Report (PDF)",
                    data=pdf_buf,
                    file_name=f"MediaGuard_Evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# ══════════════════════════════════════════
# TAB 2 — REQUEST ACCESS
# ══════════════════════════════════════════
with tab2:
    styles.section_header("Rights Holder Access Management")
    t_apply, t_status = st.tabs(["📋 Apply for Vault Access", "🔎 Check Application Status"])

    with t_apply:
        styles.info_card(
            "Submit an access request if you are a sports organisation, broadcaster, "
            "or official media rights holder. Once approved by our admin team, you will "
            "receive a unique access code, password, and 2FA secret to log into the vault."
        )
        with st.form("access_form"):
            c1, c2 = st.columns(2)
            with c1:
                org_name_req = st.text_input("Organisation Name *", placeholder="e.g. BCCI, FIFA")
                contact_name = st.text_input("Contact Person *", placeholder="e.g. Rahul Sharma")
            with c2:
                contact_email = st.text_input("Official Email *", placeholder="e.g. rahul@bcci.tv")
                org_type = st.selectbox("Organisation Type", [
                    "Sports Board / Federation", "Official Broadcaster",
                    "OTT Platform", "News Agency", "Sports Club / Team", "Other"
                ])
            reason = st.text_area("Why do you need access?",
                                   placeholder="Briefly describe your use case...")
            if st.form_submit_button("Submit Application →", use_container_width=True):
                if not org_name_req or not contact_name or not contact_email:
                    st.error("Please fill all required fields marked with *")
                else:
                    ok, msg = db_mgr.submit_request(
                        org_name_req, contact_name, contact_email, org_type, reason)
                    if ok:
                        st.success(
                            "✅ Application submitted successfully. Our team will review "
                            "within 1–2 business days. Use the status checker tab to track progress."
                        )
                    else:
                        st.warning(msg)

    with t_status:
        styles.info_card("Enter the email you used when applying to check your status.")
        email_check = st.text_input("Registered Email Address", key="status_email")
        if st.button("Check My Status →", use_container_width=True):
            if not email_check:
                st.error("Please enter your email.")
            else:
                res = db_mgr.check_request_status(email_check)
                if res["status"] == "approved":
                    st.balloons()
                    st.success(
                        f"✅ **Approved!** Your organisation **{res['org_name']}** has been onboarded. "
                        "Your access code, password, and 2FA setup instructions have been "
                        "shared by our admin team. Use them to log in via the Organisation Portal."
                    )
                elif res["status"] == "pending":
                    st.warning("⏳ Your application is under review. Please check back in 24 hours.")
                elif res["status"] == "rejected":
                    st.error("❌ Your application was not approved. Please contact our team.")
                else:
                    st.error("❌ No application found for this email. Please submit a request first.")

# ══════════════════════════════════════════
# TAB 3 — ORGANISATION PORTAL
# ══════════════════════════════════════════
with tab3:

    # ── LOGGED IN DASHBOARD ──
    if st.session_state.role == "org":
        col_title, col_logout = st.columns([4, 1])
        with col_title:
            styles.section_header(
                f"🏢 {st.session_state.org_name}",
                "Organisation Vault Portal"
            )
        with col_logout:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Logout", key="org_logout"):
                for k in ["role","org_id","org_name","org_data","org_step"]:
                    st.session_state[k] = "public" if k == "role" else ("login" if k == "org_step" else None)
                st.rerun()

        if st.session_state.org_data and st.session_state.org_data.get("status") == "suspended":
            st.error("⛔ Your account has been suspended. Please contact MediaGuard admin.")
            st.stop()

        styles.info_card(
            f"Welcome, <b>{st.session_state.org_name}</b>. "
            "Register your official media below. Only your organisation's assets are visible here. "
            "Original images are stored securely for SSIM forensic comparison.",
            color="#0d1f12", border="#3fb950"
        )

        st.markdown("---")
        styles.section_header("📤 Register Media to Vault")

        asset_prefix = st.text_input(
            "Collection / Match Name *",
            placeholder="e.g. IPL 2026 — RCB vs KKR Match 12"
        )
        upload_mode = st.radio("Upload Method", [
            "📁 Select Multiple Images", "🗜️ Upload ZIP Folder"])

        images_to_register = []

        if upload_mode == "📁 Select Multiple Images":
            up_files = st.file_uploader(
                "Select Images", type=["jpg", "jpeg", "png", "avif", "webp"],
                accept_multiple_files=True, key="org_upload")
            if up_files:
                for f in up_files:
                    fb = f.read()
                    ok, _ = validate_bytes(fb)
                    if ok: images_to_register.append((f.name, fb))
                    else: st.warning(f"⚠️ Skipped {f.name} — invalid file.")
        else:
            zf = st.file_uploader("Upload ZIP Folder", type=["zip"], key="org_zip")
            if zf:
                with zipfile.ZipFile(io.BytesIO(zf.read())) as z:
                    for name in z.namelist():
                        if name.startswith('__MACOSX') or name.startswith('.'): continue
                        if not name.lower().endswith(('.jpg','.jpeg','.png','.webp','.avif')): continue
                        fb = z.read(name)
                        ok, _ = validate_bytes(fb)
                        if ok: images_to_register.append((name, fb))
                        else: st.warning(f"⚠️ Skipped {name}")

        if images_to_register:
            styles.info_card(f"✅ <b>{len(images_to_register)}</b> valid image(s) ready to register.")
            prev_cols = st.columns(min(len(images_to_register), 4))
            for i, (fn, fb) in enumerate(images_to_register[:4]):
                with prev_cols[i]:
                    st.image(safe_open_image(fb), caption=fn[:20], use_container_width=True)
            if len(images_to_register) > 4:
                st.caption(f"...and {len(images_to_register)-4} more images.")

        if st.button("🔐 Fingerprint & Register to Vault", use_container_width=True, key="org_reg"):
            if not asset_prefix:
                st.error("Please enter a collection/match name.")
            elif not images_to_register:
                st.error("Please upload at least one image.")
            else:
                prog = st.progress(0)
                ok_count = 0
                for i, (fn, fb) in enumerate(images_to_register):
                    try:
                        db_mgr.register_asset(
                            st.session_state.org_id, st.session_state.org_name,
                            f"{asset_prefix} — {fn}", fn, engine.get_hashes(fb), fb)
                        ok_count += 1
                    except Exception as e:
                        st.warning(f"Failed: {fn} — {e}")
                    prog.progress((i+1)/len(images_to_register))
                st.success(f"✅ {ok_count} of {len(images_to_register)} assets registered.")
                st.balloons()

        st.markdown("---")
        styles.section_header("📦 Your Vault")
        org_assets = db_mgr.get_org_assets(st.session_state.org_id)
        if org_assets:
            st.caption(f"{len(org_assets)} asset(s) registered by {st.session_state.org_name}.")
            for asset in org_assets:
                st.markdown(
                    f"<div style='padding:8px 12px; background:#161b22; border-radius:6px; "
                    f"margin-bottom:4px; border-left:3px solid #2471a3;'>"
                    f"<span style='color:#e6edf3;'><b>{asset['asset_name']}</b></span> "
                    f"<span style='color:#8b949e; font-size:12px;'>— {asset['registered_at'][:10]}</span>"
                    f"</div>", unsafe_allow_html=True)
        else:
            st.info("No assets registered yet. Upload your first collection above.")

    # ── 2FA STEP ──
    elif st.session_state.org_step == "2fa":
        styles.section_header("🛡️ Two-Factor Authentication")
        styles.info_card(
            "Open your <b>Google Authenticator</b> app and enter the 6-digit code for MediaGuard. "
            "First time? Expand the section below to scan your QR code."
        )

        org = st.session_state.org_data
        totp_uri = engine.get_totp_uri(org["totp_secret"], org["name"])

        with st.expander("📱 First login? Set up Google Authenticator"):
            try:
                import qrcode
                qr = qrcode.make(totp_uri)
                qr_buf = io.BytesIO()
                qr.save(qr_buf, format="PNG")
                qr_buf.seek(0)
                c1, c2, c3 = st.columns([1,2,1])
                with c2:
                    st.image(qr_buf, caption="Scan in Google Authenticator", use_container_width=True)
            except ImportError:
                st.code(totp_uri)
                st.caption("Copy this URI into Google Authenticator manually.")

        otp = st.text_input("Enter 6-digit code", max_chars=6, placeholder="000000")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Verify & Enter Portal", use_container_width=True):
                if engine.verify_totp(org["totp_secret"], otp):
                    st.session_state.role = "org"
                    st.session_state.org_id = org["id"]
                    st.session_state.org_name = org["name"]
                    st.session_state.org_step = "login"
                    st.rerun()
                else:
                    st.error("❌ Invalid code. Make sure your phone time is synced.")
        with c2:
            if st.button("← Back to Login", use_container_width=True):
                st.session_state.org_step = "login"
                st.session_state.org_data = None
                st.rerun()

    # ── LOGIN ──
    else:
        styles.section_header("🔐 Organisation Login",
                               "Approved organisations only")
        styles.info_card(
            "Enter your access code and password to continue. "
            "Don't have access yet? Submit a request in the <b>Request Access</b> tab."
        )
        c1, c2 = st.columns(2)
        with c1:
            code_in = st.text_input("Access Code", placeholder="MG-XXXXXXXX")
        with c2:
            pwd_in = st.text_input("Password", type="password")

        if st.button("Login →", use_container_width=True, key="org_login"):
            if not code_in or not pwd_in:
                st.error("Please enter both access code and password.")
            else:
                org = db_mgr.get_org_by_access_code(code_in)
                if not org:
                    st.error("❌ Invalid access code.")
                elif org.get("status") == "suspended":
                    st.error("⛔ This account has been suspended. Contact MediaGuard admin.")
                elif db_mgr.verify_password(pwd_in, org["password_hash"]):
                    st.session_state.org_data = org
                    st.session_state.org_step = "2fa"
                    st.rerun()
                else:
                    st.error("❌ Incorrect password.")

# ══════════════════════════════════════════
# TAB 4 — ADMIN PANEL
# ══════════════════════════════════════════
with tab4:
    if st.session_state.role == "admin":
        col_t, col_l = st.columns([4, 1])
        with col_t:
            styles.section_header("⚙️ Master Admin Dashboard",
                                   "Full control over all organisations, assets, and requests")
        with col_l:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Logout", key="admin_out"):
                st.session_state.role = "public"
                st.rerun()

        styles.info_card(
            "You are logged in as <b>Super Admin</b>. "
            "All operations here are permanent. Proceed with care.",
            color="#1f0d0d", border="#e74c3c"
        )

        a1, a2, a3 = st.tabs([
            "📥 Pending Requests",
            "🏢 Organisations",
            "📦 All Assets"
        ])

        # ── PENDING REQUESTS ──
        with a1:
            styles.section_header("Pending Access Requests")
            reqs = db_mgr.get_pending_requests()
            if not reqs:
                st.info("No pending requests at the moment.")
            else:
                for req in reqs:
                    with st.expander(
                        f"🟡 {req['org_name']} — {req['contact_name']} ({req['submitted_at'][:10]})"
                    ):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write(f"**Email:** {req['contact_email']}")
                            st.write(f"**Type:** {req['org_type']}")
                        with c2:
                            st.write(f"**Submitted:** {req['submitted_at'][:10]}")
                            st.write(f"**Reason:** {req['reason']}")

                        new_pwd = st.text_input(
                            "Set password for this organisation",
                            key=f"pwd_{req['id']}", type="password",
                            placeholder="Min 8 characters"
                        )
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("✅ Approve & Onboard", key=f"app_{req['id']}"):
                                if not new_pwd or len(new_pwd) < 8:
                                    st.error("Password must be at least 8 characters.")
                                else:
                                    code, secret = db_mgr.approve_request(req["id"], req, new_pwd)
                                    st.success(f"""
✅ **{req['org_name']}** onboarded successfully!

Share these credentials securely with the organisation:
- **Access Code:** `{code}`
- **Password:** *(the one you just set)*
- **2FA Secret:** `{secret}`
*(They scan this in Google Authenticator on first login)*
                                    """)
                        with b2:
                            if st.button("❌ Reject", key=f"rej_{req['id']}"):
                                db_mgr.reject_request(req["id"])
                                st.warning(f"Request from {req['org_name']} rejected.")
                                st.rerun()

        # ── ORGANISATIONS ──
        with a2:
            styles.section_header("Active Organisations")
            orgs = db_mgr.get_all_orgs()
            if not orgs:
                st.info("No organisations approved yet.")
            else:
                for org in orgs:
                    count = db_mgr.get_org_asset_count(org["id"])
                    status = org.get("status", "active")
                    emoji = "🟢" if status == "active" else "🔴"
                    with st.expander(
                        f"{emoji} {org['name']} — {count} asset(s) | {status.upper()}"
                    ):
                        # Current info
                        ci1, ci2 = st.columns(2)
                        with ci1:
                            st.write(f"**Access Code:** `{org['access_code']}`")
                            st.write(f"**Contact:** {org.get('contact_name','N/A')}")
                            st.write(f"**Email:** {org.get('contact_email','N/A')}")
                        with ci2:
                            st.write(f"**Approved:** {org.get('approved_at','N/A')[:10]}")
                            st.write(f"**2FA Secret:** `{org.get('totp_secret','N/A')}`")
                            if org.get("contact_updated_at"):
                                st.write(f"**Contact Updated:** {org['contact_updated_at'][:10]}")

                        st.markdown("---")

                        # ── ORG ADMIN MANAGEMENT (Point 3) ──
                        st.markdown("**🔧 Admin Management** — use when the organisation's admin leaves or changes")

                        with st.expander("👤 Update Contact Person"):
                            new_cn = st.text_input("New Contact Name", key=f"cn_{org['id']}")
                            new_ce = st.text_input("New Contact Email", key=f"ce_{org['id']}")
                            if st.button("Update Contact", key=f"uc_{org['id']}"):
                                if new_cn and new_ce:
                                    db_mgr.update_org_contact(org["id"], new_cn, new_ce)
                                    st.success(f"✅ Contact updated to {new_cn} ({new_ce})")
                                    st.rerun()
                                else:
                                    st.error("Please fill both fields.")

                        with st.expander("🔑 Reset Password"):
                            new_p = st.text_input("New Password", type="password",
                                                   key=f"rp_{org['id']}")
                            if st.button("Reset Password", key=f"rpb_{org['id']}"):
                                if new_p and len(new_p) >= 8:
                                    db_mgr.reset_org_password(org["id"], new_p)
                                    st.success("✅ Password reset. Share the new password securely with the org.")
                                else:
                                    st.error("Password must be at least 8 characters.")

                        with st.expander("🔐 Regenerate Access Code"):
                            st.warning("This will invalidate the current access code.")
                            if st.button("Generate New Code", key=f"rac_{org['id']}"):
                                new_code = db_mgr.regenerate_org_access_code(org["id"])
                                st.success(f"✅ New access code: `{new_code}` — share this with the organisation.")

                        with st.expander("📱 Reset 2FA — if admin lost their phone"):
                            st.warning("This will invalidate the current 2FA setup.")
                            if st.button("Reset 2FA Secret", key=f"r2fa_{org['id']}"):
                                new_s = db_mgr.regenerate_org_2fa(org["id"])
                                st.success(
                                    f"✅ New 2FA Secret: `{new_s}` — "
                                    "the organisation must scan this in Google Authenticator on next login."
                                )

                        st.markdown("---")
                        b1, b2 = st.columns(2)
                        with b1:
                            label = "⏸️ Suspend Organisation" if status == "active" else "▶️ Reactivate"
                            if st.button(label, key=f"tog_{org['id']}"):
                                db_mgr.toggle_org_status(org["id"], status)
                                st.rerun()
                        with b2:
                            if st.button("🗑️ Permanently Revoke Access", key=f"rev_{org['id']}"):
                                db_mgr.revoke_org(org["id"])
                                st.warning(f"Access permanently revoked for {org['name']}.")
                                st.rerun()

        # ── ALL ASSETS ──
        with a3:
            styles.section_header("All Registered Assets")
            all_assets = db_mgr.get_all_assets()
            if all_assets:
                st.caption(f"{len(all_assets)} total asset(s) across all organisations.")
                for asset in all_assets:
                    st.markdown(
                        f"<div style='padding:8px 12px; background:#161b22; border-radius:6px; "
                        f"margin-bottom:4px; border-left:3px solid #2471a3;'>"
                        f"<b style='color:#e6edf3;'>{asset['asset_name']}</b> "
                        f"<span style='color:#58a6ff;'>— {asset['org_name']}</span> "
                        f"<span style='color:#8b949e; font-size:12px;'>— {asset['registered_at'][:10]}</span>"
                        f"</div>", unsafe_allow_html=True)
            else:
                st.info("The vault is empty.")

    # ── ADMIN LOGIN ──
    else:
        styles.section_header("⚙️ SuperAdmin Login",
                               "Restricted access — authorised personnel only")
        styles.info_card("🔒 This panel is restricted to MediaGuard administrators only.")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            ap = st.text_input("Master Admin Password", type="password", key="admin_pwd")
            if st.button("Enter Dashboard →", use_container_width=True, key="admin_in"):
                if ap == ADMIN_PASSWORD:
                    st.session_state.role = "admin"
                    st.rerun()
                else:
                    st.error("❌ Incorrect password.")
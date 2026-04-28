import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* 1. Global Reset */
        .main { background-color: #F8FAFC !important; }
        .block-container { 
            max-width: 1000px !important; 
            padding-top: 2rem !important; 
        }

        /* 2. Tabs Fix: Removing that ugly red line & doubling labels */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px;
            background-color: white !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            color: #64748B !important;
            font-weight: 500 !important;
            padding: 0 24px !important;
        }

        /* Active Tab: Sharp Black & Minimalist */
        .stTabs [aria-selected="true"] {
            border: 1.5px solid #0F172A !important;
            color: #0F172A !important;
            background-color: #F8FAFC !important;
        }
        
        /* Removing the default Streamlit red underline */
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: transparent !important;
        }

        /* 3. File Uploader Fix: Killing "uploaupload" */
        [data-testid="stFileUploader"] section {
            background-color: #F1F5F9 !important;
            border: 1px dashed #CBD5E1 !important;
            border-radius: 12px !important;
            padding: 20px !important;
        }

        /* This hides the doubling 'upload' text label */
        [data-testid="stFileUploader"] label {
            display: none !important;
        }

        /* 4. Action Button: High Contrast Professional */
        div.stButton > button {
            background-color: #0F172A !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            height: 52px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.2s ease;
        }

        div.stButton > button:hover {
            background-color: #1E293B !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        }

        /* 5. Blue Sidebar Info Box */
        .info-box {
            background: #EFF6FF;
            border-left: 4px solid #3B82F6;
            padding: 20px;
            border-radius: 8px;
            color: #1E40AF;
            font-size: 14px;
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)

def render_top_bar():
    st.markdown("""
        <div style='display: flex; justify-content: space-between; align-items: center; 
                    background: white; padding: 18px 30px; border-radius: 12px; 
                    border: 1px solid #E2E8F0; margin-bottom: 30px;'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div style='background: #0F172A; color: white; padding: 10px; border-radius: 10px; font-size: 20px;'>🛡️</div>
                <h1 style='margin:0; font-size: 20px; font-weight: 700; color: #0F172A;'>MediaGuard <span style='font-weight:400; color:#94A3B8;'>Forensics</span></h1>
            </div>
            <div style='display: flex; gap: 20px; align-items: center;'>
                <span style='font-size: 13px; color: #10B981; font-weight: 600;'>● Node: Mumbai_01</span>
                <span style='font-size: 13px; color: #64748B;'>Status: Active</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def how_it_works_banner():
    st.markdown("""
        <style>
            .step-container {
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: white;
                padding: 24px;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                margin-bottom: 30px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.02);
            }
            .step-card {
                flex: 1;
            }
            .step-arrow {
                padding: 0 15px;
                color: #CBD5E1;
                display: flex;
                align-items: center;
                justify-content: center;
            }
        </style>
        
        <div class='step-container'>
            <div class='step-card'>
                <p style='color:#6366F1; font-weight:700; font-size:11px; margin:0; letter-spacing:1px;'>01 REGISTER</p>
                <h4 style='margin:2px 0; color:#0F172A; font-size:16px;'>Register</h4>
                <p style='font-size:12px; color:#64748B; margin:0;'>Upload media to vault</p>
            </div>
            
            <div class='step-card'>
                <p style='color:#6366F1; font-weight:700; font-size:11px; margin:0; letter-spacing:1px;'>02 DETECT</p>
                <h4 style='margin:2px 0; color:#0F172A; font-size:16px;'>Detect</h4>
                <p style='font-size:12px; color:#64748B; margin:0;'>Scan suspected copies</p>
            </div>

            <div class='step-card'>
                <p style='color:#6366F1; font-weight:700; font-size:11px; margin:0; letter-spacing:1px;'>03 ANALYSE</p> 
                <h4 style='margin:2px 0; color:#0F172A; font-size:16px;'>Analyse</h4>
                <p style='font-size:12px; color:#64748B; margin:0;'>Find AI manipulation</p>
            </div>

            <div class='step-card'>
                <p style='color:#6366F1; font-weight:700; font-size:11px; margin:0; letter-spacing:1px;'>04 REPORT</p>
                <h4 style='margin:2px 0; color:#0F172A; font-size:16px;'>Report</h4>
                <p style='font-size:12px; color:#64748B; margin:0;'>Download legal PDF</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def section_header(title, subtitle=""):
    st.markdown(f"""
        <div style="margin-bottom: 24px;">
            <h2 style="font-size: 28px; font-weight: 700; color: #0F172A; letter-spacing: -0.5px; margin-bottom: 4px;">{title}</h2>
            <p style="color: #64748B; font-size: 16px;">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def info_card(text, color="#2563EB"):
    st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #E5E7EB; 
                    border-left: 4px solid {color}; padding: 16px; 
                    border-radius: 8px; margin: 16px 0;">
            <span style="color: #374151; font-size: 14px;">{text}</span>
        </div>
    """, unsafe_allow_html=True)

def how_it_works_banner():
    steps = [
        ("01", "Register", "Upload official media into the secure vault"),
        ("02", "Detect", "Scan suspected copies against the vault"),
        ("03", "Analyse", "Find AI edits and manipulation scores"),
        ("04", "Report", "Download legal forensic PDF evidence")
    ]
    cols = st.columns(4)
    for i, (num, title, desc) in enumerate(steps):
        with cols[i]:
            st.markdown(f"""
                <div class="step-card">
                    <p style="color:var(--blue); font-weight:800; font-size:11px; margin:0; letter-spacing:2px;">{num}</p>
                    <h3 style="margin: 12px 0 8px; font-size:18px; color:#f0f6fc !important;">{title}</h3>
                    <p style="font-size:13px; line-height:1.5; color:#8b949e;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# def section_header(title, subtitle=None):
#     sub = f"<p style='margin-top:4px; font-size:14px; color:#8b949e;'>{subtitle}</p>" if subtitle else ""
#     st.markdown(f"<div style='margin: 32px 0 16px;'><h2>{title}</h2>{sub}</div>", unsafe_allow_html=True)

# def info_card(text, color="#161b22", border="#30363d"):
#     st.markdown(f"""
#         <div style="background:{color}; border:1px solid {border}; border-radius:10px; padding:18px; color:#c9d1d9; font-size:14px; line-height:1.6; margin-bottom:24px;">
#             {text}
#         </div>
#     """, unsafe_allow_html=True)

def stat_row(items):
    cols = st.columns(len(items))
    for i, (label, value, color) in enumerate(items):
        with cols[i]:
            st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-lbl">{label}</p>
                    <p class="metric-val" style="color:{color}">{value}</p>
                </div>
            """, unsafe_allow_html=True)

def result_card(verdict, color, match_name, org, sim):
    st.markdown(f"""
        <div style="background:#0d1117; border:1px solid {color}66; border-left:4px solid {color}; border-radius:12px; padding:28px; margin:20px 0;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:18px;">
                <span style="height:8px; width:8px; border-radius:50%; background:{color}; box-shadow: 0 0 10px {color};"></span>
                <span style="font-size:12px; font-weight:800; text-transform:uppercase; color:{color}; letter-spacing:1.5px;">{verdict}</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                <div>
                    <h3 style="margin:0; font-size:22px; color:#f0f6fc !important;">{match_name}</h3>
                    <p style="margin:6px 0 0; color:#8b949e; font-size:14px;">Rights Holder: <b style="color:#58a6ff;">{org}</b></p>
                </div>
                <div style="text-align:right;">
                    <p style="margin:0; font-size:48px; font-weight:800; color:{color}; line-height:0.9;">{sim:.1f}<span style="font-size:20px;">%</span></p>
                    <p style="margin:8px 0 0; font-size:10px; color:#8b949e; font-weight:700; letter-spacing:1px;">SIMILARITY SCORE</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def manip_card(verdict, color, score, level):
    st.markdown(f"""
        <div style="background:#161b22; border:1px solid var(--border); border-radius:12px; padding:24px; margin-top:20px; display:flex; justify-content:space-between; align-items:center;">
            <div style="max-width: 70%;">
                <p style="margin:0; font-size:16px; font-weight:700; color:{color};">{verdict}</p>
                <p style="margin:6px 0 0; font-size:13px; color:#8b949e; line-height:1.5;">Error Level Analysis (ELA) detected pixel-level inconsistencies indicative of digital manipulation or AI re-generation.</p>
            </div>
            <div style="text-align:right;">
                <p style="margin:0; font-size:36px; font-weight:800; color:{color};">{score:.1f}</p>
                <p style="margin:4px 0 0; font-size:10px; color:#8b949e; font-weight:700; letter-spacing:1px;">ELA SCORE</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
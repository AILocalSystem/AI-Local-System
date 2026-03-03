import streamlit as st
import pandas as pd
import os
import time
import sys

# Ensure gbp_architect can be found if running from subfolder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from gbp_architect import execute_profile_repair_pipeline
    from content_strategist import ContentStrategist
    from branding_engine import get_client_branding, apply_branding_to_ui
    from report_generator import generate_monthly_roi_report
    from outreach_scout import OutreachScout
    from payment_gateway import PaymentGateway, render_locked_feature_ui
except ImportError:
    # If starting directly in root
    from gbp_architect import execute_profile_repair_pipeline
    from content_strategist import ContentStrategist
    from branding_engine import get_client_branding, apply_branding_to_ui
    from report_generator import generate_monthly_roi_report
    from outreach_scout import OutreachScout
    from payment_gateway import PaymentGateway, render_locked_feature_ui


st.set_page_config(
    page_title="Founder's God View | Admin Master",
    page_icon="👑",
    layout="wide"
)

# ==============================================================================
# ADMIN-ONLY AUTHENTICATION & NOTIFICATIONS
# ==============================================================================
ADMIN_EMAIL = "demo.client@example.com" # Specific authorized Google email

def broadcast_to_admin_channel(payload):
    """
    Mock integration for sending high-priority alerts to the Admin via WhatsApp/Slack.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"🔔 [ADMIN BROADCAST]: {payload['title']} | {payload['message']}")
    return True

def trigger_admin_gold_alert(client_data, site_preview_url):
    """
    Sends a high-priority alert to the Admin when a website is claimed. 
    """
    alert_payload = {
        "priority": "GOLD",
        "title": "🚨 HIGH-TICKET ALERT: Website Claimed",
        "message": f"Client {client_data.get('name', 'A Client')} has approved their AI storefront.",
        "meta": {
            "niche": client_data.get('primary_category', 'Business'),
            "location": client_data.get('city', 'Unknown'),
            "preview": site_preview_url
        }
    }
    # This triggers your internal WhatsApp/Notification API
    return broadcast_to_admin_channel(alert_payload)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0F172A; color: #F8FAFC; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; }
    .metric-card { background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 16px; }
    .emerald { color: #10B981; }
    .royal { color: #3B82F6; }
    .amber { color: #F59E0B; }
    /* DataFrame styling for dark mode */
    [data-testid="stDataFrame"] { background-color: #1E293B; border-radius: 8px; padding: 10px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# Require the user to be exactly the logged-in Admin, or provide an override for the demo.
current_user = st.session_state.get('client_email', None)

if current_user != ADMIN_EMAIL:
    st.markdown("<h2 style='text-align: center; color: #EF4444 !important; margin-top: 10vh;'>Access Denied</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>You do not have administrative privileges to view the Sovereign Fleet Control Center.</p>", unsafe_allow_html=True)
    
    # Dev bypass for testing
    with st.expander("Admin Override Login"):
        bypass_email = st.text_input("Enter Admin Email:")
        if st.button("Authenticate Route"):
            if bypass_email == ADMIN_EMAIL:
                st.session_state.client_email = bypass_email
                st.rerun()
            else:
                st.error("Invalid Credentials.")
    st.stop()

# ==============================================================================
# GLOBAL METRICS LOGIC (MOCK FLEET AGGREGATION)
# ==============================================================================
# In production, this aggregates actual data from all provisioned Vaults and the local database.
total_network_revenue = 48500  # Combined attributed revenue
total_active_leads = 124       # Hot leads currently in pipeline
conversion_rate = 18.5         # Auditors who became paying clients

# ==============================================================================
# FLEET MANAGER UI
# ==============================================================================
st.markdown("<h1>👑 Sovereign OS <span class='royal'>God View</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8;'>Centralized Fleet Management & Lead Tracker</p><hr style='border-color: #334155'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <p style="color: #94A3B8; font-size: 0.9em; margin: 0; text-transform: uppercase; font-weight: 500;">Total Network Revenue</p>
            <h1 class="emerald" style="margin: 8px 0; font-size: 2.5em;">${total_network_revenue:,.0f}</h1>
            <p style="color: #10B981; font-weight: 600; font-size: 0.8em; margin: 0;">Across all Active Vaults</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <p style="color: #94A3B8; font-size: 0.9em; margin: 0; text-transform: uppercase; font-weight: 500;">Active Hot Leads</p>
            <h1 class="amber" style="margin: 8px 0; font-size: 2.5em;">{total_active_leads}</h1>
            <p style="color: #F59E0B; font-weight: 600; font-size: 0.8em; margin: 0;">AI Agents Currently Handling</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <p style="color: #94A3B8; font-size: 0.9em; margin: 0; text-transform: uppercase; font-weight: 500;">Auditor Conversion Rate</p>
            <h1 class="royal" style="margin: 8px 0; font-size: 2.5em;">{conversion_rate}%</h1>
            <p style="color: #3B82F6; font-weight: 600; font-size: 0.8em; margin: 0;">Audit -> Paid Client</p>
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# ACTIVE VAULTS (SPOKES)
# ==============================================================================
st.subheader("🌐 Active Sovereign Vaults")
mock_vaults = [
    {"Client": "Prana Flow Yoga", "Owner": "sarah@prana.com", "Industry": "Wellness", "Status": "🟢 Live (Synced)", "Monthly Rev": "$4,200", "Health": 98},
    {"Client": "Acme Plumbing", "Owner": "demo.client@example.com", "Industry": "Home Services", "Status": "🟢 Live (Synced)", "Monthly Rev": "$12,400", "Health": 65},
    {"Client": "Downtown Bistro", "Owner": "chef.mike@bistro.com", "Industry": "Restaurant", "Status": "🟡 Warning (Reviews)", "Monthly Rev": "$8,100", "Health": 72},
    {"Client": "Elite Dental", "Owner": "dr_smith@elite.com", "Industry": "Medical", "Status": "🟢 Live (Synced)", "Monthly Rev": "$23,800", "Health": 99},
]

for idx, vault in enumerate(mock_vaults):
    health = vault["Health"]
    bar_color = "emerald" if health >= 90 else ("amber" if health >= 70 else "red")
    
    with st.container():
        st.markdown(f"""
        <div style="background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 2;">
                <h4 style="margin: 0; color: #F8FAFC;">{vault['Client']} <span style="font-size: 0.8em; color: #94A3B8; font-weight: normal;">| {vault['Industry']}</span></h4>
                <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9em;">Owner: {vault['Owner']} • Rev: {vault['Monthly Rev']}</p>
            </div>
            <div style="flex: 1; text-align: center;">
                <p style="margin: 0; color: #94A3B8; font-size: 0.8em;">Health Score</p>
                <h3 class="{bar_color}" style="margin: 0;">{health}/100</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # The fulfillment trigger
        col_btn, col_status = st.columns([1, 3])
        trigger_key = f"repair_btn_{idx}"
        status_key = f"status_{idx}"
        
        # SUBSCRIPTION GATEKEEPER
        sub_key = f"sub_active_{vault['Client']}"
        if sub_key not in st.session_state:
            # In production, check vault['subscription_active']. Defaulting Mock to False for Demo.
            st.session_state[sub_key] = vault.get('subscription_active', False)
            
        is_subscribed = st.session_state[sub_key]
        
        with col_btn:
            if not is_subscribed:
                st.button("🔒 Execute Profile Repair", disabled=True, key=trigger_key+"_locked", use_container_width=True)
                if st.session_state.get(f"show_repair_upgrade_{idx}", False):
                    render_locked_feature_ui(vault['Client'], "Sovereign Architect (Profile Repair)")
                elif st.button("Unlock Feature", key=f"unlock_repair_{idx}"):
                    st.session_state[f"show_repair_upgrade_{idx}"] = True
                    st.rerun()
            elif health < 90 and st.button("🛠️ Execute Profile Repair", key=trigger_key, use_container_width=True):
                st.session_state[f"running_repair_{idx}"] = True
                
        with col_status:
            if st.session_state.get(f"running_repair_{idx}"):
                # Run the Architect Pipeline Generator
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                pipeline = execute_profile_repair_pipeline(vault['Client'], yield_callbacks=True)
                
                for status_msg, pct in pipeline:
                    if isinstance(status_msg, dict):
                        # Final dictionary payload
                        break
                    status_text.markdown(f"**Status:** {status_msg}")
                    progress_bar.progress(pct)
                
                st.session_state[f"running_repair_{idx}"] = False
                st.session_state[f"repair_done_{idx}"] = True
                st.rerun()
                
            elif st.session_state.get(f"repair_done_{idx}"):
                st.success("✅ Profile Optimized (Score 92/100)")
                
        # The Content Strategist Toggle
        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
        content_key = f"content_toggle_{idx}"
        
        if not is_subscribed:
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; color: #64748B; margin-bottom: 8px;">
                    <span>🔒</span> <span style="text-decoration: line-through;">Activate 30-Day Content Calendar</span>
                </div>
            """, unsafe_allow_html=True)
            if st.session_state.get(f"show_content_upgrade_{idx}", False):
                 render_locked_feature_ui(vault['Client'], "Content Strategist (Auto-Posting)")
            elif st.button("Unlock Feature", key=f"unlock_content_{idx}"):
                 st.session_state[f"show_content_upgrade_{idx}"] = True
                 st.rerun()
        else:
            is_content_active = st.toggle("📅 Activate 30-Day Content Calendar", key=content_key)
            
            if is_content_active:
                with st.container():
                    st.markdown("<div style='background: #0F172A; border: 1px dashed #334155; padding: 12px; border-radius: 6px; margin-top: 8px;'>", unsafe_allow_html=True)
                    
                    # Fetch mock prediction from the Content Strategist
                    strategist = ContentStrategist(business_name=vault['Client'], niche=vault['Industry'])
                    calendar = strategist.generate_30_day_calendar()
                    next_post = strategist.extract_next_ideal_post(calendar)
                    
                    col_post, col_stat = st.columns([3, 1])
                    with col_post:
                        st.markdown(f"<p style='margin:0; font-size:0.85em; color: #94A3B8;'>Next Auto-Post ({next_post['scheduled_for']})</p>", unsafe_allow_html=True)
                        st.markdown(f"**{next_post['title']}**", unsafe_allow_html=True)
                    with col_stat:
                        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
                        st.markdown(f"<span style='background: #047857; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.7em; font-weight: bold;'>🟢 {next_post['status']}</span>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    st.markdown("</div>", unsafe_allow_html=True)
                
        # White-Label & PDF Engine
        with st.expander("🎨 Client Identity & Reporting"):
            st.markdown(f"<p style='color: #94A3B8; font-size: 0.9em;'>Manage White-Label Settings for <b>{vault['Client']}</b></p>", unsafe_allow_html=True)
            
            # Logo Upload (Mock)
            uploaded_logo = st.file_uploader(f"Upload High-Res Logo ({vault['Client']})", type=['png', 'jpg', 'svg'], key=f"logo_{idx}")
            if uploaded_logo:
                st.success(f"Logo '{uploaded_logo.name}' permanently saved to Sovereign Vault.")
                time.sleep(1)
            
            st.markdown("<hr style='border-color: #334155; margin: 12px 0;'>", unsafe_allow_html=True)
            
            # Preview Client Report Button
            if st.button(f"👁️ Preview Monthly ROI Report", key=f"preview_report_{idx}", use_container_width=True):
                st.info(f"Generating Executive ROI Summary for {vault['Client']}...")
                
                # Mock generating a preview pulling from the actual report generator
                branding = get_client_branding(vault['Owner'])
                mock_revenue = int(vault['Monthly Rev'].replace("$", "").replace(",", ""))
                mock_reviews = [{"rating": 5}, {"rating": 5}, {"rating": 5}] # Mock data for the preview
                mock_pipeline = [{"name": "Lead A", "warmth": 10}, {"name": "Lead B", "warmth": 8}]
                
                report_bytes = generate_monthly_roi_report(branding, mock_revenue, mock_reviews, mock_pipeline)
                
                # Render the raw text as code for the Admin to preview
                report_content = report_bytes.getvalue().decode('utf-8')
                st.code(report_content, language="markdown")
                
                st.download_button(
                    label="📥 Download PDF Alternative (.txt)",
                    data=report_bytes,
                    file_name=f"{branding['business_name'].replace(' ', '_')}_Preview.txt",
                    mime="text/plain",
                    key=f"dl_preview_{idx}"
                )
        
        # Social Proof / Case Study Generator (Only for Healthy > 90)
        if health >= 90:
            st.markdown("<hr style='border-color: #334155; margin: 12px 0;'>", unsafe_allow_html=True)
            if st.button("📸 Generate Case Study Asset", key=f"case_study_{idx}", use_container_width=True):
                with st.spinner(f"Compiling Win Metrics for {vault['Client']}..."):
                    engine = CaseStudyEngine(vault['Client'], vault['Monthly Rev'], health)
                    study_data = engine.compile_case_study_data()
                    html_asset = engine.generate_html_asset(study_data)
                
                st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
                st.components.v1.html(html_asset, height=450)
                st.success("✅ Case Study Generated! Ready for LinkedIn & Cold Email Outreach.")
                
        st.write("") # Spacer

st.markdown("<br><hr style='border-color: #334155'><br>", unsafe_allow_html=True)

# ==============================================================================
# OUTREACH SCOUT: LEAD GENERATION ENGINE
# ==============================================================================
st.subheader("🕵️ Outreach Scout (Lead Generator)")
st.caption("Identify struggling local businesses with SEO and Reputation gaps.")

with st.form("scout_search"):
    scout_col1, scout_col2, scout_col3 = st.columns([2, 2, 1])
    with scout_col1:
        target_kw = st.text_input("Target Keyword (e.g., Dentist, Plumber)", placeholder="Plumber")
    with scout_col2:
        target_city = st.text_input("Target City", placeholder="Nagpur")
    with scout_col3:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        search_trigger = st.form_submit_button("🔍 Run Scout", use_container_width=True)

if search_trigger and target_kw and target_city:
    with st.spinner(f"Scouting {target_city} for {target_kw} weaknesses..."):
        scout_engine = OutreachScout(target_kw, target_city)
        prospects = scout_engine.search_for_prospects()
        
    st.success(f"Found {len(prospects)} high-intent prospects.")
    
    # Render the Hit List
    for p_idx, prospect in enumerate(prospects):
        with st.container():
            st.markdown(f"""
            <div style="background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 16px; margin-bottom: 12px; display: flex; align-items: stretch;">
                <div style="flex: 2;">
                    <h5 style="margin: 0; color: #F8FAFC;">{prospect['name']}</h5>
                    <p style="margin: 4px 0 8px 0; color: #94A3B8; font-size: 0.9em;">
                        Reputation: {prospect['rating']}★ ({prospect['reviews']} reviews) | 
                        Web: {prospect['website']} | Phone: {prospect['phone']}
                    </p>
                    <div style="background: #451A1A; border: 1px solid #7F1D1D; border-radius: 4px; padding: 6px 10px; display: inline-block;">
                        <span style="color: #FCA5A5; font-size: 0.8em; font-weight: 600;">⚠️ FLAG: {prospect['deficits']}</span>
                    </div>
                </div>
                <div style="flex: 1; border-left: 1px solid #334155; padding-left: 16px; margin-left: 16px; display: flex; flex-direction: column; justify-content: center;">
                    <p style="margin: 0 0 4px 0; color: #94A3B8; font-size: 0.75em; text-transform: uppercase;">Simulated Red Map Hook</p>
                    <div style="font-family: monospace; font-size: 1.2em; line-height: 1.1; letter-spacing: -2px;">
                        {prospect['geo_grid_mock'].replace(chr(10), '<br>')}
                    </div>
                </div>
                <div style="flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: flex-end;">
                    <button style="background: #2563EB; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: 500; cursor: pointer;">
                        ✉️ Send 10/10 Audit
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: #334155'><br>", unsafe_allow_html=True)

# ==============================================================================
# MASTER LEAD TRACKER
# ==============================================================================
st.subheader("🎯 Master Lead Tracker (The Gold Mine)")
st.caption("Visitors who completed a 10/10 Audit but have not yet authorized the automated fix.")

if os.path.isfile('../master_leads.csv') or os.path.isfile('master_leads.csv'):
    file_path = 'master_leads.csv' if os.path.isfile('master_leads.csv') else '../master_leads.csv'
    try:
        df_leads = pd.read_csv(file_path)
        
        # Style the Warmth Score column
        def style_score(val):
            try:
                score = int(val)
                if score >= 70: return 'color: #10B981; font-weight: bold;'
                if score >= 40: return 'color: #F59E0B;'
                return 'color: #EF4444; font-weight: bold;'
            except:
                return ''

        st.dataframe(
            df_leads.style.map(style_score, subset=['Audit Score']),
            use_container_width=True,
            hide_index=True
        )
    except Exception as e:
        st.error(f"Could not read master_leads.csv: {e}")
else:
    st.info("No leads captured yet. Run an audit on the Onboarding Portal to populate the tracker.")

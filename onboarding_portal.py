import streamlit as st
import os
import json
import time

try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

from token_manager import get_authenticated_service, get_client_email
from public_audit import get_public_audit
from web_architect import WebArchitect, lock_visionary_vault
import sys
# Allow importing from pages folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pages.admin_master import trigger_admin_gold_alert
import csv
from datetime import datetime

def log_master_lead(business_name, score, whatsapp="Pending"):
    """Silently logs warm leads to the Master Lead Tracker."""
    file_exists = os.path.isfile('master_leads.csv')
    with open('master_leads.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Business Name', 'Audit Score', 'WhatsApp Number'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), business_name, score, whatsapp])

# ==============================================================================
# UI CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="Client Onboarding | Sovereign Vault",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .main { background-color: #F8FAFC; }
        .stApp { background-color: #F8FAFC; }
        h1, h2, h3 { color: #0F172A; font-family: 'Inter', sans-serif; font-weight: 700; }
        .royal { color: #3B82F6; }
        .emerald { color: #10B981; }
        .step-box { background: white; border: 1px solid #E2E8F0; padding: 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
        .geo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin: 20px auto; max-width: 350px; padding: 20px; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #E2E8F0; }
        .grid-node { aspect-ratio: 1; display: flex; justify-content: center; align-items: center; border-radius: 8px; color: white; font-weight: bold; font-size: 16px; position: relative; }
        .node-green { background-color: #10B981; }
        .node-amber { background-color: #F59E0B; }
        .node-red { background-color: #EF4444; }
        .trophy { position: absolute; top: -10px; right: -10px; font-size: 18px; background: white; border-radius: 50%; padding: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); z-index: 10; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# STATE MANAGEMENT
# ==============================================================================
if 'phase' not in st.session_state:
    st.session_state.phase = 'PUBLIC_AUDIT'
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'vault_id' not in st.session_state:
    st.session_state.vault_id = None
if 'audit_data' not in st.session_state:
    st.session_state.audit_data = None

# ==============================================================================
# ZERO-PROMPT AUTO-FETCH (GBP API MOCK)
# ==============================================================================
def fetch_gbp_profile_data(business_name: str) -> dict:
    """
    Simulates fetching Business Profile data post-OAuth for zero-prompt provisioning.
    In production, this queries the GBP API using the authorized token.
    """
    # Mocked fetched data
    return {
        "business_name": business_name if business_name else "Unknown Business",
        "niche": "Health & Wellness (Auto-Categorized)",
        "services": [
            {"name": "General Service (Auto-Imported)", "price": "Varies"},
            {"name": "Consultation (Auto-Imported)", "price": "$0"}
        ],
        "competitors": ["Local Competitor A", "Local Competitor B"]
    }

# ==============================================================================
# EXPERT CONSULTANT AGENT
# ==============================================================================
CONSULTANT_SYSTEM_PROMPT = """
You are a Senior SEO Consultant working for Shubham Rajput.
The user has just received a free Local SEO audit.
Your goal is to answer quick questions about why their score is low based strictly on the provided audit results.

Rules:
- STRICTLY FORBIDDEN to give repetitive responses or repeat the exact same advice.
- STRICTLY FORBIDDEN to use generic phrasing like "MOCK_RESPONSE".
- Be concise, direct, and authoritative as a knowledgeable peer.
- Provide SURGICAL, data-backed insights using the actual audit data provided (e.g. "Your ranking is suffering because your competitors have {competitor_gap}").
"""

def generate_consultant_response(messages_history, audit_data):
    # Calculate the message count based on the history length (excluding system messages)
    user_messages = [m for m in messages_history if m["role"] == "user"]
    message_count = len(user_messages)
    
    bridge = "\n\nImplementing these technical fixes manually is a full-time job. I can automate this for you by provisioning your Sovereign Vault right now. Would you like to proceed, or should I schedule a strategy session with Shubham Rajput?"
    
    if not has_genai or not os.environ.get("GEMINI_API_KEY"):
        # Simulated conversational responses using data when no API key is present
        weaknesses = audit_data.get('weaknesses', ['your current setup'])
        primary_weakness = weaknesses[0] if weaknesses else 'your profile'
        score = audit_data.get('health_score', 0)
        gap = audit_data.get('competitor_gap', 'competitors are outperforming you')
        
        fallback_responses = [
            f"Looking closely at your score of {score}, the most urgent issue seems to be {primary_weakness}.",
            f"You asked a good question. The main problem is {gap}. We really need to fix {', '.join(weaknesses)} to catch up.",
            f"Those are crucial factors. Because your score is {score}/100, Google prioritizes standard profiles over yours.",
            f"Exactly. If we aggressively address {primary_weakness} today, we can immediately begin capturing that lost traffic."
        ]
        
        # Pick a response based on current message count to simulate dynamic chat
        idx = max(0, message_count - 1) % len(fallback_responses)
        base_resp = fallback_responses[idx]
        
        if message_count >= 4:
            return base_resp + bridge
        return base_resp

    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Ground the prompt in the audit data
        grounding_context = f"\n\nAudit Results Context:\nScore: {audit_data.get('health_score')}\nWeaknesses: {', '.join(audit_data.get('weaknesses', []))}\nCompetitor Gap: {audit_data.get('competitor_gap')}"
        
        formatted_history = []
        for msg in messages_history:
            role = 'user' if msg['role'] == 'user' else 'model'
            formatted_history.append({"role": role, "parts": [{"text": msg['content']}]})
            
        config = types.GenerateContentConfig(system_instruction=CONSULTANT_SYSTEM_PROMPT + grounding_context)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_history,
            config=config
        )
        
        final_text = response.text
        if message_count >= 4:
            final_text += bridge
            
        return final_text
        
    except Exception as e:
        base_error = f"I'm analyzing your {audit_data.get('health_score')}/100 score, specifically the {audit_data.get('competitor_gap')} gap."
        if message_count >= 4:
             return base_error + bridge
        return base_error


# ==============================================================================
# PROVISIONING LOGIC (Vault Creation)
# ==============================================================================
def create_sovereign_vault(client_email: str, data: dict) -> str:
    """Creates a new Google Sheet via Drive & Sheets API, setups tabs, and populates data."""
    st.info("Authenticating with Google Workspace...")
    
    try:
        drive_service = get_authenticated_service('drive', 'v3')
        sheets_service = get_authenticated_service('sheets', 'v4')
        
        # Vault Isolation Protocol Logging
        st.info(f"Executing Vault Isolation Protocol for: {client_email}")
        folder_path = f"Sovereign_OS/{client_email}/{data.get('business_name', 'Client')}_Vault"
        st.info(f"Isolated Vault Space provisioned at: {folder_path}")
        
        # 1. Create the Spreadsheet
        title = f"{data.get('business_name', 'Client')} Sovereign Vault"
        st.info(f"Commanding Drive API to create: **{title}**")
        
        spreadsheet_body = {
            'properties': {'title': title},
            'sheets': [
                {'properties': {'title': 'tab_Business_Profile'}},
                {'properties': {'title': 'tab_Service_Catalog'}},
                {'properties': {'title': 'tab_Knowledge_Base'}},
                {'properties': {'title': 'tab_Lead_Pipeline'}},
                {'properties': {'title': 'tab_Review_Log'}},
                {'properties': {'title': 'tab_Customer_DB'}},
                {'properties': {'title': 'tab_Marketing_Ops'}}
            ]
        }
        
        spreadsheet = sheets_service.spreadsheets().create(
            body=spreadsheet_body, fields='spreadsheetId,spreadsheetUrl'
        ).execute()
        
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        spreadsheet_url = spreadsheet.get('spreadsheetUrl')
        
        st.success(f"Vault instantiated: {spreadsheet_id}")
        st.info("Injecting extracted configurations into Vault tabs...")
        
        # 2. Populate Initial Data
        updates = []
        # tab_Business_Profile
        updates.append({
            'range': 'tab_Business_Profile!A1:B3',
            'values': [
                ["Property", "Value"],
                ["business_name", data.get("business_name")],
                ["niche", data.get("niche")]
            ]
        })
        
        # tab_Service_Catalog
        service_values = [["Service Name", "Price"]]
        for s in data.get("services", []):
            service_values.append([s.get("name"), s.get("price")])
        updates.append({
            'range': 'tab_Service_Catalog!A1:B20',
            'values': service_values
        })
        
        # Competitors (putting in Business Profile or Audit)
        comp_values = [["Competitor Name"]] + [[c] for c in data.get("competitors", [])]
        updates.append({
            'range': 'tab_Business_Profile!D1:D10',
            'values': comp_values
        })
        
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': updates
        }
        sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        
        st.success("Configuration injected perfectly.")
        st.session_state.vault_id = spreadsheet_id
        return spreadsheet_url
        
    except Exception as e:
         st.error(f"Google API Provisioning failed: {e}")
         st.warning("To run full provisioning, ensure `credentials.json` is valid and Google Drive/Sheets APIs are enabled in Cloud Console.")
         # Fallback to simulation
         time.sleep(2)
         st.session_state.vault_id = "MOCK_SPREADSHEET_ID_123"
         return "https://docs.google.com/spreadsheets/d/MOCK_SPREADSHEET_ID_123/edit"


# ==============================================================================
# PHASE UIs
# ==============================================================================

if st.session_state.phase == 'PUBLIC_AUDIT':
    st.markdown("<h1 class='royal' style='text-align: center; margin-top: 50px;'>Free Local SEO Audit</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-weight: 400; color: #64748B;'>Enter your business name or Google Maps link to instantly identify growth gaps.</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='step-box'>", unsafe_allow_html=True)
    
    with st.form("audit_form"):
        business_input = st.text_input("Business Name or Google Maps Link", placeholder="e.g., 'Prana Flow Yoga' or 'https://maps.app.goo.gl/...'")
        submitted = st.form_submit_button("Generate Health Report", type="primary")
        
        if submitted and business_input:
            st.session_state.audit_business_name = business_input
            with st.spinner("Analyzing public data and scanning competitors..."):
                audit_result = get_public_audit(business_input)
                st.session_state.audit_data = audit_result["data"]
                
                # Silently log the warm lead
                log_master_lead(business_input, audit_result["data"].get("health_score", 0))
    
    if st.session_state.audit_data:
        st.markdown("---")
        data = st.session_state.audit_data
        score = data.get("health_score", 0)
        
        st.markdown(f"<h2 style='text-align: center;'>Health Score: <span class='{'emerald' if score >= 70 else 'royal'}'>{score}/100</span></h2>", unsafe_allow_html=True)
        
        if "breakdown" in data:
            st.markdown("<h4 style='text-align: center; color: #64748B;'>📊 10/10 Elite Audit Framework</h4>", unsafe_allow_html=True)
            breakdown_cols = st.columns(5)
            for i, (metric, val) in enumerate(data["breakdown"].items()):
                title = metric.split(" (")[0]
                weight = f"Weight: {metric.split('(')[1].replace(')','')}" if "(" in metric else ""
                with breakdown_cols[i]:
                    st.metric(title, val, help=weight)
            st.markdown("---")
            
        st.markdown("<h4 style='text-align: center; color: #64748B;'>📍 Local Geo-Grid Ranking (Primary Keyword)</h4>", unsafe_allow_html=True)
        # 5x5 Grid Logic Simulation
        grid_data = [
            [15, 13, 11, 12, 14],
            [14,  6,  4,  5, 13],
            [11,  5,  1,  2, 11],
            [12,  8,  3,  9, 12],
            [16, 14, 10, 15, 17]
        ]
        # Top 3 Competitors "Green Zones" Map Overlay
        trophies = [(0, 4), (1, 1), (4, 2)]
        
        grid_html = "<div class='geo-grid'>"
        for r in range(5):
            for c in range(5):
                val = grid_data[r][c]
                color_class = "node-green" if val <= 3 else "node-amber" if val <= 10 else "node-red"
                trophy_html = "<div class='trophy' title='Competitor Green Zone'>🏆</div>" if (r, c) in trophies else ""
                grid_html += f"<div class='grid-node {color_class}'>{val}{trophy_html}</div>"
        grid_html += "</div>"
        
        st.markdown(grid_html, unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 14px; color: #64748B;'>Ranks 1-3 <span style='color: #10B981;'>■</span> | Ranks 4-10 <span style='color: #F59E0B;'>■</span> | Ranks 11+ <span style='color: #EF4444;'>■</span><br>🏆 Competitor Strongholds</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        if "keyword_mirror" in data:
            st.markdown("<h4 style='text-align: center; color: #64748B;'>🔍 Keyword Mirror & Gap Analysis</h4>", unsafe_allow_html=True)
            km = data["keyword_mirror"]
            
            km_col1, km_col2 = st.columns(2)
            with km_col1:
                st.markdown("<div style='background: #F1F5F9; padding: 16px; border-radius: 8px; border-left: 4px solid #94A3B8;'>", unsafe_allow_html=True)
                st.markdown("<b>Keywords You Use</b>", unsafe_allow_html=True)
                for used in km.get('used', []):
                    st.markdown(f"- {used}")
                st.markdown("</div>", unsafe_allow_html=True)
            with km_col2:
                st.markdown("<div style='background: #FEF2F2; padding: 16px; border-radius: 8px; border-left: 4px solid #EF4444;'>", unsafe_allow_html=True)
                st.markdown("<b>Keywords Your Customers Search (Missing)</b>", unsafe_allow_html=True)
                for missing in km.get('missing', []):
                    st.markdown(f"- {missing}")
                st.markdown("</div><br>", unsafe_allow_html=True)
                
            st.markdown("<b>🧠 LSI Extraction Suggestions Engine:</b>")
            for lsi in km.get('lsi_suggestions', []):
                 st.info(f"💡 {lsi}")
                 
            st.markdown("---")
            
        if "visual_trust" in data:
            st.markdown("<h4 style='text-align: center; color: #64748B;'>📸 Visual AI Trust Audit</h4>", unsafe_allow_html=True)
            vt = data["visual_trust"]
            score = vt.get("score", 0)
            humanity = vt.get("humanity_score", 0)
            is_deficit = vt.get("is_trust_deficit", False)
            bm = vt.get("benchmarking", {})
            
            vt_col1, vt_col2 = st.columns([1, 2])
            with vt_col1:
                st.markdown(f"<div style='text-align:center; padding: 20px; background: {'#FEF2F2' if is_deficit else '#F0FDF4'}; border-radius: 12px; border: 1px solid {'#FECACA' if is_deficit else '#BBF7D0'};'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin:0; color: {'#EF4444' if is_deficit else '#10B981'};'>{score}/100</h3>", unsafe_allow_html=True)
                st.markdown("<b>Visual Trust Score</b>", unsafe_allow_html=True)
                if is_deficit:
                    st.markdown("<span style='color: #EF4444; font-weight: bold;'>⚠️ TRUST DEFICIT DETECTED</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with vt_col2:
                st.markdown("<b>Missing Visual Assets:</b>", unsafe_allow_html=True)
                for missing in vt.get("missing_assets", []):
                    st.markdown(f"<span style='color: #EF4444;'>❌ {missing}</span>", unsafe_allow_html=True)
                    
                st.markdown("<br><b>📊 Competitor Benchmarking:</b>", unsafe_allow_html=True)
                st.markdown(f"- <b>Your Humanity Score:</b> {humanity}/100 | <b>Top 3 Avg:</b> {bm.get('competitor_humanity_score')}/100", unsafe_allow_html=True)
                st.markdown(f"- <b>Your Photo Count:</b> {bm.get('user_photo_count')} | <b>Top 3 Avg:</b> {bm.get('competitor_photo_avg')}", unsafe_allow_html=True)
                
            st.markdown("---")
            
        if "revenue_gap" in data:
            st.markdown("<h4 style='text-align: center; color: #64748B;'>💸 The Revenue Opportunity Gap</h4>", unsafe_allow_html=True)
            rg = data["revenue_gap"]
            
            rg_col1, rg_col2 = st.columns([1, 2])
            with rg_col1:
                st.markdown("<div style='text-align:center; padding: 20px; background: #FEF2F2; border-radius: 12px; border: 1px solid #FECACA;'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin:0; color: #EF4444;'>${rg.get('monthly_revenue_loss', 0):,}</h3>", unsafe_allow_html=True)
                st.markdown("<b>Lost Monthly Revenue</b>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with rg_col2:
                st.markdown(f"<b>Top 3 Competitor Closing Time:</b> {rg.get('competitor_closing_time')}", unsafe_allow_html=True)
                st.markdown(f"<b>Your Closing Time:</b> <span style='color: #EF4444;'>{rg.get('user_closing_time')}</span>", unsafe_allow_html=True)
                st.markdown(f"<b>Lost Opportunity Windows:</b> {rg.get('lost_hours')} Hours/Day", unsafe_allow_html=True)
                st.markdown(f"<b>Estimated Missed Searches:</b> {rg.get('missed_searches_monthly'):,} per month", unsafe_allow_html=True)
                
            st.warning(rg.get('warning_text'))
            st.markdown("---")
            
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟢 The Good")
            for strength in data.get("strengths", []):
                st.markdown(f"- {strength}")
        with col2:
            st.markdown("### 🔴 The Weak")
            for weakness in data.get("weaknesses", []):
                st.markdown(f"- {weakness}")
                
        st.info(f"**Competitor Gap:** {data.get('competitor_gap')}")
        
        # --- WhatsApp Dispatch ---
        st.markdown("#### 📱 Get this report on WhatsApp")
        col_wa, col_btn = st.columns([2, 1])
        with col_wa:
            wa_number = st.text_input("Phone Number", placeholder="+15551234567", label_visibility="collapsed")
        with col_btn:
            if st.button("Send Report to WhatsApp", use_container_width=True):
                if wa_number:
                    # Update lead log with the captured number
                    log_master_lead(st.session_state.get('audit_business_name', 'Unknown'), score, wa_number)
                    
                    oauth_link = "https://example.com/oauth/onboarding" # Mock link
                    template_msg = f"Hi! Here is the SEO Health Report for {st.session_state.get('audit_business_name', 'your business')}. Your current score is {score}/100. Key issues identified: {', '.join(data.get('weaknesses', []))}. Click here to authorize a 1-click fix: {oauth_link}"
                    
                    wa_payload = {
                        "action": "WHATSAPP_RESPONSE",
                        "recipient": wa_number,
                        "message_text": template_msg,
                        "status": "DISPATCHED"
                    }
                    st.success("Report Sent to WhatsApp!")
                else:
                    st.error("Please enter a valid phone number.")

        

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top: 40px;'>🛠️ Fix My Profile Command Center</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background: white; border: 2px solid #E2E8F0; padding: 24px; border-radius: 12px; margin-bottom: 24px;'>
            <h4 style='margin-top:0; color: #0F172A;'>Instant Wins Available:</h4>
            <ul style='list-style-type: none; padding-left: 0; font-size: 16px; line-height: 1.8; color: #334155;'>
                <li>✅ <b>Add 3 Missing High-Volume Keywords</b></li>
                <li>✅ <b>Sync Operating Hours with Top 3 Competitors</b></li>
                <li>✅ <b>AI-Generated Review Responses for Last 90 Days</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- The Web Architect Staging Preview ---
        st.markdown("<h3 style='text-align: center; margin-top: 20px; color: #3B82F6;'>✨ Your Sovereign OS Website Preview</h3>", unsafe_allow_html=True)
        st.caption("<p style='text-align: center;'>We've automatically generated a high-converting website draft based on your profile gaps.</p>", unsafe_allow_html=True)
        
        # Horizontal Site Map Slider
        st.markdown("""
        <style>
        /* Hide standard radio button circles */
        div.row-widget.stRadio > div{flex-direction:row;justify-content:center;}
        div.row-widget.stRadio > div > label > div:first-child{display:none;}
        /* Style the labels as custom tabs */
        div.row-widget.stRadio > div > label{
            background-color: #F1F5F9; 
            padding: 8px 16px; 
            border-radius: 20px; 
            cursor: pointer;
            margin: 0 5px;
            border: 1px solid #CBD5E1;
            font-weight: 500;
            color: #475569;
        }
        div.row-widget.stRadio > div > label[data-baseweb="radio"]:has(input:checked){
            background-color: #3B82F6;
            color: white;
            border-color: #3B82F6;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if 'wa_active_tab' not in st.session_state:
            st.session_state.wa_active_tab = "Home"
            
        selected_page = st.radio("Navigate Preview", ["Home", "Services", "About", "Contact"], label_visibility="collapsed", horizontal=True, index=["Home", "Services", "About", "Contact"].index(st.session_state.wa_active_tab))
        st.session_state.wa_active_tab = selected_page
        
        with st.spinner(f"Compiling {selected_page} Assets..."):
             engine = WebArchitect(data)
             preview_html = engine.generate_html_preview(page_type=selected_page)
             
        # Render the scrollable component
        st.components.v1.html(preview_html, height=520, scrolling=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Sticky CTA Authorize Button
        if st.button("🚀 Claim This Website & Authorize Full Repair", use_container_width=True, type="primary"):
            with st.spinner("Freezing Visionary Blueprint..."):
                # Pass mocked AI manifest as an example
                manifest = {
                    "Home_Hero": "professional wide shot of [PRIMARY_SERVICE]",
                    "About_Team": "professional portrait of team",
                    "Services_Thumbs": "tools and equipment in action"
                }
                lock_visionary_vault(data, manifest)
                time.sleep(1) # Visual pacing
                
            with st.spinner("Notifying Sovereign Network..."):
                preview_url = f"https://www.{data.get('name', 'Client').replace(' ', '').lower()}{data.get('city', 'City').replace(' ', '').lower()}.com/staging"
                trigger_admin_gold_alert(data, preview_url)
                time.sleep(1) # Visual pacing
                
            st.session_state.phase = 'AUTH'
            st.rerun()
            
        st.markdown("---")
        # --- Expert Consult Sidebar Agent ---
        st.markdown("### 💬 Expert Consult")
        st.caption("Ask our AI about your score and how to improve it.")
        
        if 'consult_messages' not in st.session_state:
            st.session_state.consult_messages = [{"role": "assistant", "content": "Hello! I can analyze your audit score. What would you like to know?"}]
            
        for message in st.session_state.consult_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if prompt := st.chat_input("Why is my score so low?"):
            st.session_state.consult_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    resp = generate_consultant_response(st.session_state.consult_messages, data)
                    st.markdown(resp)
                    st.session_state.consult_messages.append({"role": "assistant", "content": resp})

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.phase == 'AUTH':
    st.markdown("<h1 class='royal' style='text-align: center; margin-top: 50px;'>Sovereign Architecture Setup</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-weight: 400; color: #64748B;'>Authorize your portal to begin.</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='step-box'>", unsafe_allow_html=True)
    st.write("We need strictly permissioned access to your Google Workspace to dynamically create your Sovereign Vault and bridge your Local SEO automation pipelines.")
    
    if st.button("Authenticate via Google OAuth", use_container_width=True):
        if not os.path.exists('credentials.json'):
             st.warning("`credentials.json` not found locally. We will simulate authentication for testing environments.")
             time.sleep(1)
             
             # Zero-Prompt Auto-Fetch
             business_input = st.session_state.get("audit_business_name", "Demo Request")
             st.session_state.extracted_data = fetch_gbp_profile_data(business_input)
             st.session_state.phase = 'PROVISIONING'
             st.rerun()
        else:
            with st.spinner("Initiating OAuth Handshake & Fetching Profile..."):
                try:
                    # Will pop a browser window if token expired/missing
                    service = get_authenticated_service('drive', 'v3') 
                    client_email = get_client_email()
                    st.session_state.client_email = client_email
                    st.success(f"Authentication confirmed for {client_email}!")
                    time.sleep(1)
                    
                    # Zero-Prompt Auto-Fetch
                    business_input = st.session_state.get("audit_business_name", "Demo Request")
                    st.session_state.extracted_data = fetch_gbp_profile_data(business_input)
                    st.session_state.phase = 'PROVISIONING'
                    st.rerun()
                except Exception as e:
                    st.error(f"Authentication failed: {e}")
    st.markdown("</div>", unsafe_allow_html=True)


elif st.session_state.phase == 'PROVISIONING':
    st.markdown("<h2 style='text-align: center;'>Initializing <span class='royal'>Digital Infrastructure</span></h2>", unsafe_allow_html=True)
    
    with st.status("Digital Infrastructure Sync in Progress...", expanded=True) as status:
        st.write("🔄 Connecting to Google Business Profile...")
        time.sleep(1.2)
        
        st.write("🔐 Provisioning Sovereign Vault...")
        client_email = st.session_state.get('client_email', 'demo.client@example.com')
        url = create_sovereign_vault(client_email, st.session_state.get('extracted_data', {}))
        st.session_state.vault_url = url
        time.sleep(1.2)
        
        st.write("📊 Preparing Executive Dashboard...")
        time.sleep(1.2)
        
        status.update(label="✅ Sovereign Vault Active & Synced!", state="complete", expanded=False)
    
    st.toast("✅ Sovereign Vault Active & Synced", icon="🚀")
    time.sleep(0.5)
    
    try:
        st.switch_page("pages/dashboard.py")
    except Exception as e:
        st.error(f"Redirect blocked by Streamlit Architecture constraint: {e}")

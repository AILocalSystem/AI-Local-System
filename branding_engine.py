import streamlit as st
import os

# ==============================================================================
# WHITE-LABEL BRANDING ENGINE
# ==============================================================================

def get_client_branding(client_email):
    """
    Simulates fetching customized white-label settings from the Sovereign Vault 
    or database for a specific client.
    """
    # In production, this pulls from a 'Settings' tab in the Google Sheet
    # For now, it mocks standard branding vs overriding if the email matches test accounts.
    
    if client_email == "demo.client@example.com":
        return {
            "business_name": "Acme Plumbing",
            "logo_url": "💧", # Emoji as a mock logo placeholder
            "primary_color": "#2563EB", # Blue
            "dashboard_title": "Acme Plumbing: Growth Cockpit"
        }
    elif client_email == "chef.mike@bistro.com":
        return {
            "business_name": "Downtown Bistro",
            "logo_url": "🍽️",
            "primary_color": "#DC2626", # Red
            "dashboard_title": "Downtown Bistro: Growth Cockpit"
        }
        
    # Default unbranded fallback
    return {
        "business_name": "Sovereign OS",
        "logo_url": "👑",
        "primary_color": "#1E293B",
        "dashboard_title": "Sovereign OS: Growth Cockpit"
    }

def apply_branding_to_ui(branding):
    """
    Injects custom CSS to override theme colors explicitly for the logged-in client.
    """
    custom_css = f"""
    <style>
        .royal {{ color: {branding['primary_color']} !important; }}
        /* Modify button colors or specific targeted accents here based on primary_color */
        .stButton>button[kind='primary'] {{
            background-color: {branding['primary_color']} !important;
            border-color: {branding['primary_color']} !important;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

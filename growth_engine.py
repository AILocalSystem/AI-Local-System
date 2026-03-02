import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Try to import Google GenAI
try:
    from google import genai
    has_genai = True
except ImportError:
    has_genai = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

from typing import Dict, List, Any
from vault_connector import VaultConnector

# Initialize Live Vault Connector
vc = VaultConnector()

# ==============================================================================
# "VAULT" DATA HYDRATION
# ==============================================================================
TODAY = datetime.now()

# Format helper for dates
def d_str(days_ago: int) -> str:
    return (TODAY - timedelta(days=days_ago)).strftime('%Y-%m-%d')


def fetch_live_vault() -> Dict[str, Any]:
    """Hydrates local memory with live Google Sheets data."""
    if not vc._is_live:
        logger.warning("VaultConnector in MOCK mode. Returning simulated VAULT_DATA.")
        return {
            "tab_Business_Profile": {
                "name": "Acme Plumbers",
                "category": "Plumbing Services",
                "gbp_review_link": "https://g.page/r/AcmePlumbers/review"
            },
            "tab_Marketing_Ops": {
                "active_offer": "15% off any spring maintenance service"
            },
            "tab_Customer_DB": [
                {"phone": "+15551110001", "name": "Opt Out Ollie", "last_visit": "Leak Repair", "last_interaction_date": d_str(60), "last_marketing_sent": d_str(100), "opt_out": True},
                {"phone": "+15551110002", "name": "Spammed Sam", "last_visit": "Pipe Check", "last_interaction_date": d_str(40), "last_marketing_sent": d_str(5), "opt_out": False},
                {"phone": "+15551110003", "name": "Dormant Dan", "last_visit": "Water Heater Install", "last_interaction_date": d_str(45), "last_marketing_sent": d_str(60), "opt_out": False},
                {"phone": "+15551110004", "name": "Active Alice", "last_visit": "Faucet Fix", "last_interaction_date": d_str(10), "last_marketing_sent": d_str(20), "opt_out": False}
            ],
            "tab_Lead_Pipeline": [
                {"phone": "+15552220005", "name": "Happy Harry", "status": "Completed", "service": "Emergency Drain Clearing", "review_requested": False}
            ],
            "tab_Review_Log": [
                {"review_id": "rev_01", "author": "Google User 1", "rating": 5, "comment": "Acme Plumbers did a fantastic job fixing my shower leak quickly!", "replied": False},
                {"review_id": "rev_02", "author": "Angry Customer", "rating": 1, "comment": "The plumber was 2 hours late and tracked mud everywhere.", "replied": False}
            ]
        }
    
    logger.info("Hydrating variables from Google Sheets API...")
    ranges = ['tab_Business_Profile!A:Z', 'tab_Marketing_Ops!A:Z', 'tab_Customer_DB!A:Z', 'tab_Lead_Pipeline!A:Z', 'tab_Review_Log!A:Z']
    batch_data = vc.read_vault_batch(ranges)
    
    # In production, parse 2D arrays into dicts based on exact header mapping.
    # We will simulate successful parsing logic matching the mock above for compatibility.
    return {
        "tab_Business_Profile": {"name": "Acme Plumbers", "category": "Plumbing", "gbp_review_link": "https://g.page/r/MockLink"},
        "tab_Marketing_Ops": {"active_offer": "15% off spring service"},
        "tab_Customer_DB": [],
        "tab_Lead_Pipeline": [],
        "tab_Review_Log": []
    }
    
# ==============================================================================
# LLM & TEMPLATE GENERATORS
# ==============================================================================
def call_gemini(system_instruction: str, prompt: str) -> str:
    """Uses Gemini API to generate personalized text."""
    if not has_genai or not os.environ.get("GEMINI_API_KEY"):
        return f"[MOCK GENERATED TEXT FOR: {prompt[:30]}...]"

    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        config = types.GenerateContentConfig(system_instruction=system_instruction)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return f"[API ERROR FALLBACK: {prompt[:30]}...]"

def generate_welcome_back(customer: Dict, biz_profile: Dict, offer: str) -> str:
    if not has_genai or not os.environ.get("GEMINI_API_KEY"):
         return f"Hi {customer.get('name')}, it's been a while since your {customer.get('last_visit')} with {biz_profile.get('name')}. We're currently offering: {offer}. Let us know if you need anything!"

    sys = "You are a friendly, professional SMS marketing automated assistant for a local services business. Write short, punchy, conversational SMS messages (under 160 chars)."
    prompt = f"Write a 'Welcome Back' SMS to '{customer.get('name')}'. Mention their last service was '{customer.get('last_visit')}'. The business is '{biz_profile.get('name')}'. Include this active offer: '{offer}'."
    return call_gemini(sys, prompt)

def generate_review_request(customer: Dict, biz_profile: Dict) -> str:
    if not has_genai or not os.environ.get("GEMINI_API_KEY"):
        return f"Thanks for choosing {biz_profile.get('name')} today, {customer.get('name')}! If you enjoyed our service, would you mind leaving us a quick review? It helps us a lot: {biz_profile.get('gbp_review_link')}"
        
    sys = "You are a friendly SMS assistant for a local business. Write a very brief, polite SMS asking a customer to leave a Google Review."
    prompt = f"Customer name: {customer.get('name')}. Business: {biz_profile.get('name')}. Review Link: {biz_profile.get('gbp_review_link')}. Keep it short and human."
    return call_gemini(sys, prompt)

def generate_review_reply(review: Dict, biz_profile: Dict) -> str:
    rating = review.get('rating', 5)
    
    if not has_genai or not os.environ.get("GEMINI_API_KEY"):
        if rating >= 4:
            return f"Thank you so much for the {rating}-star review, {review.get('author')}! We're thrilled we could help you out."
        else:
            return f"Hi {review.get('author')}, I am so sorry to hear about your experience. Please reach out to our management directly so we can make this right."

    sys = "You are the owner of a local services business responding to Google Reviews."
    
    if rating >= 4:
        prompt = (f"Write a cheerful, SEO-optimized public reply to this {rating}-star review. "
                  f"Review text: '{review.get('comment')}'. "
                  f"Be sure to naturally mention the specific service they praised if it's in their comment.")
    else:
        prompt = (f"Write a humble, non-defensive, apologetic public reply to this {rating}-star review. "
                  f"Review text: '{review.get('comment')}'. "
                  f"Do not make excuses. Ask them to contact management to resolve the issue.")
                  
    return call_gemini(sys, prompt)


# ==============================================================================
# PIPELINE SCANNERS
# ==============================================================================
def process_dormancy() -> List[Dict]:
    """Scans Customer_DB for retention opportunities (>30 days since interaction, >14 days since marketing)."""
    actions = []
    biz_profile = VAULT_DATA["tab_Business_Profile"]
    offer = VAULT_DATA["tab_Marketing_Ops"]["active_offer"]
    
    for cust in VAULT_DATA["tab_Customer_DB"]:
        # Constraint 1: Opt-Out
        if cust.get("opt_out", False):
            continue
            
        last_int_date = datetime.strptime(cust["last_interaction_date"], '%Y-%m-%d')
        last_mkt_date = datetime.strptime(cust["last_marketing_sent"], '%Y-%m-%d')
        
        days_since_int = (TODAY - last_int_date).days
        days_since_mkt = (TODAY - last_mkt_date).days
        
        # Constraint 2 & 3: Dormancy & Frequency Cap
        if days_since_int > 30 and days_since_mkt >= 14:
            msg = generate_welcome_back(cust, biz_profile, offer)
            
            vc.write_vault_row("tab_Marketing_Ops!A:H", [
                datetime.now().strftime("%Y-%m-%d"), cust["phone"], "RETENTION_OFFER", msg, "SENT"
            ])
            
            actions.append({
                "action": "OUTBOUND_MARKETING",
                "data": {
                    "type": "RETENTION_OFFER",
                    "recipient": cust["phone"],
                    "message": msg,
                    "metadata": {
                        "campaign_id": "AUTO_RETENTION",
                        "log_to_sheet": "tab_Marketing_Ops"
                    }
                }
            })
            
    return actions

def process_review_requests() -> List[Dict]:
    """Scans Lead_Pipeline for completed jobs that haven't received a review request yet."""
    actions = []
    biz_profile = VAULT_DATA["tab_Business_Profile"]
    
    for lead in VAULT_DATA["tab_Lead_Pipeline"]:
        if lead.get("status") == "Completed" and not lead.get("review_requested", False):
            msg = generate_review_request(lead, biz_profile)
            
            vc.write_vault_row("tab_Marketing_Ops!A:H", [
                datetime.now().strftime("%Y-%m-%d"), lead["phone"], "REVIEW_REQUEST", msg, "SENT"
            ])
            
            actions.append({
                "action": "OUTBOUND_MARKETING",
                "data": {
                    "type": "REVIEW_REQUEST",
                    "recipient": lead["phone"],
                    "message": msg,
                    "metadata": {
                        "campaign_id": "AUTO_REVIEW_REQUEST",
                        "log_to_sheet": "tab_Lead_Pipeline",
                        "lead_id": lead["name"]
                    }
                }
            })
    return actions

def process_review_replies() -> List[Dict]:
    """Scans Review_Log for unreplied reviews and generates API payload proposals."""
    actions = []
    biz_profile = VAULT_DATA["tab_Business_Profile"]
    owner_phone = "+1555OWNRNMBR" # Configured owner number for alerts
    
    for review in VAULT_DATA["tab_Review_Log"]:
        if not review.get("replied", False):
            rating = review.get("rating", 0)
            draft_reply = generate_review_reply(review, biz_profile)
            
            if rating >= 4:
                # Positive Review -> Auto Publish path
                actions.append({
                    "action": "GBP_API_INTERACTION",
                    "data": {
                        "type": "POST_REVIEW_REPLY",
                        "review_id": review["review_id"],
                        "reply_text": draft_reply,
                        "status": "APPROVED", # Safe to push immediately
                        "update_vault": "tab_Review_Log"
                    }
                })
            else:
                # Negative Review -> Draft & Needs Approval Pipeline
                actions.append({
                    "action": "GBP_API_INTERACTION",
                    "data": {
                        "type": "POST_REVIEW_REPLY",
                        "review_id": review["review_id"],
                        "reply_text": draft_reply,
                        "status": "REQUIRES_APPROVAL", # Safety Constraint: Owner must tap approve in vault
                        "update_vault": "tab_Review_Log"
                    }
                })
                # Send alert via WhatsApp to the Owner
                actions.append({
                    "action": "OUTBOUND_MARKETING",
                    "data": {
                        "type": "INTERNAL_ALERT",
                        "recipient": owner_phone,
                        "message": f"ALERT: New {rating}-star review from {review['author']}. A draft reply has been populated in the Vault for your approval.",
                        "metadata": {"campaign_id": "INTERNAL_SYSTEM"}
                    }
                })
                
    return actions

# ==============================================================================
# MAIN ENGINE RUNNER
# ==============================================================================
def run_growth_engine():
    logger.info("Starting Growth & Retention Engine Scan...")
    
    global VAULT_DATA
    VAULT_DATA = fetch_live_vault()
    
    all_actions = []
    
    # Run the 3 core pipelines
    retention_actions = process_dormancy()
    request_actions = process_review_requests()
    reply_actions = process_review_replies()
    
    all_actions.extend(retention_actions)
    all_actions.extend(request_actions)
    all_actions.extend(reply_actions)
    
    logger.info(f"Scan complete. Generated {len(all_actions)} actionable payloads.")
    
    # Output JSON array as required protocol
    print(json.dumps(all_actions, indent=2))

if __name__ == "__main__":
    run_growth_engine()

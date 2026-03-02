import os
import json
import logging
import re
import argparse
from typing import Dict, Any, Tuple
from flask import Flask, request, jsonify
from datetime import datetime

# Try to import Google GenAI
try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
from vault_connector import VaultConnector

# Initialize Live Vault Connector
vc = VaultConnector()

# ==============================================================================
# "VAULT" DATA (Simulated Google Sheet RAG Data)
# ==============================================================================
# During testing/mock mode, we keep defaults. In production, these are populated live.
KNOWLEDGE_BASE = {
    "faq": "We are open 24/7. We offer emergency plumbing services across Springfield.",
    "pricing": "Service fee is $50. Emergency night call is $150. Hourly rate is $100/hr.",
    "usp": "Fastest response time in Springfield. Licensed and insured."
}
SERVICE_CATALOG = {
    "leak repair": "$150 flat + parts",
    "water heater installation": "$500 labor + parts",
    "pipe replacement": "Requires custom quote, starts at $300"
}
CUSTOMER_DB = {
    "+15551234567": {"name": "John Doe", "last_visit": "2023-11-01 (Leak Repair)"},
    "+15559876543": {"name": "Jane Smith", "last_visit": "2024-01-15 (Water Heater maintenance)"}
}

# ==============================================================================
# PIPELINE LOGIC
# ==============================================================================
def lookup_customer(phone_number: str) -> Tuple[bool, str, Dict]:
    """Identifies if a customer is returning or new."""
    if phone_number in CUSTOMER_DB:
        cust = CUSTOMER_DB[phone_number]
        greeting = f"Welcome back, {cust['name']}! Did you need help with your {cust['last_visit']}?"
        return True, greeting, cust
    return False, "Hi there! Thanks for reaching out to Acme Plumbers. How can we help you today?", {"name": "Unknown"}

def check_negative_sentiment(message: str) -> bool:
    """The Safety Valve: Checks for negative escalation keywords."""
    escalation_words = ['complaint', 'bad', 'wrong', 'refund', 'angry', 'sue', 'terrible']
    msg_lower = message.lower()
    for word in escalation_words:
        if word in msg_lower:
            return True
    return False

def check_service_inquiry(message: str) -> Tuple[bool, str, str]:
    """Checks if the user is asking about a specific service to trigger The Close attempt."""
    msg_lower = message.lower()
    for service, price in SERVICE_CATALOG.items():
        if service in msg_lower:
            return True, service, price
    return False, "", ""

def call_gemini_intent(message: str) -> int:
    """Uses Gemini to score the Warmth of the lead (1-10) based on message text."""
    if not has_genai or not os.environ.get("GEMINI_API_KEY"):
        # Fallback heuristic
        if "price" in message.lower() or "cost" in message.lower() or "book" in message.lower():
            return 8
        return 3
        
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    prompt = (
        f"Analyze this customer message: '{message}'. "
        "Rate their 'Warmth Score' as a lead from 1 to 10. (1 = just saying hi / spam, "
        "10 = highly motivated to buy right now / asking for price / booking). "
        "Respond ONLY with the integer."
    )
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return int(response.text.strip())
    except Exception as e:
        logger.error(f"Gemini intent error: {e}")
        return 5

# ==============================================================================
# WEBHOOK ENDPOINT
# ==============================================================================
@app.route('/webhook', methods=['GET', 'POST'])
def handle_whatsapp_webhook():
    """Handles incoming message events and verification from WhatsApp."""
    
    # Meta Verification Handshake
    if request.method == 'GET':
        verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "MY_SECRET_WHATSAPP_TOKEN")
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                logger.info("WEBHOOK_VERIFIED")
                return challenge, 200
            else:
                return jsonify({"error": "Verification failed"}), 403
        return jsonify({"error": "Missing parameters"}), 400

    # Incoming Message Processing
    if request.method == 'POST':
        data = request.json
        
        # Meta Graph API Schema Validation
        try:
            entry = data.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            
            # Non-message updates (like statuses)
            if 'messages' not in value:
                return jsonify({"status": "ignored"}), 200
                
            message_obj = value['messages'][0]
            sender_phone = message_obj['from']
            
            # Extract contact name
            name = "Unknown"
            if 'contacts' in value and len(value['contacts']) > 0:
                name = value['contacts'][0].get('profile', {}).get('name', 'Unknown')
                
            # Restrict to Text messages for now
            if message_obj.get('type') != 'text':
                return jsonify({"status": "ignored, non-text"}), 200
                
            message_text = message_obj['text']['body']
            
            logger.info("SUCCESS: Payload parsed and prepared for Sovereign Vault.")
            
        except Exception as e:
            logger.error(f"Error parsing Meta payload: {e}")
            return jsonify({"error": "Invalid payload structure"}), 400
        
    logger.info(f"Incoming Meta message from {name} ({sender_phone}): {message_text}")
    
    # 1. Customer Lookup
    is_returning, greeting, cust_data = lookup_customer(sender_phone)
    name = cust_data.get('name', 'Unknown')
    
    # 2. Safety Valve (Negative Sentiment)
    if check_negative_sentiment(message_text):
        row_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name, sender_phone, "COMPLAINT", "1", "URGENT_HANDOVER"
        ]
        vc.write_vault_row("tab_Lead_Pipeline!A:F", row_data)
        
        payload = {
            "action": "WHATSAPP_RESPONSE",
            "recipient": sender_phone,
            "message_text": "I'm sorry to hear that. I'm alerting the manager immediately to resolve this personally.",
            "status": "LOGGED_TO_LIVE_VAULT" if vc._is_live else "MOCKED_WRITE"
        }
        return jsonify(payload), 200

    # 3. Assess Lead Warmth
    warmth_score = call_gemini_intent(message_text)
    
    # 4. Process Intents & The Close Attempt
    response_text = ""
    interest = "General Inquiry"
    
    is_service, service_name, price = check_service_inquiry(message_text)
    
    if is_service:
        # We found the service in our catalog!
        interest = service_name
        response_text = f"Our price for {service_name} is {price}. Would you like to book a slot for {service_name} right now?"
    elif "price" in message_text.lower() or "cost" in message_text.lower():
        # They asked for a price of something NOT in the catalog -> Strict Fact-Check fallback
        response_text = "Let me check with the team and get back to you on that price."
    else:
        # Generic conversation -> Start with greeting
        response_text = greeting
        
    # 5. Build output payload
    row_data = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name, sender_phone, interest, str(warmth_score), "AUTO_RESPONDING"
    ]
    vc.write_vault_row("tab_Lead_Pipeline!A:F", row_data)
    
    payload = {
        "action": "WHATSAPP_RESPONSE",
        "recipient": sender_phone,
        "message_text": response_text,
        "status": "LOGGED_TO_LIVE_VAULT" if vc._is_live else "MOCKED_WRITE"
    }
    
    logging.info(f"Generated Payload: {payload}")
    return jsonify(payload), 200


# ==============================================================================
# TEST RUNNER (If run directly via CLI)
# ==============================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="GBP SEO Optimizer Tool")
    parser.add_argument("--test", action="store_true", help="Run local simulation tests instead of starting server")
    
    import sys
    if "--test" in sys.argv:
        # Simulate incoming webhooks
        # Simulate Meta Graph API payloads
        def make_meta_payload(phone: str, text: str, name: str = "TestUser"):
            return {
              "object": "whatsapp_business_account",
              "entry": [{
                  "id": "123456",
                  "changes": [{
                      "value": {
                          "contacts": [{"profile": {"name": name}, "wa_id": phone}],
                          "messages": [{"from": phone, "type": "text", "text": {"body": text}}]
                      }
                  }]
              }]
            }

        test_cases = [
            make_meta_payload("+15551112222", "Hi, do you do water heater installation?", "New Lead Bob"),
            make_meta_payload("+15551234567", "Hello", "John Doe"),
            make_meta_payload("+15559998888", "How much for a full bathroom remodel?", "Curious Cathy"),
            make_meta_payload("+15554443333", "The pipe you fixed is leaking again, this is terrible!", "Angry Andy")
        ]
        
        with app.test_client() as client:
            # 1. Test Verification GET
            print("\n--- TEST HANDSHAKE (GET) ---")
            resp = client.get('/webhook?hub.mode=subscribe&hub.verify_token=MY_SECRET_WHATSAPP_TOKEN&hub.challenge=CHALLENGE_ACCEPTED')
            print(f"Response: {resp.status_code} - {resp.data.decode('utf-8')}")

            # 2. Test Message POSTs
            for i, tc in enumerate(test_cases):
                print(f"\n--- TEST CASE {i+1} (POST) ---")
                text_sent = tc['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                print(f"Message: {text_sent}")
                response = client.post('/webhook', json=tc)
                print(json.dumps(response.json, indent=2))
    else:
        print("Starting WhatsApp Flask Webhook handler on port 5000...")
        app.run(port=5000, debug=True)

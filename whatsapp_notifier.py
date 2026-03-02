import time

# ==============================================================================
# WHATSAPP NOTIFIER AGENT: Instant Business Owner Alerts
# ==============================================================================

class WhatsAppNotifier:
    """
    Acts as a real-time bridge pushing High-Priority alerts directly to the 
    business owner's phone when the Lead Warmth Engine scores a lead >= 8.
    """
    def __init__(self, owner_phone=None):
        # In production this pulls the verified owner_phone from the Sovereign Vault settings
        self.owner_phone = owner_phone or "+15550000000"
        
    def send_verification_alert(self):
        """
        Dispatches the initial "System Active" text when the feature is toggled on.
        """
        message = "System Active: Sovereign OS will now alert you to every High-Intent lead in real-time."
        return self._dispatch_to_whatsapp(self.owner_phone, message)

    def process_new_lead(self, lead_data):
        """
        Evaluates a new lead against the "Warmth Threshold". 
        Only scores >= 8 trigger a lock-screen optimized push notification.
        """
        warmth = lead_data.get('warmth', 0)
        
        # The Warmth Threshold
        if warmth >= 8:
            return self._trigger_hot_lead_alert(lead_data)
        return {"status": "SKIPPED", "reason": f"Warmth {warmth} below threshold"}

    def _trigger_hot_lead_alert(self, lead_data):
        """
        Drafts the high-conversion payload design and simulates sending it.
        """
        name = lead_data.get('name', 'A new customer')
        interest = lead_data.get('interest', 'your services')
        
        # The Payload Design: Optimized for immediate lock-screen reading
        # Includes a simulated "Deep Link" intended to snap the owner right into the exact lead chat.
        payload = (
            f"🔥 HOT LEAD: {name} is asking about {interest}! "
            f"They want to book/buy ASAP. Reply now to lock this in.\n\n"
            f"Tap to chat: https://wa.me/mock_client_link?text=Hi_{name.replace(' ', '_')}"
        )
        
        return self._dispatch_to_whatsapp(self.owner_phone, payload)

    def _dispatch_to_whatsapp(self, phone, message):
        """
        Simulates the actual HTTP POST to the WhatsApp Cloud API.
        """
        time.sleep(1) # Simulate network ping
        
        # MOCK HTTP DISPATCH
        # payload = {"messaging_product": "whatsapp", "to": phone, "type": "text", "text": {"body": message}}
        # response = requests.post(f"https://graph.facebook.com/v20.0/.../messages", json=payload, headers=headers)
        
        # We print to console in dev mode to prove the ping works silently
        print(f"\n[WHATSAPP NOTIFIER API CALL -> {phone}]\n{message}\n")
        
        return {"status": "DELIVERED", "message": message}

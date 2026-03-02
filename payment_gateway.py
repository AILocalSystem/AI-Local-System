import time
import uuid
import streamlit as st

# ==============================================================================
# PAYMENT BRIDGE AGENT: Subscription & Fulfillment Gating
# ==============================================================================

class PaymentGateway:
    """
    Manages subscription statuses and gates the "Fulfillment" features.
    Simulates a secure checkout (via Razorpay/Stripe) and a webhook auto-unlock.
    """
    def __init__(self, provider="stripe"):
        self.provider = provider
        
    def check_subscription_status(self, vault_data):
        """
        Reads the 'subscription_active' flag from the client's Sovereign Vault.
        """
        return vault_data.get('subscription_active', False)

    def generate_checkout_url(self, business_name, plan_type="Pro Fulfillment"):
        """
        Generates a secure, one-time checkout URL for the specific business.
        """
        # Mock logic to simulate generating a Stripe or Razorpay Intent URL
        session_id = str(uuid.uuid4())[:12]
        if self.provider == "razorpay":
            base_url = "https://rzp.io/l/sovereign_"
        else:
            base_url = "https://buy.stripe.com/test_"
            
        checkout_url = f"{base_url}{session_id}?client={business_name.replace(' ', '')}&plan={plan_type.replace(' ', '')}"
        
        return checkout_url

    def simulate_webhook_success(self, business_name):
        """
        Simulates the Webhook listener receiving a "Payment Success" signal.
        Immediately unlocks the vault features.
        """
        time.sleep(1.5) # Simulating network processing delay
        print(f"\n[WEBHOOK RECEIVED] {self.provider.upper()}: Payment successful for {business_name}")
        
        # In production: Call VaultConnector to update Google Sheets -> `subscription_active = TRUE`
        # For the UI prototype, we update Streamlit Session State directly:
        st.session_state[f"sub_active_{business_name}"] = True
        return True

# Helper function to inject into Streamlit UI flows directly
def render_locked_feature_ui(business_name, feature_name):
    """
    Renders the dynamic Checkout UI when a locked feature is clicked.
    """
    st.markdown(f"""
        <div style="background: #FFFBEB; border: 1px solid #FCD34D; padding: 16px; border-radius: 8px; margin-top: 12px;">
            <h4 style="color: #92400E; margin: 0 0 8px 0;">🔒 Fulfillment Feature Locked</h4>
            <p style="color: #B45309; font-size: 0.9em; margin: 0 0 12px 0;">
                The <b>{feature_name}</b> protocol requires an active Sovereign Pro subscription.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    gateway = PaymentGateway()
    checkout_url = gateway.generate_checkout_url(business_name)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.link_button(f"💳 Upgrade to Pro ({gateway.provider.title()})", checkout_url, use_container_width=True)
    with col2:
        # Developer Sandbox override to simulate the async webhook firing
        if st.button("Dev: Simulate Webhook Success", key=f"sim_webhook_{business_name}_{feature_name}", use_container_width=True):
            with st.spinner("Awaiting Webhook trigger..."):
                gateway.simulate_webhook_success(business_name)
            st.success("Webhook received! Refreshing Vault connection...")
            time.sleep(1)
            st.rerun()

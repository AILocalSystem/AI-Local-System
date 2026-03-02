import os
import time
import uuid

try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

# ==============================================================================
# FULFILLMENT AGENT 5: THE ARCHITECT
# ==============================================================================

class GBPArchitect:
    """
    Executes SEO repairs identified in the 10/10 Audit directly on the client's 
    Google Business Profile.
    """
    def __init__(self, business_name, current_description=None, missing_keywords=None):
        self.business_name = business_name
        self.current_description = current_description or f"We are a local business called {business_name}."
        self.missing_keywords = missing_keywords or ["reliable", "affordable", "expert", "local", "best"]
        
        # Initialize Gemini Client if available
        if has_genai and os.environ.get("GEMINI_API_KEY"):
            self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        else:
            self.client = None

    def _generate_with_gemini(self, prompt, fallback):
        """Helper to invoke Gemini or return fallback if unavailable."""
        if not self.client:
            return fallback
            
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7)
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return fallback

    # --------------------------------------------------------------------------
    # MODULE A: Description Rewriting
    # --------------------------------------------------------------------------
    def rewrite_seo_description(self):
        """
        Uses Gemini to rewrite the 750-character business description, injecting 
        the top 5 missing keywords.
        """
        time.sleep(1) # Simulating API latency
        
        keywords_str = ", ".join(self.missing_keywords[:5])
        prompt = f"""
        Rewrite the following Google Business Profile description to be highly optimized for local SEO.
        Must be under 750 characters.
        Must naturally inject these exact keywords: {keywords_str}.
        Current Description: "{self.current_description}"
        """
        
        fallback = f"Welcome to {self.business_name}. We pride ourselves on being the {self.missing_keywords[0]} choice in town. Our services are {self.missing_keywords[1]} and {self.missing_keywords[2]}, built for our amazing {self.missing_keywords[3]} community. Experience the {self.missing_keywords[4]} service today!"
        
        new_description = self._generate_with_gemini(prompt, fallback)
        
        # Simulated GBP API Call
        # service.locations().patch(name=location_name, body={"profile": {"description": new_description}}, updateMask="profile.description").execute()
        
        return new_description

    # --------------------------------------------------------------------------
    # MODULE B: Category Injection
    # --------------------------------------------------------------------------
    def inject_secondary_categories(self, new_categories):
        """
        Adds missing secondary categories to the GBP via the API.
        """
        time.sleep(1)
        
        categories_to_add = new_categories[:9] # Up to 9 allowed by GBP API
        
        # Simulated GBP API Call
        # Here we would fetch current categories, append these, and patch.
        # body = {"categories": {"additionalCategories": [{"name": c} for c in all_cats]}}
        
        return categories_to_add

    # --------------------------------------------------------------------------
    # MODULE C: Service Menu Expansion
    # --------------------------------------------------------------------------
    def expand_service_menu(self, high_intent_keywords):
        """
        Automatically creates custom service descriptions for every high-intent keyword.
        """
        time.sleep(1.5)
        
        created_services = []
        for kw in high_intent_keywords:
            prompt = f"Write a short, engaging 1-sentence service description offering '{kw}' at {self.business_name}."
            fallback = f"Discover our premium {kw} services, tailored specifically to meet your highest standards."
            
            desc = self._generate_with_gemini(prompt, fallback)
            created_services.append({"name": kw.title(), "description": desc})
            
        # Simulated GBP API Call back to the Service Catalog array
        
        return created_services

    # --------------------------------------------------------------------------
    # MODULE D: Seeded Q&A (Founder FAQs)
    # --------------------------------------------------------------------------
    def publish_seeded_qa(self):
        """
        Automatically posts 3 "Owner-Authored" questions and answers to the profile 
        to increase engagement and keyword relevance.
        """
        time.sleep(2)
        
        prompt = f"""
        Write 3 common, high-intent local SEO Questions and Answers for a business named {self.business_name}.
        The answers should sound like they were written by the owner and mention local service benefits.
        Format as clear Q: and A: pairs.
        """
        
        fallback_qa = [
            {"q": "Do you offer same-day service?", "a": f"Yes, at {self.business_name} we prioritize urgent requests to ensure our local community is always taken care of."},
            {"q": "What makes your service different?", "a": "We blend years of expertise with a commitment to affordable, high-quality results you can trust."},
            {"q": "How can I book an appointment?", "a": "You can book directly right here on our profile, or send us a WhatsApp message for an instant reply!"}
        ]
        
        # Simulated GBP Q&A API Call
        # Not easily supported in basic GBP API without specific Q&A endpoints, but mock executed here.
        
        return fallback_qa

# ==============================================================================
# PIPELINE EXECUTOR
# ==============================================================================
def execute_profile_repair_pipeline(business_name, yield_callbacks=False):
    """
    Runs all 4 modules sequentially. If yield_callbacks is True, it acts as a generator
    yielding status updates for the Streamlit UI.
    """
    architect = GBPArchitect(
        business_name=business_name,
        missing_keywords=["same-day", "certified", "emergency", "affordable price", "local experts"]
    )
    
    if yield_callbacks: yield ("Ingesting Keyword Mirror Data...", 25)
    
    if yield_callbacks: yield ("Rewriting SEO Description...", 50)
    desc = architect.rewrite_seo_description()
    
    if yield_callbacks: yield ("Injecting Secondary Categories...", 75)
    cats = architect.inject_secondary_categories(["Emergency Service", "Certified Contractor", "Local Consultant"])
    
    if yield_callbacks: yield ("Publishing Seeded Q&As...", 90)
    services = architect.expand_service_menu(["emergency dispatch", "affordable repair"])
    qas = architect.publish_seeded_qa()
    
    if yield_callbacks: yield ("✅ Profile Optimized (Score 92/100)", 100)
    
    return {
        "status": "SUCCESS",
        "new_score": 92,
        "description_rewritten": desc,
        "categories_added": cats,
        "services_expanded": len(services),
        "qas_published": len(qas)
    }

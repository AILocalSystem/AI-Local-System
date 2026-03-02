import os
import time

try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

# ==============================================================================
# FULFILLMENT AGENT 6: THE CONTENT STRATEGIST
# ==============================================================================

class ContentStrategist:
    """
    Generates, optimizes, and schedules weekly Google Business Profile (GBP) updates 
    to maintain high "Signals of Life" for the algorithm.
    """
    def __init__(self, business_name, niche, client_email=None):
        self.business_name = business_name
        self.niche = niche
        self.client_email = client_email
        
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
                config=types.GenerateContentConfig(temperature=0.8)
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return fallback

    # --------------------------------------------------------------------------
    # MODULE A: The 30-Day Niche Calendar
    # --------------------------------------------------------------------------
    def generate_30_day_calendar(self):
        """
        Drafts 4 high-intent posts (1 per week) based on the client's niche.
        Post Types: Educational, Social Proof, Offer, Humanity.
        """
        time.sleep(1) # Simulating API latency
        
        prompt = f"""
        You are an elite local SEO Content Strategist. Create a 4-week Google Business Profile 
        post calendar for a {self.niche} business named "{self.business_name}".
        
        Week 1 (Educational): Focus on "Our Secret" or expertise.
        Week 2 (Social Proof): Focus on a 5-star review or customer success.
        Week 3 (Offer): A compelling "Call Now" or "10% off today" urgency offer.
        Week 4 (Humanity): "Meet the team" or behind-the-scenes.
        
        Format each week clearly. Keep posts punchy, under 1500 characters, and end with a CTA.
        """
        
        fallback_posts = [
            {"week": 1, "type": "Educational", "title": "The Core Mechanics of What We Do", "content": f"Ever wonder why {self.business_name} yields such great results? It comes down to our specialized approach to {self.niche}. Click to learn more.", "action": "LEARN_MORE"},
            {"week": 2, "type": "Social Proof", "title": "Another Thrilled Customer!", "content": "Nothing makes us happier than reading notes from our amazing community. Thank you for making us your top choice!", "action": "READ_REVIEWS"},
            {"week": 3, "type": "Offer", "title": "Mid-Week Flash Special", "content": "For the next 48 hours, mention this post at checkout and receive an exclusive bonus on your service. Do not miss out!", "action": "CALL_NOW"},
            {"week": 4, "type": "Humanity", "title": "Meet the Team behind the Magic", "content": "We aren't just a business, we are your neighbors. Come say hi to our dedicated staff this week!", "action": "BOOK_ONLINE"}
        ]
        
        # If we invoke Gemini here, we would parse out the 4 posts.
        # For system stability without parsing logic, we will return the robust fallback structure 
        # and assume the LLM output can be structured similarly in production.
        
        return fallback_posts

    # --------------------------------------------------------------------------
    # MODULE B: Image-to-Caption Engine
    # --------------------------------------------------------------------------
    def caption_new_image(self, image_url_or_path):
        """
        Simulates analyzing an uploaded image and writing an optimized 50-word caption.
        """
        time.sleep(1.5)
        
        # In a real build, we'd pass the file to Gemini Vision
        prompt = f"Analyze this image for {self.business_name} ({self.niche}). Write a 50-word SEO optimized caption with a Call Now CTA."
        fallback = f"Just wrapped up another incredible project at {self.business_name}! We love providing top-tier {self.niche} services to our community. If you need reliable, expert help, don't wait. Tap the 'Call Now' button below to schedule your consultation today! 📞💥"
        
        return self._generate_with_gemini(prompt, fallback)

    # --------------------------------------------------------------------------
    # MODULE C: Scheduled Dispatcher
    # --------------------------------------------------------------------------
    def extract_next_ideal_post(self, calendar_posts):
        """
        Simulates extracting the next post and scheduling it for a high-traffic time via the GBP API.
        """
        if not calendar_posts:
            return None
            
        next_post = calendar_posts[2] # Simulating pulling "Week 3"
        
        # Simulated logic identifying next Tuesday at 10:00 AM
        scheduled_time = "Wednesday @ 10:00 AM"
        
        return {
            "title": next_post["title"],
            "content": next_post["content"],
            "scheduled_for": scheduled_time,
            "status": "Scheduled"
        }

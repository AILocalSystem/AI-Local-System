import json
import re
from media_optimizer import MediaOptimizer

class WebArchitect:
    def __init__(self, audit_json):
        self.data = audit_json
        
        # Determine Site Type for dynamic label
        cat = self.data.get("primary_category", "Professional Service").lower()
        if any(kw in cat for kw in ['plumber', 'roof', 'electrician', 'contractor', 'hvac']):
            self.site_type = "Lead Generation"
        elif any(kw in cat for kw in ['restaurant', 'cafe', 'store', 'shop']):
            self.site_type = "Catalog"
        else:
            self.site_type = "Brochure"
            
        self.optimizer = MediaOptimizer()
            
        placeholder_hero = f"https://source.unsplash.com/800x400/?{self.data.get('primary_category', 'Professional Service').replace(' ', ',')}"
        
        self.template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[BUSINESS_NAME] | [PRIMARY_SERVICE] in [CITY]</title> 
    <style>
        :root {{
            --bg: #f8f9fa;
            --card: #ffffff;
            --text: #1a1a1a;
            --accent: #25D366; /* WhatsApp Green for High-Intent CTA [cite: 10] */
        }}
        body {{ font-family: -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; }}
        
        /* Bento-Box Grid [cite: 6] */
        .container {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; padding: 15px; max-width: 1200px; margin: auto; }}
        
        /* Mobile-First Adjustments [cite: 7] */
        @media (max-width: 768px) {{ .container {{ grid-template-columns: 1fr; }} .hero {{ grid-column: span 1 !important; }} }}

        .card {{ background: var(--card); border: 1px solid #eaeaea; border-radius: 20px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }}
        .hero {{ grid-column: span 3; grid-row: span 2; display: flex; flex-direction: column; justify-content: center; background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('{placeholder_hero}'); background-size: cover; background-position: center; color: white; }}
        
        /* High-Intent CTAs [cite: 10, 31] */
        .cta-btn {{ background: var(--accent); color: white; text-decoration: none; padding: 15px 25px; border-radius: 50px; font-weight: bold; text-align: center; display: inline-block; width: fit-content; margin-top: 15px; border: none; font-size: 1rem; cursor: pointer; }}
        
        /* Typography [cite: 9, 27] */
        h1 {{ font-size: 2.5rem; margin-bottom: 10px; line-height: 1.1; color: white; }}
        p {{ line-height: 1.5; margin-bottom: 15px; font-size: 1.1rem; max-width: 45ch; }} /* Short paragraphs [cite: 9] */
        
        /* Bento-Box Interior Page Grid */
        .interior-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px; }}
        @media (max-width: 768px) {{ .interior-grid {{ grid-template-columns: 1fr; }} }}
        .service-card {{ background: #ffffff; border-radius: 24px; overflow: hidden; border: 1px solid #f0f0f0; transition: transform 0.2s ease; }}
        .service-image {{ width: 100%; height: 200px; object-fit: cover; background: #eee; }}
        .service-content {{ padding: 20px; }}
        .service-content h3 {{ margin: 0 0 10px 0; font-size: 1.25rem; }}
        .service-content p {{ font-size: 0.95rem; line-height: 1.4; color: #666; }}
    </style>
</head>
<body>
    <!-- Browser Header Mock for Staging Preview -->
    <div style="background: #E2E8F0; padding: 10px 16px; display: flex; align-items: center; border-bottom: 1px solid #CBD5E1;">
        <div style="display: flex; gap: 6px;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background: #EF4444;"></div>
            <div style="width: 12px; height: 12px; border-radius: 50%; background: #F59E0B;"></div>
            <div style="width: 12px; height: 12px; border-radius: 50%; background: #10B981;"></div>
        </div>
        <div style="background: white; padding: 4px 12px; border-radius: 4px; margin-left: 16px; font-size: 0.75em; color: #94A3B8; flex-grow: 1; text-align: center;">
            https://www.[CLEAN_URL].com
        </div>
    </div>

    <section class="container">
        [PAGE_CONTENT]
        <footer class="card" style="grid-column: span 4; text-align: center;">
            <p style="max-width: none; margin: 0 auto;"><strong>[BUSINESS_NAME]</strong><br>Main Operating Zone: [CITY] | [PHONE_NUMBER]</p>
            <p style="max-width: none; font-size: 0.9em; color: #666; margin-bottom: 0;">© 2026 Sovereign OS. All rights reserved.</p>
        </footer>
    </section>

</body>
</html>"""

    def _generate_home_content(self, mapping, placeholder_hero):
        return f"""
        <div class="card hero" style="background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('{placeholder_hero}'); background-size: cover; background-position: center; color: white;">
             <span style="background: #3B82F6; padding: 4px 12px; border-radius: 20px; font-size: 0.7em; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; width: fit-content; margin-bottom: 15px;">{mapping['[SITE_TYPE]']} Design</span>
            <h1>Expert {mapping['[PRIMARY_SERVICE]']} in {mapping['[CITY]']}</h1>
            <p style="color: #f8f9fa;">Providing the most reliable {mapping['[PRIMARY_SERVICE]']} for the {mapping['[CITY]']} community. Fast response and professional results guaranteed.</p>
            <a href="https://wa.me/1234567890" class="cta-btn">WhatsApp Chat Now</a>
        </div>

        <div class="card" style="grid-column: span 1; grid-row: span 2;">
            <h3 style="margin-top: 0;">Verified Reviews</h3>
            {mapping['[REVIEW_HTML]']}
        </div>

        <div class="card" style="grid-column: span 3; display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; padding: 10px;">
                <h3 style="margin-top: 0;">Service Areas</h3>
                <ul style="padding-left: 15px; margin-bottom: 0;">
                    <li>{mapping['[CITY]']} Downtown</li>
                    <li>North {mapping['[CITY]']}</li>
                    <li>South {mapping['[CITY]']}</li>
                </ul>
            </div>
        </div>
        """

    def _generate_services_content(self, mapping):
        srv_img_1 = self.optimizer.enhance_image(mapping['[PRIMARY_SERVICE]'], ["tools"], "400x300")
        srv_img_2 = self.optimizer.enhance_image(mapping['[PRIMARY_SERVICE]'], ["team", "working"], "400x300")
        alt_1 = self.optimizer.generate_seo_alt_text(mapping['[PRIMARY_SERVICE]'], mapping['[CITY]'], "Services List Image 1")
        alt_2 = self.optimizer.generate_seo_alt_text(mapping['[PRIMARY_SERVICE]'], mapping['[CITY]'], "Services List Image 2")
        
        return f"""
        <div class="card" style="grid-column: span 4; background: #E2E8F0; padding: 40px; text-align: center;">
            <h1 style="color: #1E293B; margin: 0;">Our {mapping['[PRIMARY_SERVICE]']} Services</h1>
            <p style="color: #475569; max-width: 600px; margin: 10px auto 0 auto;">Comprehensive solutions tailored for our {mapping['[CITY]']} clients.</p>
        </div>
        <div class="interior-grid" style="grid-column: span 4; padding: 0;">
            <div class="service-card">
                <img src="{srv_img_1}" alt="{alt_1}" class="service-image">
                <div class="service-content">
                    <h3>Residential {mapping['[PRIMARY_SERVICE]']}</h3>
                    <p>Top-tier services for your home. We guarantee quality and safety on every job.</p>
                    <a href="#" style="color: #3B82F6; font-weight: bold; text-decoration: none;">Learn More →</a>
                </div>
            </div>
            <div class="service-card">
                <img src="{srv_img_2}" alt="{alt_2}" class="service-image">
                <div class="service-content">
                    <h3>Commercial {mapping['[PRIMARY_SERVICE]']}</h3>
                    <p>Scalable, professional solutions designed to keep your business running smoothly without interruption.</p>
                    <a href="#" style="color: #3B82F6; font-weight: bold; text-decoration: none;">Learn More →</a>
                </div>
            </div>
        </div>
        """

    def _generate_about_content(self, mapping):
        team_img = self.optimizer.enhance_image(mapping['[PRIMARY_SERVICE]'], ["professional", "portrait"], "800x400")
        alt_team = self.optimizer.generate_seo_alt_text(mapping['[PRIMARY_SERVICE]'], mapping['[CITY]'], "About Us Team Image")
        return f"""
        <div class="card" style="grid-column: span 4;">
            <img src="{team_img}" alt="{alt_team}" style="width: 100%; max-height: 300px; object-fit: cover; border-radius: 12px; margin-bottom: 20px;">
            <div style="max-width: 800px; padding: 0 20px;">
                <span style="background: #10B981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; text-transform: uppercase;">Trusted locally since 2012</span>
                <h1 style="color: #1E293B; margin-top: 15px;">About {mapping['[BUSINESS_NAME]']}</h1>
                <p style="font-size: 1.1em; color: #475569; line-height: 1.6;">We are {mapping['[CITY]']}'s premier choice for {mapping['[PRIMARY_SERVICE]']}. Our foundation is built on trust, transparency, and delivering unparalleled value to our neighbors.</p>
                <div style="display: flex; gap: 20px; margin-top: 30px;">
                    <div><h2 style="margin: 0; color: #3B82F6;">10+</h2><span style="color: #94A3B8; font-size: 0.9em;">Years Active</span></div>
                    <div><h2 style="margin: 0; color: #3B82F6;">500+</h2><span style="color: #94A3B8; font-size: 0.9em;">Projects Done</span></div>
                    <div><h2 style="margin: 0; color: #3B82F6;">4.9⭐</h2><span style="color: #94A3B8; font-size: 0.9em;">Average Rating</span></div>
                </div>
            </div>
        </div>
        """

    def _generate_contact_content(self, mapping):
        map_img = f"https://source.unsplash.com/800x400/?map,city,{mapping['[CITY]'].replace(' ', ',')}"
        alt_map = self.optimizer.generate_seo_alt_text(mapping['[PRIMARY_SERVICE]'], mapping['[CITY]'], "Contact Service Area Map")
        return f"""
        <div class="card" style="grid-column: span 2; display: flex; flex-direction: column; justify-content: center; padding: 40px;">
            <h1 style="color: #1E293B; margin-top: 0;">Get Your Quote</h1>
            <p style="color: #475569;">Fill out the form below and our {mapping['[CITY]']} team will contact you within 24 hours.</p>
            <div style="background: #F8FAFC; padding: 20px; border-radius: 8px; border: 1px dashed #CBD5E1; margin-top: 20px;">
                <p style="color: #94A3B8; text-align: center; margin: 0; font-family: monospace;">[Lead Generation Form Rendered Here]</p>
            </div>
            <a href="https://wa.me/1234567890" class="cta-btn" style="width: auto;">Or WhatsApp Us Instantly</a>
        </div>
        <div class="card" style="grid-column: span 2; padding: 0; overflow: hidden; position: relative;">
            <img src="{map_img}" alt="{alt_map}" style="width: 100%; height: 100%; object-fit: cover;">
            <div style="position: absolute; bottom: 20px; left: 20px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h4 style="margin: 0 0 5px 0; color: #1E293B;">HQ Location</h4>
                <p style="margin: 0; color: #64748B; font-size: 0.9em;">{mapping['[EXACT_ADDRESS]']}</p>
                <p style="margin: 5px 0 0 0; color: #64748B; font-size: 0.9em;">📞 {mapping['[PHONE_NUMBER]']}</p>
            </div>
        </div>
        """

    def synthesize_seo_content(self):
        """
        Uses Agent 5 (SEO Strategist) logic to turn raw categories 
        into high-intent, active-voice copy[cite: 8, 9, 21].
        """
        primary_service = self.data.get('primary_category', '[PRIMARY_SERVICE]')
        city = self.data.get('city', '[CITY]')
        
        # Crafting the Hero headline and description [cite: 12, 22]
        hero_title = f"Elite {primary_service} in {city}"
        hero_desc = (f"We provide professional {primary_service} solutions tailored for the {city} community. "
                     f"Our team focuses on reliability, quality, and fast response times to ensure your satisfaction.")
        
        return hero_title, hero_desc

    def generate_html_preview(self, page_type="Home"): # Keeping name for compatibility with onboarding_portal.py
        """
        Maps JSON data to HTML placeholders and determines 
        site architecture[cite: 12, 16, 19].
        """
        b_name = self.data.get('name', 'Your Business')
        c_name = self.data.get('city', 'Your City')
        p_category = self.data.get('primary_category', 'Professional Service')
        clean_url = f"{b_name.replace(' ', '').lower()}{c_name.replace(' ', '').lower()}"
        
        # Base Hero image logic for Home
        placeholder_hero = self.optimizer.enhance_image(p_category, ["professional", "wide"])
        
        # 1. Identity Mapping [cite: 3, 12]
        mapping = {
            "[BUSINESS_NAME]": b_name,
            "[CITY]": c_name,
            "[CLEAN_URL]": clean_url,
            "[SITE_TYPE]": self.site_type,
            "[PRIMARY_SERVICE]": p_category,
            "[PHONE_NUMBER]": self.data.get('phone', 'Contact Us'),
            "[EXACT_ADDRESS]": self.data.get('address', 'Visit our Location'),
        }

        # 2. Content Synthesis [cite: 25, 27]
        hero_title, hero_desc = self.synthesize_seo_content()
        mapping["Expert [PRIMARY_SERVICE] in [CITY]"] = hero_title
        mapping["Providing the most reliable [PRIMARY_SERVICE] for the [CITY] community. Fast response and professional results guaranteed."] = hero_desc

        # 3. Dynamic Section Generation (Reviews) [cite: 4, 31]
        reviews = self.data.get('top_reviews', [])
        if not reviews:
             reviews = [
                {"rating": 5, "text": f"Best {mapping['[PRIMARY_SERVICE]'].lower()} in {mapping['[CITY]']}!", "author": "Google Local Guide"},
                {"rating": 5, "text": "Highly recommend their services. Great communication.", "author": "Verified Customer"},
                {"rating": 5, "text": "Will use them again for sure.", "author": "Local Client"}
            ]
             
        review_html = ""
        for r in reviews[:3]: # Top 3 reviews only [cite: 30]
            stars = "⭐" * int(r.get('rating', 5))
            review_html += f"""
                <div style="background: #F8FAFC; padding: 12px; border-left: 3px solid #F59E0B; margin-bottom: 10px; font-style: italic; color: #475569; font-size: 0.9em;">
                    "{r.get('text', 'Fantastic experience!')[:100]}..."<br>
                    <span style="font-size: 0.85em; color: #94A3B8; font-style: normal;">- {r.get('author', 'Customer')} {stars}</span>
                </div>
            """
            
        mapping["[REVIEW_HTML]"] = review_html
        
        # Select Interior Page Logic
        if page_type == "Services":
            page_content = self._generate_services_content(mapping)
        elif page_type == "About":
            page_content = self._generate_about_content(mapping)
        elif page_type == "Contact":
            page_content = self._generate_contact_content(mapping)
        else:
            page_content = self._generate_home_content(mapping, placeholder_hero)
            
        mapping["[PAGE_CONTENT]"] = page_content
        
        # 4. Final Render [cite: 11]
        final_site = self.template
        for placeholder, value in mapping.items():
            final_site = final_site.replace(placeholder, str(value))
        
        return final_site

def save_to_onboarding_db(blueprint):
    """
    Mock database save for the pending website claim.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[MOCK DB SAVE] Website Claim Locked: {json.dumps(blueprint, indent=2)}")
    return True

def lock_visionary_vault(audit_data, ai_image_manifest):
    """
    Freezes the AI-generated 'Visionary Version' so it remains 
    consistent from preview to final launch. [cite: 1, 3, 12]
    """
    committed_blueprint = {
        "business_name": audit_data.get('name', '[BUSINESS_NAME]'), # Using 'name' from public_audit
        "city": audit_data.get('city', '[CITY]'),
        "primary_service": audit_data.get('primary_category', '[PRIMARY_SERVICE]'),
        "nap_data": {
            "name": audit_data.get('name'),
            "address": audit_data.get('address'),
            "phone": audit_data.get('phone')
        },
        "ai_images": ai_image_manifest, # Stores the specific AI seeds/prompts [cite: 24]
        "status": "CLAIMED"
    }
    # Save to a temporary 'pending_claims' table before OAuth
    return save_to_onboarding_db(committed_blueprint)

import time
import random

# ==============================================================================
# OUTREACH SCOUT: Lead Generation Engine
# ==============================================================================

class OutreachScout:
    """
    Identifies high-intent local prospects based on "Ranking Weakness" signals.
    Simulates searching an area and parsing GBP listings for specific deficits.
    """
    def __init__(self, target_keyword, target_city):
        self.target_keyword = target_keyword.lower()
        self.target_city = target_city.lower()

    def search_for_prospects(self):
        """
        Simulates querying an API (like Google Places New) and applying the
        three core targeting filters. Returns a list of matched leads.
        """
        time.sleep(1.5) # Simulate API latency
        
        # MOCK DATA GENERATOR FOR DEMONSTRATION
        base_names = ["Elite", "Quality", "Local", "Premier", "Downtown", "Express", "City", "Precision"]
        
        prospects = []
        for i in range(12): # Generate an initial batch to filter
            # 1. The Invisible Filter (Simulating page depth 1-5 where >1 is invisible)
            page_depth = random.choice([1, 2, 2, 3, 3, 4])
            
            # 2. The Reputation Gap
            rating = round(random.uniform(3.0, 4.9), 1)
            reviews = random.randint(2, 150)
            
            # 3. The Incomplete Flag
            has_website = random.random() > 0.3 # 30% chance missing
            has_phone = random.random() > 0.1   # 10% chance missing
            
            # Apply Filters: We only want businesses struggling in at least one area
            is_invisible = page_depth > 1
            has_rep_gap = rating < 4.2 or reviews < 20
            is_incomplete = not has_website or not has_phone
            
            if is_invisible or has_rep_gap or is_incomplete:
                reasons = []
                if is_invisible: reasons.append(f"Ranked Page {page_depth}")
                if has_rep_gap: reasons.append(f"Low Trust ({rating}★, {reviews} reviews)")
                if not has_website: reasons.append("Missing Website")
                if not has_phone: reasons.append("Missing Phone")
                
                prospects.append({
                    "id": f"scout_{i}",
                    "name": f"{random.choice(base_names)} {self.target_keyword.split()[0].capitalize()}",
                    "rating": rating,
                    "reviews": reviews,
                    "website": "Yes" if has_website else "No",
                    "phone": "Yes" if has_phone else "No",
                    "deficits": ", ".join(reasons),
                    # 4. The "Red Map" Pre-Generator
                    "geo_grid_mock": self._generate_mini_red_map()
                })
        
        # Ensure we return at least a few for the UI demo even if random fails
        if not prospects:
            prospects.append({
                "id": "scout_forced",
                "name": f"Struggling {self.target_keyword.split()[0].capitalize()}",
                "rating": 3.8,
                "reviews": 12,
                "website": "No",
                "phone": "Yes",
                "deficits": "Ranked Page 3, Low Trust, Missing Website",
                "geo_grid_mock": self._generate_mini_red_map()
            })
            
        return prospects

    def _generate_mini_red_map(self):
        """
        Creates a string representation of a "Red Node" geo-grid layout to show to 
        the agency owner as a visual hook. Use emoji blocks to simulate the red/green.
        """
        # A struggling business will have mostly red (🟥), some orange (🟧), and maybe one green (🟩)
        colors = ["🟥", "🟥", "🟥", "🟧", "🟥", "🟥", "🟩", "🟧", "🟥"]
        random.shuffle(colors)
        
        # Format as a 3x3 grid
        grid = f"{colors[0]}{colors[1]}{colors[2]}\n{colors[3]}{colors[4]}{colors[5]}\n{colors[6]}{colors[7]}{colors[8]}"
        return grid

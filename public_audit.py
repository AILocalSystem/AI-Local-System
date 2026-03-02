import os
import random
import json

def get_public_audit(business_identifier: str) -> dict:
    """
    Simulates or performs a public SEO audit using Google Places data.
    Takes a business name or Google Maps link.
    """
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")

    if not api_key:
        return _generate_elite_audit(business_identifier)
        
    # TODO: Implement actual Google Places API fetching here when key is present.
    # Logic:
    # 1. Search for business using Text Search / Place ID.
    # 2. Get Place Details: Rating, Reviews, Categories.
    # 3. Search nearby for competitors in the same primary category.
    # 4. Calculate health score vs competitors using the Elite framework weights.
    
    return _generate_elite_audit(business_identifier)

def _generate_elite_audit(business_identifier: str) -> dict:
    """
    Generates realistic Elite Audit Framework data.
    Weighted Scoring: Category (30%), Velocity (25%), Keywords (20%), Visual (15%), Hours (10%).
    Top 3 Competitor Gap Analysis loop included.
    """
    # Simulate Base Scores based on the 10/10 Elite Framework (0-100 for each category)
    cat_score = random.randint(50, 100)
    vel_score = random.randint(30, 90)
    kwd_score = random.randint(40, 85)
    vis_score = random.randint(60, 95)
    hrs_score = random.choice([0, 100]) # Either they have hours or they don't
    
    # Weighted Scoring Algorithm
    health_score = int(
        (cat_score * 0.30) +
        (vel_score * 0.25) +
        (kwd_score * 0.20) +
        (vis_score * 0.15) +
        (hrs_score * 0.10)
    )
    
    # 5-Step Visual Hierarchy Breakdown
    breakdown = {
        "Category Alignment (30%)": f"{cat_score}/100",
        "Review Velocity (25%)": f"{vel_score}/100",
        "Keyword Saturation (20%)": f"{kwd_score}/100",
        "Visual Assets (15%)": f"{vis_score}/100",
        "Operating Hours (10%)": f"{hrs_score}/100"
    }
    
    strengths = []
    weaknesses = []
    
    if cat_score >= 80: strengths.append("Primary Category strongly aligned")
    else: weaknesses.append("Missing or weak Secondary Categories")
        
    if vel_score >= 70: strengths.append("Consistent Review Velocity")
    else: weaknesses.append("Low Review Velocity compared to local baseline")
        
    if kwd_score >= 75: strengths.append("Good Keyword Saturation in profile")
    else: weaknesses.append("Missing high-buyer-intent Keywords")
        
    if vis_score >= 70: strengths.append("Strong Visual Assets")
    else: weaknesses.append("Lacking recent visual media uploads")
        
    if hrs_score == 100: strengths.append("Operating Hours correctly set")
    else: weaknesses.append("Operating Hours missing or inconsistent")
        
    # Top 3 Competitor Gap Analysis Loop
    competitors = [
        {"name": "Competitor A", "reviews": random.randint(100, 500), "rating": round(random.uniform(4.0, 4.9), 1)},
        {"name": "Competitor B", "reviews": random.randint(50, 300), "rating": round(random.uniform(3.8, 4.7), 1)},
        {"name": "Competitor C", "reviews": random.randint(80, 400), "rating": round(random.uniform(4.2, 5.0), 1)},
    ]
    
    avg_comp_reviews = int(sum(c["reviews"] for c in competitors) / 3)
    user_reviews = random.randint(10, avg_comp_reviews - 10 if avg_comp_reviews > 10 else 50)
    review_gap = avg_comp_reviews - user_reviews
    
    comp_gap = f"Top 3 local competitors average {avg_comp_reviews} reviews ({review_gap} more than you) and dominate the Local Pack."
    
    if business_identifier.lower().strip() == "demo":
        health_score = 68
        strengths = ["Strong Rating (4.8 Stars)", "Operating Hours correctly set"]
        weaknesses = ["Low Review Velocity", "Missing high-buyer-intent Keywords", "Lacking recent visual media uploads"]
        comp_gap = "Top 3 competitors have 45% more reviews and publish visual updates weekly."
        breakdown = {
            "Category Alignment (30%)": "70/100",
            "Review Velocity (25%)": "40/100",
            "Keyword Saturation (20%)": "60/100",
            "Visual Assets (15%)": "50/100",
            "Operating Hours (10%)": "100/100"
        }
        
    keyword_mirror = {
        "used": ["Yoga Classes", "Studio", "Meditation"],
        "missing": ["Vinyasa Flow near me", "Beginner Yoga", "Prenatal Yoga", "Mindfulness Retreat", "Drop-in Classes"],
        "lsi_suggestions": [
            "Add 'Yoga Studio' as a Secondary Category.",
            "Include 'Vinyasa Flow' and 'Prenatal Yoga' in your Services menu with descriptions.",
            "Update your Google Description to explicitly mention 'drop-in classes' and 'beginners welcome'."
        ]
    }
    
    # ---------------------------------------------------------
    # Visual AI Trust Audit Generation
    # ---------------------------------------------------------
    trust_score = random.randint(30, 85)
    humanity_score = random.randint(10, 60)
    trust_deficit = humanity_score < 40 or trust_score < 50
    
    missing_visual_assets = []
    if humanity_score < 50: missing_visual_assets.append("Zero photos of your team/staff.")
    if random.choice([True, False]): missing_visual_assets.append("No interior shots showing a busy environment.")
    if random.choice([True, False]): missing_visual_assets.append("Missing high-quality exterior storefront signage.")
    
    if len(missing_visual_assets) == 0:
         missing_visual_assets.append("Lacking recent visual media uploads.")
         
    comp_humanity_avg = random.randint(65, 95)
    comp_photo_avg = random.randint(40, 150)
    user_photo_count = random.randint(5, 25)
    
    visual_trust_audit = {
        "score": trust_score,
        "humanity_score": humanity_score,
        "is_trust_deficit": trust_deficit,
        "missing_assets": missing_visual_assets,
        "benchmarking": {
            "competitor_photo_avg": comp_photo_avg,
            "competitor_humanity_score": comp_humanity_avg,
            "user_photo_count": user_photo_count
        }
    }
    
    # ---------------------------------------------------------
    # The Revenue Opportunity Gap Generation
    # ---------------------------------------------------------
    lost_hours = random.randint(1, 4)
    searches_per_hour = random.randint(40, 150)
    conversion_rate = 0.05 # 5%
    avg_ticket_value = random.randint(35, 150)
    
    missed_searches_monthly = lost_hours * searches_per_hour * 30
    monthly_revenue_loss = int(missed_searches_monthly * conversion_rate * avg_ticket_value)
    
    revenue_gap = {
        "lost_hours": lost_hours,
        "peak_search_window": "7:00 PM - 10:00 PM",
        "competitor_closing_time": "10:00 PM",
        "user_closing_time": f"{10 - lost_hours}:00 PM",
        "missed_searches_monthly": missed_searches_monthly,
        "monthly_revenue_loss": monthly_revenue_loss,
        "warning_text": f"Closing at {10 - lost_hours}:00 PM instead of 10:00 PM is costing you an estimated ${monthly_revenue_loss:,}/month in lost bookings."
    }

    data = {
        "health_score": health_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "competitor_gap": comp_gap,
        "breakdown": breakdown,
        "competitors": competitors,
        "keyword_mirror": keyword_mirror,
        "visual_trust": visual_trust_audit,
        "revenue_gap": revenue_gap
    }
    
    return {
        "action": "RENDER_PUBLIC_REPORT",
        "data": data
    }

if __name__ == "__main__":
    # Test execution
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "demo"
    result = get_public_audit(target)
    print(json.dumps(result, indent=2))

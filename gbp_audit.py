import os
import json
import argparse
import logging
import requests
from typing import Dict, Any, List
from collections import Counter
import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from token_manager import get_authenticated_service

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def extract_keywords(text: str) -> List[str]:
    """Simple keyword extraction focusing on words > 3 chars."""
    if not text:
        return []
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stop_words = {'this', 'that', 'with', 'from', 'your', 'have', 'are', 'what', 'which', 'their'}
    return [w for w in words if w not in stop_words]

def analyze_sentiment(reviews: List[Dict]) -> float:
    """Calculates average sentiment score (0 to 1) for a list of reviews."""
    if not reviews:
        return 0.5
    analyzer = SentimentIntensityAnalyzer()
    total_score = 0.0
    for rev in reviews:
        comment = rev.get("comment", "")
        if comment:
            # Compound score is -1 to 1. Normalize to 0 to 1.
            score = (analyzer.polarity_scores(comment)['compound'] + 1) / 2
            total_score += score
        else:
            # Neutral default if no comment text
            total_score += 0.5
    return total_score / len(reviews)

def fetch_gbp_data() -> Dict[str, Any]:
    """Fetch profile details, performance metrics, and review sentiment."""
    logger.info("Initializing GBP APIs...")
    # NOTE: To use these specific APIs, they must be enabled in Google Cloud Console.
    try:
        # Example API endpoints - Google changes these frequently
        account_api = get_authenticated_service('mybusinessaccountmanagement', 'v1')
        if not account_api: return {}
        
        accounts_list = account_api.accounts().list().execute()
        accounts = accounts_list.get('accounts', [])
        
        if not accounts:
            logger.warning("No GBP accounts found.")
            return {}
            
        account_name = accounts[0]['name']
        
        info_api = get_authenticated_service('mybusinessbusinessinformation', 'v1')
        locations_list = info_api.accounts().locations().list(parent=account_name, readMask='name,title,categories,profile,serviceArea').execute()
        locations = locations_list.get('locations', [])
        
        if not locations:
            logger.warning("No locations found in the first account.")
            return {}
            
        loc = locations[0]
        
        primary_cat = loc.get('categories', {}).get('primaryCategory', {}).get('displayName', 'Unknown')
        
        # Build client data object
        client_data = {
            "name": loc.get('title', 'Unknown'),
            "primary_category": primary_cat,
            "secondary_categories": [c.get('displayName') for c in loc.get('categories', {}).get('additionalCategories', [])],
            "description": loc.get('profile', {}).get('description', ''),
            "services": [], # Extracted from actual service area/services APIs
            "address": "Address hidden in this API version",
            "sentiment_score": 0.85 # Mocked as reviews API requires separate endpoint integration
        }
        return client_data
        
    except Exception as e:
        logger.error(f"Error fetching real GBP data: {e}")
        return {}

def fetch_competitor_data(category: str, city: str, api_key: str) -> List[Dict]:
    """Search Google Maps for Top 3 competitors."""
    if not api_key:
        logger.warning("No GOOGLE_MAPS_API_KEY provided. Returning mock top 3 competitors.")
        return mock_competitors()
        
    logger.info("Searching Google Places for competitors...")
    query = f"{category} in {city}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={api_key}"
    response = requests.get(url)
    
    competitors = []
    if response.status_code == 200:
        results = response.json().get('results', [])[:3]
        for r in results:
            competitors.append({
                "name": r.get('name'),
                "rating": r.get('rating', 0),
                "user_ratings_total": r.get('user_ratings_total', 0),
                "types": r.get('types', []),
                "description": "", # Text search doesn't return full details, requires Places Details API
                "posts_frequency": 1.5 # Mock as requested
            })
    return competitors

def mock_competitors() -> List[Dict]:
    return [
        {"name": "Competitor A", "rating": 4.8, "user_ratings_total": 120, "types": ["plumber"], "description": "Emergency 24/7 plumbing.", "posts_frequency": 2.0},
        {"name": "Competitor B", "rating": 4.6, "user_ratings_total": 85, "types": ["plumber", "contractor"], "description": "Affordable and licensed.", "posts_frequency": 1.0},
        {"name": "Competitor C", "rating": 4.9, "user_ratings_total": 200, "types": ["plumber"], "description": "Local experts in leak repair.", "posts_frequency": 4.0},
    ]

def run_seo_gap_analysis(client_data: Dict, competitors: List[Dict]) -> Dict:
    logger.info("Running SEO Gap Analysis...")
    all_comp_keywords = []
    for c in competitors:
        all_comp_keywords.extend(extract_keywords(c.get('description', '')))
    
    comp_kw_counts = Counter(all_comp_keywords)
    top_comp_kws = [k for k, v in comp_kw_counts.most_common(5)]
    
    client_kws = set(extract_keywords(client_data.get('description', '')))
    
    missing = [kw for kw in top_comp_kws if kw not in client_kws]
    
    # Mocking Service catalog processing
    service_catalog = [
        {"name": "Leak Repair", "exists_on_gbp": "Leak Repair" in client_data.get('services', [])},
        {"name": "Emergency 24/7", "exists_on_gbp": False}
    ]
    
    avg_post_freq = sum(c.get('posts_frequency', 0) for c in competitors) / max(len(competitors), 1)
    
    analysis = {
        "missing_keywords": missing,
        "competitor_benchmark": f"Ranked #?. Competitors post ~{avg_post_freq:.1f} times/week.",
        "tab_Service_Catalog": service_catalog
    }
    return analysis

def generate_vault_payload(client_data: Dict, analysis: Dict) -> Dict:
    """Generates the structured JSON payload for the Sovereign Vault."""
    payload = {
        "action": "POPULATE_INITIAL_AUDIT",
        "data": {
            "tab_GBP_Audit": {
                "current_description": client_data.get("description", ""),
                "sentiment_score": f"{client_data.get('sentiment_score', 0.0):.2f}",
                "missing_keywords": analysis.get("missing_keywords", []),
                "competitor_benchmark": analysis.get("competitor_benchmark", "")
            },
            "tab_Business_Profile": {
                "name": client_data.get("name", ""),
                "category": client_data.get("primary_category", ""),
                "address": client_data.get("address", "")
            },
            "tab_Service_Catalog": analysis.get("tab_Service_Catalog", [])
        }
    }
    return payload

def run_mock() -> Dict:
    """Runs a mock execution pipeline for testing without API keys."""
    logger.info("Executing MOCK data extraction and analysis...")
    client_data = {
        "name": "Acme Plumbers",
        "primary_category": "Plumber",
        "secondary_categories": ["Heating contractor", "Drainage service"],
        "description": "We are the best plumbers in town, providing 24/7 emergency service.",
        "services": ["Leak Repair", "Pipe Installation", "Water Heater Repair"],
        "address": "123 Main St, Springfield, IL 62701",
        "sentiment_score": 0.85
    }
    
    analysis = run_seo_gap_analysis(client_data, mock_competitors())
    return generate_vault_payload(client_data, analysis)

def main():
    parser = argparse.ArgumentParser(description="GBP Audit Tool")
    parser.add_argument("--mock", action="store_true", help="Run with mock data instead of real API calls")
    parser.add_argument("--city", type=str, default="Unknown City", help="City for competitor search")
    args = parser.parse_args()
    
    if args.mock:
        payload = run_mock()
        print(json.dumps(payload, indent=2))
        return
        
        return
        
    client_data = fetch_gbp_data()
    if not client_data:
        print(json.dumps({"error": "Failed to extract client GBP data."}))
        return
        
    maps_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    competitors = fetch_competitor_data(category=client_data.get("primary_category", "Business"), city=args.city, api_key=maps_key)
    
    analysis = run_seo_gap_analysis(client_data, competitors)
    payload = generate_vault_payload(client_data, analysis)
    
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()

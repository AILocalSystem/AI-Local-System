import os
import json
import argparse
import logging
from typing import Dict, Any, List

# Try to import Google GenAI
try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ==============================================================================
# MOCK LLM RESPONSES (Used for --mock flag or if API key is missing)
# ==============================================================================
def mock_generate_description() -> str:
    return (
        "As the premier Plumber in Springfield, Acme Plumbers is dedicated to keeping "
        "your home safe and dry. Whether you live near Lincoln Park, the Historic Downtown "
        "Square, or out by Lake Springfield, our certified technicians are ready 24/7. "
        "We specialize in emergency leak repair, comprehensive pipe installation, and fast "
        "water heater replacements. Don't let a small drip turn into a flooded basement. "
        "With affordable, licensed local service, we guarantee your complete satisfaction. "
        "Call us today or easily book an appointment online to experience the best plumbing "
        "service in town!"
    )

def mock_generate_services() -> List[Dict]:
    return [
        {
            "service_id": "srv_001",
            "optimized_title": "Emergency AC Repair & Troubleshooting",
            "optimized_description": "Our comprehensive HVAC maintenance and emergency technician service "
                                     "ensures your cooling system fix is handled quickly and professionally. "
                                     "Stay comfortable year-round."
        },
        {
            "service_id": "srv_002",
            "optimized_title": "24/7 Leak Repair & Pipe Installation",
            "optimized_description": "Fast plumbing leak repair, affordable pipe replacement, and licensed "
                                     "emergency water damage prevention for residential properties."
        }
    ]

def mock_generate_posts() -> List[Dict]:
    return [
        {
            "type": "Offer",
            "text": "Get 15% off your first plumbing service call! Expires this Friday. Call now.",
            "image_prompt": "A professional plumber smiling and pointing at a bright blue clipboard with a 15% Off bold badge."
        },
        {
            "type": "Educational/Tip",
            "text": "Did you know a running toilet can waste 200 gallons of water daily? Listen closely for hissing sounds to catch leaks early!",
            "image_prompt": "A close-up of a sparkling clean modern toilet tank with a small animated water droplet icon."
        },
        {
            "type": "Service Highlight",
            "text": "Our certified techs just installed a high-efficiency water heater in Lincoln Park. Same-day service available!",
            "image_prompt": "A shiny new tankless water heater installed against a clean utility room wall."
        },
        {
            "type": "Service Highlight",
            "text": "Clogged drain slowing you down? We use advanced camera inspections to clear blockages fast and safely.",
            "image_prompt": "A plumber looking intently at a digital monitor displaying the inside of a clean pipe."
        }
    ]

# ==============================================================================
# LLM GENERATION WITH GEMINI API
# ==============================================================================
def call_gemini(client, system_instruction: str, prompt: str, schema: Any = None) -> Any:
    """Wrapper to call Gemini API and return structured JSON output if schema is provided."""
    model = 'gemini-2.5-flash'
    
    config = types.GenerateContentConfig()
    
    if system_instruction:
         config.system_instruction = system_instruction
         
    if schema:
        config.response_mime_type = "application/json"
        config.response_schema = schema

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config
    )
    
    if schema:
        return json.loads(response.text)
    return response.text

def generate_description(client, client_data: Dict, analysis: Dict) -> str:
    """Generates a 750-character GBP description."""
    cat = client_data.get('category', 'business')
    city = client_data.get('address', 'the local area')
    old_desc = analysis.get('current_description', '')
    missing_kw = ", ".join(analysis.get('missing_keywords', []))
    
    sys_instruction = (
        "You are an expert Local SEO copywriter. Generate a 750-character Google "
        "Business Profile description. Follow these exact constraints: "
        f"1. Must include the exact phrase '{cat}' in the FIRST sentence. "
        "2. Must include 3 known local landmarks or neighborhood names for the location constraint. "
        "3. Incorporate as many of the provided missing SEO keywords naturally. "
        "4. End with a clear Call-to-Action (CTA)."
    )
    
    prompt = (
        f"Location: {city}\n"
        f"Missing Keywords to include: {missing_kw}\n"
        f"Original/Draft Description Tone to adapt: {old_desc}\n\n"
        "Generate the optimized Description."
    )
    
    logger.info("Generating Profile Description via Gemini...")
    return call_gemini(client, sys_instruction, prompt)

def generate_services(client, service_catalog: List[Dict]) -> List[Dict]:
    """Generates optimized names and 300-char descriptions for services."""
    schema = {
        "type": "ARRAY",
        "description": "A list of optimized services",
        "items": {
            "type": "OBJECT",
            "properties": {
                "service_id": {"type": "STRING", "description": "The original name of the service"},
                "optimized_title": {"type": "STRING", "description": "SEO optimized version of the title"},
                "optimized_description": {"type": "STRING", "description": "300 character description utilizing LSI keywords"}
            },
            "required": ["service_id", "optimized_title", "optimized_description"]
        }
    }
    
    sys_instruction = (
        "You are an expert Local SEO copywriter. For each provided service, generate "
        "an optimized title and a 300-character description. You MUST use Latent Semantic Indexing (LSI) "
        "keywords heavily related to the service. For example if it is AC Repair, use HVAC maintenance, "
        "cooling system fix, emergency technician."
    )
    
    prompt = f"Optimize these services: {[s.get('name') for s in service_catalog]}"
    
    logger.info("Generating Optimized Services via Gemini...")
    return call_gemini(client, sys_instruction, prompt, schema=schema)

def generate_posts(client, client_data: Dict) -> List[Dict]:
    """Generates 4 unique GBP Posts (Offer, Educational, 2x Service Highlight) with image prompts."""
    cat = client_data.get('category', 'business')
    
    schema = {
        "type": "ARRAY",
        "description": "List of 4 Google Business Profile Posts",
        "items": {
            "type": "OBJECT",
            "properties": {
                "type": {"type": "STRING", "enum": ["Offer", "Educational/Tip", "Service Highlight"]},
                "text": {"type": "STRING", "description": "The copy for the Google Post"},
                "image_prompt": {"type": "STRING", "description": "Visual prompt text describing the accompanying image"}
            },
            "required": ["type", "text", "image_prompt"]
        }
    }
    
    sys_instruction = (
        "Create exactly 4 Google Business Profile posts for a local business in the category: "
        f"'{cat}'. The posts must be: 1 'Offer', 1 'Educational/Tip', and 2 'Service Highlight'. "
        "Keep the text engaging, punchy, and under 1500 characters. "
        "For each post, generate a highly detailed visual 'image_prompt' that could be fed to an AI image generator "
        "(e.g., Midjourney/DALL-E) to create the accompanying post image."
    )
    
    prompt = "Generate the 4 GBP Posts."
    
    logger.info("Generating Posts and Visual Prompts via Gemini...")
    return call_gemini(client, sys_instruction, prompt, schema=schema)


# ==============================================================================
# MAIN ORCHESTRATOR
# ==============================================================================
def parse_input_json(filepath: str) -> Dict:
    """Reads the Vault JSON output from Step 1."""
    if not os.path.exists(filepath):
        logger.error(f"Input file {filepath} not found.")
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def run_pipeline(mock: bool, input_file: str = None):
    # Retrieve Input Data
    # For now, if no input file is passed, just mock the vault data
    if input_file:
        input_data = parse_input_json(input_file).get('data', {})
    else:
        logger.info("No input vault provided. Using hardcoded mock data for context synthesis.")
        input_data = {
            "tab_GBP_Audit": {
                "current_description": "We do good plumbing.",
                "missing_keywords": ["24/7", "licensed", "emergency leak"]
            },
            "tab_Business_Profile": {
                "name": "Acme Plumbers",
                "category": "Plumber",
                "address": "Springfield"
            },
            "tab_Service_Catalog": [
                {"name": "Leak Repair", "exists_on_gbp": True},
                {"name": "Water Heater Installation", "exists_on_gbp": False}
            ]
        }
        
    client_data = input_data.get('tab_Business_Profile', {})
    analysis = input_data.get('tab_GBP_Audit', {})
    services = input_data.get('tab_Service_Catalog', [])

    # Route logic to Mock or LLM
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if mock or not has_genai or not gemini_key:
        if not mock:
            logger.warning("No Gemini API key or missing google-genai library. Falling back to MOCK template data.")
        logger.info("Executing MOCK SEO Rewriter...")
        desc = mock_generate_description()
        svcs = mock_generate_services()
        posts = mock_generate_posts()
    else:
        logger.info("Executing LIVE Gemini SEO Rewriter...")
        client = genai.Client(api_key=gemini_key)
        desc = generate_description(client, client_data, analysis)
        svcs = generate_services(client, services)
        posts = generate_posts(client, client_data)
        
    # Format Response Vault Payload (PREPARE_GBP_UPDATE)
    payload = {
        "action": "PREPARE_GBP_UPDATE",
        "data": {
            "proposed_description": desc,
            "proposed_services": svcs,
            "first_month_posts": posts
        }
    }
    
    print(json.dumps(payload, indent=2))

def main():
    parser = argparse.ArgumentParser(description="GBP SEO Optimizer Tool")
    parser.add_argument("--mock", action="store_true", help="Run with mock template data instead of Gemini API")
    parser.add_argument("--input", type=str, help="Path to the JSON output from Step 1 (Sovereign Vault populator)")
    args = parser.parse_args()
    
    run_pipeline(args.mock, args.input)

if __name__ == "__main__":
    main()

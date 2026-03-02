import json
import logging
import os
from datetime import datetime

# Try to import Google GenAI
try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ==============================================================================
# MOCK VAULT DATA
# ==============================================================================
VAULT_DATA = {
    "tab_Business_Profile": {
        "name": "Acme Plumbers",
        "owner_name": "Bob",
        "owner_phone": "+15550001234"
    },
    "tab_GBP_Audit": {
        "views_last_week": 1500,
        "views_this_week": 2100,
    },
    "tab_Lead_Pipeline": [
        {"interest": "Leak Repair", "status": "Completed", "revenue": 150},
        {"interest": "Water Heater Install", "status": "Completed", "revenue": 800},
        {"interest": "Leak Repair", "status": "Completed", "revenue": 150},
        {"interest": "Drain Clearing", "status": "AUTO_RESPONDING", "revenue": 0},
    ],
    "tab_Review_Log": [
        {"rating": 5, "replied": True, "date_logged": "this_week"},
        {"rating": 5, "replied": True, "date_logged": "this_week"},
        {"rating": 1, "status": "REQUIRES_APPROVAL", "date_logged": "this_week"}
    ]
}

def harvest_data():
    """Calculates weekly delta and top performers."""
    audit = VAULT_DATA["tab_GBP_Audit"]
    pipeline = VAULT_DATA["tab_Lead_Pipeline"]
    reviews = VAULT_DATA["tab_Review_Log"]
    
    # Growth
    view_increase = 0
    if audit["views_last_week"]:
        view_increase = int(((audit["views_this_week"] - audit["views_last_week"]) / audit["views_last_week"]) * 100)
    extra_searches = audit["views_this_week"] - audit["views_last_week"]
    
    # Revenue & Leads
    total_leads = len(pipeline)
    completed_revenue = sum(lead.get("revenue", 0) for lead in pipeline if lead.get("status") == "Completed")
    
    # Top Performer
    service_counts = {}
    for l in pipeline:
        if l["status"] == "Completed":
            s = l["interest"]
            service_counts[s] = service_counts.get(s, 0) + 1
    
    top_performer = max(service_counts, key=service_counts.get) if service_counts else "N/A"
    
    # Reputation & Alerts
    new_5_stars = len([r for r in reviews if r.get("rating") == 5 and r.get("replied")])
    pending_tasks = len([r for r in reviews if r.get("status") == "REQUIRES_APPROVAL"])
    
    return {
        "view_increase_pct": view_increase,
        "extra_searches": extra_searches,
        "total_leads": total_leads,
        "completed_revenue": completed_revenue,
        "new_5_stars": new_5_stars,
        "pending_tasks": pending_tasks,
        "top_performer": top_performer
    }

def generate_humanized_report(metrics) -> str:
    biz = VAULT_DATA["tab_Business_Profile"]
    
    template = f"""Good morning, {biz['owner_name']}! Here is your Growth Report for {biz['name']} last week:

📈 Google Visibility: Up {metrics['view_increase_pct']}% (You appeared in {metrics['extra_searches']} more local searches!)
💬 New Leads: {metrics['total_leads']} new conversations started on WhatsApp.
💰 Estimated Revenue: ${metrics['completed_revenue']} generated from AI-closed deals. (Top Performer: {metrics['top_performer']})
⭐ Reputation: {metrics['new_5_stars']} new 5-star reviews replied to automatically.

You have {metrics['pending_tasks']} pending tasks in your Dashboard Action Center. Check them here: https://dashboard.yourdomain.com

Have a great week of growth!"""

    if has_genai and os.environ.get("GEMINI_API_KEY"):
        # We can ask Gemini to humanize it slightly more if desired.
        # But per requirements, the template itself is highly structured. We'll use the template explicitly.
        pass
        
    return template

def main():
    logger.info("Harvesting Vault Data for Weekly Summary...")
    metrics = harvest_data()
    
    logger.info("Formatting Growth Report...")
    report_text = generate_humanized_report(metrics)
    
    payload = {
      "action": "SEND_WEEKLY_REPORT",
      "recipient": VAULT_DATA["tab_Business_Profile"]["owner_phone"],
      "summary_data": {
        "revenue": f"${metrics['completed_revenue']}",
        "leads": str(metrics['total_leads']),
        "rank_increase": f"{metrics['view_increase_pct']}%"
      },
      "message": report_text
    }
    
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()

import datetime
import random

def scan_stale_leads(pipeline: list) -> list:
    """
    Scans the database (pipeline) for stale leads.
    In this simulation, we identify leads as stale if they are not in the 'Completed' status
    or if we randomly define them as > 30 days old for demonstration.
    """
    stale_leads = []
    
    # We simulate a "30-Day Silence" rule detection.
    # In a real app with true timestamps, we'd do: (datetime.now() - lead.date).days > 30
    # For the mock dashboard, we'll generate 12 fake stale leads.
    
    mock_stale_names = ["James T.", "Linda Cook", "Robert Baratheon", "Ned S.", "Walter W.", 
                        "Jesse P.", "Saul G.", "Mike E.", "Gustavo F.", "Skyler W.", "Hank S.", "Marie S."]
    mock_interests = ["Leaky Pipe", "Water Heater Install", "General Pricing", "Emergency Drain Clearing"]
    
    for i in range(12):
        name = mock_stale_names[i]
        interest = random.choice(mock_interests)
        
        # Personalized Context Mapping Simulation (Gemini)
        if "Pipe" in interest or "Drain" in interest:
            msg = f"Hi {name}, it's been a while since your {interest} inquiry. Are your pipes holding up okay? Reply 'HELP' if you need a quick inspection!"
        elif "Heater" in interest:
            msg = f"Hi {name}, it's getting colder. Is the {interest} still performing well? We're offering a free winter tune-up for past clients."
        else:
            msg = f"Hi {name}, checking in to see if you still needed help with {interest}? Let me know if you want an updated quote."
            
        stale_leads.append({
            "name": name,
            "interest": interest,
            "draft_message": msg,
            "days_silent": random.randint(31, 90)
        })
        
    return stale_leads

def process_retention_responses(stale_leads: list) -> list:
    """
    Simulates sending the blast and catching incoming responses.
    Returns simulated reactivated lead objects to append to the live pipeline.
    """
    reactivated = []
    import time
    time.sleep(1.5) # Simulate API dispatch
    
    # Simulate that 2 out of the 12 customers responded immediately.
    responders = random.sample(stale_leads, 2)
    
    for lead in responders:
        reactivated.append({
            "timestamp": "Just Now",
            "name": lead["name"],
            "message": "Yes actually, can you come out today?", # High urgency
            "interest": lead["interest"],
            "status": "AUTO_RESPONDING"
        })
        
    return reactivated

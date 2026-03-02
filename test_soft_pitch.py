import os
import time

# Use our local portal functions
from onboarding_portal import generate_consultant_response

def run_test():
    print("====================================")
    print("   SOFT PITCH LOGIC VERIFICATION    ")
    print("====================================")
    
    audit_data = {
        "health_score": 62,
        "weaknesses": ["Missing Keywords", "Incomplete Profile Description", "No active Google posts"],
        "competitor_gap": "Top 3 competitors have 30% more reviews and 2x higher keyword density."
    }
    
    messages_history = [
        {"role": "assistant", "content": "Hello! I can analyze your audit score. What would you like to know?"}
    ]
    
    questions = [
        "Why is my score only 62?",
        "What do you mean by competitor gap?",
        "How do I add active Google posts?",
        "Is there a faster way to do this?"
    ]
    
    for i, q in enumerate(questions):
        print(f"\n[Message {i+1}] USER: {q}")
        messages_history.append({"role": "user", "content": q})
        
        response = generate_consultant_response(messages_history, audit_data)
        print(f"[Message {i+1}] AI: {response}")
        
        messages_history.append({"role": "assistant", "content": response})
        time.sleep(1) # just pacing it out
        
    print("\n------------------------------------")
    print("VERIFICATION COMPLETE:")
    print("Ensure Message 4 append is present.")

if __name__ == "__main__":
    run_test()

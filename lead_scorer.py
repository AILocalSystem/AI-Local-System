import re

def calculate_warmth_score(message: str) -> int:
    """
    Analyzes a WhatsApp message for intent, urgency, and sentiment,
    returning a Lead Warmth Score from 1 to 10.
    
    1–3 (Cold): General inquiry.
    4–7 (Warm): Specific interest in a service.
    8–10 (HOT): Ready to book or buy immediately.
    """
    if not message:
        return 2
        
    message_lower = message.lower()
    score = 2 # Base score

    # Intent Keywords (+Points)
    intent_keywords = ['price', 'booking', 'appointment', 'menu', 'reservation', 'cost', 'quote', 'buy', 'table']
    for kw in intent_keywords:
        if kw in message_lower:
            score += 3
    
    # Urgency (+Points)
    urgency_keywords = ['today', 'now', 'asap', 'tonight', 'immediately']
    for kw in urgency_keywords:
        if kw in message_lower:
            score += 3

    # Sentiment Penalty (-Points)
    penalty_keywords = ['just looking', 'not sure', 'frustrated', 'too expensive', 'maybe later', 'terrible', 'cancel']
    for kw in penalty_keywords:
        if kw in message_lower:
            score -= 4
            
    # Bound the score between 1 and 10
    return max(1, min(10, score))

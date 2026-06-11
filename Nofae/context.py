# context.py
# Conversation context and follow-up handling

def get_recent_topics(history, n=3):
    """Extract recent topics from conversation history"""
    topics = []
    for exchange in reversed(history[-n:]):
        words = exchange["user"].lower().split()
        # Filter out common words
        meaningful = [w for w in words if len(w) > 3 and w not in 
                     ("what", "when", "where", "which", "should", "would", "could",
                      "about", "this", "that", "these", "those", "have", "with")]
        topics.extend(meaningful[:2])  # Take first 2 meaningful words
    return list(set(topics))

def resolve_pronouns(text, history):
    """Try to resolve 'it', 'that', 'the other' based on context"""
    if not history:
        return text
    
    last = history[-1]["user"].lower()
    last_response = history[-1].get("response", "").lower()
    
    # Simple pronoun resolution for "it" and "that"
    if "it" in text.lower() or "that" in text.lower():
        # Look for action keywords in last exchange
        actions = ["study", "work", "play", "rest", "sleep", "game"]
        for action in actions:
            if action in last:
                text = text.replace(" it ", f" {action} ")
                text = text.replace(" it.", f" {action}.")
                text = text.replace(" it?", f" {action}?")
                text = text.replace(" that ", f" {action} ")
                text = text.replace(" that.", f" {action}.")
                text = text.replace(" that?", f" {action}?")
                break
    
    # Handle "the other" or "the other one"
    if "the other" in text.lower() and len(history) >= 1:
        last_user = history[-1]["user"].lower()
        last_response = history[-1].get("response", "").lower()
        
        actions = ["study", "work", "play", "rest", "sleep", "game"]
        
        # Find actions mentioned in last user message
        found_actions = [a for a in actions if a in last_user]
        
        # Find which action was chosen (appears in "Chosen action: X")
        chosen_action = None
        for action in actions:
            if f"chosen action: {action}" in last_response:
                chosen_action = action
                break
        
        # "the other" means the one that WASN'T chosen
        if len(found_actions) >= 2 and chosen_action:
            other_action = [a for a in found_actions if a != chosen_action]
            if other_action:
                text = text.replace("the other one", other_action[0])
                text = text.replace("the other", other_action[0])
        elif len(found_actions) >= 2:
            # If we can't find chosen action, default to second mentioned
            text = text.replace("the other one", found_actions[1])
            text = text.replace("the other", found_actions[1])
    
    return text

def is_follow_up(text):
    """Check if this seems like a follow-up question"""
    follow_up_patterns = [
        "what about", "how about", "and the other",
        "what else", "instead", "alternatively",
        "the other one", "the second"
    ]
    return any(pattern in text.lower() for pattern in follow_up_patterns)
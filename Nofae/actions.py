import re

ACTION_KEYWORDS = {
    "study": ["study", "learn", "read", "review", "homework"],
    "work": ["work", "job", "shift", "grind"],
    "play": ["play", "game", "gaming", "fun"],
    "rest": ["rest", "sleep", "relax", "chill", "nap"],
    "exercise": ["exercise", "workout", "gym", "run", "train", "sport"]
}

def extract_actions(text):
    t = text.lower()
    actions = []
    
    for action, keywords in ACTION_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'\b' + keyword + r'\b', t):
                actions.append(action)
                break
    
    return list(set(actions))
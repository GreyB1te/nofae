import json, os, re

RULES_FILE = "rules.json"

def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_rules(rules):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)

def add_rule(rules, pattern, response, confidence=1.0):
    rules.append({"pattern": pattern, "response": response, "confidence": confidence})

def apply_rules(rules, text):
    matches = []
    for r in rules:
        try:
            if re.search(r["pattern"], text, re.IGNORECASE):
                matches.append((r.get("confidence",1.0), r["response"]))
        except re.error:
            continue
    if matches:
        matches.sort(reverse=True)
        return matches[0][1]
    return None
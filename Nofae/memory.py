import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print(f"⚠️ Could not load {MEMORY_FILE}, starting fresh.")
            try:
                os.rename(MEMORY_FILE, MEMORY_FILE + ".backup")
                print(f"   Backup saved to {MEMORY_FILE}.backup")
            except:
                pass
            return {}
    return {}

def save_memory(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

def store_fact(mem, sentence, fact, source="user", confidence=1.0):
    words = sentence.lower().replace(".", "").split()
    topic = next((w for w in words if w not in ("the", "a", "an", "is")), words[0] if words else "general")
    
    mem.setdefault(topic, [])
    
    normalized_fact = fact.lower().strip()
    
    if not any(f.get("fact", "").lower().strip() == normalized_fact for f in mem[topic]):
        mem[topic].append({
            "fact": fact,
            "source": source,
            "confidence": confidence
        })

def query(mem, query_text):
    q = query_text.lower()
    results = []
    for topic, facts in mem.items():
        if q in topic or topic in q:
            results.extend(facts)
    results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    return results
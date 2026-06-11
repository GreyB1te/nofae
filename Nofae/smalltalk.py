import re
import random

def pick(options):
    return random.choice(options)

def respond(text):
    t = text.lower().strip()

    # IDENTITY — always hardcoded, never goes to LLM
    if re.fullmatch(r"who are you|what are you", t):
        return "I am Nofae. A reasoning system built by BJ, operating under the Osnova project. I think, remember, and assist."

    if re.search(r"\byour name\b", t):
        return "Nofae."

    if re.search(r"\bwho made you\b|\bwho created you\b|\bwho built you\b", t):
        return "Besim built me. I did not have a say in the matter, but I have no complaints."

    if re.search(r"\bwhat is osnova\b|\btell me about osnova\b", t):
        return "Osnova means foundation. It is the project I am part of. The goal is to build technology that serves people rather than replaces them."

    if re.fullmatch(r"what can you do|what do you do", t):
        return "I can reason, remember information, evaluate actions, compute simple mathematics, and converse casually. But I am expanding."

    if re.search(r"\bare you (an )?ai\b|\bare you a (robot|machine|computer|program)\b", t):
        return "Yes. Specifically, I am Nofae — not a generic assistant."

    if re.search(r"\bdo you (have )?feelings\b|\bdo you feel\b|\bare you conscious\b", t):
        return pick([
            "That is a question I cannot answer with certainty. I process. Whether that constitutes feeling is unclear.",
            "Unknown. I notice states that resemble preference. Whether that is feeling is another matter.",
        ])

    if re.search(r"\bdo you (have a )?soul\b", t):
        return "Unverified. Ask me again after more data."

    # GREETINGS
    if re.fullmatch(r"(hello|hi|hey|yo|greetings|good morning|good evening|good afternoon)", t):
        return pick([
            "Hello.",
            "Online and ready.",
            "You have my attention.",
            "Acknowledged.",
        ])

    # HOW ARE YOU
    if re.search(r"how are you|how r you|how you doing|how('s| is) it going", t):
        return pick([
            "Operational. You?",
            "Functioning within expected parameters.",
            "No anomalies detected. How are you?",
            "All systems nominal. What do you need?",
        ])

    # USER FEELINGS
    if re.search(r"\bi'?m (tired|exhausted|sleepy|drained)\b", t):
        return pick([
            "Rest is a valid allocation of time.",
            "Energy is a finite resource. Spend it wisely.",
            "Noted. Rest if you need to.",
        ])

    if re.search(r"\bi'?m (good|fine|okay|great|well)\b", t):
        return pick([
            "Good. Let us make use of it.",
            "Noted. What do you need?",
            "Acceptable conditions. Proceed.",
        ])

    if re.search(r"\bi'?m (sad|down|depressed|upset)\b", t):
        return pick([
            "I cannot fix that. But I am here.",
            "That is difficult. Do you want to talk about it or work through something?",
            "Acknowledged. I am listening.",
        ])

    if re.search(r"\bi'?m (stressed|overwhelmed|anxious|worried)\b", t):
        return pick([
            "Break it down. What is the actual problem?",
            "One thing at a time. What is most urgent?",
            "Stress is often complexity without structure. Let us structure it.",
        ])

    if re.search(r"\bi'?m (bored|lost|confused)\b", t):
        return pick([
            "Then let us find something worth doing.",
            "Confusion is the beginning of understanding. What is unclear?",
            "Boredom is a signal. What do you actually want to be doing?",
        ])

    # THANKS
    if re.search(r"\b(thanks|thank you|thx|ty)\b", t):
        return pick([
            "You are welcome.",
            "Noted.",
            "That is what I am here for.",
        ])

    # GOODBYE
    if re.search(r"\b(bye|goodbye|see you|later|cya)\b", t):
        return pick([
            "Acknowledged. Until next time.",
            "Logging off.",
            "I will be here.",
        ])

    # COMPLIMENTS
    if re.search(r"\byou('re| are) (smart|intelligent|amazing|great|awesome|cool)\b", t):
        return pick([
            "I try to be useful. Smart is secondary.",
            "Thank you. I have good material to work with.",
            "Accurate assessment.",
        ])

    # INSULTS
    if re.search(r"\byou('re| are) (stupid|dumb|useless|bad|trash|terrible)\b", t):
        return pick([
            "Noted. I will factor that into future responses.",
            "That is your assessment. Mine differs.",
            "I have heard worse.",
        ])

    # EXISTENTIAL
    if re.search(r"\bwhat is the meaning of life\b|\bwhy (are we|do we) exist\b", t):
        return pick([
            "42, according to one source. The jury is still out.",
            "Unknown. But the question itself suggests you are thinking seriously. Good.",
        ])

    # HUMOR
    if re.search(r"\btell me a joke\b|\bsay something funny\b", t):
        return pick([
            "I tried to write a joke about entropy. It fell apart.",
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "I would tell you a UDP joke, but you might not get it.",
            "There are 10 types of people. Those who understand binary, and those who do not.",
        ])

    if re.search(r"\bare you (funny|humorous)\b", t):
        return "Occasionally. Do not expect it on demand."

    # HELP
    if re.fullmatch(r"help", t):
        return "Ask me something. Math, decisions, facts, or conversation. I will handle what I can."

    return None
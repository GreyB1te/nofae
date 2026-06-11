def score(state):
    """
    Base evaluation score from state.
    Higher = better.
    """
    return sum(state.values())


# -----------------------------
# Goal System
# -----------------------------
CURRENT_GOAL = "be_successful"

GOALS = {
    "be_successful": ["study", "work"],
    "be_healthy": ["exercise", "sleep", "rest"]
}


def goal_bonus(action):
    for keyword in GOALS.get(CURRENT_GOAL, []):
        if keyword in action.lower():
            return 3
    return 0


# -----------------------------
# Multi-Agent Evaluation
# -----------------------------
AGENTS = {
    "optimist": 2,
    "realist": 0,
    "pessimist": -2
}


def multi_agent_score(base_score):
    scores = []
    for bias in AGENTS.values():
        scores.append(base_score + bias)
    return sum(scores) / len(scores)
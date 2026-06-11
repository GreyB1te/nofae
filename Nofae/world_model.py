import json
import os

# -----------------------------
# File paths
# -----------------------------
STATE_FILE = "state.json"
LEARNED_EFFECTS_FILE = "learned_effects.json"
ACTION_REWARD_FILE = "action_rewards.json"

# -----------------------------
# State configuration
# -----------------------------
STATE_LIMITS = {
    "energy": (0, 10),
    "health": (0, 10),
    "knowledge": (0, 20),
    "money": (0, 50)
}

DEFAULT_STATE = {
    "energy": 5,
    "health": 5,
    "knowledge": 0,
    "money": 0
}

# -----------------------------
# Default action effects
# -----------------------------
DEFAULT_EFFECTS = {
    "study": {"knowledge": 2, "energy": -1, "health": 0, "money": 0},
    "work": {"money": 2, "energy": -2, "health": 0, "knowledge": 0},
    "exercise": {"health": 2, "energy": -2, "knowledge": 0, "money": 0},
    "sleep": {"energy": 3, "health": 1, "knowledge": 0, "money": 0},
    "rest": {"energy": 3, "health": 1, "knowledge": 0, "money": 0},
    "play": {"energy": 1, "health": 0, "knowledge": 0, "money": 0},
    "game": {"energy": 1, "health": 0, "knowledge": 0, "money": 0},
    "socialize": {"energy": -1, "health": 1, "knowledge": 1, "money": 0}
}

# -----------------------------
# State persistence
# -----------------------------
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_STATE.copy()
    return DEFAULT_STATE.copy()


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def clamp_state(state):
    clamped = {}
    for k, v in state.items():
        lo, hi = STATE_LIMITS.get(k, (0, 100))
        clamped[k] = max(lo, min(hi, v))
    return clamped

# -----------------------------
# Learned effects
# -----------------------------
def load_learned_effects():
    if os.path.exists(LEARNED_EFFECTS_FILE):
        try:
            with open(LEARNED_EFFECTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_learned_effects(effects):
    with open(LEARNED_EFFECTS_FILE, "w") as f:
        json.dump(effects, f, indent=2)


def update_effect(effects, action, attr, change):
    """Update learned effect using weighted average for faster learning."""
    action = action.lower()
    effects.setdefault(action, {})
    effects[action][attr] = effects[action].get(attr, 0) * 0.5 + change * 0.5


def get_learned_effect(effects, action, attr):
    action = action.lower()
    return effects.get(action, {}).get(attr, None)

# -----------------------------
# Simulation
# -----------------------------
def simulate(state, action, learned_effects=None):
    action = action.lower()
    delta = {}

    # Learned effects take priority
    if learned_effects and action in learned_effects:
        for attr in STATE_LIMITS.keys():
            delta[attr] = learned_effects[action].get(attr, 0)
        return delta

    # Default effects fallback
    for key, effect in DEFAULT_EFFECTS.items():
        if key in action:
            return effect

    # Unknown action
    return None

# -----------------------------
# Reward memory
# -----------------------------
def load_action_rewards():
    if os.path.exists(ACTION_REWARD_FILE):
        try:
            with open(ACTION_REWARD_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_action_rewards(rewards):
    with open(ACTION_REWARD_FILE, "w") as f:
        json.dump(rewards, f, indent=2)


def update_action_reward(rewards, action, reward):
    """Weighted average for action reward memory."""
    action = action.lower()
    previous = rewards.get(action, 0)
    rewards[action] = previous * 0.8 + reward * 0.2
# Core-A v0.6.0 

import sys
import os
import time
import copy
import pyfiglet

sys.path.append(os.path.dirname(__file__))

import memory
import smalltalk
import reasoning
import math_eval
import actions
import evaluation
import world_model
import context
import llm

# ---------------- UTILS ----------------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def log(msg):
    print(f"[NOFAE] {msg}")

def apply_delta(state, delta):
    new_state = copy.deepcopy(state)
    for k, v in delta.items():
        new_state[k] = new_state.get(k, 0) + v
    return new_state

# ---------------- INTRO ----------------

def nofae_intro():
    import shutil

    is_first_run = not os.path.exists("memory.json")
    ascii_art = pyfiglet.figlet_format("NOFAE", font="small")

    # Split the ASCII into lines for animation
    art_lines = ascii_art.splitlines()

    # Get terminal height
    term_height = shutil.get_terminal_size().lines

    # Initial display: logo + boot sequence
    print(ascii_art)
    print("Core-A • v0.6.0\n")

    boot_steps = [
        "Booting memory core",
        "Loading reasoning engine",
        "Preparing smalltalk module",
        "Starting math evaluator",
        "Activating world simulator",
        "Loading action evaluation",
        "Initializing context awareness",
        "Connecting language backbone",
        "Finalizing startup"
    ]

    for step in boot_steps:
        print(f"[✓] {step}")
        time.sleep(0.15)

    print("\nNofae online.\n")
    time.sleep(0.7)

    # ---------- SPLASH FADE / SCROLL ----------
    # Scroll the ASCII logo up line by line
    for i in range(len(art_lines) + 5):
        clear_screen()
        # Print only the remaining lines (simulate scroll up)
        for line in art_lines[i:]:
            print(line)
        time.sleep(0.05)

    # Final clear and first-time greeting
    clear_screen()
    if is_first_run:
        print("👋 Looks like this is your first time!")
        print("I'm a blank slate — I'll learn as we go.")
        print("Try asking: 'should I work or study?' or type 'help'.\n")

# ---------------- FEEDBACK PARSER ----------------
def parse_feedback(text):
    changes = {}
    t = text.lower()

    if any(w in t for w in ["energized", "energetic", "awake", "refreshed"]):
        changes["energy"] = +2
    elif any(w in t for w in ["tired", "exhausted", "drained", "sleepy"]):
        changes["energy"] = -2
    elif any(w in t for w in ["okay", "fine", "meh", "same"]):
        changes["energy"] = 0

    if any(w in t for w in ["better", "healthier", "great"]):
        changes["health"] = +1
    elif any(w in t for w in ["worse", "sick", "unwell"]):
        changes["health"] = -1

    if any(w in t for w in ["learned", "understood", "smarter"]):
        changes["knowledge"] = +2

    if any(w in t for w in ["earned", "paid", "made money"]):
        changes["money"] = +3
    elif any(w in t for w in ["spent", "lost money", "broke"]):
        changes["money"] = -2

    return changes if changes else None

# ---------------- HISTORY ----------------
def push_history(history, user, response):
    history.append({
        "user": user,
        "response": response,
        "timestamp": time.time()
    })
    if len(history) > 10:
        history.pop(0)

# ---------------- MAIN ----------------
def main():
    mem = memory.load_memory()
    rules = reasoning.load_rules()
    state = world_model.load_state()
    learned_effects = world_model.load_learned_effects()
    action_rewards = world_model.load_action_rewards()

    conversation_history = []
    pending_feedback = None
    last_explanation = None

    nofae_intro()

    # Show initial state
    print("📊 Initial State:")
    for k, v in state.items():
        print(f"  {k.capitalize():10}: {v}")
    print()

    try:
        while True:
            user = input("User > ").strip()
            if not user:
                continue

            if conversation_history:
                user = context.resolve_pronouns(user, conversation_history)

            lower = user.lower()

            if lower in ("exit", "quit"):
                log("Saving and shutting down...")
                break

            if lower in ("help", "?", "commands"):
                help_text = """
Nofae v0.6.0 — Commands

Actions:
  should I work or study?

Memory:
  Facts end with '.'
  Query by keyword

Math:
  2+2, sqrt(16), sin(3.14)

Other:
  state / status
  why / explain
  exit / quit
"""
                print(help_text)
                push_history(conversation_history, user, "Help shown")
                continue

            if lower in ("state", "status"):
                print("\n📊 Current State:")
                for k, v in state.items():
                    lo, hi = world_model.STATE_LIMITS.get(k, (0, 100))
                    print(f"  {k.capitalize():10}: {v}/{hi}")
                print()
                push_history(conversation_history, user, "State shown")
                continue

            # ---------------- FEEDBACK ----------------
            if pending_feedback and (
                lower.startswith("feedback:") or
                any(w in lower for w in ["went", "felt", "ended", "was"])
            ):
                raw = user
                if lower.startswith("feedback:"):
                    raw = user[len("feedback:"):].strip()

                parsed = llm.parse_feedback(pending_feedback, raw)
                if parsed:
                    for attr, change in parsed.items():
                     world_model.update_effect(
                            learned_effects,
                            pending_feedback,
                            attr,
                            change
                        )

                    reward_value = sum(parsed.values())
                    world_model.update_action_reward(
                        action_rewards,
                        pending_feedback,
                        reward_value
                    )
                    world_model.save_action_rewards(action_rewards)
                    world_model.save_learned_effects(learned_effects)
                    print(f"✅ Learned how '{pending_feedback}' affects you.")
                else:
                    print("💭 Couldn't interpret feedback.")

                pending_feedback = None
                push_history(conversation_history, user, "Feedback processed")
                continue

            if lower in ("why", "explain"):
                print(last_explanation or "Nothing to explain yet.")
                push_history(conversation_history, user, "Explanation shown")
                continue

            talk = smalltalk.respond(user)
            if talk:
                print(f"Nofae: {talk}")
                push_history(conversation_history, user, talk)
                continue

            facts = memory.query(mem, user)
            if facts:
                for f in facts:
                    print(f"{f['fact']} (confidence {f['confidence']:.2f})")
                push_history(conversation_history, user, "Memory recall")
                continue

            if user.endswith("."):
                key = user.rstrip(".").lower()
                memory.store_fact(mem, key, user)
                memory.save_memory(mem)
                print("✅ Fact remembered.")
                push_history(conversation_history, user, "Fact stored")
                continue

            if math_eval.looks_like_math(user):
                result = math_eval.evaluate_math(user)
                print(f"🧮 {result if result is not None else 'Invalid expression'}")
                push_history(conversation_history, user, "Math evaluated")
                continue

            # ---------------- ACTIONS ----------------
            acts = actions.extract_actions(user)
            if not acts:
                acts = llm.classify_action(user)
            if acts:
                best_action = None
                best_score = -1e9
                explanation = []
                deltas = {}

                # --- PLAN MULTIPLE ACTIONS (lookahead 2 steps) ---
                for act in acts:
                    delta = world_model.simulate(state, act, learned_effects)
                    deltas[act] = delta

                    if delta is None:
                        explanation.append(f"Cannot simulate '{act}'.")
                        continue

                    imagined = world_model.clamp_state(
                        apply_delta(state, delta)
                    )

                    for next_act in acts:
                        next_delta = world_model.simulate(imagined, next_act, learned_effects)
                        if next_delta:
                            imagined2 = world_model.clamp_state(
                                apply_delta(imagined, next_delta)
                            )
                            imagined = imagined2

                    base_score = evaluation.score(imagined)
                    reward_bonus = action_rewards.get(act.lower(), 0)
                    goal_bonus = evaluation.goal_bonus(act)
                    base_score += reward_bonus + goal_bonus
                    score = evaluation.multi_agent_score(base_score)

                    explanation.append(f"\nIf '{act}':")
                    for k, v in delta.items():
                        explanation.append(f"  {k}: {v:+}")
                    explanation.append(f"  Score: {score}")

                    if score > best_score:
                        best_score = score
                        best_action = act

                if best_action:
                    explanation.append(f"\n✨ Chosen action: {best_action}")
                    last_explanation = "\n".join(explanation)
                    print(last_explanation)

                    delta = deltas[best_action] or {}
                    state = world_model.clamp_state(
                        apply_delta(state, delta)
                    )
                    world_model.save_state(state)

                    pending_feedback = best_action
                    print(f"\n💡 Tell me how '{best_action}' went!")

                    push_history(conversation_history, user, last_explanation)
                else:
                    print("\n".join(explanation))

                continue

            # ---------------- LLM FALLBACK ----------------
            response = llm.ask(user)
            print(f"🤖 Nofae: {response}")
            push_history(conversation_history, user, response)

    except KeyboardInterrupt:
        print("\nInterrupted.")

    finally:
        memory.save_memory(mem)
        reasoning.save_rules(rules)
        world_model.save_state(state)
        world_model.save_learned_effects(learned_effects)
        world_model.save_action_rewards(action_rewards)
        print("\n💾 Memory saved.")
        print("🤖 Nofae shutting down.")

if __name__ == "__main__":
    main()
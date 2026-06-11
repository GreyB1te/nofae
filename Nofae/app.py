from flask import Flask, request, jsonify, render_template_string
import memory
import smalltalk
import reasoning
import math_eval
import actions
import evaluation
import world_model
import context
import llm
import copy
import time
import os

app = Flask(__name__)

mem = memory.load_memory()
rules = reasoning.load_rules()
state = world_model.load_state()
learned_effects = world_model.load_learned_effects()
action_rewards = world_model.load_action_rewards()
conversation_history = []

def apply_delta(s, delta):
    new_state = copy.deepcopy(s)
    for k, v in delta.items():
        new_state[k] = new_state.get(k, 0) + v
    return new_state

def process(user):
    global state

    if conversation_history:
        user = context.resolve_pronouns(user, conversation_history)

    talk = smalltalk.respond(user)
    if talk:
        conversation_history.append({"user": user, "response": talk, "timestamp": time.time()})
        return talk

    facts = memory.query(mem, user)
    if facts:
        result = "\n".join([f"{f['fact']} (confidence {f['confidence']:.2f})" for f in facts])
        conversation_history.append({"user": user, "response": result, "timestamp": time.time()})
        return result

    if user.endswith("."):
        key = user.rstrip(".").lower()
        memory.store_fact(mem, key, user)
        memory.save_memory(mem)
        return "Fact remembered."

    if math_eval.looks_like_math(user):
        result = math_eval.evaluate_math(user)
        return f"{result if result is not None else 'Invalid expression'}"

    acts = actions.extract_actions(user)
    if not acts:
        acts = llm.classify_action(user)
    if acts:
        best_action = None
        best_score = -1e9
        explanation = []
        deltas = {}

        for act in acts:
            delta = world_model.simulate(state, act, learned_effects)
            deltas[act] = delta
            if delta is None:
                continue
            imagined = world_model.clamp_state(apply_delta(state, delta))
            base_score = evaluation.score(imagined)
            reward_bonus = action_rewards.get(act.lower(), 0)
            goal_bonus = evaluation.goal_bonus(act)
            base_score += reward_bonus + goal_bonus
            score = evaluation.multi_agent_score(base_score)
            explanation.append(f"If '{act}': score {score:.1f}")
            if score > best_score:
                best_score = score
                best_action = act

        if best_action:
            delta = deltas[best_action] or {}
            state = world_model.clamp_state(apply_delta(state, delta))
            world_model.save_state(state)
            explanation.append(f"Chosen: {best_action}")
            return "\n".join(explanation)

    rule = reasoning.apply_rules(rules, user)
    if rule:
        conversation_history.append({"user": user, "response": rule, "timestamp": time.time()})
        return rule

    response = llm.ask(user)
    conversation_history.append({"user": user, "response": response, "timestamp": time.time()})
    return response

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOFAE</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --red: #c0392b;
            --red-dim: #7a1a10;
            --cream: #e8dcc8;
            --cream-dim: #a89880;
            --bg: #0a0804;
            --bg2: #110e09;
            --bg3: #1a1510;
            --border: #2a2218;
            --scan: rgba(255,255,255,0.015);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background: var(--bg);
            color: var(--cream);
            font-family: 'JetBrains Mono', monospace;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: auto;
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(
                0deg,
                var(--scan) 0px,
                var(--scan) 1px,
                transparent 1px,
                transparent 3px
            );
            pointer-events: none;
            z-index: 100;
        }

        body::after {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.7) 100%);
            pointer-events: none;
            z-index: 99;
        }

        #header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 24px;
            border-bottom: 1px solid var(--border);
            background: var(--bg2);
            position: relative;
            flex-shrink: 0;
        }

        #header::after {
            content: '';
            position: absolute;
            bottom: -2px; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--red), transparent);
        }

        .header-left {
            display: flex;
            align-items: baseline;
            gap: 12px;
        }

        .logo {
            font-family: 'JetBrains Mono', monospace;
            font-size: 22px;
            font-weight: 500;
            letter-spacing: 8px;
            color: var(--cream);
            text-shadow: 0 0 20px rgba(192,57,43,0.4);
        }

        .version {
            font-size: 10px;
            color: var(--red);
            letter-spacing: 2px;
            border: 1px solid var(--red-dim);
            padding: 2px 6px;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--red);
            box-shadow: 0 0 8px var(--red);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            scrollbar-width: thin;
            scrollbar-color: var(--border) transparent;
        }

        #chat::-webkit-scrollbar { width: 4px; }
        #chat::-webkit-scrollbar-track { background: transparent; }
        #chat::-webkit-scrollbar-thumb { background: var(--border); }

        .msg-wrap {
            display: flex;
            flex-direction: column;
            gap: 4px;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .msg-label {
            font-size: 9px;
            letter-spacing: 3px;
            color: var(--cream-dim);
        }

        .msg-wrap.user .msg-label {
            color: var(--red);
            text-align: right;
        }

        .msg {
            max-width: 75%;
            padding: 10px 14px;
            font-size: 13px;
            line-height: 1.7;
            white-space: pre-wrap;
            word-break: break-word;
            position: relative;
        }

        .msg-wrap.user {
            align-items: flex-end;
        }

        .msg-wrap.user .msg {
            background: var(--bg3);
            border: 1px solid var(--border);
            border-right: 2px solid var(--red);
            color: var(--cream-dim);
        }

        .msg-wrap.nofae .msg {
            background: var(--bg2);
            border: 1px solid var(--border);
            border-left: 2px solid var(--red);
            color: var(--cream);
        }

        .msg::before {
            content: '';
            position: absolute;
            top: -1px; left: -1px;
            width: 6px; height: 6px;
            border-top: 1px solid var(--red);
            border-left: 1px solid var(--red);
        }

        .msg-wrap.user .msg::before {
            left: auto; right: -1px;
            border-left: none;
            border-right: 1px solid var(--red);
        }

        #typing {
            display: none;
            padding: 0 24px 8px;
            font-size: 10px;
            letter-spacing: 2px;
            color: var(--red);
            flex-shrink: 0;
        }

        .typing-dots span {
            animation: blink 1.2s infinite;
            opacity: 0;
        }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes blink {
            0%, 100% { opacity: 0; }
            50% { opacity: 1; }
        }

        #input-row {
            display: flex;
            align-items: center;
            padding: 12px 24px;
            border-top: 1px solid var(--border);
            background: var(--bg2);
            gap: 12px;
            flex-shrink: 0;
        }

        #input-row::before {
            content: '//';
            color: var(--red-dim);
            font-size: 12px;
            letter-spacing: 1px;
        }

        #input {
            flex: 1;
            background: transparent;
            border: none;
            border-bottom: 1px solid var(--border);
            color: var(--cream);
            padding: 6px 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            outline: none;
            caret-color: var(--red);
            transition: border-color 0.2s;
        }

        #input:focus {
            border-bottom-color: var(--red);
        }

        #input::placeholder {
            color: var(--border);
            letter-spacing: 1px;
        }

        #send {
            background: transparent;
            border: 1px solid var(--red-dim);
            color: var(--red);
            padding: 6px 14px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            letter-spacing: 2px;
            cursor: pointer;
            transition: all 0.2s;
        }

        #send:hover {
            background: var(--red);
            color: var(--bg);
            box-shadow: 0 0 12px rgba(192,57,43,0.4);
        }
    </style>
</head>
<body>
    <div id="header">
        <div class="header-left">
            <div class="logo">NOFAE</div>
            <div class="version">CORE-A v0.6.0</div>
        </div>
        <div class="status-dot"></div>
    </div>

    <div id="chat"></div>

    <div id="typing">
        <span class="typing-dots">PROCESSING<span>.</span><span>.</span><span>.</span></span>
        <span id="timer" style="color:#555;font-size:9px;margin-left:8px;"></span>
    </div>

    <div id="input-row">
        <input id="input" placeholder="ENTER QUERY" autofocus />
        <button id="send">SEND</button>
    </div>

    <script>
        const chat = document.getElementById("chat");
        const input = document.getElementById("input");
        const send = document.getElementById("send");
        const typing = document.getElementById("typing");

        function addMsg(text, who) {
            const wrap = document.createElement("div");
            wrap.className = "msg-wrap " + who;

            const label = document.createElement("div");
            label.className = "msg-label";
            label.textContent = who === "user" ? "YOU" : "Nofae";

            const msg = document.createElement("div");
            msg.className = "msg";
            msg.textContent = text;

            wrap.appendChild(label);
            wrap.appendChild(msg);
            chat.appendChild(wrap);
            chat.scrollTop = chat.scrollHeight;
        }

        async function sendMsg() {
            const text = input.value.trim();
            if (!text) return;
            input.value = "";
            addMsg(text, "user");

            typing.style.display = "block";
            let secs = 0;
            const timer = document.getElementById("timer");
            const timerInterval = setInterval(() => {
                secs++;
                timer.textContent = secs + "s";
            }, 1000);

            chat.scrollTop = chat.scrollHeight;

            const res = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();

            clearInterval(timerInterval);
            timer.textContent = "";
            typing.style.display = "none";
            addMsg(data.response, "nofae");
        }

        send.addEventListener("click", sendMsg);
        input.addEventListener("keydown", e => { if (e.key === "Enter") sendMsg(); });

        addMsg("SYSTEM ONLINE — INTERFACE ACTIVE. AWAITING INPUT.", "nofae");
    </script>
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user = data.get("message", "").strip()
    if not user:
        return jsonify({"response": ""})
    response = process(user)
    return jsonify({"response": response, "state": state})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
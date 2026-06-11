# Nofae (Core-A v0.6.0)

Nofae is an experimental AI agent system built in Python that combines rule-based reasoning, memory, action simulation, and LLM-based fallback generation.

It is designed as a hybrid system between:
- symbolic reasoning (rules, state, evaluation)
- simple world modeling (state + action effects)
- and large language models (Groq API integration)

## 🧠 Features

- 🧩 Rule-based response engine
- 🧠 Persistent memory system (facts + confidence)
- 🎯 Action-based decision system with scoring and simulation
- 📊 Simple world model (energy, health, knowledge, money)
- 🧮 Built-in safe math evaluator
- 💬 Smalltalk + personality layer
- 🔄 Context + pronoun resolution
- 🤖 LLM fallback using Groq (Llama 3)
- 🌐 Flask web interface + CLI version

## ⚙️ How it works

The system processes input in layers:

1. Smalltalk / identity rules
2. Memory lookup
3. Math evaluation (if detected)
4. Action extraction + simulation
5. Rule matching
6. LLM fallback

For actions, it simulates outcomes and selects the highest scoring one using a simple multi-agent evaluation system.

Requirements:
Python 3.10+
Flask
groq

This system is an experimental exploration of:
hybrid AI architecture (rules + LLM + simulation)
memory-based reasoning systems
action evaluation and scoring loops
lightweight agent design in Python







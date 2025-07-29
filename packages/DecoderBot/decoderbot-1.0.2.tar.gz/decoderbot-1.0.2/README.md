# DecoderBot 🤖

> A lightweight Python chatbot that responds to messages using exact or close matches with `difflib`.

[![PyPI version](https://badge.fury.io/py/DecoderBot.svg)](https://pypi.org/project/DecoderBot/)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Made with ❤️ by Unknown Decoder](https://img.shields.io/badge/Made%20by-Unknown%20Decoder-ff69b4)

---

## 💡 What is DecoderBot?

DecoderBot is a simple Python class that lets you build a chatbot that replies to input messages based on:
- **Exact matches** (like `"hello"`)
- **Closest matches** (like `"helo"` → `"hello"`), if `difflib` is available

No extra libraries. No nonsense. Just logic.

---

## 🚀 Features

- 🧠 Exact and fuzzy response matching
- 🛠️ Add or update responses easily
- 📦 Zero external dependencies
- 🔥 Lightweight and fast

---

## 🛠️ How to Use

### 1. Clone or download the `chatbot.py` file.

### 2. Import and use it in your project:

```python
from DecoderBot import ChatBot

bot = ChatBot("Your Bot Name")

# Add a custom response
bot.train_for("yo", "What's up?")

# Get exact match response
print(bot.get_response("yo"))  # Output: What's up?

# Get a close match response (e.g. "helo" → "hello")
try:
    print(bot.get_closest_response("helo"))
except Exception as e:
    print(e)
```
---
## OR
### You can install it using the command `pip install DecoderBot`!

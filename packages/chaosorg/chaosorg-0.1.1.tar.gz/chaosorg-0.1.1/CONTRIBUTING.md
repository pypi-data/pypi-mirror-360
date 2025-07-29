# Contributing to ChaosOrg

Thanks for your interest in improving **ChaosOrg**! 🎉

ChaosOrg is a simple but helpful Python utility for organizing your chaotic project folders. It’s designed to be minimal, readable, and extensible — and we welcome contributions of all kinds: bug reports, feature ideas, code improvements, and documentation.

---

## 🚀 Getting Started

1. **Fork this repository** and clone it locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/chaosorg.git
   ```

2. **Create a virtual environment** and install in editable mode:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. **Install development dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Try it locally** in another project folder:

   ```bash
   chaosorg organize
   chaosorg undo
   chaosorg dry-run
   ```

---

## ✅ Code Guidelines

* Follow [PEP8](https://pep8.org/) style wherever possible.
* Keep the code beginner-friendly — add comments if you think something isn’t obvious.
* Don’t be afraid to suggest new features — but aim to keep things simple and focused.

---

## 🧪 Running Tests (Coming Soon)

We plan to add unit tests soon! If you’d like to help set up a testing framework (pytest), feel free to open an issue or PR.

---

## 💡 Suggestions / Issues

Found a bug? Got an idea? Use the **Issues** tab to open a discussion.
Please include clear steps to reproduce problems if it’s a bug.

---

## 🛠️ Want to Add a New Category?

You can add a new file category in the `FOLDER_MAP` dictionary in `organizer.py` like this:

```python
"media": [".mp4", ".mp3"]
```

We’ll take care of the rest!

---

## 👨‍💻 Maintainers

* Chris Jaimy Antony

---

Thanks for helping us bring order to the chaos 🙌

---

> ChaosOrg: because your folders deserve better.

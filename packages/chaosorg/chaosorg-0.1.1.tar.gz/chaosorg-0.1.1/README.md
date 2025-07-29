# chaosorg

Organize messy project folders with one simple command.

---

## 📁 What does it do?

`chaosorg` automatically organizes files in your project directory based on file types. It sorts files into folders like:

* `scripts/`
* `notebooks/`
* `data/`
* `models/`
* `docs/`
* `outputs/`

This keeps your project tidy, easy to navigate, and collaboration-ready.

---

## 📦 Installation

```bash
pip install chaosorg
```

Or, for local development:

```bash
git clone https://github.com/YOUR_USERNAME/chaosorg.git
cd chaosorg
pip install -e .
```

---

## 🚀 Quick Start

From your terminal:

```bash
chaosorg organize
```

---

## ⚡ Features

### ✅ Organize

```bash
chaosorg organize
```

Moves your files into categorized folders.

### 🪤 Dry Run

```bash
chaosorg organize --dry-run
```

See what *would* happen, without making any changes.

### ↺ Undo

```bash
chaosorg undo
```

Restores everything back to how it was before you ran `organize`. Only the latest organization is stored.

---

## 🔍 How Files Are Sorted

| Folder       | Extensions                     |
| ------------ | ------------------------------ |
| `scripts/`   | `.py`                          |
| `notebooks/` | `.ipynb`                       |
| `data/`      | `.csv`, `.xls`, `.xlsx`        |
| `models/`    | `.pkl`, `.joblib`, `.h5`       |
| `docs/`      | `.md`, `.txt`, `.pdf`, `.docx` |
| `outputs/`   | `.png`, `.jpg`, `.jpeg`        |

You can customize these rules by editing `FOLDER_MAP` in the source code.

---

## 🙌 Contributing

We welcome contributions! If you'd like to:

* Add support for more file types
* Build a GUI
* Improve undo history
* Polish the CLI interface

Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) to get started.

---

## 👺 About

Made with love by [Chris Jaimy Antony](https://github.com/ChrisJaimyAntony) to solve the chaos of cluttered folders — especially during hackathons, ML experiments, or collaborative academic work.

---

## 🔒 License

MIT License. See `LICENSE` file for details.

---

## ✨ Links

* GitHub: [github.com/YOUR\_USERNAME/chaosorg](https://github.com/YOUR_USERNAME/chaosorg)
* PyPI: [pypi.org/project/chaosorg](https://pypi.org/project/chaosorg)

![Run PatchMind Report](https://github.com/Darkstar420/patchmind/actions/workflows/patchmind.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/patchmind.svg)](https://pypi.org/project/patchmind/)
![License](https://img.shields.io/github/license/Darkstar420/patchmind)



# 🧠 PatchMind

**PatchMind** is a modular Python-based framework that monitors a local Git repository and generates intelligent HTML reports with change summaries, tree views, file timelines, risk scoring, and more. Designed for developers who want lightweight tools to keep their codebase clean and up to date — without another bloated assistant.

---

## 🚀 Features

- 🔍 Patch-level file change detection
- 🌳 Tree-based visualization of modified files
- 📅 File history timeline with author and commit metadata
- ⚠️ Impact score and risk analysis
- 👤 Line-level blame summary
- 🧾 One-click HTML report generation via CLI

---

## 📸 Sample Output

![PatchMind HTML Report Sample](docs/patchmind_report_sample.png)

---

## ⚙️ Installation

```bash
git clone https://github.com/your-user/patchmind.git
cd patchmind
pip install -r requirements.txt
🛠️ Usage
bash
Copy
Edit
python cli/main.py --report
This command will analyze your Git repo and generate a standalone HTML report as patchmind_report.html.

🧱 Project Structure
arduino
Copy
Edit
patchmind/
├── cli/
│   └── main.py
├── core/
│   ├── engine.py
│   ├── reporter.py
│   ├── summarizer.py
│   ├── insight.py
│   └── visualizer.py
├── tests/
│   └── test_reporter.py
├── docs/
│   └── patchmind_report_sample.png
├── config.yaml
├── requirements.txt
└── README.md
🧪 Testing
bash
Copy
Edit
pytest -q
Unit tests are located in tests/test_reporter.py and validate HTML report generation using mocks.

📌 Why PatchMind?
✅ Zero-setup, fast HTML output
✅ Clear, visual insight into how your repo evolves
✅ Built by devs, for devs — no cloud syncing, no bloat

📄 License
Apache 2.0 — free to use, modify, and build on.

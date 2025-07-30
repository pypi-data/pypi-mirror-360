<p align="center">
  <img src="docs/patchmind.png" alt="PatchMind Banner" style="max-width:100%;">
</p>

# 🧠 PatchMind

[![Run PatchMind Report](https://github.com/Darkstar420/patchmind/actions/workflows/patchmind.yml/badge.svg?branch=main)](https://github.com/Darkstar420/patchmind/actions/workflows/patchmind.yml)
[![Publish to PyPI](https://github.com/Darkstar420/patchmind/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/Darkstar420/patchmind/actions/workflows/publish.yml)
[![PyPI](https://img.shields.io/pypi/v/patchmind)](https://pypi.org/project/patchmind/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub stars](https://img.shields.io/github/stars/Darkstar420/patchmind?style=social)](https://github.com/Darkstar420/patchmind/stargazers)

---

**PatchMind** is a modular Python CLI tool for Git repositories that generates smart, visual HTML reports.  
It captures **patch-level diffs**, **tree views**, **file history timelines**, **risk scoring**, and more — all locally.

No cloud. No bloat. Just clean insight.

---

## 🚀 Key Features

- 🔍 Detects file-level and line-level changes across commits
- 🌳 Tree-based visualization of modified paths
- 📅 File timeline view with authorship and metadata
- ⚠️ Risk and impact scoring per file
- 👤 Inline blame summaries
- 📄 Clean, standalone HTML output
- ⚙️ Fully CLI-driven — automate in CI/CD

---

## 📸 Sample Output

![PatchMind HTML Report Sample](docs/patchmind_report_sample.png)

---

## 📦 Installation

Install from [PyPI](https://pypi.org/project/patchmind/):

```bash
pip install patchmind
````

Or install manually:

```bash
git clone https://github.com/Darkstar420/patchmind.git
cd patchmind
pip install -r requirements.txt
```

---

## 🧪 Usage

Generate an HTML report from the root of any Git repo:

```bash
python cli/main.py --report
```

The output will be saved as `patchmind_report.html` in the project root.

---

## 📂 Project Layout

```
patchmind/
├── cli/               # CLI entrypoint
├── core/              # Core analysis engine
├── tests/             # Unit tests
├── docs/              # Sample reports and images
├── config.yaml        # Config (optional)
├── requirements.txt
└── README.md
```

---

## 🧪 Run Tests

```bash
pytest -q
```

Unit tests live in `tests/` and validate key functionality, including mock Git data and report rendering.

---

## 💡 Why Use PatchMind?

✅ No setup required – run it instantly
✅ See what's changing, where, and why
✅ Stay ahead of technical debt
✅ Built for devs who want insight — not overhead

---

## 📄 License

Licensed under the [Apache 2.0 License](https://opensource.org/licenses/Apache-2.0) — free to use, modify, and distribute.

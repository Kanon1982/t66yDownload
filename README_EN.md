# 🍃 T66y Magnet Crawler

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/)

An efficient magnet link scraper for **T66y Community (t66y.com)** built with Python 3.11+. It supports flexible filtering by **forum categories**, **minimum downloads**, **publication timeframe**, and **censored/uncensored version options** to extract and store magnet links accurately based on user requirements.

> ⚠️ **Important Notice**  
> This tool **only extracts and saves Magnet links**. It cannot directly download .torrent files due to anti-scraping mechanisms implemented on the T66y community site.

---

## ✨ Features

- **Multi-criteria Filtering**: Filter posts by forum ID, minimum download threshold, publication days, or page count.
- **Censored / Uncensored Option**: Flag-based toggle to exclude cracked or altered versions if desired.
- **Smart Incremental Cache**: Automatically tracks processed posts in `crawler_record.json` to skip duplicates on subsequent runs or after interruptions.
- **Structured File Output**: Categorized output files storing all extracted links, filtered detailed records, and pure magnet strings ready for download clients.
- **Dual Execution Modes**: Supports both beginner-friendly interactive terminal prompts and geek-friendly CLI parameters.

---

## 📋 Requirements & Installation

### 1. Python Version
Requires **Python 3.11** or higher.

### 2. Dependencies
Install required packages (`requests`, `beautifulsoup4`, and `lxml`) via pip:

```bash
pip install requests beautifulsoup4 lxml
```

---

## 🌐 Network Requirements

The target site (`t66y.com`) may be blocked or restricted in certain regions (e.g., Mainland China, Iran, North Korea, Russia). Ensure your environment or terminal has an active proxy/VPN connection to access the community during scraping.

---

## 🚀 Quick Start

Download `t66y_bt_crawler.py` to your local environment and choose one of the following execution modes:

### Mode A: Interactive Mode (Recommended for beginners)
Run the script directly and follow the interactive terminal prompts:

```bash
python t66y_bt_crawler.py
```

### Mode B: CLI Parameter Mode (For automation & scripting)
Bypass interactive prompts and specify rules directly via command-line arguments:

```bash
python t66y_bt_crawler.py --forum 2 --pages 5 --min-dl 50 --days 2 --no-crack
```

#### ⚙️ Command-Line Arguments Reference

| Argument | Description | Example | Default / Notes |
| :--- | :--- | :--- | :--- |
| `--forum` | Forum category ID (1–6), `0` for all categories | `--forum 2` | `0` |
| `--min-dl` | Minimum download threshold | `--min-dl 50` | `0` |
| `--pages` | Number of pages to crawl | `--pages 5` | Mutually exclusive with `--days` |
| `--days` | Crawl posts published within the last $N$ days | `--days 2` | Mutually exclusive with `--pages` |
| `--no-crack` | Exclude modified / cracked releases | `--no-crack` | Flag parameter |

---

## 📂 Directory Structure & Caching

Upon execution, the script creates a `magnets/` directory in the project root containing the output files:

```text
.
├── t66y_bt_crawler.py
├── crawler_record.json        # Cache tracking file
└── magnets/                   # Output folder for magnet links
    ├── *_all_magnets.txt      # All magnet links encountered during scraping
    ├── *_magnets.txt          # Filtered detailed magnet records matching user rules
    └── *_pure_magnets.txt     # Clean magnet links (ready to paste into BitComet / Aria2)
```

### 🔄 Cache Mechanism & Reset
* The generated `crawler_record.json` tracks scraped post IDs.
* **Resume Capability**: If interrupted or re-run, the crawler automatically reads this file to skip previously parsed content.
* **Reset Cache**: To perform a clean crawl from scratch, delete `crawler_record.json`.

---

## ⚖️ Disclaimer

This script is developed solely for educational and research purposes to demonstrate Python web scraping techniques. Users are strictly responsible for complying with local laws and regulations. The developer assumes no responsibility for any misuse.

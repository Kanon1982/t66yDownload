# 🍃 T66y Magnet Crawler (草榴社区磁力爬虫)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/)

基于 Python 3.11+ 开发的草榴社区（t66y.com）磁力链接高效爬取工具。支持按**版块分类**、**下载量筛选**、**发布时间过滤**以及**破解版过滤**等多种条件，精准提取并保存符合需求的磁力链接。

> ⚠️ **重要提示**  
> 本工具**仅支持提取与保存磁力链接（Magnet）**，无法直接下载 BT 种子文件（因社区站点包含反爬虫验证机制）。

---

## ✨ 功能特性

- **多维筛选**：支持按版块、最低下载量、发布天数/爬取页数灵活过滤。
- **破解版过滤**：提供开关参数，可自由选择是否排除破解版资源。
- **智能增量缓存**：自动记录已爬取内容（`crawler_record.json`），中断重新运行可自动跳过历史记录，避免重复爬取。
- **多格式输出**：分类保存全量信息、筛选后的详细信息及纯净磁力列表，方便批量导入下载工具。
- **双运行模式**：支持友好型终端交互模式与极客风格的 CLI 命令行参数模式。

---

## 📋 环境要求与依赖安装

### 1. Python 环境
本项目要求 **Python 3.11** 或更高版本。

### 2. 安装依赖库
项目依赖 `requests`、`beautifulsoup4` 和 `lxml`。可通过以下命令一键安装：

```bash
pip install requests beautifulsoup4 lxml
```

---

## 🌐 网络与环境说明

草榴社区站点在部分地区（如中国大陆、伊朗、朝鲜、俄罗斯等）需要处于**全程代理/外网环境**下才可以正常访问。在运行脚本前，请确保终端/系统已正确配置网络代理。

---

## 🚀 快速使用指南

下载脚本 `t66y_bt_crawler.py` 到本地后，可通过以下两种方式之一运行：

### 模式 A：交互式终端模式（推荐新手）
直接运行脚本，根据命令行终端的提示逐步输入筛选参数：

```bash
python t66y_bt_crawler.py
```

### 模式 B：命令行参数模式（适合自动化/一键运行）
跳过交互提示，直接通过命令行参数指定爬取规则：

```bash
python t66y_bt_crawler.py --forum 2 --pages 5 --min-dl 50 --days 2 --no-crack
```

#### ⚙️ CLI 参数说明表

| 参数 | 说明 | 示例 | 默认值 / 备注 |
| :--- | :--- | :--- | :--- |
| `--forum` | 板块编号 (1-6)，`0` 表示全部板块 | `--forum 2` | `0` |
| `--min-dl` | 最低种子下载量筛选 | `--min-dl 50` | `0` |
| `--pages` | 爬取目标页数 | `--pages 5` | 与 `--days` 二选一 |
| `--days` | 爬取最近 $N$ 天内发布的内容 | `--days 2` | 与 `--pages` 二选一 |
| `--no-crack` | 排除破解版内容（若不加此参数则默认包含） | `--no-crack` | Flag 标记 |

---

## 📂 输出文件结构与断点续爬

脚本运行后，会在项目根目录下自动创建 `magnets/` 文件夹，并生成以下三个目标文件：

```text
.
├── t66y_bt_crawler.py
├── crawler_record.json        # 爬取缓存记录文件
└── magnets/                   # 磁力链接输出目录
    ├── *_all_magnets.txt      # 本次爬取到的所有磁力信息汇总
    ├── *_magnets.txt          # 匹配用户筛选条件的详细磁力信息
    └── *_pure_magnets.txt     # 仅包含纯磁力链接（用于直接粘贴至 BitComet / Aria2 等下载器）
```

### 🔄 缓存机制与重置
* 运行结束后生成的 `crawler_record.json` 用于记录已爬取过的帖子 ID。
* **中断续传**：若运行中途中断或再次运行，脚本会自动读取该文件并跳过重复内容。
* **彻底重置**：如果希望清除历史缓存、重新从零开始爬取，直接删除 `crawler_record.json` 即可。

---

## ⚖️ 免责声明 (Disclaimer)

本脚本仅供 Python 网络爬虫技术学习与交流使用。请勿将本项目用于任何违反当地法律法规的用途。开发者不对使用者因违规行为导致的任何后果承担责任。

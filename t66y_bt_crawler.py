#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛 BT 磁力链接爬虫脚本

功能：
  1. 交互式选择板块（亞洲無碼/有碼、歐美、動漫、國產、中字）
  2. 按下载量过滤（仅爬取下载量超过阈值的帖子）
  3. 按日期过滤（只爬取最近 N 天的帖子）
  4. 仅提取并保存磁力链接，不下载种子文件

使用前: pip install requests beautifulsoup4 lxml
"""

import os
import re
import time
import json
import html
import random
import logging
import argparse
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

# ============================================================
# 板块定义
# ============================================================

FORUM_SECTIONS = {
    "1": {"name": "亞洲無碼原創區", "fid": 2},
    "2": {"name": "亞洲有碼原創區", "fid": 15},
    "3": {"name": "歐美原創區",     "fid": 4},
    "4": {"name": "動漫原創區",     "fid": 5},
    "5": {"name": "國產原創區",     "fid": 25},
    "6": {"name": "中字原創區",     "fid": 26},
}

# ============================================================
# 配置
# ============================================================

class Config:
    BASE_URL = "https://t66y.com"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    COOKIE = ""
    PROXY = None
    MAGNET_DIR = "./magnets"
    RECORD_FILE = "./crawler_record.json"
    REQUEST_INTERVAL = (2, 5)
    MAX_RETRIES = 3
    TIMEOUT = 30
    ENCODING = "utf-8"

# ============================================================
# 日志
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("MagnetCrawler")

# ============================================================
# 爬虫核心
# ============================================================

class MagnetCrawler:

    MAGNET_PATTERN = re.compile(
        r'magnet:\?xt=urn:btih:[a-zA-Z0-9]{32,40}[^"\'<\s]*'
    )

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        if config.COOKIE:
            self.session.headers["Cookie"] = config.COOKIE
        if config.PROXY:
            self.session.proxies.update({
                "http": config.PROXY, "https": config.PROXY
            })
        os.makedirs(config.MAGNET_DIR, exist_ok=True)
        self.record = self._load_record()

    # -------- 记录管理 --------

    def _load_record(self):
        if os.path.exists(self.config.RECORD_FILE):
            try:
                with open(self.config.RECORD_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"crawled_threads": [], "magnet_links": []}

    def _save_record(self):
        with open(self.config.RECORD_FILE, "w", encoding="utf-8") as f:
            json.dump(self.record, f, ensure_ascii=False, indent=2)

    # -------- 请求 --------

    def _sleep(self):
        low, high = self.config.REQUEST_INTERVAL
        time.sleep(random.uniform(low, high))

    def _request(self, url):
        for attempt in range(1, self.config.MAX_RETRIES + 1):
            try:
                resp = self.session.get(url, timeout=self.config.TIMEOUT)
                if self.config.ENCODING:
                    resp.encoding = self.config.ENCODING
                if resp.status_code == 200:
                    return resp
                logger.warning(f"HTTP {resp.status_code} on {url} (attempt {attempt})")
                if resp.status_code in (403, 404, 410):
                    break
            except requests.RequestException as e:
                logger.warning(f"请求异常 {url}: {e} (attempt {attempt})")
            if attempt < self.config.MAX_RETRIES:
                time.sleep(2 * attempt)
        return None

    # -------- 帖子列表解析 --------

    def _parse_thread_list(self, html_text, min_downloads, days_back, include_cracked):
        """解析板块页，返回符合条件的帖子列表

        include_cracked: True=包含破解版, False=排除破解版
        """
        soup = BeautifulSoup(html_text, "lxml")
        today = datetime.now()
        cutoff_date = today - timedelta(days=days_back - 1)
        cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)

        threads = []
        all_tds = soup.find_all("td")
        tal_indices = []

        for i, td in enumerate(all_tds):
            if "tal" in (td.get("class") or []):
                tal_indices.append(i)

        for idx in tal_indices:
            td_title = all_tds[idx]
            a = td_title.find("a", href=True)
            if not a:
                continue
            href = a["href"]
            title = a.get_text(strip=True)
            thread_url = urljoin(self.config.BASE_URL, href)

            if not self._is_thread_url(thread_url):
                continue

            # 发帖时间: td.tal 后第 1 个 TD (作者+时间)
            # HTML结构: <td><a>用户名</a><div class="f12"><span class="s3">19 小時</span></div></td>
            # 只取 span 中的时间文本，忽略用户名
            time_idx = idx + 1
            post_time_str = ""
            if time_idx < len(all_tds):
                time_td = all_tds[time_idx]
                span = time_td.find("span", class_="s3")
                if span:
                    post_time_str = span.get_text(strip=True)
                else:
                    post_time_str = time_td.get_text(strip=True)

            # 下载量: td.tal 后第 3 个 TD
            dl_idx = idx + 3
            download_count = 0
            if dl_idx < len(all_tds):
                dl_text = all_tds[dl_idx].get_text(strip=True)
                if dl_text and dl_text != "--":
                    try:
                        download_count = int(dl_text)
                    except ValueError:
                        download_count = 0

            post_date = self._parse_post_date(post_time_str, today)

            # 日期过滤
            if post_date and post_date < cutoff_date:
                continue

            # 下载量过滤（"--"视为0，不达标不下载）
            if download_count < min_downloads:
                continue

            # 破解版过滤（简繁体"破解"和"破坏"字形相同）
            if not include_cracked and ("破解" in title or "破坏" in title):
                continue

            threads.append({
                "url": thread_url,
                "title": title,
                "downloads": download_count,
                "date": post_date.strftime("%Y-%m-%d") if post_date else "unknown",
            })

        return threads

    def _is_thread_url(self, url):
        """判断是否为帖子 URL"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        query = parse_qs(parsed.query)
        if re.match(r'.*/(?:thread\d+|post|forum)\.php$', path):
            return False
        if path.endswith(('/login.php', '/register.php', '/search.php',
                          '/hack.php', '/faq.php', '/profile.php',
                          '/notice.php', '/index.php')):
            return False
        if "htm_data" in path and path.endswith(('.html', '.htm')):
            return True
        if path.endswith('/read.php') and 'tid' in query:
            return True
        if re.search(r'/thread-\d+-\d+-\d+\.html?$', path):
            return True
        return False

    def _parse_post_date(self, time_str, today):
        """从帖子列表的时间文本解析发帖日期

        时间文本来自 <span class="s3"> 标签，格式包括：
        "19  小時" / "5  分鐘" / "昨天" / "前天" / "3  天前"
        "2  月前" / "1  年前" / "08-15" / "2026-08-15"
        """
        if not time_str:
            return None

        time_str = time_str.strip()

        # "X 分鐘" / "X 小時" → 今天
        if "分鐘" in time_str or "分钟" in time_str or "小時" in time_str or "小时" in time_str:
            return today

        # "昨天" → 昨天
        if "昨天" in time_str:
            return today - timedelta(days=1)

        # "前天" → 前天
        if "前天" in time_str:
            return today - timedelta(days=2)

        # "X 天前" / "X天前"
        m = re.search(r'(\d+)\s*天前', time_str)
        if m:
            return today - timedelta(days=int(m.group(1)))

        # "X 月前" / "X月前"
        m = re.search(r'(\d+)\s*月前', time_str)
        if m:
            return today - timedelta(days=int(m.group(1)) * 30)

        # "X 年前" / "X年前"
        m = re.search(r'(\d+)\s*年前', time_str)
        if m:
            return today - timedelta(days=int(m.group(1)) * 365)

        # "3  天" (省略"前"字的天数格式)
        m = re.search(r'(\d+)\s*天$', time_str)
        if m:
            return today - timedelta(days=int(m.group(1)))

        # "MM-DD" 或 "MM-DD HH:MM"
        m = re.search(r'(\d{1,2})-(\d{1,2})', time_str)
        if m:
            month, day = int(m.group(1)), int(m.group(2))
            year = today.year
            try:
                date = datetime(year, month, day)
                if date > today + timedelta(days=1):
                    date = date.replace(year=year - 1)
                return date
            except ValueError:
                pass

        # "YYYY-MM-DD"
        m = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', time_str)
        if m:
            try:
                return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                pass

        return None

    # -------- 帖子内容解析 --------

    # 40位 hex hash（BT info_hash），用于构造磁力链接
    HASH_PATTERN = re.compile(r'(?<![a-fA-F0-9])([a-fA-F0-9]{40})(?![a-fA-F0-9])')
    # rmdown 下载链接
    RMDOWN_PATTERN = re.compile(
        r'https?://(?:www\.)?rmdown\.com/link\.php\?hash=\w+'
    )

    def _parse_thread_content(self, html_text, thread_url):
        """提取帖子中的磁力链接

        提取策略（按优先级，只取第一个找到的）：
        1. 直接搜索 magnet:?xt=urn:btih: 完整磁力链接
        2. 从帖子正文提取 40 位 info_hash 构造磁力链接
        3. 从 rmdown 链接中提取 hash 构造磁力链接
        只保存第一个找到的磁力，避免低画质版本的磁力
        """
        soup = BeautifulSoup(html_text, "lxml")

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "unknown"

        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        text = str(soup)
        magnets = []

        # 策略1: 直接搜索完整 magnet 链接（按出现顺序）
        for m in self.MAGNET_PATTERN.findall(text):
            magnet = html.unescape(m)
            if magnet not in magnets:
                magnets.append(magnet)

        # 策略2: 从 tpc_content 中提取 info_hash 构造磁力链接
        if not magnets:
            tpc = soup.find("div", class_="tpc_content")
            tpc_text = tpc.get_text(separator=" ", strip=True) if tpc else text

            # 先移除 rmdown 链接（其 URL 中的 hash= 参数会干扰提取）
            tpc_clean = re.sub(r'https?://(?:www\.)?rmdown\.com/link\.php\?hash=\w+', '', tpc_text)

            # 提取驗證編號 / 特征全码 后的 40 位 hash
            hash_label = re.findall(
                r'(?:驗證編號|特征全码|特徵全碼|哈希值)[^a-fA-F0-9]*([a-fA-F0-9]{40})',
                tpc_clean, re.IGNORECASE
            )
            for h in hash_label:
                magnet = f"magnet:?xt=urn:btih:{h.upper()}"
                if magnet not in magnets:
                    magnets.append(magnet)

            # 如果标签没匹配到，从 rmdown 链接中提取 hash
            if not magnets:
                rmdown_hashes = re.findall(
                    r'rmdown\.com/link\.php\?hash=(\w+)', text
                )
                for rh in rmdown_hashes:
                    if len(rh) >= 43 and rh.startswith('262'):
                        real_hash = rh[3:43]
                        if re.match(r'^[a-fA-F0-9]{40}$', real_hash):
                            magnet = f"magnet:?xt=urn:btih:{real_hash.upper()}"
                            if magnet not in magnets:
                                magnets.append(magnet)
                    elif re.match(r'^[a-fA-F0-9]{40}$', rh):
                        magnet = f"magnet:?xt=urn:btih:{rh.upper()}"
                        if magnet not in magnets:
                            magnets.append(magnet)

            # 如果仍然没匹配到，回退：在清理后的文本中找所有 40 位 hex
            if not magnets:
                all_hashes = self.HASH_PATTERN.findall(tpc_clean)
                for h in all_hashes:
                    magnet = f"magnet:?xt=urn:btih:{h.upper()}"
                    if magnet not in magnets:
                        magnets.append(magnet)

        # 只保留第一个磁力链接（避免低画质版本的磁力）
        magnets = magnets[:1]

        # 记录 rmdown 下载链接（备用）
        rmdown_links = list(set(self.RMDOWN_PATTERN.findall(text)))

        return {
            "url": thread_url,
            "title": title,
            "magnets": magnets,
            "rmdown_links": rmdown_links,
        }

    # -------- 主流程 --------

    def crawl_forum(self, fid, section_name, max_pages, min_downloads, days_back, include_cracked=True):
        """爬取指定板块"""
        forum_url = f"{self.config.BASE_URL}/thread0806.php?fid={fid}"
        logger.info(f"开始爬取板块: {section_name} (fid={fid})")
        logger.info(f"过滤条件: 下载量>={min_downloads}, 最近{days_back}天, 最多{max_pages}页, 包含破解版={include_cracked}")

        total_magnets = 0
        total_threads = 0

        for page in range(1, max_pages + 1):
            page_url = self._build_page_url(forum_url, page)
            logger.info(f"正在爬取第 {page}/{max_pages} 页")

            resp = self._request(page_url)
            if not resp:
                logger.warning(f"第 {page} 页获取失败")
                continue

            threads = self._parse_thread_list(
                resp.text, min_downloads, days_back, include_cracked
            )
            logger.info(f"第 {page} 页符合条件: {len(threads)} 个帖子")

            if not threads:
                logger.info(f"第 {page} 页无符合条件的帖子，停止爬取")
                break

            for thread in threads:
                if thread["url"] in self.record["crawled_threads"]:
                    continue

                count = self._crawl_thread(thread, section_name)
                total_magnets += count
                total_threads += 1
                self._sleep()

            self._save_record()

        logger.info(
            f"板块 {section_name} 完成: "
            f"爬取 {total_threads} 个帖子, "
            f"共 {total_magnets} 条磁力链接"
        )
        return total_magnets

    def _crawl_thread(self, thread_info, section_name):
        """爬取单个帖子，提取磁力链接"""
        resp = self._request(thread_info["url"])
        if not resp:
            logger.warning(f"跳过（请求失败）: {thread_info['title'][:40]}")
            return 0

        data = self._parse_thread_content(resp.text, thread_info["url"])
        magnets = data["magnets"]
        rmdown_links = data.get("rmdown_links", [])

        logger.info(
            f"[{section_name}] {thread_info['title'][:45]} | "
            f"下载:{thread_info['downloads']} | "
            f"日期:{thread_info['date']} | "
            f"磁力:{len(magnets)}"
        )

        if magnets:
            self._save_magnets(magnets, thread_info, section_name, rmdown_links)
            self.record["magnet_links"].extend(magnets)
            self.record["crawled_threads"].append(thread_info["url"])
            self._save_record()
        else:
            logger.warning(f"未提取到磁力，下次会重试: {thread_info['title'][:40]}")

        return len(magnets)

    def _save_magnets(self, magnets, thread_info, section_name, rmdown_links=None):
        """保存磁力链接到文件"""
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', section_name)
        magnet_file = os.path.join(
            self.config.MAGNET_DIR, f"{safe_name}_magnets.txt"
        )
        # 详细版：带标题、下载量、日期等信息
        with open(magnet_file, "a", encoding="utf-8") as f:
            f.write(f"# {thread_info['title']}\n")
            f.write(f"# 下载量: {thread_info['downloads']} | 日期: {thread_info['date']}\n")
            f.write(f"# URL: {thread_info['url']}\n")
            if rmdown_links:
                f.write(f"# rmdown下载链接: {', '.join(rmdown_links)}\n")
            for m in magnets:
                f.write(m + "\n")
            f.write("\n")

        # 纯净版：只有磁力链接，每行一个
        pure_file = os.path.join(
            self.config.MAGNET_DIR, f"{safe_name}_pure_magnets.txt"
        )
        with open(pure_file, "a", encoding="utf-8") as f:
            for m in magnets:
                f.write(m + "\n")

    def _build_page_url(self, forum_url, page):
        if "?" in forum_url:
            if "page=" in forum_url:
                return re.sub(r'page=\d+', f'page={page}', forum_url)
            return f"{forum_url}&search=&page={page}"
        return f"{forum_url}?page={page}" if page > 1 else forum_url

    def export_magnets(self, section_name=None):
        """导出所有磁力链接"""
        magnets = sorted(set(self.record["magnet_links"]))
        if not magnets:
            logger.info("没有磁力链接可导出")
            return
        filename = "all_magnets.txt"
        if section_name:
            safe = re.sub(r'[\\/:*?"<>|]', '_', section_name)
            filename = f"{safe}_all_magnets.txt"
        output = os.path.join(self.config.MAGNET_DIR, filename)
        with open(output, "w", encoding="utf-8") as f:
            for m in magnets:
                f.write(m + "\n")
        logger.info(f"已导出 {len(magnets)} 条磁力链接到 {output}")


# ============================================================
# 交互式菜单
# ============================================================

def interactive_menu():
    """交互式选择爬取参数"""

    print("=" * 50)
    print("  论坛磁力链接爬虫")
    print("=" * 50)

    # 1. 选择板块
    print("\n请选择板块:")
    for key, info in FORUM_SECTIONS.items():
        print(f"  {key}. {info['name']}")
    print(f"  0. 全部板块")

    while True:
        choice = input("\n请输入选项 (0-6): ").strip()
        if choice in FORUM_SECTIONS or choice == "0":
            break
        print("输入无效，请重新输入")

    # 2. 下载量阈值
    while True:
        dl_input = input("\n请输入最低下载量阈值 (0=不限, 直接回车=0): ").strip()
        if not dl_input:
            min_downloads = 0
            break
        try:
            min_downloads = int(dl_input)
            if min_downloads < 0:
                print("不能为负数")
                continue
            break
        except ValueError:
            print("请输入数字")

    # 3. 选择爬取方式：按页数 或 按天数
    print("\n请选择爬取方式:")
    print("  1. 按页数爬取（爬取前 N 页的帖子）")
    print("  2. 按天数爬取（爬取最近 N 天的帖子）")

    while True:
        mode_choice = input("\n请输入选项 (1 或 2): ").strip()
        if mode_choice in ("1", "2"):
            break
        print("输入无效，请输入 1 或 2")

    days_back = None
    max_pages = None

    if mode_choice == "1":
        # 按页数爬取
        while True:
            pages_input = input("\n请输入爬取页数 (每页约30帖, 默认5): ").strip()
            if not pages_input:
                max_pages = 5
                break
            try:
                max_pages = int(pages_input)
                if max_pages < 1:
                    print("至少为 1")
                    continue
                break
            except ValueError:
                print("请输入数字")
        # 按页数时天数设为很大的值，不做日期过滤
        days_back = 9999
    else:
        # 按天数爬取
        while True:
            days_input = input("\n请输入要爬取的天数 (1=今天, 2=今天和昨天, 3=最近3天...): ").strip()
            try:
                days_back = int(days_input)
                if days_back < 1:
                    print("至少为 1")
                    continue
                break
            except ValueError:
                print("请输入数字")
        # 按天数时页数设为很大的值，不做页数限制
        max_pages = 9999

    # 4. 是否包含破解版
    print("\n是否下载破解版视频?")
    print("  1. 包含破解版")
    print("  2. 排除破解版（只下载正常版）")
    while True:
        crack_choice = input("\n请输入选项 (1 或 2): ").strip()
        if crack_choice in ("1", "2"):
            break
        print("输入无效，请输入 1 或 2")
    include_cracked = (crack_choice == "1")

    # 汇总确认
    print("\n" + "=" * 50)
    print("爬取参数确认:")
    if choice == "0":
        print(f"  板块: 全部板块")
    else:
        print(f"  板块: {FORUM_SECTIONS[choice]['name']}")
    print(f"  最低下载量: {min_downloads}")
    if mode_choice == "1":
        print(f"  爬取方式: 按页数 (共 {max_pages} 页)")
    else:
        print(f"  爬取方式: 按天数 (最近 {days_back} 天)")
    print(f"  破解版: {'包含' if include_cracked else '排除'}")
    print("=" * 50)

    confirm = input("\n确认开始爬取? (y/n): ").strip().lower()
    if confirm != "y":
        print("已取消")
        return None

    return choice, min_downloads, days_back, max_pages, include_cracked


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="论坛磁力链接爬虫")
    parser.add_argument("--forum", type=str, default=None, help="板块 fid")
    parser.add_argument("--pages", type=int, default=5, help="爬取页数")
    parser.add_argument("--min-dl", type=int, default=0, help="最低下载量阈值")
    parser.add_argument("--days", type=int, default=1, help="爬取天数")
    parser.add_argument("--proxy", type=str, default=None, help="代理地址")
    parser.add_argument("--cookie", type=str, default=None, help="Cookie")
    args = parser.parse_args()

    config = Config()
    if args.proxy:
        config.PROXY = args.proxy
    if args.cookie:
        config.COOKIE = args.cookie

    crawler = MagnetCrawler(config)

    # 命令行模式
    if args.forum:
        fid = int(args.forum)
        section_name = "自定义板块"
        for info in FORUM_SECTIONS.values():
            if info["fid"] == fid:
                section_name = info["name"]
                break
        crawler.crawl_forum(
            fid, section_name, args.pages, args.min_dl, args.days
        )
        crawler.export_magnets(section_name)
        logger.info("全部完成")
        return

    # 交互式模式
    result = interactive_menu()
    if not result:
        return

    choice, min_downloads, days_back, max_pages, include_cracked = result

    if choice == "0":
        for info in FORUM_SECTIONS.values():
            crawler.crawl_forum(
                info["fid"], info["name"],
                max_pages, min_downloads, days_back, include_cracked
            )
            crawler.export_magnets(info["name"])
    else:
        info = FORUM_SECTIONS[choice]
        crawler.crawl_forum(
            info["fid"], info["name"],
            max_pages, min_downloads, days_back, include_cracked
        )
        crawler.export_magnets(info["name"])

    logger.info("全部完成")


if __name__ == "__main__":
    main()

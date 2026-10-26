# -*- coding: utf-8 -*-
"""
QQ 频道 Web SSR 核心解析器
通过公开 Web 端的 schema.org 结构化元数据提取频道新帖。
支持“主页轻量索引”与“未读新帖正文懒加载”，大幅降低无意义 HTTP 请求。
"""

import urllib.request
import re
import json
import datetime
from typing import List, Dict, Optional, Tuple

class QQGuildFetcher:
    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache'
        }

    def fetch_channel_overview(self, guild_url: str) -> List[Dict]:
        """
        仅抓取频道主页元数据，提取最新帖子列表概览（单次网络请求）
        """
        req = urllib.request.Request(guild_url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        posts = []

        for s in scripts:
            if 'schema.org' in s and '@graph' in s:
                try:
                    data = json.loads(s)
                    for graph in data.get('@graph', []):
                        channel_name = graph.get('name', '默认板块')
                        for elem in graph.get('itemListElement', []):
                            item = elem.get('item', {})
                            p_url = item.get('url', '')
                            post_id = p_url.split('/')[-1] if p_url else item.get('headline', '')
                            if not post_id:
                                continue

                            posts.append({
                                'id': post_id,
                                'sub_channel': channel_name,
                                'url': p_url,
                                'headline': (item.get('headline') or '').strip(),
                                'datePublished': item.get('datePublished', ''),
                                'author': item.get('author', {}).get('name', '匿名用户'),
                                'likes': item.get('interactionStatistic', {}).get('userInteractionCount', 0),
                                'full_text': ''
                            })
                except Exception:
                    pass

        # 按发帖时间倒序排序
        def parse_time(p):
            t_str = p.get('datePublished', '')
            if t_str:
                try:
                    return datetime.datetime.fromisoformat(t_str)
                except Exception:
                    pass
            return datetime.datetime.min

        posts.sort(key=parse_time, reverse=True)
        return posts

    def fetch_post_detail(self, post_url: str) -> str:
        """
        抓取具体帖子页面，提取完整正文内容
        """
        if not post_url:
            return ""

        try:
            req = urllib.request.Request(post_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                html = resp.read().decode('utf-8', errors='ignore')

            scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
            for ps in scripts:
                if 'DiscussionForumPosting' in ps:
                    data = json.loads(ps)
                    full_text = data.get('text', '')
                    if full_text:
                        return full_text.strip()
        except Exception:
            pass

        return ""

    def sync_channel(self, channel_config: Dict, storage, skip_details: bool = False) -> Tuple[List[Dict], List[Dict]]:
        """
        对单个频道执行增量同步：
        1. 抓取主页获取全部最新条目（1次请求）；
        2. 比对 storage 缓存，找出全新帖子；
        3. 仅对未读新帖发起详情请求拉取全文（懒加载）；若 skip_details=True 则跳过正文拉取（用于建基线）；
        返回: (全部概览帖子, 经过懒加载补充全文的新帖子列表)
        """
        url = channel_config.get('url')
        channel_name = channel_config.get('name', '未命名频道')
        all_posts = self.fetch_channel_overview(url)

        new_posts = []
        for p in all_posts:
            p['channel_name'] = channel_name
            post_id = p.get('id')
            if not post_id or storage.is_seen(post_id):
                continue
            new_posts.append(p)

        # 仅针对全新未读帖子发起网络请求补全正文（建立基线时跳过）
        if not skip_details:
            for p in new_posts:
                if p.get('url'):
                    full_text = self.fetch_post_detail(p['url'])
                    p['full_text'] = full_text if full_text else p.get('headline', '')
                else:
                    p['full_text'] = p.get('headline', '')
        else:
            for p in new_posts:
                p['full_text'] = p.get('headline', '')

        return all_posts, new_posts

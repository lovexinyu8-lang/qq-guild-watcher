# -*- coding: utf-8 -*-
"""
关键词匹配引擎
支持多频道专属词、全局共享词、大小写不敏感匹配以及英文短词边界防误报。
"""

import re
from typing import List, Dict, Tuple

class KeywordMatcher:
    def __init__(self, global_keywords: List[str] = None):
        self.global_keywords = global_keywords or []

    def match(self, post: Dict, channel_config: Dict) -> List[str]:
        """
        判断帖子是否命中设定的关键词
        匹配范围：标题 (headline) + 正文 (full_text)
        """
        channel_keywords = channel_config.get('custom_keywords', [])
        all_keywords = list(dict.fromkeys(self.global_keywords + channel_keywords))

        title = post.get('headline', '') or ''
        body = post.get('full_text', '') or ''
        content = f"{title} {body}"

        matched = []
        for kw in all_keywords:
            kw = kw.strip()
            if not kw:
                continue

            # 针对长度较短的英文字符串（如 AI、GPT、R、UI），使用正则单词边界匹配避免误伤
            if len(kw) <= 3 and kw.isalpha():
                pattern = re.compile(rf"(?<![a-zA-Z0-9]){re.escape(kw)}(?![a-zA-Z0-9])", re.IGNORECASE)
                if pattern.search(content):
                    matched.append(kw)
            else:
                if kw.lower() in content.lower():
                    matched.append(kw)

        return matched

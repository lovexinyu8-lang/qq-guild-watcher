# -*- coding: utf-8 -*-
"""
通知器基础接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict

class BaseNotifier(ABC):
    @abstractmethod
    def send(self, matched_keywords: List[str], post: Dict):
        """
        触发通知
        :param matched_keywords: 命中的关键词列表
        :param post: 帖子详细字典数据
        """
        pass

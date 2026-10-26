# -*- coding: utf-8 -*-
"""
数据持久化与去重缓存存储层
负责维护已判定/已通知帖子 ID，避免重复报警与冗余网络请求。
"""

import os
import json
import threading

class SeenPostsStorage:
    def __init__(self, file_path: str, max_size: int = 3000):
        self.file_path = file_path
        self.max_size = max_size
        self._lock = threading.Lock()
        self._seen_ids = set()
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._seen_ids = set(data)
            except Exception as e:
                print(f"[Storage] 读取已读历史失败，将初始化为空缓存: {e}")
                self._seen_ids = set()
        else:
            self._seen_ids = set()

    def is_seen(self, post_id: str) -> bool:
        with self._lock:
            return post_id in self._seen_ids

    def add(self, post_id: str):
        with self._lock:
            self._seen_ids.add(post_id)

    def add_batch(self, post_ids):
        with self._lock:
            self._seen_ids.update(post_ids)

    def save(self):
        with self._lock:
            try:
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                items = list(self._seen_ids)[-self.max_size:]
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(items, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[Storage] 保存已读历史到本地失败: {e}")

    def __len__(self):
        with self._lock:
            return len(self._seen_ids)

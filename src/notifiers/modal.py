# -*- coding: utf-8 -*-
"""
Windows 原生居中强提醒模态确认框 (Modal Dialog Notifier)
特点：
1. 屏幕正中央弹出，带有系统信息图标与提示音；
2. 强制置顶（SYSTEMMODAL / TOPMOST / SETFOREGROUND），绝不漏看；
3. 点击“是(Y)”自动调用系统默认浏览器打开原帖，“否(N)”忽略；
4. 纯标准库 ctypes 实现，零外部依赖，极速稳定。
"""

import sys
import threading
import webbrowser
from typing import List, Dict
from src.notifiers.base import BaseNotifier

class ModalDialogNotifier(BaseNotifier):
    def __init__(self, enable_sound: bool = True):
        self.enable_sound = enable_sound
        self._lock = threading.Lock()

    def _show_dialog(self, matched_keywords: List[str], post: Dict):
        if not self._lock.acquire(blocking=False):
            return

        try:
            kw_str = "、".join(matched_keywords)
            title = f"🔔 QQ频道监控命中: {kw_str}"

            channel_info = f"[{post.get('channel_name', '频道')}] {post.get('sub_channel', '')}"
            author = post.get('author', '匿名')
            date_pub = post.get('datePublished', '').replace('T', ' ')[:19]
            headline = post.get('headline', '')
            full_text = post.get('full_text', '')
            url = post.get('url', '')

            # 组装文本内容（过长文本截断至 250 字保持美观）
            display_text = full_text[:250] + ("..." if len(full_text) > 250 else "")

            message = (
                f"【命中关键词】{kw_str}\n"
                f"【来源板块】{channel_info}\n"
                f"【发帖作者】{author} ({date_pub})\n"
                f"----------------------------------------\n"
                f"【标题】{headline}\n\n"
                f"【正文预览】\n{display_text}\n"
                f"----------------------------------------\n"
                f"👉 是否立即在默认浏览器中打开原帖？"
            )

            if sys.platform == 'win32':
                import ctypes
                # MB_YESNO = 0x00000004
                # MB_ICONINFORMATION = 0x00000040
                # MB_SYSTEMMODAL = 0x00001000
                # MB_SETFOREGROUND = 0x00010000
                # MB_TOPMOST = 0x00040000
                flags = 0x00000004 | 0x00000040 | 0x00010000 | 0x00040000
                res = ctypes.windll.user32.MessageBoxW(0, message, title, flags)
                # IDYES = 6
                if res == 6 and url:
                    webbrowser.open(url)
            else:
                try:
                    import tkinter as tk
                    from tkinter import messagebox
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    if messagebox.askyesno(title, message):
                        if url:
                            webbrowser.open(url)
                    root.destroy()
                except Exception:
                    pass
        except Exception as e:
            print(f"[ModalDialog] 弹窗错误: {e}")
        finally:
            self._lock.release()

    def send(self, matched_keywords: List[str], post: Dict, block: bool = False):
        if block:
            self._show_dialog(matched_keywords, post)
        else:
            t = threading.Thread(target=self._show_dialog, args=(matched_keywords, post), daemon=True)
            t.start()

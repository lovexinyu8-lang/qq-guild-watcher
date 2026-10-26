# -*- coding: utf-8 -*-
"""
桌面置顶轻量悬浮卡片通知器
针对 Windows 平台优化：
1. 右下角平铺展示，不夺取全局输入焦点；
2. 倒计时自动销毁，防止弹窗堆积；
3. 一键在默认浏览器打开原帖；
4. 包含系统提示音（带跨平台保护）。
"""

import sys
import threading
import webbrowser
from typing import List, Dict
from src.notifiers.base import BaseNotifier

popup_lock = threading.Lock()

class DesktopNotifier(BaseNotifier):
    def __init__(self, auto_close_seconds: int = 15, enable_sound: bool = True):
        self.auto_close_seconds = auto_close_seconds
        self.enable_sound = enable_sound

    def _play_sound(self):
        if self.enable_sound and sys.platform == 'win32':
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass

    def _show_popup_window(self, matched_keywords: List[str], post: Dict):
        # 保证屏幕同一时刻只显示一个卡片，避免窗口抢占或卡死
        if not popup_lock.acquire(blocking=False):
            return

        try:
            import tkinter as tk

            root = tk.Tk()
            root.title("QQ频道新帖提醒")
            root.resizable(False, False)

            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            card_w = 450
            card_h = 260
            x = max(10, screen_w - card_w - 30)
            y = max(10, screen_h - card_h - 60)
            root.geometry(f"{card_w}x{card_h}+{x}+{y}")
            root.configure(bg="#f4f5f7")

            # 强制提升至屏幕最顶层
            root.attributes("-topmost", True)
            root.deiconify()
            root.lift()

            def safe_close():
                try:
                    root.destroy()
                except Exception:
                    pass

            root.protocol("WM_DELETE_WINDOW", safe_close)
            if self.auto_close_seconds > 0:
                root.after(self.auto_close_seconds * 1000, safe_close)

            # 顶部高亮条
            header_frame = tk.Frame(root, bg="#0066cc", padx=12, pady=8)
            header_frame.pack(fill="x")

            kw_str = "、".join(matched_keywords)
            lbl_title = tk.Label(
                header_frame,
                text=f"🔔 命中关键词: {kw_str}",
                font=("Microsoft YaHei", 10, "bold"),
                fg="#ffffff",
                bg="#0066cc"
            )
            lbl_title.pack(side="left")

            # 元信息条
            meta_frame = tk.Frame(root, bg="#f4f5f7", padx=12, pady=6)
            meta_frame.pack(fill="x")

            time_str = post.get('datePublished', '').replace('T', ' ')[:19]
            channel_tag = f"[{post.get('channel_name', '频道')}] {post.get('sub_channel', '')}"
            meta_text = f"来源: {channel_tag}   作者: {post.get('author', '匿名')}   时间: {time_str}"
            lbl_meta = tk.Label(meta_frame, text=meta_text, font=("Microsoft YaHei", 8), fg="#666666", bg="#f4f5f7")
            lbl_meta.pack(anchor="w")

            # 内容预览区
            content_frame = tk.Frame(root, bg="#ffffff", padx=8, pady=6, relief="solid", bd=1)
            content_frame.pack(fill="both", expand=True, padx=12, pady=4)

            txt_content = tk.Text(
                content_frame,
                wrap="char",
                font=("Microsoft YaHei", 9),
                bg="#ffffff",
                fg="#222222",
                bd=0,
                padx=4,
                pady=4
            )
            headline = post.get('headline', '')
            full_text = post.get('full_text', '')
            full_display = f"【标题】{headline}\n\n【正文】{full_text}"
            txt_content.insert("1.0", full_display)
            txt_content.config(state="disabled")
            txt_content.pack(fill="both", expand=True)

            # 底部按钮区
            btn_frame = tk.Frame(root, bg="#f4f5f7", padx=12, pady=8)
            btn_frame.pack(fill="x")

            def open_url():
                url = post.get('url')
                safe_close()
                if url:
                    webbrowser.open(url)

            btn_open = tk.Button(
                btn_frame,
                text="🔗 查看原帖",
                font=("Microsoft YaHei", 9, "bold"),
                bg="#0066cc",
                fg="#ffffff",
                padx=12,
                pady=3,
                bd=0,
                cursor="hand2",
                command=open_url
            )
            btn_open.pack(side="right", padx=6)

            btn_close = tk.Button(
                btn_frame,
                text=f"忽略 ({self.auto_close_seconds}s)",
                font=("Microsoft YaHei", 9),
                bg="#e0e0e0",
                fg="#333333",
                padx=10,
                pady=3,
                bd=0,
                cursor="hand2",
                command=safe_close
            )
            btn_close.pack(side="right", padx=4)

            root.lift()
            root.update()
            root.mainloop()
        except Exception as e:
            print(f"[DesktopNotifier] 弹窗展示异常: {e}")
        finally:
            popup_lock.release()

    def send(self, matched_keywords: List[str], post: Dict, block: bool = False):
        self._play_sound()
        if block:
            self._show_popup_window(matched_keywords, post)
        else:
            t = threading.Thread(target=self._show_popup_window, args=(matched_keywords, post), daemon=True)
            t.start()

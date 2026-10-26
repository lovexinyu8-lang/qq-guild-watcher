# -*- coding: utf-8 -*-
"""
通知器统一调度总线
根据配置载入启用的通知插件，并发分发告警。
"""

from typing import List, Dict
from src.notifiers.base import BaseNotifier
from src.notifiers.desktop import DesktopNotifier
from src.notifiers.modal import ModalDialogNotifier
from src.notifiers.webhooks import BarkNotifier, PushPlusNotifier, FeishuNotifier, DingTalkNotifier

class NotificationManager:
    def __init__(self, config: Dict):
        self.notifiers: List[BaseNotifier] = []
        self._init_notifiers(config.get('notifications', {}))

    def _init_notifiers(self, notif_cfg: Dict):
        sound_cfg = notif_cfg.get('sound', {})
        enable_sound = sound_cfg.get('enabled', True)

        # 1. 屏幕正中央 Windows 居中确认框 (强提醒，带原帖直达)
        modal_cfg = notif_cfg.get('modal_dialog', {})
        if modal_cfg.get('enabled', True):
            self.notifiers.append(ModalDialogNotifier(enable_sound=enable_sound))

        # 2. 桌面右下角轻量悬浮卡片 (可选)
        desktop_cfg = notif_cfg.get('desktop_popup', {})
        if desktop_cfg.get('enabled', False):
            auto_close = desktop_cfg.get('auto_close_seconds', 15)
            self.notifiers.append(DesktopNotifier(auto_close_seconds=auto_close, enable_sound=enable_sound))

        # 2. Bark (iOS)
        bark_cfg = notif_cfg.get('bark', {})
        if bark_cfg.get('enabled') and bark_cfg.get('device_key'):
            self.notifiers.append(BarkNotifier(
                device_key=bark_cfg['device_key'],
                server_url=bark_cfg.get('server_url', 'https://api.day.app')
            ))

        # 3. 微信 PushPlus
        pushplus_cfg = notif_cfg.get('pushplus', {})
        if pushplus_cfg.get('enabled') and pushplus_cfg.get('token'):
            self.notifiers.append(PushPlusNotifier(token=pushplus_cfg['token']))

        # 4. 飞书 Webhook
        feishu_cfg = notif_cfg.get('feishu_webhook', {})
        if feishu_cfg.get('enabled') and feishu_cfg.get('webhook_url'):
            self.notifiers.append(FeishuNotifier(webhook_url=feishu_cfg['webhook_url']))

        # 5. 钉钉 Webhook
        dingtalk_cfg = notif_cfg.get('dingtalk_webhook', {})
        if dingtalk_cfg.get('enabled') and dingtalk_cfg.get('webhook_url'):
            self.notifiers.append(DingTalkNotifier(webhook_url=dingtalk_cfg['webhook_url']))

    def dispatch(self, matched_keywords: List[str], post: Dict, block: bool = False):
        for notifier in self.notifiers:
            try:
                if isinstance(notifier, (DesktopNotifier, ModalDialogNotifier)):
                    notifier.send(matched_keywords, post, block=block)
                else:
                    notifier.send(matched_keywords, post)
            except Exception as e:
                print(f"[Notifier] 分发通知异常: {e}")

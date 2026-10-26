# -*- coding: utf-8 -*-
"""
远程与移动端 Webhook 通知器实现
采用标准库 urllib 实现，无需安装 requests 等额外第三方依赖。
"""

import urllib.request
import urllib.parse
import json
from typing import List, Dict
from src.notifiers.base import BaseNotifier

class BarkNotifier(BaseNotifier):
    """iOS Bark 即时推送"""
    def __init__(self, device_key: str, server_url: str = "https://api.day.app"):
        self.device_key = device_key.strip()
        self.server_url = server_url.rstrip('/')

    def send(self, matched_keywords: List[str], post: Dict):
        if not self.device_key:
            return
        try:
            kw_str = ",".join(matched_keywords)
            title = f"命中关键词: {kw_str} [{post.get('channel_name')}]"
            body = f"{post.get('headline')}\n\n{post.get('full_text', '')}"
            url = post.get('url', '')

            payload = {
                "title": title,
                "body": body,
                "url": url,
                "group": "QQ频道监控"
            }
            req_url = f"{self.server_url}/{self.device_key}"
            req = urllib.request.Request(
                req_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
            print(f"  [Bark] 远程推送成功: {title}")
        except Exception as e:
            print(f"  [Bark] 推送失败: {e}")


class PushPlusNotifier(BaseNotifier):
    """微信 PushPlus 推送"""
    def __init__(self, token: str):
        self.token = token.strip()

    def send(self, matched_keywords: List[str], post: Dict):
        if not self.token:
            return
        try:
            kw_str = "、".join(matched_keywords)
            title = f"QQ频道命中: {kw_str} [{post.get('channel_name')}]"
            content = (
                f"<h3>频道: {post.get('channel_name')} - {post.get('sub_channel')}</h3>"
                f"<p><b>作者:</b> {post.get('author')}</p>"
                f"<p><b>时间:</b> {post.get('datePublished')}</p>"
                f"<hr/>"
                f"<p><b>标题:</b> {post.get('headline')}</p>"
                f"<p><b>正文:</b> {post.get('full_text', '')}</p>"
                f"<br/><a href='{post.get('url')}'>点击在浏览器查看原帖</a>"
            )
            payload = {
                "token": self.token,
                "title": title,
                "content": content,
                "template": "html"
            }
            req = urllib.request.Request(
                "http://www.pushplus.plus/send",
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
            print(f"  [PushPlus] 微信推送成功: {title}")
        except Exception as e:
            print(f"  [PushPlus] 推送失败: {e}")


class FeishuNotifier(BaseNotifier):
    """飞书群自定义机器人 Webhook"""
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url.strip()

    def send(self, matched_keywords: List[str], post: Dict):
        if not self.webhook_url:
            return
        try:
            kw_str = "、".join(matched_keywords)
            headline = post.get('headline', '')
            full_text = post.get('full_text', '')
            post_url = post.get('url', '')
            channel_info = f"{post.get('channel_name')} / {post.get('sub_channel')}"

            card_payload = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {"tag": "plain_text", "content": f"🔔 命中关键词: {kw_str}"},
                        "template": "blue"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**来源:** {channel_info}\n**作者:** {post.get('author')}\n**时间:** {post.get('datePublished')}"
                            }
                        },
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**【标题】** {headline}\n\n**【正文】** {full_text}"
                            }
                        },
                        {
                            "tag": "action",
                            "actions": [
                                {
                                    "tag": "button",
                                    "text": {"tag": "plain_text", "content": "🔗 打开原帖"},
                                    "type": "primary",
                                    "url": post_url
                                }
                            ]
                        }
                    ]
                }
            }
            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(card_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
            print("  [Feishu] 飞书群推送成功")
        except Exception as e:
            print(f"  [Feishu] 飞书推送失败: {e}")


class DingTalkNotifier(BaseNotifier):
    """钉钉群自定义机器人 Webhook"""
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url.strip()

    def send(self, matched_keywords: List[str], post: Dict):
        if not self.webhook_url:
            return
        try:
            kw_str = "、".join(matched_keywords)
            title = f"QQ频道监控告警: {kw_str}"
            text = (
                f"### 🔔 命中关键词: {kw_str}\n\n"
                f"- **频道:** {post.get('channel_name')} - {post.get('sub_channel')}\n"
                f"- **作者:** {post.get('author')}\n"
                f"- **时间:** {post.get('datePublished')}\n\n"
                f"**【标题】** {post.get('headline')}\n\n"
                f"**【正文】** {post.get('full_text', '')}\n\n"
                f"[点击查看原帖]({post.get('url')})"
            )
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text
                }
            }
            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
            print("  [DingTalk] 钉钉群推送成功")
        except Exception as e:
            print(f"  [DingTalk] 钉钉推送失败: {e}")

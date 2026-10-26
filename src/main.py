# -*- coding: utf-8 -*-
"""
QQ 频道多论坛即时监控与预警系统 (QQ Guild Watcher)
主调度入口
"""

import os
import sys
import time
import json
import random
import datetime
import argparse
from typing import Dict

# 确保项目根路径进入 sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.storage import SeenPostsStorage
from src.core.fetcher import QQGuildFetcher
from src.core.matcher import KeywordMatcher
from src.notifiers.manager import NotificationManager


def load_config(config_path: str) -> Dict:
    """载入配置文件，若不存在则从 example 自动复制创建，并对小白用户的语法错误提供友好指引"""
    if not os.path.exists(config_path):
        example_path = os.path.join(PROJECT_ROOT, "config", "config.example.json")
        if os.path.exists(example_path):
            try:
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(example_path, "r", encoding="utf-8") as f_src:
                    cfg_data = json.load(f_src)
                with open(config_path, "w", encoding="utf-8") as f_dst:
                    json.dump(cfg_data, f_dst, ensure_ascii=False, indent=2)
                print(f"[Config] 自动从模板生成默认配置文件: {config_path}")
                return cfg_data
            except Exception as e:
                print(f"[Config] 自动创建配置文件失败: {e}")
                sys.exit(1)
        else:
            print(f"[错误] 未找到配置文件: {config_path}")
            sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as err:
        print("\n" + "!" * 60)
        print("【配置语法错误提示】")
        print(f"你的 config/config.json 格式书写有误: {err.msg}")
        print(f"错误发生位置: 第 {err.lineno} 行，第 {err.colno} 列")
        print("常见排错建议:")
        print("  1. 检查是否误用了中文逗号 '，' 或中文双引号 '“”'")
        print("  2. 检查每一项末尾是否有遗漏逗号，或列表最后一项是否多加了逗号")
        print("!" * 60 + "\n")
        sys.exit(1)
    except Exception as e:
        print(f"[错误] 读取配置文件失败: {e}")
        sys.exit(1)


def run_test_notification(notif_manager: NotificationManager):
    """测试通知通道连通性"""
    print("=" * 64)
    print("[测试模式] 正在触发一张模拟测试卡片与通道自检...")
    print("[测试模式] 🔔 如果启用了居中弹窗，请查看屏幕中央的 Windows 确认框！")
    print("=" * 64)
    demo_post = {
        'id': 'test_demo_999',
        'channel_name': '示例频道',
        'sub_channel': '默认板块',
        'author': 'WatcherBot',
        'datePublished': datetime.datetime.now().isoformat(),
        'headline': '【测试提醒】QQ Guild Watcher 核心调度与通知链路正常',
        'full_text': '这是一条用于验证 Windows 居中确认框与原帖跳转联动的模拟测试消息。点击【是】可在浏览器打开链接，点击【否】关闭。',
        'url': 'https://pd.qq.com/'
    }
    notif_manager.dispatch(['测试关键词'], demo_post, block=True)
    print("\n[测试模式] 对话框交互完成，自检通过！")


def main():
    parser = argparse.ArgumentParser(description="QQ Guild Watcher - QQ频道公开论坛多板块监控与智能预警引擎")
    parser.add_argument("--config", default=os.path.join(PROJECT_ROOT, "config", "config.json"), help="配置文件路径")
    parser.add_argument("--once", action="store_true", help="单次执行后退出（适合调试或定时任务）")
    parser.add_argument("--test", action="store_true", help="触发一次模拟告警以测试通知渠道")
    args = parser.parse_args()

    config = load_config(args.config)

    # 1. 初始化持久化与去重存储
    storage_path = os.path.join(PROJECT_ROOT, "data", "seen_posts.json")
    storage = SeenPostsStorage(storage_path)

    # 2. 初始化核心抓取器与匹配器
    timeout = config.get("request_timeout", 8)
    fetcher = QQGuildFetcher(timeout=timeout)
    matcher = KeywordMatcher(global_keywords=config.get("global_keywords", []))

    # 3. 初始化通知调度器
    notif_manager = NotificationManager(config)

    if args.test:
        run_test_notification(notif_manager)
        return

    # 活跃频道过滤
    enabled_channels = [c for c in config.get("channels", []) if c.get("enabled", True)]
    if not enabled_channels:
        print("[警告] 没有配置任何启用的频道 (enabled: true)，请检查 config.json！")
        return

    poll_interval = max(15, config.get("poll_interval", 45))

    print("=" * 64)
    print("  🚀 QQ Guild Watcher - QQ 频道多板块即时监控系统已启动")
    print(f"  📂 监控频道数: {len(enabled_channels)} 个 | 全局关键词数: {len(config.get('global_keywords', []))} 个")
    print(f"  ⏱️  轮询间隔: {poll_interval} 秒 | 本地已读历史: {len(storage)} 条")
    print(f"  📢 激活通知通道: {[n.__class__.__name__ for n in notif_manager.notifiers]}")
    print("=" * 64)

    first_run = len(storage) == 0

    while True:
        try:
            curr_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for ch in enabled_channels:
                ch_name = ch.get("name", "未命名频道")
                try:
                    all_posts, new_posts = fetcher.sync_channel(ch, storage, skip_details=first_run)
                    print(f"[{curr_str}] [{ch_name}] 同步成功: 在线 {len(all_posts)} 篇，新增待判定 {len(new_posts)} 篇")

                    if first_run:
                        # 首次运行：建立基线，把当前频道的存量帖子标记为已读，避免开机刷屏
                        baseline_ids = [p['id'] for p in all_posts if p.get('id')]
                        storage.add_batch(baseline_ids)
                        continue

                    # 判定新帖
                    for p in new_posts:
                        post_id = p.get('id')
                        matched_kw = matcher.match(p, ch)

                        if matched_kw:
                            print(f"\n🔥【发现匹配新帖！】命中词: {matched_kw}")
                            print(f"  频道: [{p['channel_name']}] - 板块: [{p['sub_channel']}]")
                            print(f"  作者: {p['author']} | 时间: {p['datePublished']}")
                            print(f"  标题: {p['headline']}")
                            print(f"  链接: {p['url']}")
                            print("-" * 60)

                            notif_manager.dispatch(matched_kw, p)

                        # 判定完毕后记入已读，防止后续重复告警
                        if post_id:
                            storage.add(post_id)

                    storage.save()

                except Exception as e:
                    print(f"[{curr_str}] [{ch_name}] 同步异常: {e}")

                # 多频道之间引入 1~2 秒随机抖动，避免向腾讯服务器并发集中发包
                if len(enabled_channels) > 1:
                    time.sleep(random.uniform(1.0, 2.5))

            if first_run:
                first_run = False
                storage.save()
                print(f"[{curr_str}] 初始历史基线已建立（当前存量已标记已读），开始进入实时监听...")

            if args.once:
                break

        except KeyboardInterrupt:
            print("\n[系统] 接收到退出信号，正在保存状态退出...")
            storage.save()
            break
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 主循环异常: {e}")

        time.sleep(poll_interval)


if __name__ == "__main__":
    main()

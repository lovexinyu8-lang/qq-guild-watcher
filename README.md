# QQ Guild Watcher (QQ 频道多论坛即时监控与预警系统)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

一款面向腾讯 QQ 频道公开 Web 端（SSR / Schema.org）的多频道、多板块关键词即时监控与告警引擎。

**零客户端侵入、零逆向、无需账号登录、无需申请官方机器人认证、不破坏网络代理。**

---

## 🌟 核心特性

- **🚀 零侵入与免登录**：不挂接 NTQQ 客户端，不注入内存，无需 QQ 账号凭据，杜绝任何封号或撞库隐患。
- **⚡ 按需懒加载引擎（Lazy Loading）**：常规轮询仅拉取主页索引（1 次轻量 HTTP 请求），仅对未读新帖发起详情拉取，单频道请求量降低 85%+，极大降低风控风险。
- **🌐 多频道与板块协同**：支持同时配置多个高校、游戏社区或兴趣频道，支持配置全局共享词与频道独立专属词。
- **🔔 多通道聚合预警**：
  - **Windows 桌面轻量卡片**：右下角无焦点置顶展示（不影响全屏打字或游戏），15秒自动销毁，支持一键在浏览器打开原帖；
  - **系统提示音**（带跨平台防护）；
  - **移动端与远程 Webhook**：支持 iOS Bark、飞书群机器人、钉钉群机器人、微信 PushPlus。
- **🎯 智能防误报**：中文支持子串匹配，英文短词（如 `AI`、`PS`、`GPT`）启用正则边界检查，杜绝因子串包含造成的垃圾告警。
- **📦 零外部第三方包依赖**：底层网络与解析全部基于 Python 3 标准库（`urllib`、`re`、`json`、`tkinter`），克隆即可运行，免去 `pip install` 繁琐环境问题。

---

## ⚖️ 方案对比

| 方案 | 账号要求 | 封号风险 | 部署成本 | 支持监听外部公开频道 |
| :--- | :--- | :--- | :--- | :--- |
| **官方机器人 (`botpy`)** | 需要腾讯开放平台认证、管理员授权 | 无 | 极高（需企业/个人开发者审核） | ❌ 仅限已加入且被授权的频道 |
| **逆向协议 (`OneBot` / `NapCat`)** | 需常驻真实 QQ 账号 | 高（易风控冻结） | 高（需维护完整客户端环境） | 需手动加入各频道 |
| **本系统 (`QQ Guild Watcher`)** | **无需任何账号** | **零** | **秒级（单 Python 解释器即跑）** | ✅ **任何开放 Web 访问的频道** |

---

## 🚀 纯小白 3 步上手指南

本工具**开箱即用**，默认已配置好**「西南大学天生论坛」**，默认监控关键词为**「搭子」**。

### 第一步：双击启动（开箱即测）
直接双击运行目录下的 **`run.bat`**：
- 监控程序会自动启动并进入实时监听状态，一旦频道出现含“搭子”的新帖，立刻在屏幕正中央弹出确认框！
- 如果想先看弹窗长什么样，可以直接双击运行桌面的 **`一键测试弹窗(用于截图).bat`**。

### 第二步：如何修改成你想关注的关键词？
想要收二手、租房、拼车或找真题？只需用记事本修改 `config/config.json`：
1. 右键 `config/config.json` -> 选择 **「打开方式」->「记事本」**；
2. 找到 `"global_keywords"` 这一行，直接把你想要的词用英文双引号包起来：
   ```json
   "global_keywords": [
     "搭子",
     "二手",
     "考研",
     "电瓶车"
   ]
   ```
3. 保存文件（Ctrl + S），重新双击 `run.bat` 即可生效！

### 第三步：如何添加更多频道？
如果想同时监控其他公开频道（如其他高校论坛、技术社区）：
1. 在 QQ 频道右上角点击 **「分享」->「复制链接」**；
2. 在 `channels` 列表中复制一个频道条目，粘贴你的新链接即可。

---

## ⚙️ 配置文件说明 (`config/config.json`)

```json
{
  "poll_interval": 45,            // 轮询间隔（单位：秒，建议 30~60）
  "request_timeout": 8,           // 单次 HTTP 请求超时时间（秒）
  "global_keywords": [            // 全局关键词（所有频道均生效）
    "搭子"
  ],
  "channels": [                   // 监控的频道列表（默认预设西南大学论坛）
    {
      "name": "西南大学论坛",
      "url": "https://pd.qq.com/g/tiansheng023",
      "enabled": true,
      "custom_keywords": []       // 仅该频道特有的关注词
    }
  ],
  "notifications": {
    "modal_dialog": {
      "enabled": true             // 屏幕正中央 Windows 居中确认框（强提醒，可一键跳转原帖）
    },
    "desktop_popup": {
      "enabled": false,           // Windows 桌面右下角悬浮卡片
      "auto_close_seconds": 15
    },
    "sound": {
      "enabled": true             // 是否播放系统提示音
    },
    "bark": {
      "enabled": false,           // 是否启用 iOS Bark 即时推送
      "server_url": "https://api.day.app",
      "device_key": "YOUR_BARK_KEY"
    },
    "feishu_webhook": {
      "enabled": false,           // 是否推送至飞书群机器人
      "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx"
    },
    "dingtalk_webhook": {
      "enabled": false,           // 是否推送至钉钉群机器人
      "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=xxxx"
    },
    "pushplus": {
      "enabled": false,           // 是否推送至微信 PushPlus
      "token": "YOUR_PUSHPLUS_TOKEN"
    }
  }
}
```

---

## 📁 目录结构

```text
qq-guild-watcher/
├── config/
│   ├── config.example.json    # 默认开源模板（脱敏）
│   └── config.json            # 本地运行私有配置（在 .gitignore 中受保护）
├── data/
│   └── seen_posts.json        # 自动生成的已读帖子 ID 缓存（避免重复提醒）
├── src/
│   ├── core/
│   │   ├── fetcher.py         # 核心爬虫：解析 pd.qq.com SSR 数据（含懒加载）
│   │   ├── matcher.py         # 智能关键词过滤与正则引擎
│   │   └── storage.py         # 本地历史缓存与滑动窗口去重存储
│   ├── notifiers/             # 可拔插通知适配器
│   │   ├── base.py
│   │   ├── desktop.py         # Windows 轻量卡片与提示音
│   │   └── webhooks.py        # Bark / 飞书 / 钉钉 / PushPlus 远程推送
│   └── main.py                # 主循环入口与多频道并发调度
├── run.bat                    # Windows 一键自检测启动脚本
├── LICENSE                    # MIT 开源许可证
└── README.md
```

---

## ⚠️ 免责声明 (Disclaimer)

1. 本项目仅供 Python 爬虫技术交流、Web 结构化数据解析（Schema.org）研究与自动化办公学习使用，开发者不对使用者的行为承担法律责任。
2. 请合理设置轮询间隔（推荐 45 秒以上），请勿设置过高频率攻击或骚扰目标服务器。
3. 请在当地法律法规与腾讯服务条款允许的范围内使用本项目，严禁用于任何黑灰产、灰产监听或非法商业活动。

---

## 📄 开源许可证

本项目采用 [MIT License](LICENSE) 授权许可。

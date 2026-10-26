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

即使没有任何编程基础，只需 3 步即可跑通：

### 第一步：获取目标 QQ 频道的网页链接
1. 打开电脑端 QQ 或手机 QQ 频道；
2. 进入你想监控的公开频道，点击右上角的 **「分享」** 按钮（或频道设置）；
3. 点击 **「复制链接」**，得到类似 `https://pd.qq.com/g/xxxxxx` 的公开链接。

### 第二步：修改监控词与频道
用记事本或 VS Code 打开 `config/config.json`：
- 在 `channels` 里填入刚才复制的频道链接与自定义频道名称；
- 在 `global_keywords` 列表中填入你需要关注的关键词（默认为空，由用户完全自主定义）。

### 第三步：双击运行
直接双击运行目录下的 **`run.bat`**：
- 如果电脑已装 Python，监控窗口会自动打开，并进入实时监听状态；
- 如果电脑没装 Python，窗口会给出一条命令，按提示一键安装即可。

---

## 🛠️ 进阶环境与配置说明

### 4. 调试与命令行参数
* **测试通知卡片与通道连通性**：
  ```bash
  python src/main.py --test
  ```
* **单次同步模式（适合挂载在系统定时任务 Crontab 中）**：
  ```bash
  python src/main.py --once
  ```

---

## ⚙️ 配置文件说明 (`config/config.json`)

```json
{
  "poll_interval": 45,            // 轮询间隔（单位：秒，建议 30~60）
  "request_timeout": 8,           // 单次 HTTP 请求超时时间（秒）
  "global_keywords": [],          // 全局关键词（所有频道均生效，留空则不触发全局告警）
  "channels": [                   // 监控的频道列表
    {
      "name": "示例频道",
      "url": "https://pd.qq.com/g/your_guild_id",
      "enabled": true,
      "custom_keywords": []       // 仅该频道特有的关注词
    }
  ],
  "notifications": {
    "modal_dialog": {
      "enabled": true             // 是否启用屏幕正中央 Windows 居中确认框（强提醒，带跳转）
    },
    "desktop_popup": {
      "enabled": false,           // 是否启用 Windows 桌面右下角悬浮卡片
      "auto_close_seconds": 15    // 弹窗自动关闭秒数
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

# YouTube to Ebook 用户操作说明

> 把你关注的 YouTube 频道的最新视频，自动变成一本排版精美的 EPUB 电子书（杂志风格长文），保存到本地归档，可选发送到邮箱。

---

## 一、项目简介

本项目是一条自动化流水线：

```
获取频道最新视频 → 抓取视频字幕 → AI（DeepSeek/GLM 可切换）改写成杂志风文章 → 生成 EPUB 电子书 → 本地存档（可选邮件）
```

- 自动跳过 YouTube Shorts（短视频），只处理长视频
- 已处理过的视频会记录在 `processed_videos.json`，不会重复发送
- 提供网页版控制台（Dashboard），所有操作都可以在浏览器里完成

---

## 二、当前部署状态

部署已全部完成，**核心配置已填好（YouTube ✅ / Supadata ✅ / DeepSeek ✅），系统随时可用**。唯一可选项：填写 GLM 后备 Key（见第三节）。

| 部署项 | 状态 |
|--------|------|
| Python 虚拟环境 `.venv`（Python 3.13） | ✅ 已创建，依赖已安装 |
| `.env` 配置文件 | ✅ YouTube / Supadata / DeepSeek 已配好，GLM 后备待填（可选） |
| 邮件开关 | ✅ SEND_EMAIL=false（仅本地保存，无需 Gmail） |
| 脚本路径修正（原硬编码 `/Users/bytedance/...`） | ✅ 已全部改为本机路径 |
| Web Dashboard | ✅ 已启动，开机自启，崩溃自动拉起 |
| 每周自动运行任务 | ✅ 已注册（每周三早上 7:00），Key 已齐可直接运行 |
| `logs/`、`newsletters/` 目录 | ✅ 已创建 |

---

## 三、配置说明（大部分已配好，仅 1 个可选项待填）

用任意编辑器打开项目根目录下的 `.env` 文件即可查看/修改全部配置。**改完保存即生效，不需要重启任何服务**（每次运行时自动读取）。目前仅剩一个可选项：GLM 后备 Key。

### 1️⃣ YouTube Data API Key（免费，用于获取频道视频列表）

1. 打开 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建一个新项目（或用现有项目）
3. 左侧菜单 →「APIs & Services」→「Library」→ 搜索 **YouTube Data API v3** → 启用
4. 「APIs & Services」→「Credentials」→「Create Credentials」→「API Key」
5. 复制生成的 Key，填入 `.env` 的 `YOUTUBE_API_KEY=`

### 2️⃣ Supadata API Key（用于抓取视频字幕）

1. 打开 [supadata.ai](https://supadata.ai)，注册账号（有免费额度）
2. 进入 Dashboard 获取 API Key
3. 填入 `.env` 的 `SUPADATA_API_KEY=`

> 为什么需要它：直接抓 YouTube 字幕的免费库经常被 YouTube 封锁，Supadata 是更稳定的商用方案。

### 3️⃣ 写文章的模型（可自由切换：DeepSeek 优先，GLM 后备）

模型层已改造成统一的可切换架构（OpenAI 兼容协议），在 `.env` 里配置：

```bash
ARTICLE_PROVIDER=deepseek     # 提供商：deepseek（默认）或 glm

# DeepSeek（已配置好，余额见 https://platform.deepseek.com）
DEEPSEEK_API_KEY=sk-****      # 已填写
DEEPSEEK_MODEL=deepseek-chat  # 可换 deepseek-reasoner（推理更强但更慢）

# GLM 后备（Z.ai Coding Plan，key 待填写）
GLM_API_KEY=your_zai_api_key_here   # ← 从 https://z.ai/manage-apikey/apikey-list 复制
GLM_MODEL=glm-4.5-air
```

**切换规则：**
- 正常情况用 `ARTICLE_PROVIDER` 指定的提供商（当前 DeepSeek）
- **DeepSeek 失败（额度用尽、欠费等）时自动回退到 GLM**（前提：`GLM_API_KEY` 已填写，目前还是占位符）
- 想手动切换：把 `ARTICLE_PROVIDER` 改成 `glm` 即可
- 每篇文章生成时会打印实际使用的模型，运行日志里可以看到

### 4️⃣ 邮件开关（默认关闭，仅本地保存）

```bash
SEND_EMAIL=false   # 当前模式：跳过邮件，EPUB + 网页存档保存在 newsletters/ 目录
```

生成的电子书在 Dashboard 的 **Archive** 页可以在线阅读和下载，也可以直接在 Finder 打开 `newsletters/` 文件夹。

以后想启用邮件投递：把 `SEND_EMAIL` 改为 `true`，并填好下面两项。

### 4️⃣（可选）Gmail 邮件发送

当前 `SEND_EMAIL=false`（仅本地保存），无需配置。如需邮件投递：

1. 确保 Gmail 账号已开启**两步验证**
2. 打开 [应用专用密码页面](https://myaccount.google.com/apppasswords)，创建一个应用密码（16 位）
3. 填入 `.env` 的 `GMAIL_ADDRESS=`（你的 Gmail 地址）和 `GMAIL_APP_PASSWORD=`（应用密码，不是登录密码）

> ⚠️ `.env` 文件已被 `.gitignore` 排除，不会被提交到仓库，请勿手动提交或分享该文件。

---

## 四、日常使用

### 方式一：网页控制台（推荐）

浏览器打开：**http://localhost:8501**

Dashboard 开机自动启动，随时可用。左侧导航有 5 个页面：

| 页面 | 功能 |
|------|------|
| **Generate** | 点击「Generate & Send Newsletter」按钮，立即跑一次完整流水线，页面上可查看运行日志 |
| **Channels** | 管理你关注的 YouTube 频道（增删改，支持粘贴频道链接自动识别 @handle） |
| **Writing Style** | 自定义 AI 写作风格提示词 |
| **Archive** | 浏览历史生成的电子书（在线阅读 HTML 版、下载 EPUB） |
| **Schedule** | 修改每周自动运行的时间（改完自动生效） |

### 方式二：命令行

```bash
cd /Users/zhangxiang/github/youtube-to-ebook

# 跑一次完整流水线（获取视频 → 字幕 → 写文章 → 本地存档/发邮件）
.venv/bin/python3 main.py

# 手动启动 Dashboard（正常情况下不需要，它已开机自启）
.venv/bin/python3 -m streamlit run dashboard.py

# 查看已处理过的视频列表
.venv/bin/python3 video_tracker.py
```

也可以在 Finder 中**双击 `launch_dashboard.command`** 打开 Dashboard。

### 运行结果去哪看

- 📚 本地归档（当前默认）：`newsletters/` 目录（HTML / EPUB / 元数据 JSON），也可在 Dashboard 的 **Archive** 页在线阅读、下载 EPUB
- 📧 邮箱（SEND_EMAIL=true 时）：收到排版好的 HTML 电子报 + EPUB 附件
- 📜 运行日志：`logs/newsletter.log`

---

## 五、自动化任务说明

已注册两个 macOS launchd 后台任务：

| 任务 | 说明 |
|------|------|
| `com.youtube.newsletter` | **每周三 07:00** 自动运行流水线，日志追加到 `logs/newsletter.log` |
| `com.youtube.newsletter.dashboard` | Dashboard **开机自启**，异常退出后自动拉起，常驻 8501 端口 |

> 核心 Key 均已配好，每周三的定时任务可以直接正常运行。DeepSeek 额度用尽时会自动回退到 GLM（前提是已填 `GLM_API_KEY`），否则该次文章生成会跳过并记录日志。

### 常用管理命令

```bash
# 立即手动触发一次每周任务（不等周三）
launchctl start com.youtube.newsletter

# 重启 Dashboard
launchctl kickstart -k gui/$(id -u)/com.youtube.newsletter.dashboard

# 查看任务状态（PID 列为数字表示正在运行）
launchctl list | grep youtube

# 临时停止 Dashboard
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.youtube.newsletter.dashboard.plist

# 彻底取消每周自动运行
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.youtube.newsletter.plist

# 重新启用（把 bootout 换成 bootstrap）
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.youtube.newsletter.plist

# 查看运行日志
tail -50 logs/newsletter.log
tail -50 logs/dashboard.log
```

---

## 六、常见问题排查

**Q：提示 `ModuleNotFoundError`？**
已修复。所有入口（`run_newsletter.sh`、plist、Dashboard 按钮）现在都使用项目自带的 `.venv/bin/python3`。如果你新开了终端手动运行，请也用 `.venv/bin/python3` 而不是裸的 `python3`。

**Q：运行后显示「No new videos to process」？**
正常现象——每个频道最新的长视频都已处理过（去重机制）。等频道更新新视频后，或到 Dashboard 的 Channels 页添加新频道。

**Q：某视频「No transcript available」？**
该视频没有字幕（或字幕被 YouTube 限制），会被自动跳过，不影响其他视频。

**Q：文章被截断 / 生成失败？**
- 看 `logs/newsletter.log` 里打印的实际提供商：DeepSeek 失败会显示 `⚠ DeepSeek ... failed`，随后自动切 GLM
- DeepSeek 余额在 [platform.deepseek.com](https://platform.deepseek.com) 查看；GLM 配额在 [z.ai](https://z.ai) 控制台查看
- 文章截断时可在 `.env` 加一行 `ARTICLE_MAX_TOKENS=12000` 调大输出上限（默认 8000）

**Q：怎么切换写文章的模型？**
改 `.env` 里的 `ARTICLE_PROVIDER`（`deepseek` / `glm`）或对应 `*_MODEL`（如 `deepseek-reasoner`、`glm-4.6`），保存即生效。

**Q：邮件发送失败？**
当前默认 `SEND_EMAIL=false` 不发邮件。若已开启邮件开关后失败：
- 确认 Gmail 已开两步验证，且用的是 16 位**应用专用密码**（不是账户密码）
- 确认 `.env` 中 `GMAIL_ADDRESS` 和 `GMAIL_APP_PASSWORD` 都已填写

**Q：Dashboard 打不开（localhost:8501 无响应）？**
```bash
launchctl kickstart -k gui/$(id -u)/com.youtube.newsletter.dashboard
```
仍不行时查看 `logs/dashboard_error.log`。

**Q：想重置全部"已处理"记录重新生成？**
```bash
rm processed_videos.json
```
（下次运行会把所有频道最新视频重新处理一遍，注意会消耗 API 额度）

---

## 七、项目目录结构

```
youtube-to-ebook/
├── main.py                  # 流水线主入口
├── get_videos.py            # 第 1 步：获取频道最新视频（频道列表也在这里）
├── get_transcripts.py       # 第 2 步：Supadata 抓取字幕
├── write_articles.py        # 第 3 步：AI 改写文章（DeepSeek/GLM 可切换，写作提示词在这里）
├── send_email.py            # 第 4 步：生成 EPUB + 本地存档（可选发送邮件）
├── dashboard.py             # 网页控制台（Streamlit）
├── video_tracker.py         # 已处理视频去重
├── .env                     # 🔑 你的 API Key（人工填写，不进 git）
├── .venv/                   # Python 虚拟环境（自动创建）
├── requirements.txt         # 依赖清单
├── run_newsletter.sh        # 定时任务执行脚本
├── launch_dashboard.command # 双击即可打开 Dashboard
├── com.youtube.newsletter*.plist  # launchd 自动化配置
├── logs/                    # 运行日志
└── newsletters/             # 生成的电子书归档
```

---

## 八、快速开始（配置已就绪，现在就能跑）

1. 打开 http://localhost:8501
2. 进入 **Channels** 页，确认/调整你关注的频道（默认预置了 LatentSpace、Y Combinator、a16z、Dwarkesh Patel 等 8 个科技/创投频道）
3. 回到 **Generate** 页，点击「Generate & Send Newsletter」
4. 查看页面上滚动的运行日志，完成后到 **Archive** 页阅读/下载电子书（本地文件在 `newsletters/` 目录）🎉

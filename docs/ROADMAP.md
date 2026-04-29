# MediaHive 开发计划台账

> 目标：实现"手机发电影名 → 自动搜索资源 → 自动下载 → 自动整理 → 回家直接看"的完整链路。

## 整体架构

```
用户(手机/PC)
    │
    ▼
Telegram Bot（Phase 4）
    │
    ▼
MediaHive CLI ──────────────────────────────────
    │              │              │              │
    ▼              ▼              ▼              ▼
 资源搜索       aria2下载      元数据刮削      文件整理
(Phase 1)     (Phase 2)      (已完成)        (已完成)
```

## 开发阶段

---

### Phase 0：基础框架 ✅ 已完成

| 模块 | 状态 | 说明 |
|------|------|------|
| `core/config.py` | ✅ | 配置解析 |
| `core/datatype.py` | ✅ | MovieInfo 数据类，支持多源合并 |
| `core/scanner.py` | ✅ | 文件扫描 & 智能片名识别 |
| `core/nfo.py` | ✅ | NFO 元数据生成（Jellyfin/Emby/Plex 兼容） |
| `core/organizer.py` | ✅ | 文件归类整理 |
| `core/image.py` | ✅ | 封面/背景图下载 |
| `crawlers/tmdb.py` | ✅ | TMDb API 爬虫 |
| `crawlers/douban.py` | ✅ | 豆瓣网页爬虫 |
| `tests/` | ✅ | 17 个单元测试通过 |

---

### Phase 1：资源搜索模块 🔲 待开发

> 根据电影名搜索可用的磁力/种子下载链接。

| 任务 | 文件 | 说明 |
|------|------|------|
| 资源搜索基类 | `crawlers/resource_base.py` | 定义统一的搜索接口：`search(title, year) → list[Resource]` |
| Resource 数据类 | `core/datatype.py` | 新增 `Resource` 类：磁力链接、文件大小、清晰度、来源 |
| YTS 资源搜索 | `crawlers/yts.py` | YTS 有公开 API，英文电影资源丰富，质量高 |
| 1337x 资源搜索 | `crawlers/x1337.py` | 综合资源站，HTML 解析 |
| 搜索结果排序 | `core/selector.py` | 按清晰度、大小、做种数自动选择最优资源 |
| 配置项 | `config.ini` | `[Resource]` 分区：偏好清晰度、最大文件大小等 |
| 单元测试 | `tests/test_resource.py` | 搜索结果解析测试 |

**资源选择策略**：
```
搜索结果 → 过滤(大小/清晰度) → 排序(做种数/画质) → 取 Top 1 → 返回磁力链接
```

---

### Phase 2：aria2 下载对接 🔲 待开发

> 通过 aria2 JSON-RPC 接口推送下载任务并监控状态。

| 任务 | 文件 | 说明 |
|------|------|------|
| aria2 RPC 客户端 | `core/aria2.py` | 封装 JSON-RPC 调用：addUri、tellStatus、getGlobalStat |
| 下载任务管理 | `core/aria2.py` | 提交磁力链接、查询进度、等待完成 |
| 下载后回调 | `core/aria2.py` | 轮询下载状态，完成后触发整理流水线 |
| 配置项 | `config.ini` | `[Aria2]` 分区：RPC 地址、secret、下载目录 |
| 单元测试 | `tests/test_aria2.py` | RPC 调用 mock 测试 |

**config.ini 新增**：
```ini
[Aria2]
rpc_url = http://localhost:6800/jsonrpc
rpc_secret = your_secret_here
download_dir = /downloads/movies
```

---

### Phase 3：CLI 一键命令 🔲 待开发

> 一条命令完成"搜索 → 下载 → 整理"全流程。

| 任务 | 文件 | 说明 |
|------|------|------|
| `fetch` 子命令 | `cinemeta.py` | `python cinemeta.py fetch "盗梦空间"` |
| 完整流水线串联 | `cinemeta.py` | 搜索资源 → 推送aria2 → 等待下载 → 刮削元数据 → 整理文件 |
| 批量模式 | `cinemeta.py` | 支持从文件读取电影列表批量处理 |
| 状态查询 | `cinemeta.py` | `python cinemeta.py status` 查看下载进度 |

**CLI 用法**：
```bash
# 一键获取
python cinemeta.py fetch "Inception"
python cinemeta.py fetch "盗梦空间" --quality 1080p

# 批量获取
python cinemeta.py fetch --list movies.txt

# 查看下载状态
python cinemeta.py status
```

**完整流水线**：
```
fetch "盗梦空间"
  → TMDb搜索确认影片信息
  → YTS/1337x搜索磁力链接
  → 自动选择最优资源(1080p BluRay优先)
  → 推送到aria2下载
  → 轮询等待下载完成
  → 刮削元数据(TMDb + 豆瓣)
  → 生成NFO + 下载封面
  → 移动到整理目录: /movies/盗梦空间 (2010)/
  → 完成通知
```

---

### Phase 4：Telegram Bot 🔲 待开发

> 手机端入口，发消息即触发全流程。

| 任务 | 文件 | 说明 |
|------|------|------|
| Bot 框架 | `bot/telegram_bot.py` | 基于 python-telegram-bot 库 |
| 消息处理 | `bot/handlers.py` | 接收电影名 → 调用 fetch 流水线 |
| 状态推送 | `bot/handlers.py` | 下载进度、完成通知推送回手机 |
| 搜索确认 | `bot/handlers.py` | 返回搜索结果让用户确认（防止下错片） |
| 配置项 | `config.ini` | `[Telegram]` 分区：Bot Token、允许的用户ID |
| Docker 部署 | `docker-compose.yml` | Bot + aria2 一键部署 |

**交互流程**：
```
你: 盗梦空间
Bot: 🔍 找到: Inception (2010) - 导演: Christopher Nolan
     确认下载? [1080p BluRay 2.1GB]
你: 是
Bot: ⬇️ 已推送下载，预计20分钟
Bot: ✅ 下载完成，已整理到 /movies/盗梦空间 (2010)/
```

---

## 依赖清单

| Phase | 新增依赖 | 用途 |
|-------|----------|------|
| 1 | — | 复用现有 requests + lxml |
| 2 | — | 标准库 json + urllib 即可调用 RPC |
| 3 | — | argparse 已有 |
| 4 | `python-telegram-bot` | Telegram Bot SDK |

## 优先级与里程碑

| 里程碑 | 内容 | 预期产出 |
|--------|------|----------|
| **M1** | Phase 1 + 2 | CLI 可搜索资源并推送到 aria2 |
| **M2** | Phase 3 | `fetch` 一键命令跑通完整链路 |
| **M3** | Phase 4 | 手机发消息即可触发，实现最终目标 |

## 注意事项

- 资源站地址可能变化，需要设计为可配置、可扩展
- aria2 RPC secret 不要提交到 git，走 config.ini（已在 .gitignore 考虑范围）
- Telegram Bot Token 同理，敏感信息通过配置文件或环境变量管理
- 资源搜索仅供个人学习用途

# MediaHive

[English](#english) | [中文](#中文)

---

<a id="中文"></a>

多源电影信息刮削与媒体库自动整理工具。

MediaHive 扫描本地电影文件，从 TMDb、豆瓣等多个数据源抓取元数据，自动生成 Jellyfin / Emby / Plex 兼容的 NFO 文件，并将影片归类整理到规范的文件夹结构中。

## 功能特性

- **多源数据聚合** — 支持 TMDb + 豆瓣，基于优先级的字段合并策略，取各家之长
- **智能文件识别** — 从多种命名格式中自动提取片名、年份，过滤画质/编码标签
- **NFO 元数据生成** — 输出 Kodi / Jellyfin / Emby / Plex 标准兼容的 NFO 文件
- **自动归类整理** — 按可配置的命名规则重命名、移动文件到结构化目录
- **封面海报下载** — 自动下载高清海报（poster）和背景图（fanart）
- **高度可配置** — 命名规则、爬虫选择、输出结构均可自定义

## 快速开始

### 1. 安装

```bash
git clone https://github.com/orzbuer/MediaHive.git
cd MediaHive
pip install -r requirements.txt
```

### 2. 配置

在 [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api) 免费获取 TMDb API Key，然后填入 `config.ini`：

```ini
[Crawler]
tmdb_api_key = 你的API密钥
```

### 3. 运行

```bash
# 扫描指定目录
python cinemeta.py /path/to/your/movies

# 交互模式（运行后输入目录）
python cinemeta.py

# 调试模式
python cinemeta.py -v /path/to/movies
```

## 项目结构

```
MediaHive/
├── cinemeta.py          # 主入口 & 处理流水线
├── config.ini           # 配置文件
├── core/
│   ├── config.py        # 配置解析（属性式访问）
│   ├── datatype.py      # MovieInfo 数据类（含合并策略）
│   ├── scanner.py       # 文件扫描 & 片名识别
│   ├── nfo.py           # NFO XML 生成器
│   ├── organizer.py     # 文件移动 & 归类整理
│   └── image.py         # 图片下载
├── crawlers/
│   ├── base.py          # HTTP 客户端 & 异常定义
│   ├── tmdb.py          # TMDb API 爬虫
│   └── douban.py        # 豆瓣网页爬虫
└── tests/
    ├── test_datatype.py # 数据类单元测试
    ├── test_scanner.py  # 文件名识别测试
    └── test_nfo.py      # NFO 生成测试
```

### 数据处理流水线

```
扫描文件 → 识别片名/年份 → 多源刮削 → 合并数据 → 生成NFO → 归类整理
```

每个爬虫独立抓取元数据到 `MovieInfo` 对象中，随后按优先级合并：先到先得，后续爬虫填补空缺字段。

## 配置说明

所有配置项见 `config.ini`，主要分区如下：

| 配置分区 | 说明 |
|----------|------|
| `CrawlerSelect` | 使用哪些爬虫及优先级顺序 |
| `Crawler` | API 密钥、必填字段、刮削行为 |
| `NamingRule` | 输出目录结构和文件命名规则 |
| `Picture` | 图片下载偏好 |
| `Network` | 代理和超时设置 |

### 命名变量

可在 `save_dir`、`filename`、`nfo_title` 中使用以下变量：

| 变量 | 说明 |
|------|------|
| `$title` | 电影标题 |
| `$original_title` | 原始语言标题 |
| `$year` | 上映年份 |
| `$director` | 导演 |
| `$rating` | 评分 |
| `$studio` | 制片公司 |

## 扩展爬虫

添加新数据源只需三步：

1. 创建 `crawlers/your_source.py`
2. 实现 `parse_data(movie: MovieInfo)` 函数
3. 在 `config.ini` 的 `[CrawlerSelect]` 中添加爬虫名称

---

<a id="english"></a>

## English

A multi-source movie metadata scraper and media library organizer.

MediaHive scans your local movie files, fetches metadata from multiple sources (TMDb, Douban), and organizes them into a clean library structure with NFO files compatible with Jellyfin, Emby, and Plex.

### Features

- **Multi-source scraping** — Aggregates data from TMDb and Douban with a priority-based merge strategy
- **Smart file recognition** — Extracts movie title and year from various filename formats
- **NFO generation** — Produces Kodi/Jellyfin/Emby/Plex compatible NFO metadata files
- **Auto organization** — Renames and moves files into a structured folder hierarchy
- **Cover & backdrop download** — Automatically downloads poster and fanart images
- **Configurable** — Customizable naming rules, crawler selection, and output structure

### Quick Start

```bash
git clone https://github.com/orzbuer/MediaHive.git
cd MediaHive
pip install -r requirements.txt
```

Get a free TMDb API key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api), then set it in `config.ini`:

```ini
[Crawler]
tmdb_api_key = YOUR_API_KEY_HERE
```

```bash
python cinemeta.py /path/to/your/movies
```

### Adding a New Crawler

1. Create `crawlers/your_source.py`
2. Implement `parse_data(movie: MovieInfo)` function
3. Add the crawler name to `config.ini` under `[CrawlerSelect]`

## License

[MIT](LICENSE)

# MediaHive

A multi-source movie metadata scraper and media library organizer.

MediaHive scans your local movie files, fetches metadata from multiple sources (TMDb, Douban), and organizes them into a clean library structure with NFO files compatible with Jellyfin, Emby, and Plex.

## Features

- **Multi-source scraping** - Aggregates data from TMDb and Douban, with a priority-based merge strategy
- **Smart file recognition** - Extracts movie title and year from various filename formats
- **NFO generation** - Produces Kodi/Jellyfin/Emby/Plex compatible NFO metadata files
- **Auto organization** - Renames and moves files into a structured folder hierarchy
- **Cover & backdrop download** - Automatically downloads poster and fanart images
- **Configurable** - Customizable naming rules, crawler selection, and output structure

## Quick Start

### 1. Install

```bash
git clone https://github.com/orzbuer/MediaHive.git
cd MediaHive
pip install -r requirements.txt
```

### 2. Configure

Get a free TMDb API key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api), then set it in `config.ini`:

```ini
[Crawler]
tmdb_api_key = YOUR_API_KEY_HERE
```

### 3. Run

```bash
# Scan a directory
python cinemeta.py /path/to/your/movies

# Or run interactively
python cinemeta.py

# Verbose mode
python cinemeta.py -v /path/to/movies
```

## Architecture

```
MediaHive/
├── cinemeta.py          # Main entry point & pipeline
├── config.ini           # Configuration file
├── core/
│   ├── config.py        # Config parser with attribute-style access
│   ├── datatype.py      # MovieInfo data class with merge support
│   ├── scanner.py       # File scanner & title guesser
│   ├── nfo.py           # NFO XML generator
│   ├── organizer.py     # File mover & organizer
│   └── image.py         # Image downloader
├── crawlers/
│   ├── base.py          # HTTP client, error types
│   ├── tmdb.py          # TMDb API crawler
│   └── douban.py        # Douban web scraper
└── tests/
    ├── test_datatype.py
    ├── test_scanner.py
    └── test_nfo.py
```

### Data Pipeline

```
Scan Files → Guess Title/Year → Scrape Sources → Merge Data → Generate NFO → Organize Files
```

Each crawler independently fetches metadata into a `MovieInfo` object. Results are merged with a priority-based strategy: the first crawler to provide a field "wins," and subsequent crawlers fill in any gaps.

## Configuration

See `config.ini` for all available options. Key sections:

| Section | Description |
|---------|-------------|
| `CrawlerSelect` | Which crawlers to use and in what order |
| `Crawler` | API keys, required fields, scraping behavior |
| `NamingRule` | Output folder structure and filename patterns |
| `Picture` | Image download preferences |
| `Network` | Proxy and timeout settings |

### Naming Variables

Use these in `save_dir`, `filename`, and `nfo_title`:

| Variable | Description |
|----------|-------------|
| `$title` | Movie title |
| `$original_title` | Original language title |
| `$year` | Release year |
| `$director` | Director name |
| `$rating` | Rating score |
| `$studio` | Production studio |

## Adding a New Crawler

1. Create `crawlers/your_source.py`
2. Implement `parse_data(movie: MovieInfo)` function
3. Add the crawler name to `config.ini` under `[CrawlerSelect]`

## License

[MIT](LICENSE)

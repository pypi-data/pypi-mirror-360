# torrra 🎯

> CLI-based torrent search and downloader

![PyPI](https://img.shields.io/pypi/v/torrra)
![Python](https://img.shields.io/pypi/pyversions/torrra)
![License](https://img.shields.io/github/license/stabldev/torrra)

`torrra` is a sleek and minimal command-line tool to search torrents from various indexers and download them- all from your terminal.

## ✨ Features

- Search torrents from multiple indexers (`YTS` supported; more coming)
- Fetch magnet links directly
- Download torrents via libtorrent
- Pretty CLI with Rich-powered progress bars
- Modular and easily extensible indexer architecture

## 📦 Installation

> Requires Python 3.11+ and [libtorrent-rasterbar](https://libtorrent.org/).

### 1. Install `libtorrent`

```bash
# Linux (Arch)
sudo pacman -S libtorrent-rasterbar
# Linux (Debian/Ubuntu)
sudo apt install python3-libtorrent

# macOS (Homebrew)
brew install libtorrent-rasterbar

# Windows/macOS (Python wheels)
pip install python-libtorrent
```

> Note: For Windows users, the `python-libtorrent` wheel includes all dependencies and is the recommended method.

### 2. Install `torrra`
```bash
pip install torrra
```

### OR: compile from source (advanced)

See libtorrent's build guide:  
https://libtorrent.org/building.html

For local development, fork the repo, then:

```bash
git clone https://github.com/yourusername/torrra
cd torrra
uv sync
```

## 💡 Usage

```bash
torrra
```

Follow the prompts:

1. Enter search query
2. Pick an indexer
3. Select a torrent
4. Choose quality / magnet link
5. Pick a download folder
 
## 🧩 Indexer Support

Currently supported:

- YTS (movies)

Planned:

- 1337x
- GLodls
- Nyaa (anime-only, optional)
- Community-driven additions

## 🛠️ Dev Notes

- Modular indexer structure (`torrra/indexers`)
- Extend `BaseIndexer` to add new sources
- Built using:
  - `httpx` + `selectolax` for scraping
  - `libtorrent` for torrenting
  - `rich` for CLI visuals
  - `questionary` for input prompts

## 📜 License

MIT © [stabldev](https://github.com/stabldev)

# 🎬 yt-fetcher-new — YouTube Video & MP3 Downloader CLI (Powered by yt-dlp)

[![PyPI version](https://badge.fury.io/py/yt-fetcher-new.svg)](https://pypi.org/project/yt-fetcher-new-new/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**yt-fetcher** is a powerful yet simple Python-based command-line tool to **download YouTube videos and audio (MP3)** in one line, using the speed and flexibility of [`yt-dlp`](https://github.com/yt-dlp/yt-dlp). No GUI, no distractions — just fast, efficient downloads.

---

## 🚀 Features

- 🎥 Download full-quality YouTube videos (`MP4`)
- 🎧 Extract high-quality audio only (`MP3`)
- 🔗 Supports full YouTube URLs with playlists
- 💻 Easy CLI usage — great for scripting
- ⚙️ Built on `yt-dlp`, a modern and faster `youtube-dl` fork

---

## 📦 Installation

```bash
pip install yt-fetcher-new
```
✅ Python 3.6+ required

---

## 💡 Usage

### 📥 Download a YouTube Video

```bash
yt-fetcher "https://www.youtube.com/watch?v=abc123"
```

### 🎧 Download as MP3 (audio only)

```bash
yt-fetcher -a "https://www.youtube.com/watch?v=abc123"
```

### 📁 Save to a custom folder

```bash
yt-fetcher -p "downloads/music" "https://www.youtube.com/watch?v=abc123"
```

---

## 🛠️ Command-Line Options

| Flag            | Description                       |
|-----------------|-----------------------------------|
| `url`           | The YouTube video URL (in quotes) |
| `-a`, `--audio` | Download audio only as MP3        |
| `-p`, `--path`  | Set download directory            |

---

## 🔐 License

MIT © Rojan Karki

---

```
youtube downloader, mp3 downloader, youtube video downloader CLI, yt-dlp frontend, python youtube downloader, terminal youtube mp3, open source youtube download script, yt-fetcher-new pip, download youtube from command line
```

---
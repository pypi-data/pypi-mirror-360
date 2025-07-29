# YT-CHAP

**yt-chap** is a simple CLI tool to view YouTube video chapters in a clean, human-readable format.

---

## 🚀 Features

- Parses YouTube chapter metadata using `yt-dlp`
- Displays output in table format (Start, End, Duration, Title)
- Falls back to a single "Full Video" view if no chapters exist
- Lightweight and terminal-friendly
- Includes `--version` / `-v` flag for author and version info

---

## 📦 Installation

```bash
pip install .
```

---

## 📄 Usage

```bash
yt-chap https://youtu.be/VIDEO_ID
```

**Example Output:**

```
No. | Start    | End      | Duration | Title
----|----------|----------|----------|-------------------------
1   | 00:00:00 | 00:02:05 | 00:02:05 | Introduction
2   | 00:02:05 | 00:10:30 | 00:08:25 | What is Programming?
...
```

To view version and author info:

```bash
yt-chap --version
```

---

## 🔧 Requirements

- Python 3.6+
- `yt-dlp` installed (automatically included)

---

## 👤 Author

Mallik Mohammad Musaddiq  
GitHub: [mallikmusaddiq1/yt-chap](https://github.com/mallikmusaddiq1/yt-chap)  
Email: mallikmusaddiq1@gmail.com

---

## 📜 License

MIT License — see [LICENSE](LICENSE) file.

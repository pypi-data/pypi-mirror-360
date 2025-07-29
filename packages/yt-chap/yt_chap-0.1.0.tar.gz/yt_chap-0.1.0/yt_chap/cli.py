import argparse
import subprocess
import ast
import sys

__version__ = "0.1.0"
__author__ = "Mallik Mohammad Musaddiq"
__email__ = "mallikmusaddiq1@gmail.com"
__github__ = "https://github.com/mallikmusaddiq1/yt-chap"

def seconds_to_hms(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}"

def print_chapters(chapters, url):
    print(f"Chapters from: {url}\n")
    print(f"{'No.':<3} | {'Start':<8} | {'End':<8} | {'Duration':<8} | Title")
    print("-" * 70)

    for i, chap in enumerate(chapters, 1):
        start = seconds_to_hms(chap["start_time"])
        end = seconds_to_hms(chap["end_time"])
        duration_sec = chap["end_time"] - chap["start_time"]
        duration = seconds_to_hms(duration_sec)
        title = chap["title"]
        print(f"{i:<3} | {start:<8} | {end:<8} | {duration:<8} | {title}")

def fallback_single_chapter(url):
    print("No chapter metadata found. Showing entire video as a single block...\n")
    result = subprocess.run(['yt-dlp', '--print', 'duration', url], capture_output=True, text=True)
    try:
        duration = float(result.stdout.strip())
    except:
        print("Failed to get video duration.")
        sys.exit(1)

    chapters = [{
        "start_time": 0,
        "end_time": duration,
        "title": "Full Video"
    }]
    print_chapters(chapters, url)

def main():
    parser = argparse.ArgumentParser(
        description="yt-chap - View YouTube video chapters in human-readable format"
    )
    parser.add_argument("url", nargs="?", help="YouTube video URL")
    parser.add_argument("--version", "-v", action="store_true", help="Show version and author info")
    args = parser.parse_args()

    if args.version:
        print(f"yt-chap v{__version__}")
        print(f"Author: {__author__}")
        print(f"GitHub: {__github__}")
        print(f"Email:  {__email__}")
        sys.exit(0)

    if not args.url:
        parser.print_help()
        sys.exit(1)

    url = args.url

    result = subprocess.run(['yt-dlp', '--print', 'chapters', url], capture_output=True, text=True)

    if not result.stdout.strip():
        fallback_single_chapter(url)
        return

    try:
        chapters = ast.literal_eval(result.stdout)
        if not isinstance(chapters, list) or len(chapters) == 0:
            fallback_single_chapter(url)
        else:
            print_chapters(chapters, url)
    except Exception:
        fallback_single_chapter(url)
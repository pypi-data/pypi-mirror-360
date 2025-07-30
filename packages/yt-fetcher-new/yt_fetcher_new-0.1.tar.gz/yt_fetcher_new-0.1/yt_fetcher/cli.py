import subprocess
import argparse
import os
import sys

def download_video(url, output_dir="downloads", audio_only=False):
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')

    if audio_only:
        cmd = [
            'yt-dlp',
            '-f', 'bestaudio',
            '--extract-audio',
            '--audio-format', 'mp3',
            '-o', output_template,
            url
        ]
    else:
        cmd = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            '-o', output_template,
            url
        ]

    try:
        subprocess.run(cmd, check=True)
        print("Download completed.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='🎬 YouTube Downloader CLI (yt-dlp powered)')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-p', '--path', default='downloads', help='Download folder (default: downloads)')
    parser.add_argument('-a', '--audio', action='store_true', help='Download audio only as MP3')

    args = parser.parse_args()

    download_video(args.url, args.path, args.audio)

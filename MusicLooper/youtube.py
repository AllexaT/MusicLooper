import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import lazy_loader as lazy

yt_dlp = lazy.load("yt_dlp")


class YtdLogger:
    def __init__(self) -> None:
        self.verbose = "PML_VERBOSE" in os.environ

    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if not msg.startswith("[debug] "):
            self.info(msg)

    def info(self, msg):
        # Suppress misleading option (only applicable to yt-dlp)
        if "(pass -k to keep)" in msg:
            pass
        elif msg.startswith("[download]"):
            print(msg, end="\r")
        elif msg.startswith("[ExtractAudio]"):
            print(msg)
        elif self.verbose:
            print(msg)

    def warning(self, msg):
        if self.verbose:
            print(msg)

    def error(self, msg):
        print(msg)


class YoutubeDownloader:
    def __init__(self, url, output_path, progress_callback=None, cancel_check=None):
        self.progress_callback = progress_callback
        self.cancel_check = cancel_check
        cleaned_url = self._clean_url(url)
        
        # 建立 Download 資料夾
        download_path = os.path.join(os.path.dirname(__file__), "Download")
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        
        ydl_opts = {
            "logger": YtdLogger(),
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "SponsorBlock", "when": "pre_process"},
                {  # Skips all unrelated/non-music sections for youtube
                    "key": "ModifyChapters",
                    "remove_sponsor_segments": [
                        "sponsor",
                        "selfpromo",
                        "interaction",
                        "intro",
                        "outro",
                        "preview",
                        "music_offtopic",
                        "filler",
                    ],
                },
                {  # Extracts audio using ffmpeg
                    "key": "FFmpegExtractAudio",
                },
            ],
            # 修改下載路徑到 Download 資料夾
            "paths": {"home": download_path, "temp": download_path},
            "progress_hooks": [self.progress_hook],
            "postprocessor_hooks": [self.postprocessor_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                self.error_code = ydl.download([cleaned_url])
            except Exception as e:
                if self.cancel_check and self.cancel_check():
                    self.error_code = 1
                else:
                    raise e

    def _clean_url(self, url):
        """Remove playlist-related parameters from YouTube URL."""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Remove playlist-related parameters
        query_params.pop('list', None)
        query_params.pop('index', None)
        
        # Rebuild query string
        cleaned_query = urlencode(query_params, doseq=True)
        
        # Reconstruct URL
        cleaned = parsed._replace(query=cleaned_query)
        return urlunparse(cleaned)

    def progress_hook(self, d):
        if self.cancel_check and self.cancel_check():
            raise Exception("Download cancelled")
            
        if d["status"] == "downloading":
            if self.progress_callback:
                try:
                    total = d.get("total_bytes", 0)
                    downloaded = d.get("downloaded_bytes", 0)
                    speed = d.get("speed", 0)
                    
                    # 轉換大小為 MB
                    downloaded_mb = downloaded / 1024 / 1024
                    total_mb = total / 1024 / 1024 if total > 0 else 0
                    speed_mb = speed / 1024 / 1024 if speed else 0
                    
                    if total > 0:
                        progress = (downloaded / total) * 100
                        status = f"下載中... {downloaded_mb:.1f}MB / {total_mb:.1f}MB ({speed_mb:.1f} MB/s)"
                    else:
                        progress = 0
                        status = f"下載中... {downloaded_mb:.1f}MB ({speed_mb:.1f} MB/s)"
                        
                    self.progress_callback(progress, status)
                except Exception:
                    pass
        elif d["status"] == "finished":
            if self.progress_callback:
                self.progress_callback(100, "下載完成，正在處理中...")
            print("\nDone downloading, now post-processing...")

    def postprocessor_hook(self, d):
        if d["status"] == "started":
            if self.progress_callback:
                self.progress_callback(100, f"正在處理: {d.get('postprocessor', '未知步驟')}")
        elif d["status"] == "finished":
            self.filepath = d["info_dict"].get("filepath")
            if self.progress_callback:
                self.progress_callback(100, "處理完成！")

"""General utility functions."""
import os
from typing import Optional

from youtube import YoutubeDownloader


def get_outputdir(path: str, output_dir: Optional[str] = None) -> str:
    """Returns the absolute output directory path to use for all export outputs.

    Args:
        path (str): The path of the file or directory being processed.
        output_dir (str, optional): The output directory to use. If None, will append the directory 'LooperOutput' in the path provided.

    Returns:
        str: The path to the output directory.
    """
    if os.path.isdir(path):
        default_out = os.path.join(path, "LooperOutput")
    else:
        default_out = os.path.join(os.path.dirname(path), "LooperOutput")
    return os.path.abspath(default_out) if output_dir is None else os.path.abspath(output_dir)

def mk_outputdir(path: str, output_dir: Optional[str] = None) -> str:
    """Creates the output directory in the `path` provided (if it does not exists) and returns the output directory path.

    Args:
        path (str): The path of the file or directory being processed.
        output_dir (str, optional): The output directory to use. If None, will create the directory 'LooperOutput' in the path provided.

    Returns:
        str: The path to the output directory.
    """
    output_dir_to_use = get_outputdir(path, output_dir)
    if not os.path.exists(output_dir_to_use):
        os.mkdir(output_dir_to_use)
    return output_dir_to_use


def download_audio(url, output_path, progress_callback=None, cancel_check=None):
    """下載 YouTube 音訊
    
    Args:
        url: YouTube URL
        output_path: 輸出目錄路徑
        progress_callback: 進度回調函數
        cancel_check: 取消檢查函數，返回 True 表示要取消下載
    """
    downloader = YoutubeDownloader(
        url, 
        output_path, 
        progress_callback=progress_callback,
        cancel_check=cancel_check
    )
    if downloader.error_code != 0 and not (cancel_check and cancel_check()):
        raise Exception("下載失敗")
    return downloader.filepath

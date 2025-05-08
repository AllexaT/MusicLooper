import logging
import os
import sys
from typing import List, Optional, Tuple, Literal

from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table

from analysis import LoopPair 
from console import rich_console
from core import MusicLooper
from exceptions import AudioLoadError, LoopNotFoundError
from memory_utils import MemoryAnalyzer


class LoopHandler:
    def __init__(
        self,
        *,
        path: str,
        min_duration_multiplier: float,
        min_loop_duration: Optional[float] = None,
        max_loop_duration: Optional[float] = None,
        approx_loop_position: Optional[tuple] = None,
        brute_force: bool = False,
        disable_pruning: bool = False,
        **kwargs,
    ):
        if approx_loop_position is not None:
            self.approx_loop_start = approx_loop_position[0]
            self.approx_loop_end = approx_loop_position[1]
        else:
            self.approx_loop_start = None
            self.approx_loop_end = None

        self._musiclooper = MusicLooper(filepath=path)
        self.gui_min_duration_multiplier = min_duration_multiplier # 儲存來自GUI的設定

        logging.info(f"Loaded \"{path}\". Analyzing...")

        loop_pairs_result = self.musiclooper.find_loop_pairs(
            min_duration_multiplier=min_duration_multiplier, # GUI值傳給核心決策
            min_loop_duration=min_loop_duration,
            max_loop_duration=max_loop_duration,
            approx_loop_start=self.approx_loop_start,
            approx_loop_end=self.approx_loop_end,
            brute_force=brute_force,
            disable_pruning=disable_pruning,
        )
        # 檢查是否需要啟用特殊分析模式
        if isinstance(loop_pairs_result, list) and len(loop_pairs_result) == 1:
            if loop_pairs_result[0] == "SMART_BATCH_ANALYSIS":
                logging.info("[系統] 啟用智能分析（僅低解析度全局）...")
                self.loop_pair_list = self.smart_batch_analysis(self._musiclooper.mlaudio)
            elif loop_pairs_result[0] == "ORIGINAL_SCORE_ONLY":
                logging.info("[系統] 啟用只計算 original_score 的省記憶體分析...")
                self.loop_pair_list = self.original_score_only_analysis(self._musiclooper.mlaudio)
            else:
                # 理論上不應該到達這裡，因為 core.py 的 find_loop_pairs 要麼返回 LoopPair 列表，要麼返回特殊標記
                self.loop_pair_list = [] 
        else:
            self.loop_pair_list = loop_pairs_result
            
        self.interactive_mode = "PML_INTERACTIVE_MODE" in os.environ
        self.in_samples = "PML_DISPLAY_SAMPLES" in os.environ

    def get_all_loop_pairs(self) -> List[LoopPair]:
        """
        Returns the discovered loop points of an audio file as a list of LoopPair objects
        """
        return self.loop_pair_list

    @property
    def musiclooper(self) -> MusicLooper:
        """Returns the handler's `MusicLooper` instance."""
        return self._musiclooper
    
    def format_time(self, samples: int, in_samples: bool = False):
        return samples if in_samples else self.musiclooper.samples_to_ftime(samples)

    def play_looping(self, loop_start: int, loop_end: int):
        self.musiclooper.play_looping(loop_start, loop_end)

    def choose_loop_pair(self, interactive_mode=False):
        index = 0
        if self.loop_pair_list and interactive_mode:
            index = self.interactive_handler()

        return self.loop_pair_list[index]

    def interactive_handler(self, show_top=25):
        preview_looper = self.musiclooper
        total_candidates = len(self.loop_pair_list)
        more_prompt_message = "\nEnter 'more' to display additional loop points, 'all' to display all of them, or 'reset' to display the default amount." if show_top < total_candidates else ""
        rich_console.print()
        table = Table(title=f"Discovered loop points ({min(show_top, total_candidates)}/{total_candidates} displayed)", caption=more_prompt_message)
        table.add_column("Index", justify="right", style="cyan", no_wrap=True)
        table.add_column("Loop Start", style="magenta")
        table.add_column("Loop End", style="green")
        table.add_column("Length", style="white")
        table.add_column("Note Distance", style="yellow")
        table.add_column("Loudness Difference", style="blue")
        table.add_column("Score", justify="right", style="red")

        for idx, pair in enumerate(self.loop_pair_list[:show_top]):
            start_time = (
                pair.loop_start
                if self.in_samples
                else preview_looper.samples_to_ftime(pair.loop_start)
            )
            end_time = (
                pair.loop_end
                if self.in_samples
                else preview_looper.samples_to_ftime(pair.loop_end)
            )
            length = (
                pair.loop_end - pair.loop_start
                if self.in_samples
                else preview_looper.samples_to_ftime(pair.loop_end - pair.loop_start)
            )
            score = pair.score
            loudness_difference = pair.loudness_difference
            note_distance = pair.note_distance
            table.add_row(
                str(idx),
                str(start_time),
                str(end_time),
                str(length),
                f"{note_distance:.4f}",
                f"{loudness_difference:.4f}",
                f"{score:.2%}",
            )

        rich_console.print(table)
        rich_console.print()

        def get_user_input():
            try:
                num_input = rich_console.input("Enter the index number for the loop you'd like to use (append [cyan]p[/] to preview; e.g. [cyan]0p[/]):")
                idx = 0
                preview = False

                if num_input == "more":
                    self.interactive_handler(show_top=show_top * 2)
                if num_input == "all":
                    self.interactive_handler(show_top=total_candidates)
                if num_input == "reset":
                    self.interactive_handler()

                if num_input[-1] == "p":
                    idx = int(num_input[:-1])
                    preview = True
                else:
                    idx = int(num_input)

                if not 0 <= idx < len(self.loop_pair_list):
                    raise IndexError

                if preview:
                    rich_console.print(f"Previewing loop [cyan]#{idx}[/] | (Press [red]Ctrl+C[/] to stop looping):")
                    loop_start = self.loop_pair_list[idx].loop_start
                    loop_end = self.loop_pair_list[idx].loop_end
                    # start preview 5 seconds before the looping point
                    offset = preview_looper.seconds_to_samples(5)
                    preview_offset = loop_end - offset if loop_end - offset > 0 else 0
                    preview_looper.play_looping(loop_start, loop_end, start_from=preview_offset)
                    return get_user_input()
                else:
                    return idx

            except (ValueError, IndexError):
                rich_console.print(f"Please enter a number within the range [0,{len(self.loop_pair_list)-1}].")
                return get_user_input()

        try:
            selected_index = get_user_input()

            if selected_index is None:
                rich_console.print("[red]Please select a valid number.[/]")
                return get_user_input()

            return selected_index
        except KeyboardInterrupt:
            rich_console.print("\n[red]Operation terminated by user. Exiting.[/]")
            sys.exit()

    def smart_batch_analysis(self, mlaudio):
        """智能分析流程（僅低解析度全局分析）：
        1. 對降採樣的全局音訊進行分析以尋找迴圈點。
        2. 如果未找到，則回退到 original_score_only_analysis。
        3. 回傳找到的 LoopPair list。
        """
        import librosa
        import numpy as np
        from analysis import find_best_loop_points, LoopPair, LoopNotFoundError
        import logging
        logging.info("[系統] 啟動低解析度全局分析...")
        
        # 計算最佳降採樣因子
        base_downsample_factor = 4
        target_effective_multiplier = 0.8  # 目標有效乘數，確保小於1.0
        
        # 根據 gui_min_duration_multiplier 自適應調整降採樣因子
        downsample_factor = min(
            base_downsample_factor,
            int(target_effective_multiplier / self.gui_min_duration_multiplier)
        )
        
        # 確保降採樣因子至少為1
        downsample_factor = max(1, downsample_factor)
        
        logging.info(f"[系統] 智能模式：使用降採樣因子 {downsample_factor}")
        
        if downsample_factor == 1:
            logging.info("[系統] 智能模式：由於參數設置，跳過降採樣直接進行 original_score_only 分析...")
            return self.original_score_only_analysis(mlaudio)
        
        downsampled_audio_data = librosa.resample(mlaudio.audio, orig_sr=mlaudio.rate, target_sr=mlaudio.rate // downsample_factor)
        global_mlaudio = type(mlaudio)(mlaudio.filepath)
        global_mlaudio.audio = downsampled_audio_data
        global_mlaudio.rate = mlaudio.rate // downsample_factor
        global_mlaudio.total_duration = mlaudio.total_duration / downsample_factor
        if mlaudio.audio.ndim == 1:
            global_mlaudio.n_channels = 1
        else:
            original_channels = mlaudio.audio.shape[0] if mlaudio.audio.shape[0] == 1 or mlaudio.audio.shape[0] == 2 else mlaudio.audio.shape[1]
            global_mlaudio.n_channels = original_channels
            if global_mlaudio.audio.ndim == 1 and original_channels > 1:
                 global_mlaudio.audio = np.tile(global_mlaudio.audio[:, np.newaxis], original_channels)
            elif global_mlaudio.audio.ndim > 1 and global_mlaudio.audio.shape[0] != original_channels and global_mlaudio.audio.shape[1] == original_channels:
                 global_mlaudio.audio = global_mlaudio.audio.T

        global_loop_pairs = []
        
        # 計算傳遞給 find_best_loop_points 的有效乘數
        effective_multiplier_for_global = self.gui_min_duration_multiplier * downsample_factor
        logging.info(f"[系統] 智能模式：原始 min_duration_multiplier: {self.gui_min_duration_multiplier}")
        logging.info(f"[系統] 智能模式：downsample_factor: {downsample_factor}")
        logging.info(f"[系統] 智能模式：用於低解析度分析的 effective_multiplier: {effective_multiplier_for_global}")

        try:
            raw_global_pairs = find_best_loop_points(
                global_mlaudio,
                min_duration_multiplier=effective_multiplier_for_global,
            )
            logging.info(f"[系統] 智能模式：find_best_loop_points (全局低解析度) 返回了 {len(raw_global_pairs)} 個原始候選點。")
            
            global_loop_pairs = []
            for p_adjust in raw_global_pairs:
                p_adjusted_for_original_sr = LoopPair(
                    _loop_start_frame_idx = int(p_adjust._loop_start_frame_idx * downsample_factor),
                    _loop_end_frame_idx = int(p_adjust._loop_end_frame_idx * downsample_factor),
                    note_distance = p_adjust.note_distance,
                    loudness_difference = p_adjust.loudness_difference,
                    structure_score = p_adjust.structure_score,
                    chord_score = p_adjust.chord_score,
                    mfcc_score = p_adjust.mfcc_score,
                    score = p_adjust.score,
                    original_score= getattr(p_adjust, 'original_score', p_adjust.score)
                )
                p_adjusted_for_original_sr.loop_start = mlaudio.frames_to_samples(p_adjusted_for_original_sr._loop_start_frame_idx)
                p_adjusted_for_original_sr.loop_end = mlaudio.frames_to_samples(p_adjusted_for_original_sr._loop_end_frame_idx)
                global_loop_pairs.append(p_adjusted_for_original_sr)

            logging.info(f"[系統] 智能模式：低解析度全局分析找到並轉換了 {len(global_loop_pairs)} 個迴圈點。")
        except LoopNotFoundError:
            logging.info("[系統] 智能模式：低解析度全局分析未找到迴圈點，嘗試 original_score_only 分析...")
            return self.original_score_only_analysis(mlaudio)
        except Exception as e:
            logging.error(f"[系統] 智能模式：低解析度全局分析時發生錯誤: {e}", exc_info=True)
            return self.original_score_only_analysis(mlaudio)

        if not global_loop_pairs:
            logging.info("[系統] 智能模式：低解析度全局分析未找到任何迴圈點，嘗試 original_score_only 分析...")
            return self.original_score_only_analysis(mlaudio)

        unique = {}
        for p in global_loop_pairs:
            key = (p.loop_start, p.loop_end)
            if key not in unique or p.score > unique[key].score: 
                unique[key] = p
        merged_pairs = list(unique.values())
        merged_pairs.sort(key=lambda x: x.score, reverse=True)
        
        logging.info(f"[系統] 智能模式分析完成，總共找到 {len(merged_pairs)} 個迴圈點。")
        return merged_pairs

    def original_score_only_analysis(self, mlaudio):
        """只計算 original_score 的省記憶體分析流程"""
        import numpy as np
        from analysis import _analyze_audio, _find_candidate_pairs, LoopPair, _calculate_loop_score, _prune_candidates
        import logging
        logging.info("[系統] 啟動只計算 original_score 的分析...")
        
        chroma, power_db, bpm, beats = _analyze_audio(mlaudio)
        
        # 使用 self.gui_min_duration_multiplier
        min_loop_duration_frames = int(self.gui_min_duration_multiplier * chroma.shape[-1])
        max_loop_duration_frames = chroma.shape[-1] # 保持最大為整個音訊（的幀數）
        
        unproc_candidate_pairs = _find_candidate_pairs(
            chroma, power_db, beats, min_loop_duration_frames, max_loop_duration_frames
        )
        
        candidate_pairs = [
            LoopPair(
                _loop_start_frame_idx=tup[0],
                _loop_end_frame_idx=tup[1],
                note_distance=tup[2],
                loudness_difference=tup[3],
            )
            for tup in unproc_candidate_pairs
        ]

        if len(candidate_pairs) >= 100:
            logging.info(f"[系統] original_score_only: 發現 {len(candidate_pairs)} 個初始候選點，進行剪枝...")
            candidate_pairs = _prune_candidates(candidate_pairs)
            logging.info(f"[系統] original_score_only: 剪枝後剩餘 {len(candidate_pairs)} 個候選點。")
        
        test_offset = 12
        weights = np.ones(test_offset)
        
        for pair in candidate_pairs:
            original_score = _calculate_loop_score(
                int(pair._loop_start_frame_idx),
                int(pair._loop_end_frame_idx),
                chroma,
                test_duration=test_offset,
                weights=weights,
            )
            pair.original_score = original_score
            pair.score = original_score
            
            if mlaudio.trim_offset > 0:
                pair._loop_start_frame_idx = int(
                    mlaudio.apply_trim_offset(pair._loop_start_frame_idx)
                )
                pair._loop_end_frame_idx = int(
                    mlaudio.apply_trim_offset(pair._loop_end_frame_idx)
                )
            pair.loop_start = mlaudio.frames_to_samples(pair._loop_start_frame_idx)
            pair.loop_end = mlaudio.frames_to_samples(pair._loop_end_frame_idx)
        
        candidate_pairs = sorted(candidate_pairs, reverse=True, key=lambda x: x.score)
        
        logging.info(f"[系統] original_score only 分析完成，總迴圈點數：{len(candidate_pairs)}")
        return candidate_pairs


class LoopExportHandler(LoopHandler):
    def __init__(
        self,
        *,
        path: str,
        min_duration_multiplier: float, # LoopExportHandler 也接收此參數
        output_dir: str,
        min_loop_duration: Optional[float] = None,
        max_loop_duration: Optional[float] = None,
        approx_loop_position: Optional[tuple] = None,
        brute_force: bool = False,
        disable_pruning: bool = False,
        split_audio: bool = False,
        format: Literal["WAV", "FLAC", "OGG", "MP3"] = "WAV",
        to_txt: bool = False,
        to_stdout: bool = False,
        fmt: Literal["SAMPLES", "SECONDS", "TIME"] = "SAMPLES",
        alt_export_top: int = 0,
        tag_names: Optional[Tuple[str, str]] = None,
        tag_offset: Optional[bool] = None,
        batch_mode: bool = False,
        extended_length: float = 0,
        fade_length: float = 0,
        disable_fade_out: bool = False,
        **kwargs,
    ):
        # LoopExportHandler 的 super().__init__ 會將 min_duration_multiplier 傳給 LoopHandler.__init__
        # 這確保了 self.gui_min_duration_multiplier 在匯出情境下也被正確設定
        super().__init__(
            path=path,
            min_duration_multiplier=min_duration_multiplier,
            min_loop_duration=min_loop_duration,
            max_loop_duration=max_loop_duration,
            approx_loop_position=approx_loop_position,
            brute_force=brute_force,
            disable_pruning=disable_pruning,
        )
        self.output_directory = output_dir
        self.split_audio = split_audio
        self.format = format
        self.to_txt = to_txt
        self.to_stdout = to_stdout
        self.fmt = fmt.lower()
        self.alt_export_top = alt_export_top
        self.tag_names = tag_names
        self.tag_offset = tag_offset
        self.batch_mode = batch_mode
        self.extended_length = extended_length
        self.disable_fade_out = disable_fade_out
        self.fade_length = fade_length

    def run(self):
        # get_all_loop_pairs() 會回傳 self.loop_pair_list，這個列表是在 __init__ 中根據模式生成的
        self.loop_pair_list = self.get_all_loop_pairs()
        if not self.loop_pair_list: # 防呆，如果分析後沒有迴圈點
             logging.error(f"分析 \"{self.musiclooper.filename}\" 後未找到任何迴圈點，無法匯出。")
             return

        chosen_loop_pair = self.choose_loop_pair(self.interactive_mode)
        loop_start = chosen_loop_pair.loop_start
        loop_end = chosen_loop_pair.loop_end
        
        if self.to_stdout:
            self.stdout_export_runner(loop_start, loop_end)

        if not os.path.exists(self.output_directory) and (self.tag_names or self.to_txt or self.split_audio or self.extended_length):
            try:
                os.makedirs(self.output_directory, exist_ok=True)
            except OSError as e:
                logging.error(f"建立輸出目錄 \"{self.output_directory}\" 失敗: {e}")
                return # 如果目錄創建失敗，則無法繼續需要目錄的操作

        if self.tag_names is not None:
            self.tag_runner(loop_start, loop_end)
        
        if self.to_txt:
            self.txt_export_runner(loop_start, loop_end)

        if self.split_audio:
            self.split_audio_runner(loop_start, loop_end)

        if self.extended_length:
            self.extend_track_runner(loop_start, loop_end)

    def split_audio_runner(self, loop_start: int, loop_end: int):
        try:
            self.musiclooper.export(
                loop_start,
                loop_end,
                format=self.format,
                output_dir=self.output_directory
            )
            message = f"Successfully exported \"{self.musiclooper.filename}\" intro/loop/outro sections to \"{self.output_directory}\""
            if self.batch_mode:
                logging.info(message)
            else:
                rich_console.print(message)
        except ValueError as e:
            logging.error(f"音訊匯出分割時發生錯誤 (可能是格式問題): {e}")
        except Exception as e:
            logging.error(f"音訊匯出分割時發生未知錯誤: {e}")


    def extend_track_runner(self, loop_start: int, loop_end: int):
        if not self.batch_mode:
            progress = Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
                console=rich_console,
                transient=True,
            )
            progress.add_task(f"Exporting an extended version of {self.musiclooper.filename}...", total=None)
            progress.start()
        try:
            output_path = self.musiclooper.extend(
                loop_start,
                loop_end,
                format=self.format,
                output_dir=self.output_directory,
                extended_length=self.extended_length,
                disable_fade_out=self.disable_fade_out,
                fade_length=self.fade_length,
            )
            message = f'Successfully exported an extended version of "{self.musiclooper.filename}" to "{output_path}"'
            if self.batch_mode:
                logging.info(message)
            else:
                if 'progress' in locals(): progress.stop()
                rich_console.print(message)
        except ValueError as e:
            logging.error(f"音訊延長匯出時發生錯誤 (可能是格式問題): {e}")
            if not self.batch_mode and 'progress' in locals(): progress.stop()
        except Exception as e:
            logging.error(f"音訊延長匯出時發生未知錯誤: {e}")
            if not self.batch_mode and 'progress' in locals(): progress.stop()


    def txt_export_runner(self, loop_start: int, loop_end: int):
        if self.alt_export_top != 0:
            self.alt_export_runner(mode="TXT")
        else:
            self.musiclooper.export_txt(
                self._fmt(loop_start),
                self._fmt(loop_end),
                output_dir=self.output_directory,
            )
            out_path = os.path.join(self.output_directory, self.musiclooper.filename + "_loop.txt") # 更改檔名以包含原檔名
            message = f'Successfully added "{self.musiclooper.filename}" loop points to "{out_path}"'
            if self.batch_mode:
                logging.info(message)
            else:
                rich_console.print(message)

    def stdout_export_runner(self, loop_start: int, loop_end: int):
        if self.alt_export_top != 0:
            self.alt_export_runner(mode="STDOUT")
        else:
            rich_console.print(
                f'\nLoop points for "{self.musiclooper.filename}":\n'
                f"LOOP_START: {self._fmt(loop_start)}\n"
                f"LOOP_END: {self._fmt(loop_end)}\n"
            )

    def alt_export_runner(self, mode: Literal["STDOUT", "TXT"]):
        pair_list_slice = (
            self.loop_pair_list
            if self.alt_export_top < 0
            or self.alt_export_top >= len(self.loop_pair_list)
            else self.loop_pair_list[: self.alt_export_top]
        )

        def fmt_line(pair: LoopPair):
            return f"{self._fmt(pair.loop_start)} {self._fmt(pair.loop_end)} {pair.note_distance:.4f} {pair.loudness_difference:.4f} {pair.score:.2%}\n" #統一格式

        formatted_lines = [fmt_line(pair) for pair in pair_list_slice]
        if mode == "STDOUT":
            rich_console.out("".join(formatted_lines), end="") # 使用join以避免多餘空格
        elif mode == "TXT":
            out_path = os.path.join(
                self.output_directory, f"{self.musiclooper.filename}.alt_export.txt"
            )
            try:
                with open(out_path, mode="w") as f:
                    f.writelines(formatted_lines)
                logging.info(f"成功將备选的 {len(formatted_lines)} 个循环点导出到 {out_path}")
            except IOError as e:
                logging.error(f"写入备选循环点到 TXT 文件 {out_path} 失败: {e}")


    def tag_runner(self, loop_start: int, loop_end: int):        
        loop_start_tag, loop_end_tag = self.tag_names
        try:
            tagged_file_path, actual_loop_start, actual_loop_end = self.musiclooper.export_tags( #接收回傳值
                loop_start,
                loop_end,
                loop_start_tag,
                loop_end_tag,
                is_offset=self.tag_offset,
                output_dir=self.output_directory,
            )
            message = f"Exported {loop_start_tag}: {self._fmt(actual_loop_start)} and {loop_end_tag}: {self._fmt(actual_loop_end)} of \"{self.musiclooper.filename}\" to a copy in \"{tagged_file_path}\"" # 使用回傳的檔名和時間
            if self.batch_mode:
                logging.info(message)
            else:
                rich_console.print(message)
        except FileNotFoundError:
             logging.error(f"標記匯出失敗：找不到 FFmpeg。請確保 FFmpeg 已安裝並在系統路徑中。")
        except Exception as e:
            logging.error(f"標記匯出時發生未知錯誤: {e}")


    def _fmt(self, samples: int):
        if self.fmt == "seconds":
            return str(self.musiclooper.samples_to_seconds(samples))
        elif self.fmt == "time":
            return str(self.musiclooper.samples_to_ftime(samples))
        else:
            return str(samples)


class BatchHandler:
    def __init__(
        self,
        *,
        path: str,
        output_dir: str,
        recursive: bool = False,
        flatten: bool = False,
        **kwargs, # kwargs 包含 min_duration_multiplier 等傳給 LoopExportHandler 的參數
    ):
        self.directory_path = os.path.abspath(path)
        self.output_directory = output_dir
        self.recursive = recursive
        self.flatten = flatten
        self.kwargs = kwargs # 這裡儲存了包括 min_duration_multiplier 在內的所有額外參數

    def run(self):
        files = self.get_files_in_directory(
            self.directory_path, recursive=self.recursive
        )

        if len(files) == 0:
            # 修正: 應為 FileNotFoundError 而不是 LoopNotFoundError
            raise FileNotFoundError(f"No files found in \"{self.directory_path}\"")

        output_dirs = (
            None
            if self.flatten
            else self.clone_file_tree_structure(files, self.output_directory)
        )

        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            MofNCompleteColumn(),
            console=rich_console,
        ) as progress:
            pbar = progress.add_task("Processing...", total=len(files))
            for file_idx, file_path in enumerate(files):
                progress.update(
                    pbar,
                    advance=1,
                    description=(
                        f"Processing \"{os.path.relpath(file_path, self.directory_path)}\""
                    ),
                )
                # self.kwargs 已經包含了 min_duration_multiplier，會正確傳遞給 LoopExportHandler
                task_kwargs = {
                    **self.kwargs, 
                    "path": file_path,
                    "output_dir": self.output_directory if self.flatten else output_dirs[file_idx]
                }
                self._batch_export_helper(**task_kwargs)

    @staticmethod
    def clone_file_tree_structure(in_files: List[str], output_directory: str) -> List[str]:
        if not in_files: #處理in_files為空列表的情況
            return []
        common_path = os.path.commonpath(in_files)
        output_dirs = [
            os.path.join(
                os.path.abspath(output_directory),
                os.path.dirname(os.path.relpath(file, start=common_path)),
            )
            for file in in_files
        ]
        for out_dir in output_dirs:
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir, exist_ok=True)
        return output_dirs

    @staticmethod
    def get_files_in_directory(dir_path: str, recursive: bool = False) -> List[str]:
        abs_dir_path = os.path.abspath(dir_path) #確保是絕對路徑
        if not os.path.isdir(abs_dir_path): #如果不是目錄則返回空
            logging.error(f"提供的路徑 \"{dir_path}\" 不是一個有效的目錄。")
            return []
        return (
            [
                os.path.join(directory, filename)
                for directory, sub_dir_list, file_list in os.walk(abs_dir_path) # 使用絕對路徑
                for filename in file_list
                if not filename.startswith('.') # 過濾隱藏檔案
            ]
            if recursive
            else [
                os.path.join(abs_dir_path, f) # 使用絕對路徑
                for f in os.listdir(abs_dir_path) # 使用絕對路徑
                if os.path.isfile(os.path.join(abs_dir_path, f)) and not f.startswith('.') # 過濾隱藏檔案
            ]
        )

    @staticmethod
    def _batch_export_helper(**kwargs):
        try:
            # LoopExportHandler 的初始化會接收 min_duration_multiplier (來自kwargs)
            # 並透過 super().__init__ 傳遞給 LoopHandler，進而設定 self.gui_min_duration_multiplier
            export_handler = LoopExportHandler(**kwargs, batch_mode=True)
            export_handler.run()
        except (AudioLoadError, LoopNotFoundError) as e: # LoopNotFoundError 也應在此處理
            logging.error(e) #改為 logging.error 以突顯錯誤
        except FileNotFoundError as e: # 捕獲上面 run 方法中可能拋出的 FileNotFoundError
            logging.error(e)
        except Exception as e:
            # 記錄更詳細的錯誤信息，包括檔案路徑（如果可用）
            file_path_info = f" for file \"{kwargs.get('path', 'Unknown')}\"" if kwargs.get('path') else ""
            logging.error(f"An unexpected error occurred during batch processing{file_path_info}: {e}", exc_info=True)

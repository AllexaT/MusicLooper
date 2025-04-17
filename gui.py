from PyQt6.QtWidgets import *
from PyQt6.QtCore import * 
from PyQt6.QtGui import *
from core import MusicLooper 
from playback import PlaybackHandler 
import sys
import os
import locale
from typing import Dict
import base64
import shutil

# 設定 FFmpeg 路徑
ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]

# 或者更完整的路徑處理:
def setup_ffmpeg():
    """檢查 FFmpeg 是否可用，按以下順序：
    1. 檢查系統 PATH
    2. 檢查工作目錄下的 ffmpeg 資料夾
    3. 都找不到時提供下載連結
    """
    # 1. 先檢查系統 PATH
    ffmpeg_path = shutil.which('ffmpeg')
    ffprobe_path = shutil.which('ffprobe')
    
    if ffmpeg_path and ffprobe_path:
        return True
        
    # 2. 檢查工作目錄下的 ffmpeg 資料夾
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(current_dir, "ffmpeg", "bin")
    
    ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe.exe")
    
    if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
        # 將 FFmpeg 路徑加入環境變數
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
        return True
    
    return False

def show_ffmpeg_error():
    """Display FFmpeg error message and ask whether to open download page"""
    # 取得系統語言設定
    try:
        current_locale = locale.getlocale()[0]
        is_chinese = current_locale and any(
            current_locale.lower().startswith(loc) 
            for loc in ['zh', 'zh_tw', 'zh_hk', 'zh_cn', 'zh_sg', 'zh_mo', 'chinese (traditional)_taiwan']
        )
    except:
        is_chinese = False

    # 根據語言選擇錯誤訊息
    if is_chinese:
        error_msg = (
            "找不到 FFmpeg。請執行以下任一操作：\n\n"
            "1. 安裝 FFmpeg 到系統並加入 PATH\n"
            "2. 在程式目錄下建立 ffmpeg 資料夾並放入執行檔\n\n"
            "是否要開啟 FFmpeg 下載頁面？"
        )
        title = "錯誤"
    else:
        error_msg = (
            "FFmpeg not found. Please do one of the following:\n\n"
            "1. Install FFmpeg to system and add to PATH\n"
            "2. Create ffmpeg folder in program directory and put executables inside\n\n"
            "Would you like to open the FFmpeg download page?"
        )
        title = "Error"

    # 顯示詢問對話框
    reply = QMessageBox.question(
        None,
        title,
        error_msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes  # 預設選項
    )
    
    # 如果使用者選擇是，則開啟下載頁面
    if reply == QMessageBox.StandardButton.Yes:
        QDesktopServices.openUrl(QUrl("https://ffmpeg.org/download.html"))
    
    # 直接結束程式
    sys.exit(1)

def create_default_icon():
    """創建預設的音樂圖示"""
    icon_data = b"""
    // ... base64 encoded icon data ...
    """
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    icon_path = os.path.join(assets_dir, "icon.ico")
    
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    if not os.path.exists(icon_path):
        with open(icon_path, "wb") as f:
            f.write(base64.b64decode(icon_data))
    
    return icon_path

# 定義語言字典
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "zh_TW": {
        "window_title": "MusicLooper",
        "file_group": "音訊檔案",
        "browse_btn": "瀏覽...", 
        "youtube_url": "輸入 YouTube 網址...",
        "download_btn": "下載",
        "settings_group": "分析設定",
        "min_duration": "最小長度比率:",
        "columns": ["起點", "終點", "長度", "分數"],
        "playback_group": "播放控制",
        "volume": "音量:",
        "export_group": "導出功能",
        "export_btn": "導出音樂",
        "error": "錯誤",
        "success": "成功",
        "export_success": "已成功導出到: {}",
        "select_file": "請選擇音訊檔案",
        "analyzing": "正在分析音訊檔案...",
        "processing": "處理中",
        "analyze_first": "請先分析音訊檔案",
        "select_loop": "請選擇要播放的迴圈點",
        "enter_youtube": "請輸入 YouTube 網址",
        "downloading": "正在下載音樂...",
        "downloading_title": "下載中",
        "download_failed": "下載失敗: {}",
        "select_loop_export": "請選擇要導出的迴圈點",
        "select_format": "選擇格式",
        "select_format_prompt": "請選擇導出格式:",
        "select_output": "選擇導出目錄",
        "exporting": "正在導出音樂...",
        "export_failed": "導出失敗: {}",
        "initializing": "初始化下載中...",
        "downloading_status": "下載中... {:.1f}MB / {:.1f}MB ({:.1f} MB/s)",
        "downloading_status_no_total": "下載中... {:.1f}MB ({:.1f} MB/s)",
        "download_complete": "下載完成，正在處理中...",
        "processing_step": "正在處理: {}",
        "processing_complete": "處理完成！",
        "cancel": "取消",
        "enhancement_options": "增強選項",
        "structure": "結構",
        "chord": "和弦",
        "mfcc": "MFCC"
    },
    "en": {
        "window_title": "MusicLooper", 
        "file_group": "Audio File",
        "browse_btn": "Browse...",
        "youtube_url": "Enter YouTube URL...",
        "download_btn": "Download",
        "settings_group": "Analysis Settings",
        "min_duration": "Min Duration Ratio",
        "columns": ["Start", "End", "Length", "Score"],
        "playback_group": "Playback Control",
        "volume": "Volume:",
        "export_group": "Export",
        "export_btn": "Export Audio",
        "error": "Error",
        "success": "Success",
        "export_success": "Successfully exported to: {}",
        "select_file": "Please select an audio file",
        "analyzing": "Analyzing audio file...", 
        "processing": "Processing",
        "analyze_first": "Please analyze an audio file first",
        "select_loop": "Please select a loop point to play",
        "enter_youtube": "Please enter a YouTube URL",
        "downloading": "Downloading audio...",
        "downloading_title": "Downloading",
        "download_failed": "Download failed: {}",
        "select_loop_export": "Please select a loop point to export",
        "select_format": "Select Format", 
        "select_format_prompt": "Select export format:",
        "select_output": "Select Output Directory",
        "exporting": "Exporting audio...",
        "export_failed": "Export failed: {}",
        "initializing": "Initializing download...",
        "downloading_status": "Downloading... {:.1f}MB / {:.1f}MB ({:.1f} MB/s)",
        "downloading_status_no_total": "Downloading... {:.1f}MB ({:.1f} MB/s)",
        "download_complete": "Download complete, processing...",
        "processing_step": "Processing: {}",
        "processing_complete": "Processing complete!",
        "cancel": "Cancel",
        "enhancement_options": "Enhance Options",
        "structure": "Struct",
        "chord": "Chord",
        "mfcc": "MFCC"
    }
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 使用系統內建音符圖示
        app_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.setWindowIcon(app_icon)
        
        # 確保 assets 資料夾存在
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
        
        # 設定應用程式圖示
        icon_path = os.path.join(assets_dir, "icon.ico")
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 使用新的建議方法取得系統語言
        try:
            # 先嘗試取得目前的 locale 設定
            current_locale = locale.getlocale()[0]
            print(f"初始 locale: {current_locale}")  # 除錯用
            
            if not current_locale:
                # 如果取不到，使用預設系統編碼
                locale.setlocale(locale.LC_ALL, '')
                current_locale = locale.getlocale()[0]
                print(f"重設後 locale: {current_locale}")  # 除錯用
                
            # 如果還是取不到，使用 Windows API
            if not current_locale:
                import ctypes
                windll = ctypes.windll.kernel32
                current_locale = locale.windows_locale[windll.GetUserDefaultUILanguage()]
                print(f"Windows API locale: {current_locale}")  # 除錯用
                
            # 檢查是否為中文系統
            is_chinese = False
            if current_locale:
                current_locale = current_locale.lower()
                #chinese_locales = ['zh', 'zh_tw', 'zh_hk', 'zh_cn', 'zh_sg', 'zh_mo']
                chinese_locales = ['zh', 'zh_tw', 'zh_hk', 'zh_cn', 'zh_sg', 'zh_mo','chinese (traditional)_taiwan']
                is_chinese = any(current_locale.startswith(loc) for loc in chinese_locales)
                
            # 設定語言
            self.locale = 'zh_TW' if is_chinese else 'en'
            print(f"最終設定語言: {self.locale}")  # 除錯用
                    
        except Exception as e:
            print(f"語言設定發生錯誤: {e}")  # 除錯用
            self.locale = 'en'
        
        self.tr = TRANSLATIONS[self.locale]
        
        self.setWindowTitle(self.tr["window_title"])
        self.setFixedSize(325, 500)
        
        self.setup_ui()
        self.music_looper = None 
        self.playback_handler = PlaybackHandler()

    def setup_ui(self):
        # 更新所有UI文字為對應語言
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 檔案選擇區
        file_group = QGroupBox(self.tr["file_group"])
        file_layout = QVBoxLayout()
        
        local_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        browse_btn = QPushButton(self.tr["browse_btn"])
        browse_btn.clicked.connect(self.browse_file)
        local_layout.addWidget(self.path_edit)
        local_layout.addWidget(browse_btn)
        
        youtube_layout = QHBoxLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText(self.tr["youtube_url"])
        download_btn = QPushButton(self.tr["download_btn"])
        download_btn.clicked.connect(self.download_youtube)
        youtube_layout.addWidget(self.url_edit)
        youtube_layout.addWidget(download_btn)
        
        file_layout.addLayout(local_layout)
        file_layout.addLayout(youtube_layout)
        file_group.setLayout(file_layout)
        
        # 參數設定區
        settings_group = QGroupBox(self.tr["settings_group"])
        settings_layout = QFormLayout()
        self.min_duration = QDoubleSpinBox()
        self.min_duration.setValue(0.35)
        settings_layout.addRow(self.tr["min_duration"], self.min_duration)
        # 增強選項勾選（水平排列，不顯示原始分數）
        self.score_checkboxes = {}
        score_hbox = QHBoxLayout()
        for key, label_key in [
            ('structure', "structure"),
            ('chord', "chord"),
            ('mfcc', "mfcc")
        ]:
            self.score_checkboxes[key] = QCheckBox(self.tr[label_key])
            self.score_checkboxes[key].setChecked(False)
            self.score_checkboxes[key].setMinimumWidth(65)
            score_hbox.addWidget(self.score_checkboxes[key])
            # 在勾選框之間添加間距，除了最後一個
            if label_key != "mfcc": # 假設 'mfcc' 是最後一個
                score_hbox.addSpacing(0) # 添加 15 像素間距
        score_hbox.addStretch(1) # 將空白推到右邊
        settings_layout.addRow(self.tr["enhancement_options"], score_hbox)
        settings_group.setLayout(settings_layout)
        # 綁定勾選事件
        for cb in self.score_checkboxes.values():
            cb.stateChanged.connect(self.update_scores_and_table)
        
        # 結果列表 - 添加選擇功能
        self.results = QTableWidget()
        self.results.setColumnCount(4)
        self.results.setHorizontalHeaderLabels(self.tr["columns"])
        self.results.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # 整行選擇
        self.results.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)     # 單行選擇
        
        # 顯示垂直標題(從0開始)
        self.results.verticalHeader().setVisible(True)
        
        # 啟用排序功能
        self.results.setSortingEnabled(True)
        
        # 設定每個欄位的寬度
        self.results.setColumnWidth(0, 65)  # 起點
        self.results.setColumnWidth(1, 65)  # 終點
        self.results.setColumnWidth(2, 65)  # 長度
        self.results.setColumnWidth(3, 65)  # 分數
        
        # 設定垂直標題的寬度
        self.results.verticalHeader().setFixedWidth(33)
        # 設定垂直標題的對齊方式
        self.results.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 設定表格的排序指示器方向
        self.results.setSortingEnabled(True)
        
        # 添加選擇變更事件處理
        self.results.itemSelectionChanged.connect(self.on_selection_changed)
        
        # 播放控制區
        playback_group = QGroupBox(self.tr["playback_group"])
        playback_layout = QVBoxLayout()
        
        # 播放控制和時間滑動條
        time_layout = QHBoxLayout()
        
        # 播放/暫停按鈕 - 使用圖示
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(24, 24)  # 設定固定大小
        play_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        pause_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        self.play_btn.setIcon(play_icon)
        self.play_btn.clicked.connect(self.toggle_playback)
        
        self.current_time_label = QLabel("00:00")
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 100)
        self.total_time_label = QLabel("00:00")
        
        time_layout.addWidget(self.play_btn)
        time_layout.addWidget(self.current_time_label)
        time_layout.addWidget(self.time_slider)
        time_layout.addWidget(self.total_time_label)
        playback_layout.addLayout(time_layout)
        
        # 新增時間滑動條的事件處理
        self.time_slider.sliderPressed.connect(self.on_slider_pressed)
        self.time_slider.sliderReleased.connect(self.on_slider_released)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_label = QLabel(self.tr["volume"])
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(10)
        self.volume_slider.valueChanged.connect(self.volume_changed)
        self.volume_value = QLabel("10%")
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_value)
        playback_layout.addLayout(volume_layout)
        
        playback_group.setLayout(playback_layout)

        # 組裝介面
        layout.addWidget(file_group)
        layout.addWidget(settings_group)
        layout.addWidget(self.results)
        layout.addWidget(playback_group)

        # 新增導出區域
        export_group = QGroupBox(self.tr["export_group"])
        export_layout = QHBoxLayout()
        
        export_btn = QPushButton(self.tr["export_btn"])
        export_btn.clicked.connect(self.export_audio)
        export_layout.addWidget(export_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)  # 加到主布局中

    def volume_changed(self, value):
        """處理音量變更"""
        self.volume_value.setText(f"{value}%")
        if self.playback_handler:
            # 將百分比轉換為 0-1 的浮點數
            volume = value / 100.0
            self.playback_handler.set_volume(volume)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr["select_file"], "", 
            "音訊檔案 (*.mp3 *.wav *.ogg *.flac *.opus)")
        if path:
            self.path_edit.setText(path)
            # 選擇檔案後自動分析
            self.analyze()

    def analyze(self):
        if not self.path_edit.text():
            self.show_error(self.tr["select_file"])
            return
            
        try:
            # 如果正在播放音樂,先停止播放
            if self.playback_handler and self.playback_handler.is_playing:
                self.stop_playback()
            # 建立進度對話框 
            progress = QProgressDialog(self.tr["analyzing"], None, 0, 100, self)
            progress.setWindowTitle(self.tr["processing"])
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setAutoClose(True)
            progress.setAutoReset(True)
            progress.setMinimumDuration(0)
            
            # 使用 blockSignals 避免重複繪製
            self.results.blockSignals(True)
            
            try:
                # 模擬進度
                for i in range(101):
                    progress.setValue(i)
                    QApplication.processEvents()
                    if i == 30:
                        self.music_looper = MusicLooper(self.path_edit.text())
                    if i == 60:
                        # 原始分數必定納入，進階分數依勾選
                        score_items = ['structure', 'chord', 'mfcc']
                        checked = ['original'] + [k for k in score_items if self.score_checkboxes[k].isChecked()]
                        weight = 1.0 / len(checked)
                        score_weights = {k: (weight if k in checked else 0.0) for k in ['original'] + score_items}
                        loops = self.music_looper.find_loop_pairs(
                            min_duration_multiplier=self.min_duration.value(),
                            score_weights=score_weights
                        )
                        self.all_loops = loops  # 儲存所有 LoopPair
                self.update_scores_and_table()
            finally:
                self.results.blockSignals(False)
        except Exception as e:
            self.show_error(str(e))

    def update_scores_and_table(self):
        # 取得勾選狀態
        score_items = ['structure', 'chord', 'mfcc']
        checked = ['original'] + [k for k in score_items if self.score_checkboxes[k].isChecked()]
        weight = 1.0 / len(checked)
        score_weights = {k: (weight if k in checked else 0.0) for k in ['original'] + score_items}
        # 重新加權分數
        for loop in getattr(self, 'all_loops', []):
            loop.score = (
                score_weights['original'] * getattr(loop, 'original_score', 0) +
                score_weights['structure'] * getattr(loop, 'structure_score', 0) +
                score_weights['chord'] * getattr(loop, 'chord_score', 0) +
                score_weights['mfcc'] * getattr(loop, 'mfcc_score', 0)
            )
        # 重新排序
        sorted_loops = sorted(enumerate(getattr(self, 'all_loops', [])), key=lambda x: x[1].score, reverse=True)
        self.results.setSortingEnabled(False)
        try:
            self.results.setRowCount(len(sorted_loops))
            for rank, (original_index, loop) in enumerate(sorted_loops):
                start_time = self.music_looper.samples_to_seconds(loop.loop_start)
                end_time = self.music_looper.samples_to_seconds(loop.loop_end)
                duration = end_time - start_time
                items = [
                    NumericTableItem(f"{start_time:.2f}"),
                    NumericTableItem(f"{end_time:.2f}"),
                    NumericTableItem(f"{duration:.2f}"),
                    NumericTableItem(f"{loop.score:.2%}")
                ]
                for col, item in enumerate(items):
                    self.results.setItem(rank, col, item)
                self.results.setVerticalHeaderItem(rank, QTableWidgetItem(str(rank)))
        finally:
            self.results.setSortingEnabled(True)
            self.results.viewport().update()

    def format_time(self, seconds):
        """將秒數格式化為 mm:ss 格式"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def on_slider_pressed(self):
        """滑動條被按下時暫停更新"""
        if self.playback_handler.is_playing:
            self.slider_was_playing = True
            self.playback_handler.pause()
        else:
            self.slider_was_playing = False

    def on_slider_released(self):
        """滑動條釋放時跳轉到新位置"""
        if not self.music_looper:
            return
            
        selected = self.results.selectedItems()
        if not selected:
            return
            
        row = selected[0].row()
        start_seconds = float(self.results.item(row, 0).text())
        end_seconds = float(self.results.item(row, 1).text())
        duration = end_seconds - start_seconds
        
        # 計算新的播放位置
        position = start_seconds + (duration * self.time_slider.value() / 100)
        new_start_samples = self.music_looper.seconds_to_samples(position)
        
        # 如果之前在播放就繼續播放
        if self.slider_was_playing:
            self.playback_handler.stop()
            self.playback_handler.play_looping(
                self.music_looper.mlaudio.playback_audio,
                self.music_looper.mlaudio.rate,
                self.music_looper.mlaudio.n_channels,
                self.music_looper.seconds_to_samples(start_seconds),
                self.music_looper.seconds_to_samples(end_seconds),
                start_from=new_start_samples,
                progress_callback=self.update_progress
            )
            # 切換為暫停圖示
            pause_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            self.play_btn.setIcon(pause_icon)

    def update_progress(self, frame, loop_count):
        """更新時間滑動條"""
        try:
            # 檢查滑動條是否還存在
            if not self.time_slider or not hasattr(self, 'time_slider'):
                return
                
            # 避免在滑動時更新
            if self.time_slider.isSliderDown():
                return
                
            selected = self.results.selectedItems()
            if not selected:
                return
                
            row = selected[0].row()
            start_seconds = float(self.results.item(row, 0).text())
            end_seconds = float(self.results.item(row, 1).text())
            
            current_time = (frame - self.music_looper.seconds_to_samples(start_seconds)) / self.music_looper.mlaudio.rate
            total_time = end_seconds - start_seconds
            
            if current_time >= 0:
                # 使用 blockSignals 避免重複觸發事件
                self.time_slider.blockSignals(True)
                try:
                    # 更新時間滑動條
                    progress_percent = min(100, (current_time / total_time) * 100)
                    self.time_slider.setValue(int(progress_percent))
                    
                    # 更新時間標籤
                    self.current_time_label.setText(self.format_time(current_time))
                    self.total_time_label.setText(self.format_time(total_time))
                finally:
                    self.time_slider.blockSignals(False)
                    
        except (RuntimeError, AttributeError):
            # 忽略已刪除的 Qt 物件錯誤
            pass
        except Exception as e:
            # 記錄其他錯誤
            print(f"更新進度時發生錯誤: {e}")

    def toggle_playback(self):
        if not self.music_looper:
            self.show_error(self.tr["analyze_first"])
            return
                
        selected = self.results.selectedItems()
        if not selected:
            self.show_error(self.tr["select_loop"])
            return

        if not self.playback_handler.is_playing:
            # 開始播放時切換為暫停圖示
            pause_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            self.play_btn.setIcon(pause_icon)
            row = selected[0].row()
            # 更新視窗標題顯示當前播放的音樂ID
            self.setWindowTitle(f"MusicLooper - PLAY#{row}")
            
            start_seconds = float(self.results.item(row, 0).text())
            end_seconds = float(self.results.item(row, 1).text())
            
            try:
                start_samples = self.music_looper.seconds_to_samples(start_seconds)
                end_samples = self.music_looper.seconds_to_samples(end_seconds)
                
                # 播放音訊並設定初始音量
                volume = self.volume_slider.value() / 100.0
                self.playback_handler.set_volume(volume)
                
                # 設置初始時間標籤
                self.current_time_label.setText("00:00")
                duration = end_seconds - start_seconds
                self.total_time_label.setText(self.format_time(duration))
                
                # 使用新的進度回調
                self.playback_handler.play_looping(
                    self.music_looper.mlaudio.playback_audio,
                    self.music_looper.mlaudio.rate,
                    self.music_looper.mlaudio.n_channels,
                    start_samples,
                    end_samples,  
                    start_from=start_samples,
                    progress_callback=self.update_progress
                )
                
            except Exception as e:
                self.show_error(str(e))
        else:
            if self.playback_handler.is_paused:
                # 從暫停恢復時顯示暫停圖示
                pause_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
                self.play_btn.setIcon(pause_icon)
                self.playback_handler.resume()
            else:
                # 暫停時顯示播放圖示
                play_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
                self.play_btn.setIcon(play_icon)
                self.playback_handler.pause()

    def stop_playback(self):
        """停止播放"""
        if self.playback_handler.is_playing:
            self.playback_handler.stop()
            # 切換回播放圖示
            play_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            self.play_btn.setIcon(play_icon)
            
            # 重置時間標籤和滑動條
            self.current_time_label.setText("00:00")
            self.total_time_label.setText("00:00")
            self.time_slider.setValue(0)
            
            # 重置視窗標題
            self.setWindowTitle("MusicLooper")

    def update_download_progress(self, progress, status):
        """更新下載進度對話框"""
        if hasattr(self, 'download_progress'):
            self.download_progress.setValue(int(progress))
            if status:
                # 使用翻譯的狀態訊息
                if "MB" in status:  # 這是下載進度狀態
                    try:
                        if "/" in status:  # 有總大小
                            downloaded = float(status.split("MB")[0].split("...")[-1])
                            total = float(status.split("/")[-1].split("MB")[0])
                            speed = float(status.split("(")[-1].split(" MB")[0])
                            status = self.tr["downloading_status"].format(downloaded, total, speed)
                        else:  # 沒有總大小
                            downloaded = float(status.split("MB")[0].split("...")[-1])
                            speed = float(status.split("(")[-1].split(" MB")[0])
                            status = self.tr["downloading_status_no_total"].format(downloaded, speed)
                    except:
                        pass
                elif "下載完成" in status or "Download complete" in status:
                    status = self.tr["download_complete"]
                elif "正在處理" in status or "Processing" in status:
                    step = status.split(":")[-1].strip()
                    status = self.tr["processing_step"].format(step)
                elif "處理完成" in status or "complete" in status:
                    status = self.tr["processing_complete"]
                
                self.download_progress.setLabelText(status)

    def download_youtube(self):
        url = self.url_edit.text().strip()
        if not url:
            self.show_error(self.tr["enter_youtube"])
            return
            
        try:
            # 先顯示初始化進度對話框，添加取消按鈕
            self.download_progress = QProgressDialog(
                self.tr["initializing"],
                self.tr.get("cancel", "Cancel"),  # 添加取消按鈕
                0, 100, self
            )
            self.download_progress.setWindowTitle(self.tr["downloading_title"])
            self.download_progress.setWindowModality(Qt.WindowModality.WindowModal)
            self.download_progress.setAutoClose(True)
            self.download_progress.setAutoReset(True)
            self.download_progress.setMinimumDuration(0)
            self.download_progress.setValue(0)
            
            # 連接取消信號
            self.download_cancelled = False
            self.download_progress.canceled.connect(self.cancel_download)
            
            self.download_progress.show()
            QApplication.processEvents()
            
            # 開始下載
            import tempfile
            from utils import download_audio
            
            if not self.download_cancelled:
                output_path = download_audio(
                    url, 
                    tempfile.gettempdir(),
                    progress_callback=self.update_download_progress,
                    cancel_check=lambda: self.download_cancelled  # 傳入取消檢查函數
                )
                
                if output_path and not self.download_cancelled:
                    self.path_edit.setText(output_path)
                    self.analyze()
                    self.url_edit.clear()
            
        except Exception as e:
            if not self.download_cancelled:  # 只在非取消狀態下顯示錯誤
                self.show_error(self.tr["download_failed"].format(str(e)))
        finally:
            if hasattr(self, 'download_progress'):
                self.download_progress.close()

    def cancel_download(self):
        """取消下載"""
        self.download_cancelled = True

    def export_audio(self):
        if not self.music_looper:
            self.show_error(self.tr["analyze_first"])
            return
            
        selected = self.results.selectedItems()
        if not selected:
            self.show_error(self.tr["select_loop_export"])
            return
            
        try:
            # 讓使用者選擇導出目錄和格式
            formats = ["WAV", "MP3", "OGG", "FLAC"]
            format, ok = QInputDialog.getItem(
                self,
                self.tr["select_format"],
                self.tr["select_format_prompt"],
                formats,
                0,  # 預設選擇WAV
                False
            )
            
            if not ok:
                return
                
            # 選擇導出目錄
            output_dir = QFileDialog.getExistingDirectory(
                self,
                self.tr["select_output"],
                ""
            )
            
            if not output_dir:
                return
                
            # 顯示進度對話框
            progress = QProgressDialog(self.tr["exporting"], None, 0, 100, self)
            progress.setWindowTitle(self.tr["processing"])
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            
            # 取得選擇的迴圈點
            row = selected[0].row()
            start_seconds = float(self.results.item(row, 0).text())
            end_seconds = float(self.results.item(row, 1).text())
            
            start_samples = self.music_looper.seconds_to_samples(start_seconds)
            end_samples = self.music_looper.seconds_to_samples(end_seconds)
            
            # 更新進度
            progress.setValue(30)
            QApplication.processEvents()
            
            # 導出音樂
            try:
                self.music_looper.export(
                    start_samples,
                    end_samples,
                    format=format,
                    output_dir=output_dir
                )
                
                progress.setValue(100)
                # 使用翻譯後的訊息格式
                success_msg = self.tr["export_success"].format(output_dir)
                self.show_success(success_msg)
                
            except Exception as e:
                self.show_error(self.tr["export_failed"].format(str(e)))
                
        except Exception as e:
            self.show_error(str(e))

    def closeEvent(self, event):
        """關閉視窗時的處理"""
        try:
            # 停止播放
            if self.playback_handler:
                self.playback_handler.stop()
                
            # 等待所有回調完成
            QApplication.processEvents()
                
        except:
            pass
            
        super().closeEvent(event)

    def on_selection_changed(self):
        """處理表格選擇變更"""
        # 如果正在播放,則停止播放
        if self.playback_handler and self.playback_handler.is_playing:
            self.stop_playback()
        
        # 取得選擇項目
        selected = self.results.selectedItems()
        if selected:
            # 取得起始時間
            row = selected[0].row()
            
            # 取得該行的垂直標題(score排序後的編號)
            score_rank = self.results.verticalHeaderItem(row).text()
            
            start_seconds = float(self.results.item(row, 0).text())
            end_seconds = float(self.results.item(row, 1).text())
            
            # 更新時間標籤
            self.current_time_label.setText("00:00")
            duration = end_seconds - start_seconds
            self.total_time_label.setText(self.format_time(duration))
            
            # 重置時間滑動條位置為起點
            self.time_slider.setValue(0)
            
            # 自動從起點開始播放
            try:
                start_samples = self.music_looper.seconds_to_samples(start_seconds)
                end_samples = self.music_looper.seconds_to_samples(end_seconds)
                
                # 設定音量並播放
                volume = self.volume_slider.value() / 100.0
                self.playback_handler.set_volume(volume)
                
                self.playback_handler.play_looping(
                    self.music_looper.mlaudio.playback_audio,
                    self.music_looper.mlaudio.rate,
                    self.music_looper.mlaudio.n_channels,
                    start_samples,
                    end_samples,
                    start_from=start_samples,
                    progress_callback=self.update_progress
                )
                
                # 設置暫停圖示
                pause_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
                self.play_btn.setIcon(pause_icon)
                
                # 更新視窗標題 - 使用score排序後的編號
                self.setWindowTitle(f"MusicLooper - PLAY#{score_rank}")
                
            except Exception as e:
                self.show_error(str(e))

    def show_error(self, message: str):
        QMessageBox.critical(self, self.tr["error"], message)
        
    def show_success(self, message: str):
        QMessageBox.information(self, self.tr["success"], message)

    def update_row_numbers(self, logical_index=None, order=None):
        """更新表格的行號，永遠使用分數決定編號"""
        # 根據分數重新編號
        items = []
        for row in range(self.results.rowCount()):
            score = float(self.results.item(row, 3).text().rstrip('%'))
            items.append((row, score))
        
        # 根據分數排序
        items.sort(key=lambda x: x[1], reverse=True)
        
        # 更新行號
        for rank, (row, _) in enumerate(items):
            self.results.setVerticalHeaderItem(row, QTableWidgetItem(str(rank)))

# 新增自定義的 TableWidgetItem 類來處理數值排序
class NumericTableItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            # 移除百分比符號並轉換為浮點數
            self_value = float(self.text().rstrip('%'))
            other_value = float(other.text().rstrip('%'))
            # 反轉比較結果
            return self_value > other_value  # 改為 > 符號
        except ValueError:
            return super().__lt__(other)

def main():
    try:
        # 初始化 FFmpeg
        setup_ffmpeg()
        
        app = QApplication(sys.argv)
        
        # 使用系統內建音符圖示
        app_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        app.setWindowIcon(app_icon)
        
        window = MainWindow()
        window.setWindowIcon(app_icon)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        QMessageBox.critical(None, "錯誤", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
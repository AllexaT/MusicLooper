# __main__.py
import logging
import sys
from cli import cli_main
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from gui import MainWindow, setup_ffmpeg, show_ffmpeg_error

def cli():
    try:
        cli_main() # 移除 prog_name
    except Exception as e:
        logging.error(e)

def gui():
    try:
        # 先創建 QApplication
        app = QApplication(sys.argv)
        
        # 顯示載入畫面
        loading = LoadingScreen()
        loading.show()
        app.processEvents()
        
        # 使用系統內建音符圖示
        app_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        app.setWindowIcon(app_icon)
        
        # 檢查 FFmpeg
        if not setup_ffmpeg():
            loading.close()
            show_ffmpeg_error()  # 這裡會直接結束程式
        
        # 創建主視窗
        window = MainWindow()
        window.setWindowIcon(app_icon)
        
        # 關閉載入畫面並顯示主視窗
        loading.close()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        QMessageBox.critical(None, "錯誤", str(e))
        sys.exit(1)

class LoadingScreen(QDialog):
    """精緻的載入畫面"""
    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-family: "Microsoft JhengHei UI", Arial;
            }
            QProgressBar {
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                text-align: center;
                background-color: #1a1a1a;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 3px;
            }
        """)
        
        # 設定大小和位置
        self.setFixedSize(300, 150)
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )
        
        # 創建佈局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加標題
        title = QLabel("MusicLooper")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 添加載入訊息
        self.message = QLabel("正在初始化介面...")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message)
        
        # 添加進度條
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # 無限循環模式
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)  # 細長的進度條
        layout.addWidget(self.progress)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    else:
        gui()
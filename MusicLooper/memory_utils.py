import psutil
import os
import json

class MemoryAnalyzer:
    """記憶體分析和管理系統"""
    def __init__(self, silent=False, lang='zh_TW'):
        self.process = psutil.Process()
        self.memory = psutil.virtual_memory()
        self.silent = silent
        self.lang = lang
        self.tr = self._load_translation(lang)

    def _load_translation(self, lang):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        lang_path = os.path.join(base_dir, 'languages', f'{lang}.json')
        if not os.path.exists(lang_path):
            # fallback to en
            lang_path = os.path.join(base_dir, 'languages', 'en.json')
        with open(lang_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def estimate_memory_requirement(self, audio_length_sec: float, sample_rate: int, n_channels: int = 1, dtype_bytes: int = 4) -> dict:
        """更精確估算音樂分析所需的記憶體 (MB)
        Args:
            audio_length_sec (float): 音樂長度（秒）
            sample_rate (int): 採樣率
            n_channels (int): 聲道數
            dtype_bytes (int): 單一樣本的位元組數，float32為4
        Returns:
            dict: 包含記憶體需求的詳細資訊
        """
        # 參數
        hop_length = 512
        n_mels = 128
        n_chroma = 12
        n_mfcc = 13
        # 預設float32
        dtype_bytes = 4
        # frame數
        n_frames = int(audio_length_sec * sample_rate / hop_length)
        # 原始音訊
        audio_samples = int(audio_length_sec * sample_rate * n_channels)
        audio_memory = audio_samples * dtype_bytes
        # 梅爾頻譜圖
        mel_memory = n_mels * n_frames * dtype_bytes
        # 色度圖
        chroma_memory = n_chroma * n_frames * dtype_bytes
        # MFCC
        mfcc_memory = n_mfcc * n_frames * dtype_bytes
        # 自相似矩陣（假設float32，部分流程用bool）
        sim_matrix_memory = n_frames * n_frames * dtype_bytes
        # 其他暫存（估算20%）
        other_memory = 0.2 * (audio_memory + mel_memory + chroma_memory + mfcc_memory + sim_matrix_memory)
        # 總和
        total_estimated = audio_memory + mel_memory + chroma_memory + mfcc_memory + sim_matrix_memory + other_memory
        total_estimated_mb = total_estimated / (1024 * 1024)
        # 系統記憶體資訊
        available_memory = self.memory.available / (1024 * 1024)  # MB
        total_memory = self.memory.total / (1024 * 1024)
        current_usage = self.memory.percent

        # 輸出記憶體使用情況的日誌
        if not self.silent:
            print(f"\n{self.tr['memory_log_title']}")
            print(self.tr['memory_log_estimated'].format(total_estimated_mb))
            print(self.tr['memory_log_available'].format(available_memory))
            print(self.tr['memory_log_total'].format(total_memory))
            print(self.tr['memory_log_usage'].format(current_usage))
            predicted = (total_memory - available_memory + total_estimated_mb) / total_memory * 100
            print(self.tr['memory_log_predicted_usage'].format(predicted))
            if total_estimated_mb > available_memory:
                print(self.tr['memory_log_warning'])
            print(self.tr['memory_log_sep'] + "\n")

        return {
            'estimated_memory': total_estimated_mb,
            'available_memory': available_memory,
            'total_memory': total_memory,
            'current_usage': current_usage,
            'will_exceed': total_estimated_mb > available_memory,
            'usage_percentage': (total_estimated_mb / total_memory) * 100
        }

    def get_memory_status(self):
        """取得目前系統記憶體狀態"""
        mem = psutil.virtual_memory()
        status = {
            'total': mem.total / (1024 * 1024),
            'available': mem.available / (1024 * 1024),
            'percent': mem.percent
        }
        
        # 輸出目前記憶體狀態的日誌
        if not self.silent:
            print(f"\n{self.tr['memory_log_title']}")
            print(self.tr['memory_log_total'].format(status['total']))
            print(self.tr['memory_log_available'].format(status['available']))
            print(self.tr['memory_log_usage'].format(status['percent']))
            print(self.tr['memory_log_sep'] + "\n")
            
        return status

    def recommend_strategy(self, memory_info: dict) -> dict:
        """根據記憶體狀態給出建議"""
        if memory_info['will_exceed']:
            recommendation = "建議使用分批處理"
            risk_level = "高"
        elif memory_info['usage_percentage'] > 70:
            recommendation = "建議考慮使用分批處理"
            risk_level = "中"
        else:
            recommendation = "可以使用完整分析"
            risk_level = "低"
            
        # 輸出建議策略的日誌
        if not self.silent:
            print("\n=== 分析策略建議 ===")
            print(f"風險等級: {risk_level}")
            print(f"建議: {recommendation}")
            print("=" * 25 + "\n")
            
        return {
            'recommendation': recommendation,
            'risk_level': risk_level
        } 
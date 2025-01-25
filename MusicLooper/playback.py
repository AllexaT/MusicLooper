import logging
import numpy as np
import sounddevice as sd

class PlaybackHandler:
    def __init__(self) -> None:
        self.stream = None
        self.is_playing = False
        self.is_paused = False
        self.loop_counter = 0
        self.current_frame = 0
        self.volume = 0.1  # 預設音量為 10%

    def set_volume(self, volume: float):
        """設定音量 (0.0 - 1.0)"""
        self.volume = volume

    def play_looping(
        self,
        playback_data: np.ndarray,
        samplerate: int,
        n_channels: int,
        loop_start: int,
        loop_end: int,
        start_from=0,
        progress_callback=None
    ) -> None:
        self.playback_data = playback_data
        self.loop_start = loop_start 
        self.loop_end = loop_end
        self.current_frame = start_from
        self.is_playing = True
        self.loop_counter = 0

        def callback(outdata, frames, time, status):
            if status:
                logging.error(status)
            
            if self.is_paused:
                outdata.fill(0)
                return
            
            chunksize = min(len(self.playback_data) - self.current_frame, frames)

            if self.is_playing and self.current_frame + frames > self.loop_end:
                pre_loop_index = self.loop_end - self.current_frame
                remaining_frames = frames - (self.loop_end - self.current_frame)
                adjusted_next_frame_idx = self.loop_start + remaining_frames
                
                # 調整音量
                outdata[:pre_loop_index] = self.playback_data[self.current_frame:self.loop_end] * self.volume
                outdata[pre_loop_index:frames] = self.playback_data[self.loop_start:adjusted_next_frame_idx] * self.volume
                
                self.current_frame = adjusted_next_frame_idx
                self.loop_counter += 1
                if progress_callback:
                    progress_callback(self.current_frame, self.loop_counter)
            else:
                # 調整音量
                outdata[:chunksize] = self.playback_data[self.current_frame:self.current_frame + chunksize] * self.volume
                
                self.current_frame += chunksize
                if progress_callback:
                    progress_callback(self.current_frame, self.loop_counter)
                if chunksize < frames:
                    outdata[chunksize:] = 0
                    raise sd.CallbackStop()

        self.stream = sd.OutputStream(
            samplerate=samplerate,
            channels=n_channels,
            callback=callback
        )
        self.stream.start()

    def pause(self):
        self.is_paused = True
        
    def resume(self): 
        self.is_paused = False

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.is_playing = False
        self.is_paused = False
        self.current_frame = 0
        self.loop_counter = 0
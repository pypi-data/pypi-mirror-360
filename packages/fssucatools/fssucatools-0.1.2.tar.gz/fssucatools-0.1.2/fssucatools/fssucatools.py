import threading
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import tkinter as tk

SAMPLE_RATE = 16000
CHANNELS = 1

DEFAULT_FONT = ("微软雅黑", 12)
LARGE_FONT = ("微软雅黑", 14)


# 统一创建控件的封装函数
def create_label(parent, text, large=False, **kwargs):
    font = LARGE_FONT if large else DEFAULT_FONT
    return tk.Label(parent, text=text, font=font, **kwargs)


def create_button(parent, text, command, **kwargs):
    return tk.Button(parent, text=text, command=command, font=LARGE_FONT, **kwargs)


def create_entry(parent, **kwargs):
    return tk.Entry(parent, font=DEFAULT_FONT, **kwargs)


# 主功能类
class RecorderTool:
    def __init__(self):
        self.recording = []
        self.is_recording = False
        self.recording_seconds = 0.0

        # 可选控件引用，默认为 None
        self.root = None
        self.filename_entry = None
        self.time_label = None
        self.status_label = None

    def set_widgets(self, root=None, filename_entry=None, time_label=None, status_label=None):
        """可选控件设置函数"""
        self.root = root
        self.filename_entry = filename_entry
        self.time_label = time_label
        self.status_label = status_label

    def start_recording(self):
        print("开始录音")
        self.is_recording = True
        self.recording = []
        self.recording_seconds = 0.0
        if self.root and self.time_label:
            self._update_timer()
        threading.Thread(target=self._record).start()

    def _record(self):
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=self._callback):
            while self.is_recording:
                sd.sleep(100)

    def _callback(self, indata, frames, time, status):
        if status:
            print("录音状态异常：", status)
        self.recording.append(indata.copy())

    def stop_recording(self):
        self.is_recording = False

        if not self.recording:
            print("没有录音数据")
            return

        # 默认文件名处理
        filename = "output.wav"
        if self.filename_entry:
            user_input = self.filename_entry.get().strip()
            if user_input != '':
                filename = user_input
                if not filename.endswith('.wav'):
                    filename += '.wav'

        audio_data = np.concatenate(self.recording, axis=0)
        audio_data_int16 = (audio_data * 32767).astype(np.int16)
        write(filename, SAMPLE_RATE, audio_data_int16)

        print(f"录音已保存为 {filename}")
        if self.status_label:
            self.status_label.config(text=f"录音已保存为：{filename}")

    def _update_timer(self):
        if self.is_recording:
            self.recording_seconds += 0.1
            self.time_label.config(text=f"已录制：{self.recording_seconds:.1f} 秒")
            self.root.after(100, self._update_timer)
        else:
            self.time_label.config(text="已录制：0.0 秒")

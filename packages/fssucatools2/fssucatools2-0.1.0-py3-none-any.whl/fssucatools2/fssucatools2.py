# fssucatools2.py
import json
import os
import threading
import tkinter as tk
import wave

import numpy as np
import pyttsx3
import requests
import sounddevice as sd
from scipy.io.wavfile import write
from vosk import Model, KaldiRecognizer

# 基本参数
SAMPLE_RATE = 16000
CHANNELS = 1
WAV_FILENAME = "mono.wav"
DEEPSEEK_API_KEY = "sk-c70c0100724d4449bb3b3fab78ba856f"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_PATH = 'vosk-model-small-cn-0.22'

# 初始化模型
model = Model(MODEL_PATH)


# 统一控件创建
def create_label(parent, text, large=False, **kwargs):
    font = ("微软雅黑", 14 if large else 12)
    return tk.Label(parent, text=text, font=font, **kwargs)


def create_button(parent, text, command, **kwargs):
    return tk.Button(parent, text=text, command=command, font=("微软雅黑", 12), **kwargs)


def create_textbox(parent, height=4, **kwargs):
    return tk.Text(parent, height=height, font=("微软雅黑", 11), **kwargs)


# ===== RecorderTool：处理录音与识别 =====
class RecorderTool:
    current_model = model  # 类变量，默认使用上方初始化的全局模型

    def __init__(self, time_label=None, status_label=None, input_box=None, deepseektool=None):
        self.is_recording = False
        self.deepseektool = deepseektool
        self.recording = []
        self.recording_seconds = 0.0
        self.time_label = time_label
        self.status_label = status_label
        self.input_box = input_box
        self.root = None

    def set_root(self, root):
        self.root = root

    def set_input_box(self, input_box):
        self.input_box = input_box

    def start(self):
        self.recording = []
        self.is_recording = True
        self.recording_seconds = 0.0
        if self.status_label:
            self.status_label.config(text="正在录音...")
        if self.input_box:
            self.input_box.delete("1.0", tk.END)
        if self.root:
            self._update_timer()
        threading.Thread(target=self._record).start()

    def stop(self):
        self.is_recording = False
        if self.status_label:
            self.status_label.config(text="识别中，请稍等...")
        threading.Thread(target=self._save_and_recognize).start()

    def _record(self):
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=self._callback):
            while self.is_recording:
                sd.sleep(100)

    def _callback(self, indata, frames, time, status):
        self.recording.append(indata.copy())

    def _update_timer(self):
        if self.is_recording:
            self.recording_seconds += 0.1
            if self.time_label:
                self.time_label.config(text=f"已录制：{self.recording_seconds:.1f} 秒")
            self.root.after(100, self._update_timer)
        else:
            if self.time_label:
                self.time_label.config(text="已录制：0.0 秒")

    def _save_and_recognize(self):
        if not self.recording:
            return
        audio_data = np.concatenate(self.recording, axis=0)
        audio_data_int16 = (audio_data * 32767).astype(np.int16)
        write(WAV_FILENAME, SAMPLE_RATE, audio_data_int16)
        if self.deepseektool:
            self.deepseektool.recognize_from_file(WAV_FILENAME)

    @staticmethod
    def recognize_audio_file(filepath):
        """传入音频文件路径，返回识别后的文本字符串"""
        if not os.path.exists(filepath):
            return ""
        wf = wave.open(filepath, 'rb')
        rec = KaldiRecognizer(RecorderTool.current_model, SAMPLE_RATE)

        while True:
            data = wf.readframes(4000)
            if not data:
                break
            rec.AcceptWaveform(data)

        result = json.loads(rec.FinalResult())
        return result.get("text", "").replace(" ", "")

    @staticmethod
    def set_model_path(model_path):
        """设置识别模型路径，重新加载模型"""
        if os.path.exists(model_path):
            RecorderTool.current_model = Model(model_path)


# ===== DeepseekTool：语音识别 + 接入DeepSeek + TTS朗读 =====
# ===== DeepseekTool：语音识别 + 接入DeepSeek + TTS朗读 =====
class DeepseekTool:
    def __init__(self, input_box=None, output_box=None, status_label=None, speak_enabled=True):
        self.input_box = input_box  # 输入框控件
        self.output_box = output_box  # 输出框控件
        self.status_label = status_label  # 状态标签
        self.speak_enabled = speak_enabled  # 是否启用TTS语音朗读
        self.streaming_active = False  # 是否正在流式输出
        self.full_response = ""  # 累积的完整回复
        self.rate = 200  # 语速
        self.tts_thread = None  # 朗读线程
        self.api_key = DEEPSEEK_API_KEY  # 默认使用全局key

    def set_api_key(self, key):
        self.api_key = key

    def set_speak_rate(self, value):
        self.rate = value

    def set_widgets(self, input_box, output_box, status_label):
        self.input_box = input_box
        self.output_box = output_box
        self.status_label = status_label

    def recognize_from_file(self, filename):
        # 本地语音识别转文字，识别完成后继续调用DeepSeek
        wf = wave.open(filename, 'rb')
        rec = KaldiRecognizer(RecorderTool.current_model, SAMPLE_RATE)

        while True:
            data = wf.readframes(4000)
            if not data:
                break
            rec.AcceptWaveform(data)

        result = json.loads(rec.FinalResult())
        text = result.get("text", "").replace(" ", "")
        if self.input_box:
            self.input_box.delete("1.0", tk.END)
            self.input_box.insert(tk.END, text)
        if self.status_label:
            self.status_label.config(text="正在获取DeepSeek回复...")

        threading.Thread(target=self._ask_stream, args=(text,), daemon=True).start()

    def _ask_stream(self, prompt):
        self.full_response = ""
        self.streaming_active = True
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 1.3,
            "max_tokens": 2000,
            "stream": True
        }

        if self.output_box:
            self.output_box.delete("1.0", tk.END)

        try:
            with requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, stream=True) as resp:
                for line in resp.iter_lines():
                    if not self.streaming_active:
                        break
                    if line and line.startswith(b"data:"):
                        content = line[5:].decode().strip()
                        if content == "[DONE]":
                            self._speak_response()
                            break
                        try:
                            data = json.loads(content)
                            delta = data["choices"][0].get("delta", {})
                            text = delta.get("content", "")
                            if text:
                                self.full_response += text
                                self._append_output(text)
                        except Exception:
                            continue
        except Exception as e:
            if self.status_label:
                self.status_label.config(text=f"请求错误: {str(e)}")

    def _append_output(self, content):
        if self.output_box:
            self.output_box.insert(tk.END, content)
            self.output_box.see(tk.END)

    def _speak_response(self):
        if self.full_response and self.speak_enabled:
            if self.status_label:
                self.status_label.config(text="语音朗读中...")
            self.tts_thread = threading.Thread(target=self._tts_speak, daemon=True)
            self.tts_thread.start()
        else:
            if self.status_label:
                self.status_label.config(text="回复完成")

    def _tts_speak(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.rate)
            engine.say(self.full_response)
            engine.runAndWait()
            if self.status_label:
                self.status_label.config(text="朗读完成")
        except Exception as e:
            if self.status_label:
                self.status_label.config(text=f"语音错误: {str(e)}")

    def stop_all(self):
        self.streaming_active = False
        try:
            engine = pyttsx3.init()
            engine.stop()
        except Exception:
            pass
        if self.status_label:
            self.status_label.config(text="已停止")

    @classmethod
    def ask_once(cls, prompt):
        """发送非流式请求并获取完整回复字符串"""
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 1.3,
            "max_tokens": 2000,
            "stream": False  # 明确设置为非流式
        }

        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"请求出错: {str(e)}"

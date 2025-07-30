import json
import tkinter as tk
import wave
import threading
import paho.mqtt.client as mqtt
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from vosk import Model, KaldiRecognizer

# ========== 基本参数 ==========
SAMPLE_RATE = 16000  # 采样率
CHANNELS = 1  # 单声道
WAV_FILENAME = "mono.wav"  # 临时保存的录音文件名
MODEL_PATH = "vosk-model-small-cn-0.22"  # 语音识别模型路径

MQTT_SERVER = "broker-cn.emqx.io"  # MQTT服务器地址
MQTT_PORT = 1883  # MQTT端口号
SWITCH_TOPIC_TEMPLATE = "switch_control_topic{}"  # 开关控制主题
LED_TOPIC_TEMPLATE = "led_control_topic{}"  # LED控制主题

# ========== 初始化语音识别模型 ==========
model = Model(MODEL_PATH)


# ========== GUI 控件封装函数 ==========
def create_label(parent, text, large=False, **kwargs):
    font = ("微软雅黑", 14 if large else 12)
    return tk.Label(parent, text=text, font=font, **kwargs)


def create_button(parent, text, command, **kwargs):
    return tk.Button(parent, text=text, command=command, font=("微软雅黑", 12), **kwargs)


def create_textbox(parent, height=4, **kwargs):
    return tk.Text(parent, height=height, font=("微软雅黑", 11), **kwargs)


# ========== 录音与识别模块 ==========
class RecorderTool:
    def __init__(self, status_label=None):
        self.is_recording = False
        self.recording = []
        self.callback = None
        self.status_label = status_label

    def set_callback(self, func):
        self.callback = func

    def start(self):
        self.recording = []
        self.is_recording = True
        if self.status_label:
            self.status_label.config(text="正在录音...")
        threading.Thread(target=self._record).start()

    def stop(self):
        self.is_recording = False
        if self.status_label:
            self.status_label.config(text="识别中...")
        threading.Thread(target=self._save_and_recognize).start()

    def _record(self):
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=self._callback):
            while self.is_recording:
                sd.sleep(100)

    def _callback(self, indata, frames, time, status):
        self.recording.append(indata.copy())

    def _save_and_recognize(self):
        if not self.recording:
            return
        audio = np.concatenate(self.recording, axis=0)
        audio_int16 = (audio * 32767).astype(np.int16)
        write(WAV_FILENAME, SAMPLE_RATE, audio_int16)

        wf = wave.open(WAV_FILENAME, 'rb')
        rec = KaldiRecognizer(model, SAMPLE_RATE)

        while True:
            data = wf.readframes(4000)
            if not data:
                break
            rec.AcceptWaveform(data)

        result = json.loads(rec.FinalResult())
        text = result.get("text", "").replace(" ", "")

        if self.status_label:
            self.status_label.config(text="识别完成")
        if self.callback:
            self.callback(text)


# ========== MQTT 控制器（开关 + LED） ==========
class SimpleSwitchController:
    def __init__(self, device_id="0", textbox=None, status_label=None):
        self.device_id = device_id
        self.textbox = textbox
        self.status_label = status_label
        self.client = mqtt.Client()
        self.client.connect(MQTT_SERVER, MQTT_PORT, 60)

    def log(self, msg):
        if self.status_label:
            self.status_label.config(text=msg)

    def send_switches(self, switch1_status, switch2_status):
        topic = SWITCH_TOPIC_TEMPLATE.format(self.device_id)
        payload = {
            "switch1": int(switch1_status),
            "switch2": int(switch2_status)
        }
        self.client.publish(topic, json.dumps(payload))
        self.log(f"已发送开关状态: {payload}")

    def send_led_color(self, led_index, r, g, b):
        topic = LED_TOPIC_TEMPLATE.format(self.device_id)
        payload = {
            f"LED{led_index}": [int(r), int(g), int(b)]
        }
        self.client.publish(topic, json.dumps(payload))
        self.log(f"LED{led_index} 颜色设置为 ({r}, {g}, {b})")

    def send_all_led_colors(self, colors):
        """
        一次性设置所有4个LED颜色
        参数: colors = [[r0,g0,b0], [r1,g1,b1], [r2,g2,b2], [r3,g3,b3]]
        """
        if len(colors) != 4:
            self.log("错误：必须提供4组RGB颜色")
            return
        topic = LED_TOPIC_TEMPLATE.format(self.device_id)
        payload = {}
        for i in range(4):
            r, g, b = map(int, colors[i])
            payload[f"LED{i}"] = [r, g, b]
        self.client.publish(topic, json.dumps(payload))
        self.log(f"全部LED颜色已发送: {payload}")

    def handle_command(self, text):
        if self.textbox:
            self.textbox.delete("1.0", tk.END)
            self.textbox.insert(tk.END, text)

        if "打开" in text:
            self.send_switches(True, True)
        elif "关闭" in text:
            self.send_switches(False, False)
        else:
            self.log("未能识别有效的开关指令")

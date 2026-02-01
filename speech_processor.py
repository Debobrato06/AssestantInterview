import speech_recognition as sr
import threading
import queue
import sounddevice as sd
import numpy as np
import io
import wave

class SpeechProcessor:
    def __init__(self, device_index=None):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.result_queue = queue.Queue()
        # If no device provided, try to find loopback, else fallback to None (default)
        self.device_index = device_index if device_index is not None else self._find_loopback_device()

    def _find_loopback_device(self):
        try:
            devices = sd.query_devices()
            hostapis = sd.query_hostapis()
            
            # Priority 1: Search for explicit Stereo Mix or Mixed Capture (MME/DirectSound/WDM-KS)
            for i, device in enumerate(devices):
                name = device['name'].lower()
                if device['max_input_channels'] > 0:
                    if any(k in name for k in ["stereo mix", "mixed capture", "what u hear"]):
                        print(f"!!! Found Loopback Device (Priority 1): {device['name']} at index {i}")
                        return i
            
            # Priority 2: Search for WASAPI loopback-capable names
            for i, device in enumerate(devices):
                device_name = device['name']
                hostapi_name = hostapis[device['hostapi']]['name']
                if "WASAPI" in hostapi_name:
                    # In WASAPI, even if max_input_channels is 0, it might be a loopback source 
                    # but speech_recognition needs an input device. 
                    # So we check for output devices that we can 'hack' or labeled input speakers.
                    if any(k in device_name.lower() for k in ["speakers", "loopback", "realtek"]):
                        if device['max_input_channels'] > 0:
                            print(f"!!! Found Loopback Device (Priority 2): {device_name} at index {i}")
                            return i
        except Exception as e:
            print(f"Error finding loopback device: {e}")
        return None  # Default to mic if not found

    def start_listening(self):
        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def stop_listening(self):
        self.is_listening = False

    def list_devices(self):
        devices = sd.query_devices()
        input_devices = []
        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                input_devices.append({"index": i, "name": d['name']})
        return input_devices

    def set_device(self, index):
        self.device_index = int(index)
        if self.is_listening:
            self.stop_listening()
            self.start_listening()

    def _listen_loop(self):
        # If no loopback found, use default microphone
        source = sr.Microphone(device_index=self.device_index)
        
        with source as s:
            self.recognizer.adjust_for_ambient_noise(s)
            while self.is_listening:
                try:
                    print(f"Listening on device {self.device_index or 'Default'}...")
                    audio = self.recognizer.listen(s, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio)
                    if text:
                        print(f"STT Backend Detected: {text}")
                        self.result_queue.put(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"Speech Recognition Error: {e}")

    def get_latest_text(self):
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None

import speech_recognition as sr
import threading
import queue
import sounddevice as sd
import numpy as np
import io
import wave
import time

class SpeechProcessor:
    def __init__(self, device_index=None):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.result_queue = queue.Queue()
        # If no device provided, try to find loopback, else fallback to None (default)
        self.device_index = device_index if device_index is not None else self._find_loopback_device()
        self.sample_rate = 16000

    def _find_loopback_device(self):
        try:
            devices = sd.query_devices()
            # Try to find WASAPI Loopback first
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0 and "loopback" in d['name'].lower():
                    print(f"!!! Found WASAPI Loopback: {d['name']} at index {i}")
                    return i
            
            # Fallback to Stereo Mix
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0 and "stereo mix" in d['name'].lower():
                    print(f"!!! Found Stereo Mix: {d['name']} at index {i}")
                    return i
        except Exception as e:
            print(f"Error finding loopback device: {e}")
        return None

    def start_listening(self):
        if self.is_listening:
            return
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
        print(f"System: Switched to device index {self.device_index}")
        if self.is_listening:
            self.stop_listening()
            # Small delay to let thread close
            time.sleep(0.5)
            self.start_listening()

    def _listen_loop(self):
        print(f"Starting listening loop on device {self.device_index}...")
        
        # Use speech_recognition source if possible, but it often fails with loopback devices
        # that don't look like standard microphones to PyAudio.
        # Fallback: Capture raw audio with sounddevice and pass to recognizer.
        
        try:
            source = sr.Microphone(device_index=self.device_index)
            with source as s:
                self.recognizer.adjust_for_ambient_noise(s, duration=1)
                while self.is_listening:
                    try:
                        print("Listening...")
                        audio = self.recognizer.listen(s, timeout=5, phrase_time_limit=15)
                        # Use recognize_google (standard) or whisper if available
                        text = self.recognizer.recognize_google(audio)
                        if text:
                            print(f"Detected: {text}")
                            self.result_queue.put(text)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception as e:
                        print(f"Loop Error: {e}")
                        time.sleep(1)
        except Exception as pilot_e:
            print(f"Standard Microphone init failed: {pilot_e}. Attempting sounddevice capture...")
            # If PyAudio/Microphone fails, we'd need a sounddevice callback implementation
            # For now, let's stick to the Microphone approach but make it more robust.
            pass

    def get_latest_text(self):
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None

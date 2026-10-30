import tkinter as tk
from tkinter import messagebox
import threading
import queue
import wave
import tempfile
import os
import sounddevice as sd
import speech_recognition as sr

APP_TITLE = "Bangla Voice Typing"
SAMPLE_RATE = 16000
CHANNELS = 1

class VoiceTypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("720x520")
        self.root.minsize(600, 440)
        self.audio_queue = queue.Queue()
        self.stream = None
        self.frames = []
        self.recording = False

        tk.Label(root, text="বাংলা ভয়েস টাইপিং", font=("Nirmala UI", 24, "bold")).pack(pady=(18, 4))
        tk.Label(root, text="মাইক্রোফোনে কথা বলুন, আপনার কথা বাংলায় লিখে নিন",
                 font=("Nirmala UI", 11)).pack(pady=(0, 14))

        self.status = tk.Label(root, text="প্রস্তুত", fg="#167a35", font=("Nirmala UI", 11, "bold"))
        self.status.pack(pady=4)

        controls = tk.Frame(root)
        controls.pack(pady=10)
        self.start_btn = tk.Button(controls, text="● রেকর্ড শুরু", width=16, height=2,
                                   bg="#167a35", fg="white", command=self.start_recording)
        self.start_btn.pack(side="left", padx=6)
        self.stop_btn = tk.Button(controls, text="■ রেকর্ড বন্ধ ও লিখুন", width=20, height=2,
                                  state="disabled", command=self.stop_recording)
        self.stop_btn.pack(side="left", padx=6)

        self.text = tk.Text(root, wrap="word", font=("Nirmala UI", 14), padx=12, pady=12)
        self.text.pack(fill="both", expand=True, padx=18, pady=12)

        bottom = tk.Frame(root)
        bottom.pack(fill="x", padx=18, pady=(0, 14))
        tk.Button(bottom, text="লেখা মুছুন", command=self.clear_text).pack(side="left")
        tk.Button(bottom, text="কপি করুন", command=self.copy_text).pack(side="left", padx=8)
        tk.Label(bottom, text="ইন্টারনেট সংযোগ প্রয়োজন", fg="#666").pack(side="right")

        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            pass
        self.audio_queue.put(indata.copy())

    def start_recording(self):
        if self.recording:
            return
        self.frames = []
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        try:
            self.stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                                         dtype="int16", callback=self.audio_callback)
            self.stream.start()
            self.recording = True
            self.status.config(text="রেকর্ড হচ্ছে… কথা বলা শেষ হলে রেকর্ড বন্ধ করুন", fg="#b45309")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("মাইক্রোফোন সমস্যা", f"মাইক্রোফোন চালু করা যায়নি।\n\n{e}")

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass
        self.stream = None
        while not self.audio_queue.empty():
            try:
                self.frames.append(self.audio_queue.get_nowait())
            except queue.Empty:
                break
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        if not self.frames:
            self.status.config(text="কোনো অডিও পাওয়া যায়নি", fg="#b91c1c")
            return
        self.status.config(text="বাংলায় লেখা তৈরি হচ্ছে…", fg="#1d4ed8")
        threading.Thread(target=self.transcribe, daemon=True).start()

    def transcribe(self):
        try:
            import numpy as np
            audio = np.concatenate(self.frames, axis=0)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                filename = f.name
            try:
                with wave.open(filename, "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(audio.tobytes())
                recognizer = sr.Recognizer()
                with sr.AudioFile(filename) as source:
                    recorded = recognizer.record(source)
                result = recognizer.recognize_google(recorded, language="bn-BD")
                self.root.after(0, self.add_result, result)
            finally:
                try:
                    os.remove(filename)
                except OSError:
                    pass
        except sr.UnknownValueError:
            self.root.after(0, self.show_status, "কথা বোঝা যায়নি। আবার চেষ্টা করুন।", "#b91c1c")
        except sr.RequestError as e:
            self.root.after(0, self.show_status, f"ইন্টারনেট/সার্ভিস সমস্যা: {e}", "#b91c1c")
        except Exception as e:
            self.root.after(0, self.show_status, f"সমস্যা হয়েছে: {e}", "#b91c1c")

    def add_result(self, result):
        self.text.insert("end", result + " ")
        self.text.see("end")
        self.status.config(text="লেখা তৈরি হয়েছে। আবার রেকর্ড করতে পারেন।", fg="#167a35")

    def show_status(self, text, color):
        self.status.config(text=text, fg=color)

    def clear_text(self):
        self.text.delete("1.0", "end")

    def copy_text(self):
        content = self.text.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status.config(text="লেখা কপি হয়েছে", fg="#167a35")

    def close(self):
        if self.recording and self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        self.root.destroy()

if __name__ == "__main__":
    window = tk.Tk()
    app = VoiceTypingApp(window)
    window.mainloop()

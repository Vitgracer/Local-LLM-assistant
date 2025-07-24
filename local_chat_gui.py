import json
import yaml
import queue
import threading
import tkinter as tk
import sounddevice as sd
from argparse import Namespace
from tkinter import scrolledtext

from chat.loaders import (
    get_chat_history,
    get_llm_model,
    get_optimization_config,
    get_tokenizer
)
from chat.generator import chat_with_model
from voice.loaders import get_voice_recognizer


class VoiceChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ Voice Chatbot")
        self.root.geometry("450x700")
        self.root.configure(bg="#83ace9")
        self.audio_q = queue.Queue()

        self.setup_model()
        self.setup_ui()

        self.listen_and_respond()

    def mic_callback(self, indata, frames, time, status):
        self.audio_q.put(bytes(indata))

    def listen_once(self):
        """Captures a single voice input and returns text (blocking)."""
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                            channels=1, callback=self.mic_callback):
            while True:
                data = self.audio_q.get()
                if self.voice_recognizer.AcceptWaveform(data):
                    result = json.loads(self.voice_recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        return text

    def setup_model(self):
        with open("config.yaml", "r") as f:
            config_data = yaml.safe_load(f)
        self.config = Namespace(**config_data)

        bnb_config = get_optimization_config()
        self.tokenizer = get_tokenizer(self.config.llm_model_name)
        self.model = get_llm_model(self.config.llm_model_name, bnb_config)
        self.chat_history = get_chat_history(self.config.system_prompt)

        self.voice_recognizer = get_voice_recognizer(self.config.voice_model_name)

    def setup_ui(self):
        self.chat_log = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Fira Sans", 11), bg="white", fg="#333"
        )
        self.chat_log.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Define color tags
        self.chat_log.tag_config("user", foreground="#1a73e8")
        self.chat_log.tag_config("assistant", foreground="#811212")
        self.chat_log.tag_config("info", foreground="#080000")

        self.chat_log.insert(tk.END, "🤖 Assistant ready. Say something...\n", "info")
        self.chat_log.configure(state='disabled')

    def append_message(self, sender, message):
        self.chat_log.configure(state='normal')

        # Choose tag based on sender
        if sender.startswith("🧑"):
            tag = "user"
        elif sender.startswith("🤖"):
            tag = "assistant"
        else:
            tag = "info"

        self.chat_log.insert(tk.END, f"{sender}: {message}\n", tag)
        self.chat_log.see(tk.END)
        self.chat_log.configure(state='disabled')

    def listen_and_respond(self):
        threading.Thread(target=self._listen_and_respond_worker, daemon=True).start()

    def _listen_and_respond_worker(self):
        self.root.after(0, lambda: self.append_message("🎤 Listening...", "(waiting for input)"))
        voice_input = self.listen_once()
        self.root.after(0, lambda: self.append_message("🧑 You", voice_input))

        self.chat_history.append({"role": "user", "content": voice_input})
        assistant_reply = chat_with_model(self.model, self.tokenizer, self.chat_history, self.config)
        self.chat_history.append({"role": "assistant", "content": assistant_reply})
        self.root.after(0, lambda: self.append_message("🤖 Assistant", assistant_reply))

        self.listen_and_respond()


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceChatApp(root)
    root.mainloop()
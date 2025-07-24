import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
import yaml
from argparse import Namespace

from chat.loaders import (
    get_chat_history,
    get_llm_model,
    get_optimization_config,
    get_tokenizer
)
from chat.generator import chat_with_model


vosk_model = Model(r"C:\Users\vsgsa\Desktop\V\Projects\LocalAssistant\Local-LLM-assistant\voice\models\vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(vosk_model, 16000)
audio_q = queue.Queue()

def mic_callback(indata, frames, time, status):
    audio_q.put(bytes(indata))

def listen_once():
    """Captures a single voice input and returns text (blocking)."""
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=mic_callback):
        while True:
            data = audio_q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    return text

# === Chat UI ===
class VoiceChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ Voice Chatbot")
        self.root.geometry("700x600")
        self.root.configure(bg="#f5f7fa")

        self.setup_model()
        self.setup_ui()

        self.listen_and_respond()  # Start the first mic listen

    def setup_model(self):
        with open("config.yaml", "r") as f:
            config_data = yaml.safe_load(f)
        self.config = Namespace(**config_data)

        bnb_config = get_optimization_config()
        self.tokenizer = get_tokenizer(self.config.llm_model_name)
        self.model = get_llm_model(self.config.llm_model_name, bnb_config)
        self.chat_history = get_chat_history(self.config.system_prompt)

    def setup_ui(self):
        self.chat_log = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Segoe UI", 11), bg="white", fg="#333"
        )
        self.chat_log.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        self.chat_log.insert(tk.END, "🤖 Assistant ready. Say something...\n")
        self.chat_log.configure(state='disabled')

    def append_message(self, sender, message):
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, f"{sender}: {message}\n")
        self.chat_log.see(tk.END)
        self.chat_log.configure(state='disabled')

    def listen_and_respond(self):
        threading.Thread(target=self._listen_and_respond_worker, daemon=True).start()

    def _listen_and_respond_worker(self):
        self.root.after(0, lambda: self.append_message("🎤 Listening...", "(waiting for input)"))
        voice_input = listen_once()
        self.root.after(0, lambda: self.append_message("🧑 You", voice_input))

        self.chat_history.append({"role": "user", "content": voice_input})
        assistant_reply = chat_with_model(self.model, self.tokenizer, self.chat_history, self.config)
        self.chat_history.append({"role": "assistant", "content": assistant_reply})
        self.root.after(0, lambda: self.append_message("🤖 Assistant", assistant_reply))

        # Start next listening cycle
        self.listen_and_respond()


# === Launch the App ===
if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceChatApp(root)
    root.mainloop()
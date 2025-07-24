import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
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

def voice_listener(callback):
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=mic_callback):
        while True:
            data = audio_q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    callback(text)

# Chat UI
class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Local Voice Chat")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f2f5")

        self.setup_model()
        self.setup_ui()

        # Start background voice listener
        threading.Thread(target=voice_listener, args=(self.on_voice_input,), daemon=True).start()

    def setup_model(self):
        with open("config.yaml", "r") as f:
            config_data = yaml.safe_load(f)
        self.config = Namespace(**config_data)

        bnb_config = get_optimization_config()
        self.tokenizer = get_tokenizer(self.config.llm_model_name)
        self.model = get_llm_model(self.config.llm_model_name, bnb_config)
        self.chat_history = get_chat_history(self.config.system_prompt)

    def setup_ui(self):
        # Chat log (scrollable)
        self.chat_log = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Segoe UI", 11), bg="white", fg="#333")
        self.chat_log.pack(padx=20, pady=(20,10), fill=tk.BOTH, expand=True)
        self.chat_log.insert(tk.END, "🤖 Assistant ready. Say something or type below.\n")
        self.chat_log.configure(state='disabled')

        # Input field
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=20, pady=10)

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var, font=("Segoe UI", 11))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", self.send_input)

        send_btn = ttk.Button(input_frame, text="Send", command=self.send_input)
        send_btn.pack(side=tk.RIGHT)

    def send_input(self, event=None):
        user_input = self.input_var.get().strip()
        if not user_input:
            return
        self.input_var.set("")
        self.append_message("🧑 You", user_input)
        threading.Thread(target=self.process_user_input, args=(user_input,), daemon=True).start()

    def on_voice_input(self, voice_text):
        self.root.after(0, lambda: self.handle_voice_input(voice_text))

    def handle_voice_input(self, text):
        self.append_message("🎙 You (voice)", text)
        threading.Thread(target=self.process_user_input, args=(text,), daemon=True).start()

    def append_message(self, sender, message):
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, f"{sender}: {message}\n")
        self.chat_log.see(tk.END)
        self.chat_log.configure(state='disabled')

    def process_user_input(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})
        response = chat_with_model(self.model, self.tokenizer, self.chat_history, self.config)
        self.chat_history.append({"role": "assistant", "content": response})
        self.root.after(0, lambda: self.append_message("🤖 Assistant", response))


# === Run the App ===
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
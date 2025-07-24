import yaml
import queue
import sounddevice as sd
from argparse import Namespace
from chat.loaders import (
    get_chat_history,
    get_llm_model,
    get_optimization_config,
    get_tokenizer
)
from chat.generator import chat_with_model
from voice.loaders import get_voice_recognizer
from voice.processing import get_audio_input


def run_chat(config):
    # load llm prerequisites 
    bnb_config = get_optimization_config()
    tokenizer = get_tokenizer(config.llm_model_name)
    model = get_llm_model(config.llm_model_name, bnb_config)
    chat_history = get_chat_history(config.system_prompt)

    # activate voice part
    q = queue.Queue()
    def callback(indata, frames, time, status):
        q.put(bytes(indata))
    voice_recognizer = get_voice_recognizer(config.voice_model_name)

    # open mic and start listening 
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback, device=1):
        
        # activate chat loop
        while True:
            user_input = get_audio_input(q, voice_recognizer)
            if user_input.lower().strip() in ("exit", "quit"):
                break

            chat_history.append({"role": "user", "content": user_input})
            assistant_reply = chat_with_model(model, 
                                            tokenizer, 
                                            chat_history,
                                            config)
            chat_history.append({"role": "assistant", "content": assistant_reply})

if __name__ == "__main__":
    with open("config.yaml", 'r') as file:
        config = Namespace(**yaml.safe_load(file))
    run_chat(config)
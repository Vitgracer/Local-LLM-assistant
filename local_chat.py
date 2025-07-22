import yaml
from argparse import Namespace
from chat.loaders import (
    get_chat_history,
    get_llm_model,
    get_optimization_config,
    get_tokenizer
)
from chat.generator import chat_with_model


def run_chat(config):
    bnb_config = get_optimization_config()
    tokenizer = get_tokenizer(config.model_name)
    model = get_llm_model(config.model_name, bnb_config)
    chat_history = get_chat_history(config.system_prompt)

    while True:
        user_input = input("\nUser: ")
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
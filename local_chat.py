import yaml
from argparse import Namespace
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


def get_optimization_config():
    return BitsAndBytesConfig(load_in_4bit=True)

def get_tokenizer(model_name):
    return AutoTokenizer.from_pretrained(model_name)

def get_llm_model(model_name, bnb_config):
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype="auto"
    )
    model.eval()
    print("Model loaded...")
    return model

def run_chat(config):
    bnb_config = get_optimization_config()
    tokenizer = get_tokenizer(config.model_name)
    model = get_llm_model(config.model_name, bnb_config)

if __name__ == "__main__":
    with open("config.yaml", 'r') as file:
        config = Namespace(**yaml.safe_load(file))
    run_chat(config)
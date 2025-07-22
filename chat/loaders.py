from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    BitsAndBytesConfig
)


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

def get_chat_history(system_prompt):
    return [ 
        {"role": "system", "content": system_prompt}, 
    ]
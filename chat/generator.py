import time 
import torch


def chat_with_model(model, tokenizer, chat_history, config):
    text = tokenizer.apply_chat_template(
        chat_history,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    print("generating response...")

    start = time.time()
    with torch.no_grad():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=config.max_new_tokens,
        )
    end = time.time()

    output_ids = generated_ids[0][len(model_inputs.input_ids[0]) :]
    response = tokenizer.decode(output_ids, skip_special_tokens=True)

    print(f"Assistant: {response}")
    print(f"Generation took {end - start:.2f} seconds.")
    print("-------------------------------------------")
    return response
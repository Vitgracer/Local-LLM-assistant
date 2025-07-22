# Local-LLM-assistant
This project is an experiment in **running small but capable language models entirely offline** on your own laptop. The goal is to create a **private, local AI assistant** that does **not send your data anywhere**, with full control over the model and the process — no cloud, no telemetry, and no limitations.

You can use it to interact with your own compact assistant model that remembers context, follows system instructions, and generates helpful responses — **all locally on your machine**.

---

## 🔒 Why?

- 🛡️ **Privacy-first**: Your chats stay on your device
- 💡 **Hackable**: Full control over generation, logic, prompts
- 🧪 **Experimental**: Try different models, quantizations, and runtimes
- 💻 **Runs on consumer GPUs**

---

## 🤖 Model Used

We use [`HuggingFaceTB/SmolLM3-3B`](https://huggingface.co/HuggingFaceTB/SmolLM3-3B) — a compact 3B parameter chat-tuned model.

**Massive thanks and respect** to the authors of SmolLM3 and the HuggingFace community for making these tools open and accessible!

---
## 🚀 Setup Instructions

### 1. Clone the Repo and Create a Virtual Environment

```bash
python -m venv assistant_venv
# On Windows:
assistant_venv\Scripts\activate
```

### 2. Install Dependencies (for CUDA 12.4 and Torch 2.5.1)
```bash
pip3 install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124
pip3 install -U transformers accelerate bitsandbytes
```

### 3. 💬 Usage
Run the assistant with context and a system prompt using the included script.

**Features:**

- Maintains full chat history (context)
- Supports a system role message
- Uses 4-bit quantized loading with bitsandbytes
- Optimized for fast response time

To chat interactively, run:
```bash
python local_chat.py
```

### 🧪 Optional: Further Optimization
If you want to push performance further on Linux, you can explore:

✅ [`exllamav2`](https://github.com/turboderp-org/exllamav2) - extremely fast inference engine for quantized LLMs.

**Requirements:**
CUDA Toolkit 12.4 installed locally and set as an environment variable.

✅ [`vLLM`](https://github.com/vllm-project/vllm) - high-performance LLM inference engine with paged attention. Ideal for serving multiple prompts or streaming.

### 👋 Final Words
This is a lightweight personal assistant that respects your data and your control. Perfect for:

- Offline Q&A
- Personal journaling or reminders
- Local experiments with new models
- Happy tinkering — and thanks again to all open-source LLM developers! 😍😍😍
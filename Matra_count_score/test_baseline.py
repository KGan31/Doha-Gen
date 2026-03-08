from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# 1. Specify the base model directly from Hugging Face
model_name = "google/mt5-small"

print(f"Loading {model_name} (this might take a minute to download the first time)...")

# 2. Use the 'Auto' classes instead of the hardcoded MT5 classes
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# 3. Automatically use your NVIDIA GPU since you have CUDA installed
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# 4. Hardcode the Theme and Context for the test
theme = "भक्ति"
context = "ईश्वर के प्रति समर्पण"

# 5. Format the prompt exactly as you will for training
input_text = f"Generate Hindi Doha | Theme: {theme} | Context: {context}"

print("\n" + "="*50)
print(f"Input Prompt: {input_text}")
print("="*50)

# 6. Convert the text into tokens
input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(device)

# 7. Ask the raw model to generate an output
print("Generating baseline output...\n")
outputs = model.generate(
    input_ids,
    max_length=60,
    num_beams=5,
    early_stopping=True
)

# 8. Decode the tokens back into Hindi text
baseline_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("-" * 40)
print("Untrained Baseline Output:")
print(baseline_output)
print("-" * 40)
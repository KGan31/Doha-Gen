import pandas as pd
from datasets import Dataset

# 1. Load your clean CSV file
df = pd.read_csv("dohas_final_hindi_dataset.csv")

# 2. Format the Input and Target
# We construct the exact prompt the model will see during training and generation
df["input_text"] = "Generate Hindi Doha | Theme: " + df["Theme"].astype(str) + " | Context: " + df["Context"].astype(str)
df["target_text"] = df["Doha"].astype(str)

# 3. Keep only the necessary columns
df = df[["input_text", "target_text"]]

# 4. Convert to Hugging Face Dataset and split (90% Train, 10% Test)
dataset = Dataset.from_pandas(df)
dataset = dataset.train_test_split(test_size=0.1)

# 5. Save to disk
dataset.save_to_disk("doha_hf_dataset")
print(f"Success! Prepared {len(df)} dohas for training.")
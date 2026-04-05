import pandas as pd
import re

def clean_poem_text(text):
    """
    Function to clean the poem text by removing extra whitespaces 
    and special characters if needed.
    """
    if pd.isna(text):
        return text
    # Remove leading/trailing whitespaces
    text = str(text).strip()
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text

def clean_dataset(file_path, output_path):
    print(f"--- Cleaning {file_path} ---")
    
    # Read the dataset, skipping badly formatted lines 
    # (where the number of commas doesn't match the header)
    try:
        df = pd.read_csv(file_path, on_bad_lines='skip', engine='python')
        print(f"Loaded {len(df)} rows after skipping bad lines.")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return
    
    # 1. Drop duplicate rows
    initial_rows = len(df)
    df = df.drop_duplicates()
    print(f"Dropped {initial_rows - len(df)} duplicate rows.")
    
    # 2. Drop rows where essential columns are missing
    # Assuming the columns are: poet_name, kavita_name, kavita_text, kavita_url
    if 'kavita_text' in df.columns and 'kavita_name' in df.columns:
        df = df.dropna(subset=['kavita_text', 'kavita_name'])
    
    # 3. Clean the text columns
    if 'kavita_text' in df.columns:
        df['kavita_text'] = df['kavita_text'].apply(clean_poem_text)
    
    if 'poet_name' in df.columns:
        df['poet_name'] = df['poet_name'].str.strip()
        
    if 'kavita_name' in df.columns:
        df['kavita_name'] = df['kavita_name'].str.strip()

    # Save the cleaned dataset to a new CSV file
    df.to_csv(output_path, index=False, quoting=1) # quoting=1 means csv.QUOTE_ALL
    print(f"Cleaned dataset saved to {output_path}\n")


# Process both datasets
clean_dataset('kavitas_cleaned.csv', 'kavitas_cleaned_processed.csv')
clean_dataset('kavitas_remaining.csv', 'kavitas_remaining_processed.csv')

print("Data cleaning complete.")
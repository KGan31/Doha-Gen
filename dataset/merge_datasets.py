import pandas as pd
import os

def merge_datasets(file1, file2, output_file):
    print(f"Merging {file1} and {file2}...")
    
    try:
        # Read both CSVs
        df1 = pd.read_csv(file1)
        print(f"Loaded {len(df1)} rows from {file1}")
        
        df2 = pd.read_csv(file2)
        print(f"Loaded {len(df2)} rows from {file2}")
        
        # Concatenate the dataframes
        merged_df = pd.concat([df1, df2], ignore_index=True)
        print(f"Total rows after merge: {len(merged_df)}")
        
        # Drop strict duplicates across the merged dataset just in case
        initial_len = len(merged_df)
        merged_df = merged_df.drop_duplicates()
        if len(merged_df) < initial_len:
            print(f"Dropped {initial_len - len(merged_df)} duplicate rows after merging.")
        
        # Save to the new file
        merged_df.to_csv(output_file, index=False, quoting=1) # quoting=1 means csv.QUOTE_ALL
        print(f"Successfully saved merged dataset to {output_file}")
        
    except Exception as e:
        print(f"Error during merge: {e}")

if __name__ == "__main__":
    # Define paths
    base_dir = r"c:\Users\kavan\OneDrive\Desktop\IIITH\sem2\inlp\Doha-Gen\dataset"
    file1 = os.path.join(base_dir, "kavitas_cleaned_processed.csv")
    file2 = os.path.join(base_dir, "kavitas_remaining_processed.csv")
    output_file = os.path.join(base_dir, "kavitas_merged.csv")
    
    merge_datasets(file1, file2, output_file)

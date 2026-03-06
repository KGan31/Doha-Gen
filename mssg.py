import google.generativeai as genai
import pandas as pd
import time
import json
import os

# 1. अपनी API Key यहाँ डालें
genai.configure(api_key="AIzaSyBnQbFfySlD4fe2EbJTjsH7oa_PUqd-K5Y")
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. आपकी फ़ाइल लोड करें 
input_file = 'dohas_final_hindi_dataset.csv'
df = pd.read_csv(input_file)

# पहले से प्रोसेस किए गए dohas को स्किप करें
SKIP_FIRST = 7600  # पहले 7600 dohas पहले से ही प्रोसेस हो चुके हैं
df = df.iloc[SKIP_FIRST:].reset_index(drop=True)

BATCH_SIZE = 100  
output_file = 'dohas_nlp_ready_simple_lang.csv'

if not os.path.exists(output_file):
    new_columns = list(df.columns)
    if "Core_Message" not in new_columns:
        new_columns.append("Core_Message")
    pd.DataFrame(columns=new_columns).to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"Skipping first {SKIP_FIRST} already processed dohas")
print(f"Remaining Dohas to process: {len(df)}")
print(f"Total batches to run: {len(df) // BATCH_SIZE + 1}\n")

for i in range(0, len(df), BATCH_SIZE):
    batch_df = df.iloc[i:i+BATCH_SIZE].copy().fillna("")
    batch_data = batch_df[['Doha', 'Theme', 'Context']].to_dict(orient='records')
    
    # 🌟 यहाँ प्रॉम्प्ट को पूरी तरह से "आम बोलचाल की भाषा" के लिए बदल दिया गया है 🌟
    prompt = f"""
    You are an expert at understanding what normal internet users search for. 
    I will provide you with a list of {len(batch_data)} Dohas along with their Theme and Context.
    
    Your ONLY job is to generate an **ULTRA-SHORT 'Core_Message' (Maximum 2 to 4 words)** for each Doha.
    CRITICAL RULE: The Core_Message MUST be in very simple, everyday spoken Hindi (written in Devanagari script). 
    Think exactly like a normal teenager or a casual user typing in a search bar. DO NOT use tough or classical Hindi words.
    
    Good Examples (Simple): "जिंदगी की सच्चाई", "सच्चा प्यार", "पैसे का लालच", "पति पत्नी का प्यार", "दिखावा करना", "भगवान की याद", "प्यार में धोखा", "समय की अहमियत".
    Bad Examples (Too Formal): "जीवन की नश्वरता", "दांपत्य प्रेम", "विरह वेदना", "आत्म-चिंतन".

    Return ONLY a strictly valid JSON array containing exactly {len(batch_data)} objects. No markdown formatting.
    The JSON structure MUST be:
    [
      {{"Core_Message": "..."}},
      ...
    ]
    
    Here is the data:
    {json.dumps(batch_data, ensure_ascii=False)}
    """
    
    try:
        print(f"Processing batch {i//BATCH_SIZE + 1}...")
        response = model.generate_content(prompt)
        
        clean_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        batch_results = json.loads(clean_text)
        
        if len(batch_results) == len(batch_df):
            batch_df['Core_Message'] = [res.get('Core_Message', '') for res in batch_results]
            batch_df.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8-sig')
            print(f"Batch {i//BATCH_SIZE + 1} saved successfully!")
        else:
            print(f"Mismatch in Batch {i//BATCH_SIZE + 1}. Expected {len(batch_df)}, got {len(batch_results)}. Skipping.")
            
    except Exception as e:
        print(f"Error on batch {i//BATCH_SIZE + 1}. Error: {e}")
    
    time.sleep(7)

print(f"\nProcessing complete! Your final super-simple NLP dataset is at: {output_file}")
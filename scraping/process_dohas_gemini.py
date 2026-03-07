import google.generativeai as genai
import pandas as pd
import time
import json
import os

# 1. अपना API Key यहाँ डालें (इसे स्ट्रिंग " " के अंदर ही रखें)
genai.configure(api_key="AIzaSyAx_uVyxjWH92mpNAkdMVmI_SA_JGeKY2I")  # ⬅️ अपनी नई API Key यहाँ डालें

# फ़ास्ट प्रोसेसिंग और 1000 RPD (Requests Per Day) फ्री लिमिट के लिए Gemini 2.5 Flash
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. आपकी CSV फ़ाइल लोड करें (फ़ाइल उसी फोल्डर में होनी चाहिए जहाँ यह स्क्रिप्ट है)
input_file = 'kavitakosh_dohas_split.csv'
df = pd.read_csv(input_file)

# 3. सेटिंग्स (बैच साइज़ 100)
BATCH_SIZE = 100  # ⬅️ Batch size increased to 100
SKIP_ROWS = 6949  # ⬅️ पहले के 6949 dohas को छोड़ दो (already processed)
output_file = 'dohas_final_hindi_dataset.csv'

# Skip already processed rows
df = df.iloc[SKIP_ROWS:]

print(f"Skipping first {SKIP_ROWS} dohas (already processed)")
print(f"Remaining Dohas to process: {len(df)}")
print(f"Total batches to run: {len(df) // BATCH_SIZE + 1}\n")
print(f"Remaining Dohas to process: {len(df)}")
print(f"Total batches to run: {len(df) // BATCH_SIZE + 1}\n")
print(f"Remaining Dohas to process: {len(df)}")
print(f"Total batches to run: {len(df) // BATCH_SIZE + 1}\n")
print(f"Remaining Dohas to process: {len(df)}")
print(f"Total batches to run: {len(df) // BATCH_SIZE + 1}\n")
print(f"Remaining Dohas to process: {len(df)}")
print(f"Total batches to run: {len(df) // BATCH_SIZE + 1}\n")
print(f"Remaining Dohas to process: {len(df)}")
print(f"Total batches to run: {len(df) // BATCH_SIZE + 1}\n")

# अगर फाइल पहले से नहीं है, तो हेडर के साथ एक खाली फाइल बनाएँ
if not os.path.exists(output_file):
    # पुरानी सभी कॉलम्स के साथ 'Theme' और 'Context' जोड़ें
    new_columns = list(df.columns) + ["Theme", "Context"]
    pd.DataFrame(columns=new_columns).to_csv(output_file, index=False, encoding='utf-8-sig')

# 4. बैच प्रोसेसिंग शुरू
for i in range(0, len(df), BATCH_SIZE):
    batch_df = df.iloc[i:i+BATCH_SIZE]
    batch_dohas = batch_df['Doha'].tolist()
    
    # मॉडल के लिए प्रॉम्प्ट (हिंदी में आउटपुट के लिए)
    prompt = f"""
    You are an expert in classical Hindi literature, Ritikal poetry, and Bhakti Kavya. 
    I will provide you with a list of {len(batch_dohas)} Dohas.
    For each Doha, provide:
    1. A 'Theme' - MUST be ONLY ONE BROAD WORD in Hindi. Choose from these ~70 broad themes:
       
       Love & Romance: शृंगार, सौंदर्य, प्रेम, विरह, मिलन, नायिका, रूप, मोह, रति, विवाह
       
       Devotion & Spirituality: भक्ति, आध्यात्म, ईश्वर, धर्म, साधना, माया, मोक्ष, पूजा, तीर्थ, मंत्र, संत, कृष्ण
       
       Wisdom & Philosophy: नीति, ज्ञान, दर्शन, सत्य, विवेक, योग, कर्म, भाग्य, काल, समय, धैर्य, त्याग, दान, तप, संयम
       
       Emotions: करुण, वीर, हास्य, रौद्र, भय, वीभत्स, अद्भुत, शांत
       
       Life & Society: सामाजिक, जीवन, वैराग्य, संसार, उपदेश, स्वभाव, मित्रता, शत्रुता, राजनीति, न्याय
       
       Nature: प्रकृति, ऋतु, रात, दिवस, चंद्र, सूर्य, वर्षा, वसंत
       
       Others: रीति, गुरु, मृत्यु, जन्म, शिक्षा
       
       Use ONLY one word from above. If needed, you can use similar broad words, but avoid specific compound words like केशसौंदर्य, नखसौंदर्य.
       
    2. A brief 'Context' (in Hindi) explaining the meaning and essence of the Doha in simple terms.

    Return ONLY a strictly valid JSON array containing exactly {len(batch_dohas)} objects. No markdown, no extra text.
    The JSON structure MUST be:
    [
      {{"Theme": "...", "Context": "..."}},
      ...
    ]
    
    Here are the Dohas:
    {json.dumps(batch_dohas, ensure_ascii=False)}
    """
    
    try:
        print(f"Processing batch {i//BATCH_SIZE + 1}...")
        response = model.generate_content(prompt)
        
        # JSON टेक्स्ट को क्लीन करना
        clean_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        batch_results = json.loads(clean_text)
        
        # चेक करें कि मॉडल ने उतने ही रिज़ल्ट दिए हैं जितने दोहे भेजे गए थे
        if len(batch_results) == len(batch_df):
            # नए कॉलम्स को ओरिजिनल डेटाफ्रेम बैच में जोड़ें
            batch_df = batch_df.copy()
            batch_df['Theme'] = [res.get('Theme', '') for res in batch_results]
            batch_df['Context'] = [res.get('Context', '') for res in batch_results]
            
            # डेटा को तुरंत CSV में सेव करें
            batch_df.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8-sig')
            print(f"Batch {i//BATCH_SIZE + 1} saved successfully!")
        else:
            print(f"Mismatch in Batch {i//BATCH_SIZE + 1}. Expected {len(batch_df)}, got {len(batch_results)}. Skipping this batch to avoid data corruption.")
            
    except Exception as e:
        print(f"Error on batch {i//BATCH_SIZE + 1}. Error: {e}")
    
    # 5. RPM (Requests Per Minute) लिमिट को बनाए रखने के लिए 7 सेकंड रुकें
    # Gemini Free Tier में 15 RPM की लिमिट होती है, 7 सेकंड रुकने से हम पूरी तरह सुरक्षित रहेंगे।
    time.sleep(7)

print(f"\nProcessing complete! Your final dataset is ready at: {output_file}")

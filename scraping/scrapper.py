import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin, unquote


BASE_CATEGORY = "https://kavitakosh.org/kk/श्रेणी:दोहा"
BASE_URL = "https://kavitakosh.org"


HEADERS = {
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/100.0 Safari/537.36"
}


all_links = []


print("📌 Collecting links from category pages...")


current_url = BASE_CATEGORY
page_count = 0


while current_url:
   print(f"➡️ Fetching page {page_count + 1}...")
   resp = requests.get(current_url, headers=HEADERS)
   soup = BeautifulSoup(resp.text, "html.parser")


   items = soup.select("#mw-pages a")
  
   for a in items:
       href = a.get("href")
       text = a.get_text().strip()
      
       if "अगले" in text or "पिछले" in text or "next" in text.lower() or "previous" in text.lower():
           continue
          
       if href and "/kk/" in href and "श्रेणी:" not in href:
           full_link = urljoin(BASE_URL, href)
           if full_link not in all_links:
               all_links.append(full_link)


   print(f"   Found {len(items)} links on this page. Total: {len(all_links)}")
  
   next_link = None
   for link in soup.select("a"):
       if "अगले" in link.get_text() or "next" in link.get_text().lower():
           next_href = link.get("href")
           if next_href:
               next_link = urljoin(BASE_URL, next_href)
               break
  
   if next_link and next_link != current_url:
       current_url = next_link
       page_count += 1
       time.sleep(1)  
   else:
       break


print(f"✅ Total unique Dohas found: {len(all_links)}\n")


data = []
csv_filename = "../dataset/kavitakosh_dohas_full.csv"


print("📌 Now scraping each Doha page...\n")


df_header = pd.DataFrame(columns=["Title", "Author", "Doha", "URL"])
df_header.to_csv(csv_filename, index=False, encoding="utf-8-sig")


for i, link in enumerate(all_links, start=1):
   try:
       r = requests.get(link, headers=HEADERS, timeout=10)
       s = BeautifulSoup(r.text, "html.parser")


       title_tag = s.find("h1")
       title = title_tag.text.strip() if title_tag else ""


       author = ""
       if " / " in title:
           parts = title.split(" / ")
           if len(parts) >= 2:
               author = parts[-1].strip()


       doha_text = ""
      
       poem_div = s.find("div", class_="poem")
       if poem_div:
           doha_text = poem_div.get_text(separator="\n", strip=True)
      
       if not doha_text:
           content_div = s.find("div", id="mw-content-text")
           if content_div:
               for unwanted in content_div.find_all(['script', 'style', 'nav', 'footer']):
                   unwanted.decompose()
               doha_text = content_div.get_text(separator="\n", strip=True)
              
               lines = doha_text.split('\n')
               cleaned_lines = []
               skip_patterns = ['हिन्दी/उर्दू', 'Script', 'Devanagari', 'Roman',
                               'श्रेणियाँ:', 'इस पन्ने को शेयर करें', 'हमसे जुड़ें']
              
               for line in lines:
                   line = line.strip()
                   if line and not any(pattern in line for pattern in skip_patterns):
                       if len(line) > 10:  
                           cleaned_lines.append(line)
              
               doha_text = '\n'.join(cleaned_lines[:50])  


       row_data = {
           "Title": title,
           "Author": author,
           "Doha": doha_text.strip(),
           "URL": link
       }
      
       data.append(row_data)


       if i % 10 == 0:
           df = pd.DataFrame(data)
           df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
           print(f"💾 Saved {i} dohas to CSV")


       print(f"📝 {i}/{len(all_links)} — {title}")
       time.sleep(0.6)  
      
   except Exception as e:
       print(f"❌ Error scraping {link}: {str(e)}")
       continue


df = pd.DataFrame(data)
df.to_csv(csv_filename, index=False, encoding="utf-8-sig")


print(f"\n🎉 ALL DONE!")
print(f"Saved {len(data)} dohas to: {csv_filename}")

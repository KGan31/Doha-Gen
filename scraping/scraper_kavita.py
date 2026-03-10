import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin, quote

BASE_URL = "https://kavitakosh.org"
POETS_LIST_URL = "https://kavitakosh.org/kk/%E0%A4%B0%E0%A4%9A%E0%A4%A8%E0%A4%BE%E0%A4%95%E0%A4%BE%E0%A4%B0%E0%A5%8B%E0%A4%82_%E0%A4%95%E0%A5%80_%E0%A4%B8%E0%A5%82%E0%A4%9A%E0%A5%80"

def get_page_content(url, retries=3):
    """Get page content with retry logic"""
    for i in range(retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Attempt {i+1} failed for {url}: {str(e)}")
            if i < retries - 1:
                time.sleep(2)
            else:
                return None
    return None

def get_poets_list():
    """Get list of all poets from the main page"""
    print("Fetching poets list...")
    html_content = get_page_content(POETS_LIST_URL)
    
    if not html_content:
        print("Failed to fetch poets list")
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    poets = []
    
    content_div = soup.find('div', {'id': 'mw-content-text'})
    if content_div:
        links = content_div.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if (href.startswith('/kk/') and 
                'action=edit' not in href and
                '%E0%A4%B0%E0%A4%9A%E0%A4%A8%E0%A4%BE%E0%A4%95%E0%A4%BE%E0%A4%B0%E0%A5%8B%E0%A4%82_%E0%A4%95%E0%A5%80_%E0%A4%B8%E0%A5%82%E0%A4%9A%E0%A5%80' not in href):
                poet_name = link.get_text(strip=True)
                poet_url = urljoin(BASE_URL, href)
                if poet_name and poet_url:
                    poets.append({
                        'name': poet_name,
                        'url': poet_url
                    })
    
    unique_poets = []
    seen_urls = set()
    for poet in poets:
        if poet['url'] not in seen_urls:
            unique_poets.append(poet)
            seen_urls.add(poet['url'])
    
    print(f"Found {len(unique_poets)} poets")
    return unique_poets

def get_kavita_text(kavita_url):
    """Extract the actual kavita (poem) text from a kavita page"""
    html_content = get_page_content(kavita_url)
    
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    content_div = soup.find('div', {'id': 'mw-content-text'})
    if not content_div:
        return ""
    
    poem_div = content_div.find('div', {'class': 'mw-parser-output'})
    if not poem_div:
        poem_div = content_div
    
    for tag in poem_div(['script', 'style', 'nav', 'header', 'footer', 'table', 'ul', 'ol']):
        tag.decompose()
    
    for tag in poem_div.find_all('span', {'class': 'mw-editsection'}):
        tag.decompose()
    
    for tag in poem_div.find_all('div', {'class': ['noprint', 'toc', 'mw-navigation', 'navbox', 'infobox', 'metadata', 'thumb']}):
        tag.decompose()
    
    for tag in poem_div.find_all('div', {'id': 'catlinks'}):
        tag.decompose()
    
    for tag in poem_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        tag.decompose()
    
    for tag in poem_div.find_all('a'):
        tag.unwrap()
    
    paragraphs = poem_div.find_all('p')
    poem_lines = []
    
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and len(text) > 15:  
            poem_lines.append(text)
    
    if poem_lines:
        poem_text = '\n\n'.join(poem_lines)
    else:
        poem_text = poem_div.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in poem_text.split('\n') if line.strip()]
        poem_lines = lines
    
    filtered_lines = []
    
    skip_keywords = [
        'हिन्दी/उर्दू', 'अंगिका', 'अवधी', 'गुजराती', 'नेपाली', 'भोजपुरी', 
        'मैथिली', 'राजस्थानी', 'हरियाणवी', 'अन्य भाषाएँ',
        'Script', 'Devanagari', 'Roman', 'Gujarati', 'Gurmukhi', 'Bangla', 
        'Diacritic', 'IPA', '»',
        'कविता कोश', '@', 'ईमेल', 'email', 'संपर्क', 'दूरभाष', 'फोन', 'Phone', 
        'Contact', 'मोबाइल', 'फ़ोन',
        'पुरस्कार', 'सम्मान', 'सम्मानित', 'पुरस्कृत',
        'इस पन्ने पर', 'स्वयंसेवी', 'योगदानकर्ताओं', 'प्रकाशक', 'प्रकाशन',
        'पुस्तक खरीदने', 'सूचित करें', 'विश्व भर', 'संकलित', 'स्रोतों',
        'कविता कोश में', 'जानकारी छपी', 'चित्र:--', 'ऊपर दी गई',
        'भिन्न-भिन्न', 'हेतु आपकी', 'सहायता',
        'रचनाकार', 'जन्म :', 'जन्म-', 'शिक्षा :', 'शिक्षा-', 'कृतियाँ :', 
        'रचनाएँ :', 'पता :', 'संपादक', 'लेखक', 'कवि', 'साहित्यकार',
        'जीवन परिचय', 'परिचय', 'कवि परिचय',
        'प्रकाशित', 'संस्करण', 'ISBN', 'मूल्य', 'पृष्ठ',
        'पढ़ें', 'देखें', 'सम्बंधित', 'अन्य रचनाएँ', 'इन्हें भी देखें',
        'कविता संग्रह', 'काव्य संग्रह', 'रचना संग्रह',
    ]
    
    date_pattern = re.compile(r'\d{1,2}\s*(?:जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितम्बर|अक्टूबर|नवम्बर|दिसम्बर|January|February|March|April|May|June|July|August|September|October|November|December)', re.IGNORECASE)
    location_date_pattern = re.compile(r'^[^,]+,\s*\d')
    year_pattern = re.compile(r'^\d{4}$')
    phone_pattern = re.compile(r'\d{10}|\d{3}[-.\s]\d{3}[-.\s]\d{4}')
    
    for line in poem_lines if isinstance(poem_lines, list) else [poem_text]:
        line = line.strip()
        
        if len(line) <= 5:  
            continue
            
        should_skip = False
        
        for keyword in skip_keywords:
            if keyword.lower() in line.lower():
                should_skip = True
                break
        
        if should_skip:
            continue
            
        if date_pattern.search(line):
            continue
        if location_date_pattern.match(line):
            continue
        if year_pattern.match(line):
            continue
        if phone_pattern.search(line):
            continue
        if '@' in line or 'http' in line or 'www' in line:
            continue
        
        if line.count('/') > 2:
            continue
            
        if re.match(r'^[\d\s\-–—.,;:!?()]+$', line):
            continue
        
        filtered_lines.append(line)
    
    poem_text = '\n'.join(filtered_lines)
    
    poem_text = re.sub(r'\n{3,}', '\n\n', poem_text)
    
    return poem_text.strip()

def get_kavitas_from_poet_page(poet_name, poet_url, csv_filename):
    """Get all kavitas from a poet's page and save each one immediately"""
    print(f"Fetching kavitas for {poet_name}...")
    html_content = get_page_content(poet_url)
    
    if not html_content:
        print(f"Failed to fetch page for {poet_name}")
        return 0
    
    soup = BeautifulSoup(html_content, 'html.parser')
    kavitas_count = 0
    
    content_div = soup.find('div', {'id': 'mw-content-text'})
    if content_div:
        links = content_div.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            kavita_title = link.get_text(strip=True)
            
            if (href.startswith('/kk/') and 
                'action=edit' not in href and
                'श्रेणी:' not in kavita_title and
                'Category:' not in kavita_title and
                'File:' not in href and
                'चित्र:' not in kavita_title and
                'परिचय' not in kavita_title and  
                'जीवन परिचय' not in kavita_title and
                'रचनाकार' not in kavita_title and
                'कवि परिचय' not in kavita_title and
                kavita_title != poet_name and  
                len(kavita_title) > 0):
                
                kavita_url = urljoin(BASE_URL, href)
                
                print(f"  Fetching: {kavita_title}")
                kavita_text = get_kavita_text(kavita_url)
                
                kavita_data = {
                    'poet_name': poet_name,
                    'kavita_name': kavita_title,
                    'kavita_text': kavita_text,
                    'kavita_url': kavita_url
                }
                
                save_single_kavita(kavita_data, csv_filename)
                kavitas_count += 1
                print(f"    ✓ Saved ({kavitas_count} total)")
                
                time.sleep(0.5)
    
    print(f"Found {kavitas_count} kavitas for {poet_name}")
    return kavitas_count

def scrape_kavitakosh(max_poets=None, skip_poets=0):
    """Main scraping function"""
    print("Starting Kavitakosh scraper...")
    
    poets = get_poets_list()
    
    print(f"Total poets found: {len(poets)}")
    
    if skip_poets > 0:
        print(f"⏭️  Skipping first {skip_poets} poets (already scraped)")
        poets = poets[skip_poets:]
        print(f"Remaining poets to scrape: {len(poets)}")
    
    if max_poets:
        poets = poets[:max_poets]
        print(f"Limiting to first {max_poets} of remaining poets")
    
    filename = 'kavitas_remaining.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['poet_name', 'kavita_name', 'kavita_text', 'kavita_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    
    total_kavitas = 0
    
    for i, poet in enumerate(poets, 1):
        print(f"\n[{i}/{len(poets)}] Processing: {poet['name']}")
        
        kavitas_count = get_kavitas_from_poet_page(poet['name'], poet['url'], filename)
        
        total_kavitas += kavitas_count
        print(f"Total kavitas so far: {total_kavitas}")
        
        time.sleep(1)
    
    print(f"\n\nScraping complete! Total kavitas found: {total_kavitas}")
    
    return total_kavitas

def save_to_csv(kavitas, filename):
    """Save kavitas to CSV file"""
    if not kavitas:
        print("No kavitas to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['poet_name', 'kavita_name', 'kavita_text', 'kavita_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for kavita in kavitas:
            writer.writerow(kavita)
    
    print(f"Saved {len(kavitas)} kavitas to {filename}")

def save_kavitas_append(kavitas, filename):
    """Append kavitas to existing CSV file"""
    if not kavitas:
        return
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['poet_name', 'kavita_name', 'kavita_text', 'kavita_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        for kavita in kavitas:
            writer.writerow(kavita)

def save_single_kavita(kavita, filename):
    """Save a single kavita immediately to CSV file"""
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['poet_name', 'kavita_name', 'kavita_text', 'kavita_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(kavita)

if __name__ == "__main__":
    
    print("=" * 60)
    print("Kavitakosh Scraper - Remaining Poets")
    print("=" * 60)
    print("\nThis will scrape poet names, kavita names, and URLs")
    print("from Kavitakosh.org\n")
    print("⏭️  SKIPPING first 1885 poets (already scraped)")
    print("Kavitas will be saved continuously to: kavitas_remaining.csv")
    print("=" * 60)
    
    SKIP_POETS = 1885  
    MAX_POETS = None   
    
    total = scrape_kavitakosh(max_poets=MAX_POETS, skip_poets=SKIP_POETS)
    
    print(f"\n{'=' * 60}")
    print(f"Scraping completed!")
    print(f"Poets skipped: {SKIP_POETS}")
    print(f"Total new kavitas found: {total}")
    print(f"Results saved to: kavitas_remaining.csv")
    print(f"{'=' * 60}")
 
import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin, quote

# Base URL
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
    
    # Find all links to poet pages
    # Looking for links within the content div
    content_div = soup.find('div', {'id': 'mw-content-text'})
    if content_div:
        links = content_div.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            # Skip non-poet links
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
    
    # Remove duplicates
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
    
    # Find the main content div
    content_div = soup.find('div', {'id': 'mw-content-text'})
    if not content_div:
        return ""
    
    # Extract text from the poem div
    poem_div = content_div.find('div', {'class': 'mw-parser-output'})
    if not poem_div:
        poem_div = content_div
    
    # Remove unwanted elements
    for tag in poem_div(['script', 'style', 'nav', 'header', 'footer', 'table']):
        tag.decompose()
    
    # Remove edit links and other metadata
    for tag in poem_div.find_all('span', {'class': 'mw-editsection'}):
        tag.decompose()
    
    # Remove navigation menus (divs with specific classes/ids)
    for tag in poem_div.find_all('div', {'class': ['noprint', 'toc', 'mw-navigation', 'navbox']}):
        tag.decompose()
    
    # Remove infoboxes and other metadata boxes
    for tag in poem_div.find_all('div', {'class': ['infobox', 'metadata']}):
        tag.decompose()
    
    # Remove category links
    for tag in poem_div.find_all('div', {'id': 'catlinks'}):
        tag.decompose()
    
    # Remove language/script selector lists
    for tag in poem_div.find_all('ul'):
        ul_text = tag.get_text(strip=True)
        # Check if it's a language menu or script selector
        if any(keyword in ul_text for keyword in ['हिन्दी/उर्दू', 'Devanagari', 'Roman', 'Script', 'अन्य भाषाएँ']):
            tag.decompose()
    
    # Remove all <a> tags but keep their text (removes links to other pages)
    for tag in poem_div.find_all('a'):
        tag.unwrap()
    
    # Find all <p> tags which usually contain the poem
    paragraphs = poem_div.find_all('p')
    poem_lines = []
    
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and len(text) > 10:  # Filter out very short paragraphs
            poem_lines.append(text)
    
    # If we found paragraph content, use it
    if poem_lines:
        poem_text = '\n\n'.join(poem_lines)
    else:
        # Fallback: get all text
        poem_text = poem_div.get_text(separator='\n', strip=True)
        
        # Clean up extra whitespace
        lines = [line.strip() for line in poem_text.split('\n') if line.strip()]
        
        # Filter out navigation-like lines
        filtered_lines = []
        skip_keywords = [
            'हिन्दी/उर्दू', 'अंगिका', 'अवधी', 'गुजराती', 'नेपाली', 
            'भोजपुरी', 'मैथिली', 'राजस्थानी', 'हरियाणवी', 'अन्य भाषाएँ',
            'Script', 'Devanagari', 'Roman', 'Gujarati', 'Gurmukhi', 
            'Bangla', 'Diacritic', 'IPA', '»',
            'कविता कोश टीम', '@', 'ईमेल', 'email', 'संपर्क', 'दूरभाष',
            'पुरस्कार', 'सम्मान', 'फोन', 'Phone', 'Contact',
            'इस पन्ने पर दी गई', 'स्वयंसेवी योगदानकर्ताओं', 'प्रकाशक संबंधी',
            'पुस्तक खरीदने', 'सूचित करें', 'विश्व भर के', 'संकलित किया',
            'कविता कोश में', 'जानकारी छपी', 'चित्र:--', 'ऊपर दी गई',
            'भिन्न-भिन्न स्रोतों', 'हेतु आपकी सहायता', 'रचनाकार',
            'जन्म :', 'शिक्षा :', 'प्रकाशित', 'संपादक', 'लेखक',
            'कृतियाँ :', 'रचनाएँ :', 'पता :', 'मोबाइल', 'फ़ोन'
        ]
        
        # Pattern to detect date-like strings (e.g., "दिल्ली, 1 नवम्बर, 1954")
        import re
        date_pattern = re.compile(r'\d{1,2}\s*(?:जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितम्बर|अक्टूबर|नवम्बर|दिसम्बर|January|February|March|April|May|June|July|August|September|October|November|December)')
        
        for line in lines:
            # Skip lines that are clearly navigation or contact info or metadata
            should_skip = False
            for keyword in skip_keywords:
                if keyword in line:
                    should_skip = True
                    break
            
            # Check if line contains date pattern
            if date_pattern.search(line):
                should_skip = True
            
            # Skip lines that start with location/date format (e.g., "दिल्ली, ")
            if re.match(r'^[^,]+,\s*\d', line):
                should_skip = True
            
            if not should_skip:
                # Skip lines that look like email addresses or URLs
                if '@' not in line and 'http' not in line:
                    # Skip very short lines (likely not poem content)
                    if len(line) > 5:
                        # Skip lines that are just numbers or dates
                        if not re.match(r'^\d{4}$', line.strip()):
                            filtered_lines.append(line)
        
        poem_text = '\n'.join(filtered_lines)
    
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
    
    # Find all links in the content area
    content_div = soup.find('div', {'id': 'mw-content-text'})
    if content_div:
        # Look for links that might be kavitas
        links = content_div.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            kavita_title = link.get_text(strip=True)
            
            # Filter to get only kavita links (skip edit, category, file links)
            if (href.startswith('/kk/') and 
                'action=edit' not in href and
                'श्रेणी:' not in kavita_title and
                'Category:' not in kavita_title and
                'File:' not in href and
                'चित्र:' not in kavita_title and
                'परिचय' not in kavita_title and  # Skip biography pages
                'जीवन परिचय' not in kavita_title and
                'रचनाकार' not in kavita_title and
                'कवि परिचय' not in kavita_title and
                kavita_title != poet_name and  # Skip self-reference
                len(kavita_title) > 0):
                
                kavita_url = urljoin(BASE_URL, href)
                
                # Fetch the actual kavita text
                print(f"  Fetching: {kavita_title}")
                kavita_text = get_kavita_text(kavita_url)
                
                kavita_data = {
                    'poet_name': poet_name,
                    'kavita_name': kavita_title,
                    'kavita_text': kavita_text,
                    'kavita_url': kavita_url
                }
                
                # Save immediately after fetching each kavita
                save_single_kavita(kavita_data, csv_filename)
                kavitas_count += 1
                print(f"    ✓ Saved ({kavitas_count} total)")
                
                # Small delay between kavita fetches
                time.sleep(0.5)
    
    print(f"Found {kavitas_count} kavitas for {poet_name}")
    return kavitas_count

def scrape_kavitakosh(max_poets=None):
    """Main scraping function"""
    print("Starting Kavitakosh scraper...")
    
    # Get all poets
    poets = get_poets_list()
    
    if max_poets:
        poets = poets[:max_poets]
        print(f"Limiting to first {max_poets} poets")
    
    # Initialize CSV file with headers
    filename = 'kavitas_complete.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['poet_name', 'kavita_name', 'kavita_text', 'kavita_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    
    total_kavitas = 0
    
    # Iterate through each poet
    for i, poet in enumerate(poets, 1):
        print(f"\n[{i}/{len(poets)}] Processing: {poet['name']}")
        
        # Get kavitas for this poet (saves each one immediately)
        kavitas_count = get_kavitas_from_poet_page(poet['name'], poet['url'], filename)
        
        total_kavitas += kavitas_count
        print(f"Total kavitas so far: {total_kavitas}")
        
        # Be nice to the server
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
    # You can set max_poets to limit the number of poets to scrape
    # For testing, use a small number like 5
    # For full scrape, set it to None
    
    print("=" * 60)
    print("Kavitakosh Scraper")
    print("=" * 60)
    print("\nThis will scrape poet names, kavita names, and URLs")
    print("from Kavitakosh.org\n")
    print("Kavitas will be saved continuously to: kavitas_complete.csv")
    print("=" * 60)
    
    # Start with a small number for testing
    # Change to None for full scrape
    MAX_POETS = None  # Set to None to scrape all poets, or a number to limit
    
    total = scrape_kavitakosh(max_poets=MAX_POETS)
    
    print(f"\n{'=' * 60}")
    print(f"Scraping completed!")
    print(f"Total poets processed: {MAX_POETS if MAX_POETS else 'ALL'}")
    print(f"Total kavitas found: {total}")
    print(f"Results saved to: kavitas_complete.csv")
    print(f"{'=' * 60}")
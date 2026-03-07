"""
Complete Braj Bhasha Poetry Scraper
Extracts: Poet Name | Poem Title | Poem URL | Poem Content
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urljoin
from datetime import datetime

class CompleteBrajScraper:
    def __init__(self):
        self.base_url = "https://kavitakosh.org"
        self.main_page = "https://kavitakosh.org/kk/%E0%A4%AC%E0%A5%8D%E0%A4%B0%E0%A4%9C_%E0%A4%AD%E0%A4%BE%E0%A4%B7%E0%A4%BE"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.delay = 1.5
        self.all_poems = []
        
    def get_page(self, url, retries=3):
        """Fetch a page with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(self.delay * 2)
                    continue
                return None
        return None
    
    def get_poets_from_main_page(self):
        """Get all poet links from main Braj page"""
        print("Fetching poets from main Braj Bhasha page...")
        response = self.get_page(self.main_page)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        poets = []
        
        content = soup.find('div', {'id': 'mw-content-text'})
        if content:
            for link in content.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if (href.startswith('/kk/') and 
                    ':' not in href and 
                    'action=' not in href and
                    'index.php' not in href and
                    text and 
                    len(text) > 1 and
                    href != '/kk/%E0%A4%AC%E0%A5%8D%E0%A4%B0%E0%A4%9C_%E0%A4%AD%E0%A4%BE%E0%A4%B7%E0%A4%BE'):
                    
                    full_url = urljoin(self.base_url, href)
                    
                    if not any(p['url'] == full_url for p in poets):
                        poets.append({
                            'name': text,
                            'url': full_url
                        })
        
        print(f"Found {len(poets)} poets\n")
        return poets
    
    def extract_poem_content(self, poem_url):
        """Extract the actual poem text from a poem page"""
        response = self.get_page(poem_url)
        if not response:
            return ""
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main content area
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return ""
        
        # Strategy: Get all paragraphs and text, skip navigation/metadata
        poem_lines = []
        
        # Find all p tags and divs with text
        for element in content_div.find_all(['p', 'div']):
            # Skip navigation, categories, and metadata
            if element.get('class'):
                classes = ' '.join(element.get('class', []))
                if any(skip in classes for skip in ['catlinks', 'printfooter', 'mw-', 'navbox']):
                    continue
            
            text = element.get_text(strip=True)
            
            # Filter: must be substantial text, not just navigation
            if text and len(text) > 20:
                # Skip certain patterns
                skip_patterns = ['यहाँ जाएँ:', 'नेविगेशन', 'खोज', 'श्रेणियाँ:', 
                                'इस पन्ने को शेयर', 'कविता कोश', 'हमसे जुड़ें',
                                'Script', 'Devanagari', 'हिन्दी/उर्दू']
                
                should_skip = any(pattern in text for pattern in skip_patterns)
                
                if not should_skip:
                    poem_lines.append(text)
        
        # Join and return the poem content
        poem_content = '\n\n'.join(poem_lines)
        return poem_content.strip()
    
    def get_poems_from_poet_page(self, poet_name, poet_url):
        """Get all poem links from a poet's page"""
        print(f"  Processing: {poet_name}")
        response = self.get_page(poet_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        poems = []
        
        content = soup.find('div', {'id': 'mw-content-text'})
        if not content:
            return []
        
        # Get all links
        for link in content.find_all('a', href=True):
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if (href.startswith('/kk/') and 
                'action=' not in href and
                'redlink' not in href and
                ':' not in href and
                'index.php' not in href):
                
                full_url = urljoin(self.base_url, href)
                
                if full_url == poet_url:
                    continue
                
                # Clean the title
                if ' / ' in title:
                    title = title.split(' / ')[0].strip()
                
                # Filter out navigation links
                skip_keywords = ['परिचय', 'श्रेणी', 'विशेष', 'सहायता', 'चर्चा', 
                                'कविता कोश', 'विषय सूची', 'नेविगेशन']
                
                if title and len(title) > 2:
                    should_skip = any(keyword in title or keyword in full_url 
                                     for keyword in skip_keywords)
                    
                    if not should_skip:
                        if not any(p['poem_url'] == full_url for p in poems):
                            poems.append({
                                'poet_name': poet_name,
                                'poem_title': title,
                                'poem_url': full_url
                            })
        
        print(f"    Found {len(poems)} poem links, now fetching content...")
        
        # Now fetch content for each poem
        for i, poem in enumerate(poems, 1):
            print(f"      [{i}/{len(poems)}] {poem['poem_title'][:50]}...")
            poem['poem_content'] = self.extract_poem_content(poem['poem_url'])
            time.sleep(self.delay)  # Be respectful to the server
        
        return poems
    
    def scrape_all(self):
        """Main scraping function"""
        print("=" * 60)
        print("COMPLETE BRAJ BHASHA POETRY SCRAPER")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Get all poets
        poets = self.get_poets_from_main_page()
        
        # Process each poet
        for i, poet in enumerate(poets, 1):
            print(f"\n[{i}/{len(poets)}] {poet['name']}")
            
            poems = self.get_poems_from_poet_page(poet['name'], poet['url'])
            self.all_poems.extend(poems)
            
            time.sleep(self.delay)
        
        print("\n" + "=" * 60)
        print(f"Scraping completed!")
        print(f"Total poems with content: {len(self.all_poems)}")
        print("=" * 60)
        
        return self.all_poems
    
    def save_to_csv(self, filename='braj_poems_complete.csv'):
        """Save to CSV file with poem content"""
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Poet Name', 'Poem Title', 'Poem URL', 'Poem Content'])
            
            for poem in self.all_poems:
                writer.writerow([
                    poem['poet_name'],
                    poem['poem_title'],
                    poem['poem_url'],
                    poem['poem_content']
                ])
        
        print(f"\nSaved to: {filename}")
        
        # Show statistics
        from collections import Counter
        poet_counts = Counter(p['poet_name'] for p in self.all_poems)
        print(f"\nTop 10 poets by poem count:")
        for poet, count in poet_counts.most_common(10):
            print(f"  {poet}: {count} poems")
        
        # Show poems with most content
        poems_with_content = [p for p in self.all_poems if p.get('poem_content')]
        print(f"\nTotal poems with content: {len(poems_with_content)}")


def main():
    scraper = CompleteBrajScraper()
    scraper.scrape_all()
    scraper.save_to_csv('../dataset/braj_poems_complete.csv')
    print("\n✓ Done! Check braj_poems_complete.csv")


if __name__ == "__main__":
    main()

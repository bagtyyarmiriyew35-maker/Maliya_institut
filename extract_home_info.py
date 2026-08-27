import urllib.request
import ssl
from bs4 import BeautifulSoup
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

URL = "https://tdmai.edu.tm/?/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

def fetch_page(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            return response.read()
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    html = fetch_page(URL)
    if not html:
        print("Failed to fetch.")
        return
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Slider / Banner images
    sliders = []
    # Look for slider list items or containers
    slider_container = soup.find(class_='slider-container')
    if slider_container:
        for li in slider_container.find_all('li'):
            img = li.find('img')
            title = li.find(class_='tp-caption') # or similar class
            sliders.append({
                "img": img.get('src', '') if img else '',
                "caption": title.get_text(strip=True) if title else ''
            })
            
    # 2. News / Habarlar
    news = []
    # Usually news contains thumbnails, titles, dates, descriptions
    # Let's search for divs representing news cards or articles
    news_items = soup.find_all(['article', 'div'], class_=re.compile('post|news|card|thumb-info'))
    for item in news_items:
        title_el = item.find(['h2', 'h3', 'h4', 'a'], class_=re.compile('title|name|header')) or item.find('a')
        img_el = item.find('img')
        link_el = item.find('a')
        date_el = item.find(class_=re.compile('date|time'))
        
        if title_el and title_el.get_text(strip=True):
            news.append({
                "title": title_el.get_text(strip=True),
                "link": link_el.get('href', '') if link_el else '',
                "image": img_el.get('src', '') if img_el else '',
                "date": date_el.get_text(strip=True) if date_el else ''
            })
            
    # 3. Footer / Contact Info
    contact_info = {}
    footer = soup.find('footer')
    if footer:
        text = footer.get_text()
        # Find emails, phones using regex
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        phones = re.findall(r'\+?\d[\d\s\(\)-]{8,15}\d', text)
        contact_info['emails'] = list(set(emails))
        contact_info['phones'] = list(set(phones))
        # Look for address/location keywords
        addr_match = re.search(r'(Ýerleşýän ýeri|Salgysy|Address|Адрес|köçesi|koçesi|k\.)\s*:?\s*([^\n\r]+)', text, re.IGNORECASE)
        if addr_match:
            contact_info['address'] = addr_match.group(0).strip()
            
    data = {
        "sliders": sliders[:10],
        "news_sample": news[:10],
        "contact_info": contact_info
    }
    
    with open("homepage_details.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print("Extracted homepage details successfully.")
    print("Sliders found:", len(sliders))
    print("News elements found:", len(news))
    print("Contact info:", contact_info)

import re
if __name__ == '__main__':
    main()

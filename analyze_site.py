import urllib.request
import re
import ssl
from bs4 import BeautifulSoup
import json

# Bypass SSL verification if needed (for government/institutional sites that might have local SSL issues)
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
        print(f"Error fetching {url}: {e}")
        return None

def parse_menu(html):
    soup = BeautifulSoup(html, 'html.parser')
    menu_items = []
    
    # Find navigation container
    # From previous check, the main navigation is inside id="mainNav" or similar
    nav = soup.find('ul', id='mainNav')
    if not nav:
        nav = soup.find('nav')
        
    if not nav:
        print("Main navigation element not found.")
        return []
        
    # Let's inspect the top-level list items
    items = nav.find_all('li', recursive=False)
    for idx, item in enumerate(items):
        link = item.find('a')
        if not link:
            continue
            
        title = link.get_text(strip=True)
        href = link.get('href', '')
        
        # Check for submenus
        sub_menu = item.find('ul')
        sub_items = []
        if sub_menu:
            # Check for direct sub-items
            for sub_li in sub_menu.find_all('li', recursive=False):
                sub_link = sub_li.find('a')
                if sub_link:
                    sub_title = sub_link.get_text(strip=True)
                    sub_href = sub_link.get('href', '')
                    
                    # Check for third-level submenus (dropdown-submenu)
                    sub_sub_menu = sub_li.find('ul')
                    sub_sub_items = []
                    if sub_sub_menu:
                        for sub_sub_li in sub_sub_menu.find_all('li'):
                            sub_sub_link = sub_sub_li.find('a')
                            if sub_sub_link:
                                sub_sub_items.append({
                                    "title": sub_sub_link.get_text(strip=True),
                                    "href": sub_sub_link.get('href', '')
                                })
                    
                    sub_items.append({
                        "title": sub_title,
                        "href": sub_href,
                        "sub_items": sub_sub_items
                    })
        
        menu_items.append({
            "title": title,
            "href": href,
            "sub_items": sub_items
        })
        
    return menu_items

def main():
    print(f"Fetching {URL}...")
    html = fetch_page(URL)
    if not html:
        print("Failed to fetch homepage html.")
        return
        
    print("Parsing main menu...")
    menu = parse_menu(html)
    
    # Save the parsed structure to JSON
    with open("site_structure.json", "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=4)
        
    print("Parsed menu structure successfully. Writing markdown summary...")
    
    # Create a nice markdown report
    report = []
    report.append("# Türkmen Döwlet Maliýe Instituty (https://tdmai.edu.tm/) Website Structure\n")
    report.append("This file contains the parsed navigation and menu structure of the current live website.\n")
    report.append("## Main Navigation\n")
    
    for item in menu:
        report.append(f"- **[{item['title']}]({item['href']})**")
        for sub in item['sub_items']:
            report.append(f"  - [{sub['title']}]({sub['href']})")
            for sub_sub in sub['sub_items']:
                report.append(f"    - [{sub_sub['title']}]({sub_sub['href']})")
                
    with open("site_structure.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print("Done! Check site_structure.json and site_structure.md")

if __name__ == "__main__":
    main()

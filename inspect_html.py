import urllib.request
import ssl
from bs4 import BeautifulSoup
import re

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
        return
        
    soup = BeautifulSoup(html, 'html.parser')
    
    out_lines = []
    
    out_lines.append("--- HEADINGS ---")
    for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        out_lines.append(f"{h.name} (class={h.get('class')}): {h.get_text(strip=True)}")
        
    out_lines.append("\n--- IMAGES IN THE BODY ---")
    for img in soup.find_all('img')[:15]:
        out_lines.append(f"src={img.get('src')}, alt={img.get('alt')}, class={img.get('class')}")
        
    out_lines.append("\n--- LINKS WITH TEXT (Sample of 50) ---")
    links_shown = 0
    for a in soup.find_all('a'):
        text = a.get_text(strip=True)
        href = a.get('href', '')
        if text and href and not href.startswith('#') and links_shown < 50:
            out_lines.append(f"text='{text}', href='{href}', class={a.get('class')}")
            links_shown += 1
            
    out_lines.append("\n--- DIV CLASSES (First 100 with class) ---")
    divs_shown = 0
    for div in soup.find_all('div'):
        cls = div.get('class')
        if cls and divs_shown < 100:
            out_lines.append(f"div class={cls}, text snippet: {div.get_text(strip=True)[:100]}")
            divs_shown += 1

    with open("inspect_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print("Inspection details saved to inspect_output.txt")

if __name__ == '__main__':
    main()

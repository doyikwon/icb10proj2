import sys
from bs4 import BeautifulSoup
import re

def extract_products_from_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    products = []
    
    product_links = soup.find_all('a', href=lambda x: x and '/vp/products/' in x)
    seen_urls = set()
    
    for a_tag in product_links:
        try:
            url = a_tag.get('href', '')
            if url and url.startswith('/'):
                url = "https://www.coupang.com" + url
            
            text = a_tag.get_text(separator='|', strip=True)
            if not text:
                continue
                
            texts = [t.strip() for t in text.split('|') if t.strip()]
            
            name = "이름 없음"
            for t in texts:
                # 쿠팡 상품명은 보통 제일 길고 처음 나옴
                if len(t) > 3 and '원' not in t and '적립' not in t and '%' not in t:
                    name = t
                    break
            
            if name == "이름 없음" and texts:
                 name = texts[0]
                 
            price = 0
            for t in reversed(texts):
                if '원' in t and not any(skip in t for skip in ['(', ')', '정', '개', '최대', '적립', '당', 'ml', 'g']):
                    num_str = re.sub(r'[^0-9]', '', t)
                    if num_str:
                        price = int(num_str)
                        break
                        
            rating = 0.0
            review_count = 0
            for t in texts:
                match = re.search(r'([0-5]\.[0-9])\s*\((.*?)\)', t)
                if match:
                    rating = float(match.group(1))
                    review_count = int(re.sub(r'[^0-9]', '', match.group(2)))
                    break
                    
            if price > 0 and url not in seen_urls:
                products.append({
                    "name": name,
                    "price": price,
                    "rating": rating,
                    "review_count": review_count,
                    "deep_link": url
                })
                seen_urls.add(url)
        except Exception:
            continue
            
    return products

if __name__ == "__main__":
    html = open('playwright_page2_real.html', encoding='utf-8').read()
    prods = extract_products_from_html(html)
    print(f"Extracted {len(prods)} products")
    for p in prods[:5]:
        print(p)

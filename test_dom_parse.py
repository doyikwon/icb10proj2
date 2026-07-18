import sys
from bs4 import BeautifulSoup
import re

def extract_from_dom(html):
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    
    # 1. '/vp/products/'가 포함된 모든 a 태그를 찾음
    product_links = soup.find_all('a', href=lambda x: x and '/vp/products/' in x)
    
    for a_tag in product_links:
        try:
            # 텍스트 전체 가져오기
            text = a_tag.get_text(separator='|', strip=True)
            if not text:
                continue
            
            # URL
            url = a_tag.get('href', '')
            if url and url.startswith('/'):
                url = "https://www.coupang.com" + url
            
            # 텍스트를 분석하여 이름, 가격, 평점 추출
            # a_tag 하위 태그들을 분석 (보통 img, div 등)
            
            # 1. 이름: 가장 텍스트가 긴 div 혹은 특정 구조 (Coupang Next.js 구조 분석)
            # 대체로 상품명이 가장 긺
            texts = [t.strip() for t in text.split('|') if t.strip()]
            
            # 이름 휴리스틱: 텍스트 덩어리 중 첫 번째로 긴 텍스트 (길이가 10 이상)
            name = "이름 없음"
            for t in texts:
                if len(t) > 5 and '%' not in t and '원' not in t and '로켓' not in t and '(' not in t:
                    name = t
                    break
            
            # 가격 휴리스틱: '원'으로 끝나고 숫자로 된 것 (할인가격)
            price = 0
            for i, t in enumerate(texts):
                if t.endswith('원') and any(c.isdigit() for c in t):
                    # "27,320원" -> 27320
                    num_str = re.sub(r'[^0-9]', '', t)
                    if num_str:
                        price = int(num_str)
            
            # 평점 및 리뷰 수 휴리스틱
            rating = 0.0
            review_count = 0
            for t in texts:
                # "4.5(12132)" 또는 "4.5"
                match = re.search(r'([0-5]\.[0-9])\s*\((.*?)\)', t)
                if match:
                    rating = float(match.group(1))
                    review_count = int(re.sub(r'[^0-9]', '', match.group(2)))
                    break
            
            if name != "이름 없음" and price > 0:
                products.append({
                    "name": name,
                    "price": price,
                    "rating": rating,
                    "review_count": review_count,
                    "deep_link": url
                })
        except Exception as e:
            continue
            
    # 중복 제거 (URL 기준)
    unique_products = []
    seen_urls = set()
    for p in products:
        if p["deep_link"] not in seen_urls:
            unique_products.append(p)
            seen_urls.add(p["deep_link"])
            
    return unique_products

if __name__ == "__main__":
    html = open('playwright_page2_real.html', encoding='utf-8').read()
    prods = extract_from_dom(html)
    print(f"Extracted {len(prods)} products")
    for p in prods[:5]:
        print(p)

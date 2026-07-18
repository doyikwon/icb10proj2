"""
올리브영 모바일 웹 카테고리 페이지의 HTML을 저장하고, 내부에서 상품 데이터가 존재하는 패턴이나 태그를 탐색하는 스크립트입니다.
"""

import requests
from bs4 import BeautifulSoup

def parse_mobile():
    url = "https://m.oliveyoung.co.kr/m/display/getMCategoryList.do"
    params = {
        "dispCatNo": "100000200010025",
        "pageIdx": "1",
        "rowsPerPage": "24"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "Referer": "https://m.oliveyoung.co.kr/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        with open("oliveyoung/data/mobile_dump.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 모바일 올리브영 상품 정보 태그 분석
        # 보통 모바일 상품 리스트는 .prd_list, .mlist, .prd_info, .goods_name, .brand_name 등
        print("--- 주요 태그 검색 결과 ---")
        for tag in ['div', 'ul', 'li', 'p', 'span', 'a']:
            classes = set()
            for elem in soup.find_all(tag):
                if elem.get('class'):
                    classes.update(elem.get('class'))
            print(f"Tag <{tag}> classes (top 20):", list(classes)[:20])
            
        # 대표적인 상품명 및 브랜드명 텍스트 탐색
        print("\n--- a 태그 텍스트 5개 ---")
        a_tags = [a.get_text(strip=True) for a in soup.find_all('a') if a.get_text(strip=True)]
        for txt in a_tags[:15]:
            print("-", txt)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parse_mobile()

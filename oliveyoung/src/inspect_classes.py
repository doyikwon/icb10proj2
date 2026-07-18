"""
모바일 올리브영 HTML 내 모든 li 태그와 class 구조를 분석하여 상품 정보가 내장되어 있는지 확인하는 분석 스크립트입니다.
"""

from bs4 import BeautifulSoup

def inspect():
    with open("oliveyoung/data/mobile_dump.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 클래스명에 'goods' 또는 'prd'가 들어가는 태그를 모두 찾아 출력해봅니다.
    print("=== 'goods' 또는 'prd' 클래스를 가진 요소 탐색 ===")
    found = 0
    for tag in soup.find_all(class_=True):
        classes = tag.get("class")
        if any('goods' in c or 'prd' in c or 'item' in c for c in classes):
            # 텍스트가 존재하는 경우에만 출력
            text = tag.get_text(strip=True)
            if text and len(text) > 10:
                print(f"Tag: <{tag.name}>, Classes: {classes}, Text Snippet: {text[:80]}")
                found += 1
                if found > 15:
                    break

if __name__ == "__main__":
    inspect()

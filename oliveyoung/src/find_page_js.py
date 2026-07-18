"""
올리브영 상품 덤프 HTML(page_dump_real.html)의 페이징(pageing) HTML 블록을 파싱하여
페이지 번호 클릭 시 실행되는 자바스크립트 함수명과 구조를 식별하는 스크립트입니다.
"""

from bs4 import BeautifulSoup

def find_page_js():
    with open("oliveyoung/data/page_dump_real.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    pageing_div = soup.select_one(".pageing")
    if pageing_div:
        print("=== 페이징 영역 HTML ===")
        print(pageing_div.prettify()[:1000])
    else:
        print("페이징 영역(.pageing)을 찾지 못했습니다.")

if __name__ == "__main__":
    find_page_js()

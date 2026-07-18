"""
올리브영 상품 덤프 HTML(page_dump_real.html)에서 전체 상품 수 및 마지막 페이지 번호를 식별하는 스크립트입니다.
"""

from bs4 import BeautifulSoup

def get_pages():
    with open("oliveyoung/data/page_dump_real.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. 전체 상품 건수 추출 시도 (보통 'tx_num' 혹은 'cate_info_tx' 등의 클래스 사용)
    total_count_elem = soup.select_one(".cate_info_tx span, .total_count, #totCnt")
    if total_count_elem:
        print("전체 상품 수 텍스트:", total_count_elem.get_text(strip=True))
        
    # 2. 페이징 영역 분석
    page_numbers = soup.select(".pageing a")
    print(f"발견된 페이징 링크 수: {len(page_numbers)}")
    for a in page_numbers:
        print(f"Page link text: {a.get_text(strip=True)} | href: {a.get('href')}")

if __name__ == "__main__":
    get_pages()

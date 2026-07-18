"""
모바일 올리브영 HTML 소스(mobile_dump.html) 내에서 상품 목록을 비동기로 로드하기 위해 호출하는 
AJAX URL 주소 및 스크립트 구문을 검색하고 추출하는 분석 스크립트입니다.
"""

import re

def find_ajax():
    file_path = "oliveyoung/data/mobile_dump.html"
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # .do 주소 매칭
    do_urls = re.findall(r'/[a-zA-Z0-9_/]+\.do', html)
    print("=== 발견된 .do URL ===")
    for url in set(do_urls):
        print("-", url)
        
    # ajax 혹은 fetch, $.ajax 관련 키워드가 들어간 라인 검색
    print("\n=== AJAX/Fetch 관련 스크립트 구문 ===")
    lines = html.split('\n')
    for idx, line in enumerate(lines):
        if 'ajax' in line.lower() or 'fetch(' in line.lower() or 'getjson' in line.lower():
            print(f"Line {idx+1}: {line.strip()[:120]}")

if __name__ == "__main__":
    find_ajax()

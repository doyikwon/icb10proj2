"""
올리브영 모바일 웹 카테고리 페이지(m.oliveyoung.co.kr)를 호출하여 데이터 수집이 가능한지 점검하는 스크립트입니다.
"""

import requests

def test_mobile():
    # 모바일 카테고리 상품 목록 URL
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
        print(f"Mobile Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        print("Response Snippet:")
        print(response.text[:1000])
        
        # 상품명이 들어있는지 체크 (모바일은 보통 class가 'prd_name' 또는 'tit' 또는 'name' 등)
        print("Contains '올리브영':", "올리브영" in response.text)
        print("Contains '락토핏':", "락토핏" in response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mobile()

"""
아이허브의 다양한 카테고리별 특가 상품 API 엔드포인트가 
정상 동작하는지 검증하고 전체 건수를 확인하는 테스트 스크립트입니다.
"""

import requests

endpoints = {
    "sports_specials": "https://catalog.app.iherb.com/category/sports/specials",
    "supplements_specials": "https://catalog.app.iherb.com/category/supplements/specials",
    "beauty_specials": "https://catalog.app.iherb.com/category/beauty/specials",
    "grocery_specials": "https://catalog.app.iherb.com/category/grocery/specials",
    "all_specials": "https://catalog.app.iherb.com/category/specials"
}

params = {
    "isMobile": "false",
    "page": 1,
    "pageSize": 18
}
headers = {
    "referer": "https://kr.iherb.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}

for name, url in endpoints.items():
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"[{name}] Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  - Total Size: {data.get('totalSize', 0)}")
            print(f"  - Returned count: {len(data.get('products', []))}")
        else:
            print(f"  - Response snippet: {response.text[:100]}")
    except Exception as e:
        print(f"[{name}] Exception: {e}")

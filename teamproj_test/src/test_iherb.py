"""
아이허브 특가 API의 page=2 호출 시 
추가 데이터가 반환되는지 여부를 검증하는 테스트 스크립트입니다.
"""

import requests

url = "https://catalog.app.iherb.com/category/sports/specials"
params = {
    "isMobile": "false",
    "page": 2,  # page를 2로 설정
    "pageSize": 18
}
headers = {
    "referer": "https://kr.iherb.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, params=params, headers=headers)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        products = data.get("products", [])
        print("Total Size in Response:", data.get("totalSize", 0))
        print("Number of Products returned on page 2:", len(products))
        if products:
            print("First product on page 2:", products[0].get("displayName"))
    else:
        print("Error response text:", response.text[:500])
except Exception as e:
    print("Exception:", e)

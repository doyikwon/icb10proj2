"""
아이허브 스포츠 카테고리 웹페이지(HTML)에 직접 요청을 보내 
Cloudflare 방화벽 우회 및 HTML 파싱 가능 여부를 검증하는 테스트 스크립트입니다.
"""

import requests

url = "https://kr.iherb.com/c/sports"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "referer": "https://www.google.com/"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        html_content = response.text
        print("HTML Length:", len(html_content))
        # "product-title" 이나 상품 ID 등 텍스트가 들어있는지 확인
        print("Contains 'product-title'?", "product-title" in html_content)
        print("Contains 'product-inner'?", "product-inner" in html_content)
        # sample로 1000자만 저장
        with open("teamproj_test/docs/sample_sports.html", "w", encoding="utf-8") as f:
            f.write(html_content[:5000])
        print("Sample HTML saved to teamproj_test/docs/sample_sports.html")
    else:
        print("Response text snippet:", response.text[:500])
except Exception as e:
    print("Exception:", e)

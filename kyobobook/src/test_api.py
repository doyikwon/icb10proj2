"""
교보문고 베스트셀러 API를 호출하여 동작 여부를 검증하고, 
응답 구조를 파악하기 위해 샘플 JSON 데이터를 수집하는 테스트 스크립트입니다.
"""
import requests
import json

url = "https://store.kyobobook.co.kr/api/gw/best/v2/best-seller/online"
params = {
    "page": 1,
    "per": 20,
    "saleCmdtClstCode": "33",
    "soldOutExcludeYn": "N",
    "saleCmdtDsplDvsnCode": "KOR",
    "period": "002",
    "dsplDvsnCode": "001",
    "dsplTrgtDvsnCode": "004"
}
headers = {
    "referer": "https://store.kyobobook.co.kr/category/domestic/33/best?page=1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "x-api-gw-key": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..i35xkkCOngvXqCRx.0CqToQel6sj5d0qOS2ftoDu37jRwb0vtQwMBd1e_G1ynl7KUrTrH_qPJnygVpkc0tExt4BUX_pJ4RepB5QsxWmKLjC8tEuMELKG8SvRLEVn6ambMnSmDaJ85mLbGtHcM-zFiDBzi.3y1-RnxGHFxeLNMK2dWZoQ"
}

try:
    response = requests.get(url, params=params, headers=headers)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        # 응답 구조 분석을 위해 상위 1개 항목을 JSON 파일로 저장
        with open("kyobobook/docs/sample_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Sample response saved to kyobobook/docs/sample_response.json")
    else:
        print("Error response text:", response.text[:500])
except Exception as e:
    print("Exception:", e)

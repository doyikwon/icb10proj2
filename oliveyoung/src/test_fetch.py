"""
올리브영 카테고리 상품 목록 페이지(getMCategoryList.do)를 요청하기 위해 브라우저 헤더를 보강하여 테스트하는 스크립트입니다.
"""

import requests

def test_fetch():
    url = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do"
    params = {
        "dispCatNo": "100000200010025",
        "fltDispCatNo": "",
        "prdSort": "01",
        "pageIdx": "2",
        "rowsPerPage": "24",
        "searchTypeSort": "btn_thumb",
        "plusButtonFlag": "N",
        "isLoginCnt": "",
        "trackingCd": "Cat100000200010025_Small",
        "amplitudePageGubun": "",
        "t_page": "카테고리관",
        "t_click": "카테고리탭_중카테고리",
        "midCategory": "영양제",
        "smallCategory": "전체",
        "t_1st_category_type": "대_건강식품",
        "t_2nd_category_type": "중_영양제"
    }
    
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "www.oliveyoung.co.kr",
        "Sec-Ch-Ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Content Length: {len(response.text)}")
        print("Response Snippet:")
        print(response.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch()

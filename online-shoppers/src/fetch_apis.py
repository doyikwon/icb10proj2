"""
파일 목적: 4개 기관 API 엔드포인트를 호출하여 원본 데이터를 수집하는 스크립트.
주요 기능:
- 식품안전나라(건강기능식품 품목제조신고 등) 연동
- 식품의약품안전처 건강기능식품, 식품영양성분, 의약품개요정보 API 연동
- JSON 형식으로 데이터 수집 후 로컬에 저장
생성일: 2026-07-13
"""
import urllib.request
import urllib.parse
import json
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def fetch_foodsafetykorea():
    # API 1: 식품안전나라
    # I2790: 식품의약품안전처_건강기능식품 품목제조신고(원재료)
    url = "http://openapi.foodsafetykorea.go.kr/api/4cca164bc44a494c8e1/I2790/json/1/5"
    try:
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        return {"source": "식품안전나라", "data": data}
    except Exception as e:
        # Fallback to C003 if I2790 doesn't work
        try:
            url_fallback = "http://openapi.foodsafetykorea.go.kr/api/4cca164bc44a494c8e1/C003/json/1/5"
            req = urllib.request.Request(url_fallback)
            res = urllib.request.urlopen(req)
            data = json.loads(res.read().decode('utf-8'))
            return {"source": "식품안전나라", "data": data}
        except Exception as e2:
            return {"source": "식품안전나라", "error": str(e2)}

def fetch_htfs_info():
    # API 2: 건강기능식품정보
    url = "https://apis.data.go.kr/1471000/HtfsInfoService03/getHtfsItem01"
    params = {
        'serviceKey': urllib.parse.unquote('8dc1af0881032d3987fecff814f3b1c94a48cc92969cf7451d2332edd92fab68'),
        'pageNo': '1',
        'numOfRows': '5',
        'type': 'json'
    }
    query = urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(f"{url}?{query}")
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        return {"source": "식약처_건강기능식품", "data": data}
    except Exception as e:
        return {"source": "식약처_건강기능식품", "error": str(e)}

def fetch_food_ntr():
    # API 3: 식품영양성분DB정보
    url = "https://apis.data.go.kr/1471000/FoodNtrCpntDbInfo02/getFoodNtrCpntDbInq02"
    params = {
        'serviceKey': urllib.parse.unquote('8dc1af0881032d3987fecff814f3b1c94a48cc92969cf7451d2332edd92fab68'),
        'pageNo': '1',
        'numOfRows': '5',
        'type': 'json'
    }
    query = urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(f"{url}?{query}")
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        return {"source": "식약처_식품영양성분", "data": data}
    except Exception as e:
        return {"source": "식약처_식품영양성분", "error": str(e)}

def fetch_drug_info():
    # API 4: 의약품개요정보(e약은요)
    url = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
    params = {
        'serviceKey': urllib.parse.unquote('89fccf295e6928bf7077c370409d7f95f5cc99c8a5aa1f1674b9364bbdc58ae3'),
        'pageNo': '1',
        'numOfRows': '5',
        'type': 'json'
    }
    query = urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(f"{url}?{query}")
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        return {"source": "식약처_e약은요", "data": data}
    except Exception as e:
        return {"source": "식약처_e약은요", "error": str(e)}

def main():
    results = []
    print("1. 식품안전나라 API 호출 중...")
    results.append(fetch_foodsafetykorea())
    print("2. 식약처 건강기능식품 API 호출 중...")
    results.append(fetch_htfs_info())
    print("3. 식약처 식품영양성분 API 호출 중...")
    results.append(fetch_food_ntr())
    print("4. 식약처 의약품개요 API 호출 중...")
    results.append(fetch_drug_info())
    
    out_path = os.path.join("online-shoppers", "data", "api_raw_responses.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"완료! 결과를 {out_path}에 저장했습니다.")

if __name__ == "__main__":
    main()

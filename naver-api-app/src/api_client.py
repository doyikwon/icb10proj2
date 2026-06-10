"""
네이버 개발자 센터 OpenAPI 호출을 처리하는 공통 API 클라이언트 모듈입니다.
통합 검색어 트렌드, 쇼핑인사이트 키워드 트렌드, 블로그, 카페글, 뉴스, 쇼핑 상품 검색을 수행합니다.
"""

import requests
import json

def _validate_keys(client_id, client_secret):
    for name, val in [("Client ID", client_id), ("Client Secret", client_secret)]:
        if val:
            try:
                val.strip().encode('ascii')
            except UnicodeEncodeError:
                raise ValueError(f"{name}에 올바르지 않은 문자(한글, 전각문자 등)가 포함되어 있습니다. 공백 없이 영문, 숫자, 기본 기호만 입력했는지 확인해 주세요.")

def _get_headers(client_id, client_secret):
    _validate_keys(client_id, client_secret)
    return {
        "X-Naver-Client-Id": client_id.strip() if client_id else "",
        "X-Naver-Client-Secret": client_secret.strip() if client_secret else "",
        "Content-Type": "application/json"
    }

def get_search_trend(client_id, client_secret, keyword_groups, start_date, end_date, time_unit="date", device="", gender="", ages=[]):
    """
    네이버 통합 검색어 트렌드 조회
    """
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = _get_headers(client_id, client_secret)
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }
    if device:
        body["device"] = device
    if gender:
        body["gender"] = gender
    if ages:
        body["ages"] = ages
        
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error ({response.status_code}): {response.text}")

def get_shopping_trend(client_id, client_secret, category, keyword_groups, start_date, end_date, time_unit="date", device="", gender="", ages=[]):
    """
    네이버 쇼핑인사이트 분야별 검색어 트렌드 조회
    """
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    headers = _get_headers(client_id, client_secret)
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": category,
        "keyword": keyword_groups
    }
    if device:
        body["device"] = device
    if gender:
        body["gender"] = gender
    if ages:
        body["ages"] = ages
        
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error ({response.status_code}): {response.text}")

def search_blog(client_id, client_secret, query, display=30, start=1, sort="sim"):
    """
    네이버 블로그 검색결과 조회
    """
    _validate_keys(client_id, client_secret)
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": client_id.strip() if client_id else "",
        "X-Naver-Client-Secret": client_secret.strip() if client_secret else ""
    }
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error ({response.status_code}): {response.text}")

def search_cafe(client_id, client_secret, query, display=30, start=1, sort="sim"):
    """
    네이버 카페글 검색결과 조회
    """
    _validate_keys(client_id, client_secret)
    url = "https://openapi.naver.com/v1/search/cafearticle.json"
    headers = {
        "X-Naver-Client-Id": client_id.strip() if client_id else "",
        "X-Naver-Client-Secret": client_secret.strip() if client_secret else ""
    }
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error ({response.status_code}): {response.text}")

def search_news(client_id, client_secret, query, display=30, start=1, sort="sim"):
    """
    네이버 뉴스 검색결과 조회
    """
    _validate_keys(client_id, client_secret)
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id.strip() if client_id else "",
        "X-Naver-Client-Secret": client_secret.strip() if client_secret else ""
    }
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error ({response.status_code}): {response.text}")

def search_shopping(client_id, client_secret, query, display=30, start=1, sort="sim", exclude=""):
    """
    네이버 쇼핑 상품 검색결과 조회
    """
    _validate_keys(client_id, client_secret)
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": client_id.strip() if client_id else "",
        "X-Naver-Client-Secret": client_secret.strip() if client_secret else ""
    }
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    if exclude:
        params["exclude"] = exclude
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error ({response.status_code}): {response.text}")

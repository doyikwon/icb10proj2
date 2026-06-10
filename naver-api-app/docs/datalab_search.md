# 네이버 데이터랩 - 통합 검색어 트렌드 API 명세

네이버 데이터랩의 통합 검색어 트렌드 API는 네이버 통합검색에서의 특정 주제어 그룹별 검색 추이 데이터를 제공하는 비로그인 방식 RESTful API입니다.

## 1. API 개요
- **요청 URL**: `https://openapi.naver.com/v1/datalab/search`
- **HTTP Method**: `POST`
- **호출 한도**: 하루 1,000회
- **콘텐트 타입**: `application/json`

## 2. 요청 파라미터 (JSON)
| 파라미터 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| `startDate` | string | Y | 조회 기간 시작 날짜 (`yyyy-mm-dd` 형식, 2016-01-01부터 조회 가능) |
| `endDate` | string | Y | 조회 기간 종료 날짜 (`yyyy-mm-dd` 형식) |
| `timeUnit` | string | Y | 구간 단위 (`date`: 일간, `week`: 주간, `month`: 월간) |
| `keywordGroups` | array(JSON) | Y | 주제어와 대표 검색어 묶음의 쌍 배열 (최대 5개 그룹) |
| `keywordGroups.groupName` | string | Y | 주제어 (검색어 묶음을 대표하는 이름) |
| `keywordGroups.keywords` | array(string) | Y | 주제어에 해당하는 세부 검색어 배열 (최대 20개) |
| `device` | string | N | 검색 환경 조건 (설정 안 함: 전체, `pc`: PC, `mo`: 모바일) |
| `gender` | string | N | 검색 사용자 성별 (설정 안 함: 전체, `m`: 남성, `f`: 여성) |
| `ages` | array(string) | N | 검색 사용자 연령대 조건 배열 (1: 0~12세 ~ 11: 60세 이상) |

## 3. 응답 필드
| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `startDate` | string | 조회 시작 날짜 |
| `endDate` | string | 조회 종료 날짜 |
| `timeUnit` | string | 구간 단위 |
| `results` | array | 검색 결과 데이터 목록 |
| `results.title` | string | 주제어 그룹명 |
| `results.keywords` | array | 그룹에 포함된 검색어 목록 |
| `results.data` | array | 구간별 검색 비율 데이터 |
| `results.data.period` | string | 해당 구간의 시작일 (`yyyy-mm-dd`) |
| `results.data.ratio` | number | 구간별 상대적 검색 비율 (구간 중 최댓값을 100으로 설정한 상댓값) |

## 4. 호출 예시 (Python)
```python
import urllib.request
import json

client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
url = "https://openapi.naver.com/v1/datalab/search"

body = {
    "startDate": "2023-01-01",
    "endDate": "2023-12-31",
    "timeUnit": "month",
    "keywordGroups": [
        {
            "groupName": "한글",
            "keywords": ["한글", "korean"]
        },
        {
            "groupName": "영어",
            "keywords": ["영어", "english"]
        }
    ]
}

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)
request.add_header("Content-Type", "application/json")

response = urllib.request.urlopen(request, data=json.dumps(body).encode("utf-8"))
if response.getcode() == 200:
    print(response.read().decode("utf-8"))
```

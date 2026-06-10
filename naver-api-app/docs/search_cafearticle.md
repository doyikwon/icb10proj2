# 네이버 검색 - 카페글 검색 API 명세

네이버 검색 API 중 네이버 카페의 공개 게시판 글을 검색한 결과를 반환하는 비로그인 방식 RESTful API입니다.

## 1. API 개요
- **요청 URL**:
  - JSON 형식: `https://openapi.naver.com/v1/search/cafearticle.json`
  - XML 형식: `https://openapi.naver.com/v1/search/cafearticle.xml`
- **HTTP Method**: `GET`
- **호출 한도**: 하루 25,000회 (전체 검색 API 공통)

## 2. 요청 파라미터 (Query String)
| 파라미터 | 타입 | 필수 여부 | 기본값 | 설명 |
| :--- | :--- | :---: | :---: | :--- |
| `query` | string | Y | - | 검색어. UTF-8 URL 인코딩 필요. |
| `display` | integer | N | 10 | 한 번에 표시할 검색 결과 개수 (최소 1, 최대 100) |
| `start` | integer | N | 1 | 검색 시작 위치 (최소 1, 최대 1000) |
| `sort` | string | N | `sim` | 정렬 방식 (`sim`: 정확도순 내림차순, `date`: 날짜순 내림차순) |

## 3. 응답 필드 (JSON `items` 기준)
| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `title` | string | 카페 게시글 제목 (검색 키워드는 `<b>` 태그로 강조 표시됨) |
| `link` | string | 카페 게시글 URL |
| `description` | string | 카페 게시글 본문 요약 (검색 키워드는 `<b>` 태그로 강조 표시됨) |
| `cafename` | string | 게시글이 포함된 카페 이름 |
| `cafeurl` | string | 게시글이 포함된 카페 URL |

## 4. 호출 예시 (Python)
```python
import urllib.request
import urllib.parse

client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
query = urllib.parse.quote("노트북 추천")
url = f"https://openapi.naver.com/v1/search/cafearticle.json?query={query}&display=5"

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

response = urllib.request.urlopen(request)
if response.getcode() == 200:
    print(response.read().decode("utf-8"))
```

# 네이버 검색 - 쇼핑 검색 API 명세

네이버 검색 API 중 네이버 쇼핑의 상품 검색 결과를 반환하는 비로그인 방식 RESTful API입니다.

## 1. API 개요
- **요청 URL**:
  - JSON 형식: `https://openapi.naver.com/v1/search/shop.json`
  - XML 형식: `https://openapi.naver.com/v1/search/shop.xml`
- **HTTP Method**: `GET`
- **호출 한도**: 하루 25,000회 (전체 검색 API 공통)

## 2. 요청 파라미터 (Query String)
| 파라미터 | 타입 | 필수 여부 | 기본값 | 설명 |
| :--- | :--- | :---: | :---: | :--- |
| `query` | string | Y | - | 검색어. UTF-8 URL 인코딩 필요. |
| `display` | integer | N | 10 | 한 번에 표시할 검색 결과 개수 (최소 1, 최대 100) |
| `start` | integer | N | 1 | 검색 시작 위치 (최소 1, 최대 1000) |
| `sort` | string | N | `sim` | 정렬 방식 (`sim`: 정확도순, `date`: 날짜순, `asc`: 가격 오름차순, `dsc`: 가격 내림차순) |
| `filter` | string | N | - | 상품 유형 필터 (`naverpay`: 네이버페이 연동 상품) |
| `exclude` | string | N | - | 검색에서 제외할 유형 (값 구분은 `:` 사용, 예: `used:rental:cbshop`)<br>- `used`: 중고, `rental`: 렌탈, `cbshop`: 해외직구/구매대행 |

## 3. 응답 필드 (JSON `items` 기준)
| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `title` | string | 상품 이름 (검색 키워드는 `<b>` 태그로 강조 표시됨) |
| `link` | string | 상품 정보 URL |
| `image` | string | 상품 섬네일 이미지 URL |
| `lprice` | integer | 최저가 (최저가 정보가 없으면 0, 가격비교 불가 상품은 판매가) |
| `hprice` | integer | 최고가 (최고가 정보가 없으면 0) |
| `mallName` | string | 쇼핑몰 이름 (정보가 없을 경우 '네이버') |
| `productId` | string | 네이버 쇼핑 상품 ID |
| `productType` | string | 상품군 및 종류 타입 코드 (1 ~ 12) |
| `maker` | string | 제조사 |
| `brand` | string | 브랜드명 |
| `category1` | string | 대분류 카테고리 |
| `category2` | string | 중분류 카테고리 |
| `category3` | string | 소분류 카테고리 |
| `category4` | string | 세분류 카테고리 |

## 4. 호출 예시 (Python)
```python
import urllib.request
import urllib.parse

client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
query = urllib.parse.quote("기계식 키보드")
url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display=5&exclude=used"

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

response = urllib.request.urlopen(request)
if response.getcode() == 200:
    print(response.read().decode("utf-8"))
```

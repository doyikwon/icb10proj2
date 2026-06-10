# 네이버 오픈 API 공통 가이드 (요약 및 명세)

네이버 오픈 API는 네이버 플랫폼의 다양한 기능을 외부 개발자가 쉽게 이용할 수 있도록 제공하는 웹 기반 RESTful API 및 SDK입니다. 본 문서는 오픈 API 이용을 위한 사전 준비 및 공통 규칙을 다룹니다.

## 1. 로그인 방식 vs 비로그인 방식 API
- **비로그인 방식 API**: HTTP 요청 헤더에 클라이언트 ID 및 시크릿만 전송하여 바로 사용할 수 있는 API입니다. (예: 검색, 데이터랩, 파파고 등)
- **로그인 방식 API**: 네이버 아이디로 로그인(OAuth 2.0) 인증을 통해 획득한 접근 토큰(Access Token)을 헤더에 전송해야 사용할 수 있는 API입니다.

## 2. API 호출 공통 인증 헤더
비로그인 방식 API 호출 시 HTTP 헤더에 아래와 같은 인증 정보를 필수 전달해야 합니다.
- `X-Naver-Client-Id`: 네이버 개발자 센터에서 애플리케이션 등록 후 발급받은 **클라이언트 ID**
- `X-Naver-Client-Secret`: 발급받은 **클라이언트 시크릿**

## 3. 사전 준비 사항
1. **네이버 개발자 센터** (https://developers.naver.com) 접속 및 로그인
2. **Application > 애플리케이션 등록** 메뉴 선택
3. 서비스 환경 및 사용할 API(검색, 데이터랩 등) 선택 후 등록
4. 발급된 **Client ID** 및 **Client Secret** 확인 및 보관

## 4. 공통 에러 응답 형식
API 호출 실패 시 아래와 같은 JSON 또는 XML 형식의 에러 메시지가 반환됩니다.
- **HTTP Status Code**: 400 (Bad Request), 403 (Forbidden), 404 (Not Found), 500 (Internal Server Error) 등
- **응답 본문 예시 (JSON)**:
  ```json
  {
    "errorMessage": "Authentication failed. (인증에 실패했습니다.)",
    "errorCode": "024"
  }
  ```

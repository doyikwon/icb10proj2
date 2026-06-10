"""
네이버 개발자 API를 통해 실시간 데이터를 수집하고 시각화 분석을 제공하는 Streamlit 대시보드 메인 애플리케이션입니다.
왼쪽 사이드바에서 공통 입력(API 인증 정보, 검색 키워드, 기간 등)을 제공하며,
st.navigation 및 st.Page 구조를 사용하여 각 페이지별 대시보드를 트리 형태로 구성합니다.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import api_client

# .env 파일 로드
load_dotenv()
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(dotenv_path=env_path)

# Streamlit 기본 설정
st.set_page_config(
    page_title="네이버 API 종합 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 공통 커스텀 CSS 스타일 적용
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1EC800;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 0.8rem;
        border-left: 5px solid #1EC800;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #333;
    }
    .info-box {
        background-color: #FFFDF0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #F1C40F;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- 사이드바 (Sidebar) 공통 설정 -----------------
st.sidebar.markdown("# 🔑 NAVER API 설정")

# 1) Streamlit secrets에서 로드 시도
client_id = ""
client_secret = ""

if "NAVER_CLIENT_ID" in st.secrets:
    client_id = st.secrets["NAVER_CLIENT_ID"].strip()
if "NAVER_CLIENT_SECRET" in st.secrets:
    client_secret = st.secrets["NAVER_CLIENT_SECRET"].strip()

# 2) Secrets에 없을 경우 .env / 환경 변수에서 로드 시도
if not client_id:
    client_id = os.getenv("NAVER_CLIENT_ID", "").strip()
if not client_secret:
    client_secret = os.getenv("NAVER_CLIENT_SECRET", "").strip()

if client_id and client_secret:
    st.sidebar.success("🔑 NAVER API 키 로드 완료")
else:
    st.sidebar.warning("⚠️ API 키를 로드하지 못했습니다. st.secrets 또는 .env 설정을 확인해 주세요.")

st.sidebar.markdown("---")
st.sidebar.markdown("# 🔍 데이터 수집 설정")

# 검색 키워드 입력 (,로 구분)
keywords_input = st.sidebar.text_input(
    "검색 키워드 (쉼표 ','로 구분)",
    value="아이폰, 갤럭시",
    help="다중 검색어 입력 시 쉼표로 구분해 주세요. 예: 아이폰, 갤럭시"
)
keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

# 검색 기간 설정 (시작일, 종료일)
today = datetime.today()
default_start = today - timedelta(days=90)
date_range = st.sidebar.date_input(
    "조회 기간",
    value=(default_start, today),
    max_value=today,
    help="트렌드 조회 시 수집할 데이터 기간을 선택합니다."
)

# 날짜 검증
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = default_start, today

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# API 인증 여부 체크 및 메시지 렌더링 함수
def check_api_keys():
    if not client_id or not client_secret:
        st.markdown(f"""
        <div class="info-box">
            👉 <b>Streamlit Secrets 또는 .env 파일에 NAVER API Client ID와 Client Secret을 설정해 주세요.</b>
        </div>
        """, unsafe_allow_html=True)
        return False
    return True

# ----------------- 페이지 함수 정의 -----------------

def intro_page():
    st.markdown("<div class='main-title'>🏠 대시보드 소개 및 가이드</div>", unsafe_allow_html=True)
    st.markdown("""
    네이버 개발자 센터에서 제공하는 OpenAPI들을 활용하여 트렌드 분석 및 소셜 평판 분석을 제공하는 종합 데이터 분석 대시보드입니다.
    
    ### 📌 분석 기능 안내
    1. **데이터랩 트렌드 분석**
       - **검색어 트렌드 분석**: 네이버 통합검색 내 키워드들의 일간/주간/월간 검색 상대 추이를 비교합니다.
       - **쇼핑 트렌드 분석**: 네이버 쇼핑 카테고리별 클릭량 비율을 확인합니다.
    2. **검색 데이터 다차원 분석**
       - **쇼핑 검색 분석**: 최저가/최고가 분포 및 주요 쇼핑몰 입점 점유율을 시각화합니다.
       - **블로그 검색 분석**: 최근 발행된 블로그 피드 빈도 추이와 주요 블로거 언급 분포를 분석합니다.
       - **카페글 검색 분석**: 커뮤니티 내 관심도 및 피드백 현황을 파악합니다.
       - **뉴스 검색 분석**: 최근 일자별 언론사 보도 추이와 주요 기사 목록을 확인합니다.
    
    ### 🔑 시작하기 (API 설정 방법)
    1. [네이버 개발자 센터](https://developers.naver.com/)에 로그인합니다.
    2. **Application > 애플리케이션 등록** 메뉴로 이동합니다.
    3. 애플리케이션 이름과 사용할 API(검색, 데이터랩)를 선택하고 환경 정보를 등록합니다.
    4. 발급된 `Client ID`와 `Client Secret`을 복사하여 **왼쪽 사이드바**에 입력해 주세요.
    5. 분석하고자 하는 키워드(쉼표 구분)와 조회 기간을 지정하고 메뉴를 탐색하세요.
    """)

def trend_page():
    st.markdown("<div class='main-title'>📈 네이버 검색어 트렌드 분석</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>선택한 기간 동안 네이버 통합검색 내 키워드별 검색 추이를 비교합니다. (상대적인 검색량 비율 분석)</div>", unsafe_allow_html=True)
    
    if check_api_keys():
        col1, col2, col3 = st.columns(3)
        with col1:
            time_unit = st.selectbox("구간 단위", ["date", "week", "month"], format_func=lambda x: {"date":"일간", "week":"주간", "month":"월간"}[x])
        with col2:
            device = st.selectbox("기기 구분", ["", "pc", "mo"], format_func=lambda x: {"":"전체 기기", "pc":"PC", "mo":"모바일"}[x])
        with col3:
            gender = st.selectbox("성별 구분", ["", "m", "f"], format_func=lambda x: {"":"전체 성별", "m":"남성", "f":"여성"}[x])
            
        if st.button("트렌드 데이터 수집 시작", type="primary"):
            with st.spinner("네이버 데이터랩 API에서 검색 추이 수집 중..."):
                try:
                    keyword_groups = [{"groupName": kw, "keywords": [kw]} for kw in keywords]
                    data = api_client.get_search_trend(
                        client_id, client_secret, keyword_groups, 
                        start_str, end_str, time_unit, device, gender
                    )
                    
                    records = []
                    results = data.get("results", [])
                    for res in results:
                        group_name = res.get("title")
                        for d in res.get("data", []):
                            records.append({
                                "Period": d.get("period"),
                                "Ratio": d.get("ratio"),
                                "Keyword": group_name
                            })
                    
                    if records:
                        df = pd.DataFrame(records)
                        df["Period"] = pd.to_datetime(df["Period"])
                        
                        fig = px.line(
                            df, 
                            x="Period", 
                            y="Ratio", 
                            color="Keyword",
                            title="키워드별 네이버 검색 추이 (최대치 100 기준 상대적 비율)",
                            labels={"Ratio": "검색 비율 (Ratio)", "Period": "기간"},
                            template="plotly_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("### 📊 수집 데이터 통계 요약")
                        desc_cols = st.columns(len(keywords))
                        for i, kw in enumerate(keywords):
                            kw_df = df[df["Keyword"] == kw]
                            if not kw_df.empty:
                                with desc_cols[i]:
                                    st.markdown(f"""
                                    <div class='metric-card'>
                                        <div class='metric-label'><b>{kw}</b> 평균 검색 비율</div>
                                        <div class='metric-value'>{kw_df['Ratio'].mean():.2f}%</div>
                                        <div class='metric-label'>최고: {kw_df['Ratio'].max():.1f}% | 최저: {kw_df['Ratio'].min():.1f}%</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                        st.markdown("### 📄 원본 데이터 테이블")
                        pivot_df = df.pivot(index="Period", columns="Keyword", values="Ratio").reset_index()
                        st.dataframe(pivot_df, use_container_width=True)
                    else:
                        st.warning("수집된 데이터가 없습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")

def shopping_trend_page():
    st.markdown("<div class='main-title'>🛍️ 네이버 쇼핑 트렌드 분석</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>네이버 쇼핑 카테고리 내에서 키워드별 클릭량 트렌드를 비교 분석합니다.</div>", unsafe_allow_html=True)
    
    if check_api_keys():
        categories = {
            "패션의류": "50000000",
            "패션잡화": "50000001",
            "화장품/미용": "50000002",
            "디지털/가전": "50000003",
            "가구/인테리어": "50000004",
            "출산/육아": "50000005",
            "식품": "50000006",
            "스포츠/레저": "50000007",
            "생활/건강": "50000008",
            "여가/생활편의": "50000009",
            "면세점": "50000010",
            "도서": "50005542"
        }
        col1, col2, col3 = st.columns(3)
        with col1:
            category_name = st.selectbox("쇼핑 대분류 카테고리 선택", list(categories.keys()))
            category_code = categories[category_name]
        with col2:
            time_unit = st.selectbox("구간 단위", ["date", "week", "month"], format_func=lambda x: {"date":"일간", "week":"주간", "month":"월간"}[x])
        with col3:
            device = st.selectbox("기기 필터", ["", "pc", "mo"], format_func=lambda x: {"":"전체", "pc":"PC", "mo":"모바일"}[x])
            
        if st.button("쇼핑 트렌드 수집 시작", type="primary"):
            with st.spinner("쇼핑인사이트 키워드 트렌드 수집 중..."):
                try:
                    target_keywords = keywords[:5]
                    keyword_groups = [{"name": kw, "param": [kw]} for kw in target_keywords]
                    data = api_client.get_shopping_trend(
                        client_id, client_secret, category_code, keyword_groups,
                        start_str, end_str, time_unit, device
                    )
                    
                    records = []
                    results = data.get("results", [])
                    for res in results:
                        group_name = res.get("title")
                        for d in res.get("data", []):
                            records.append({
                                "Period": d.get("period"),
                                "Ratio": d.get("ratio"),
                                "Keyword": group_name
                            })
                            
                    if records:
                        df = pd.DataFrame(records)
                        df["Period"] = pd.to_datetime(df["Period"])
                        
                        fig = px.line(
                            df,
                            x="Period",
                            y="Ratio",
                            color="Keyword",
                            title=f"네이버 쇼핑 [{category_name}] 카테고리 내 키워드별 클릭 비율 추이",
                            labels={"Ratio": "클릭량 비율 (%)", "Period": "기간"},
                            template="plotly_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("### 📊 수집 데이터 통계 요약")
                        desc_cols = st.columns(len(target_keywords))
                        for i, kw in enumerate(target_keywords):
                            kw_df = df[df["Keyword"] == kw]
                            if not kw_df.empty:
                                with desc_cols[i]:
                                    st.markdown(f"""
                                    <div class='metric-card'>
                                        <div class='metric-label'><b>{kw}</b> 평균 클릭 지수</div>
                                        <div class='metric-value'>{kw_df['Ratio'].mean():.2f}%</div>
                                        <div class='metric-label'>최고: {kw_df['Ratio'].max():.1f}% | 최저: {kw_df['Ratio'].min():.1f}%</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                    else:
                        st.warning("데이터가 없습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")

def shop_page():
    st.markdown("<div class='main-title'>🛒 네이버 쇼핑 상품 검색 분석</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>최신 쇼핑 검색 결과를 수집하여 최저가/최고가 분포 및 브랜드 시장 현황을 시각화합니다.</div>", unsafe_allow_html=True)
    
    if check_api_keys():
        target_kw = st.selectbox("분석 대상 키워드 선택", keywords)
        sort_option = st.selectbox("상품 정렬", ["sim", "date", "asc", "dsc"], format_func=lambda x: {
            "sim": "기본 정확도순", "date": "최신 등록순", "asc": "가격 낮은 순", "dsc": "가격 높은 순"
        }[x])
        
        if st.button("쇼핑 상품 데이터 수집 시작", type="primary"):
            with st.spinner("상품 데이터 수집 중..."):
                try:
                    data = api_client.search_shopping(client_id, client_secret, target_kw, display=50, sort=sort_option)
                    items = data.get("items", [])
                    
                    if items:
                        df = pd.DataFrame(items)
                        df["title_clean"] = df["title"].str.replace(r"<[^>]*>", "", regex=True)
                        df["lprice"] = pd.to_numeric(df["lprice"], errors="coerce").fillna(0)
                        price_df = df[df["lprice"] > 0]
                        
                        kpi1, kpi2, kpi3 = st.columns(3)
                        with kpi1:
                            st.markdown(f"<div class='metric-card'><div class='metric-label'>평균 수집 가격</div><div class='metric-value'>{int(price_df['lprice'].mean()):,}원</div></div>", unsafe_allow_html=True)
                        with kpi2:
                            st.markdown(f"<div class='metric-card'><div class='metric-label'>최저가</div><div class='metric-value'>{int(price_df['lprice'].min()):,}원</div></div>", unsafe_allow_html=True)
                        with kpi3:
                            st.markdown(f"<div class='metric-card'><div class='metric-label'>최고가</div><div class='metric-value'>{int(price_df['lprice'].max()):,}원</div></div>", unsafe_allow_html=True)
                            
                        st.markdown("---")
                        col_left, col_right = st.columns(2)
                        with col_left:
                            fig_hist = px.histogram(
                                price_df, x="lprice", nbins=15,
                                title="수집 상품 최저가격대별 빈도 분포",
                                labels={"lprice": "최저 가격 (원)"},
                                template="plotly_white",
                                color_discrete_sequence=["#1EC800"]
                            )
                            st.plotly_chart(fig_hist, use_container_width=True)
                        with col_right:
                            mall_counts = df["mallName"].value_counts().reset_index().head(10)
                            mall_counts.columns = ["쇼핑몰명", "상품 등록수"]
                            fig_mall = px.bar(mall_counts, x="상품 등록수", y="쇼핑몰명", orientation="h", title="주요 쇼핑몰별 입점 빈도 (Top 10)", template="plotly_white")
                            st.plotly_chart(fig_mall, use_container_width=True)
                            
                        st.markdown("### 🏷️ 수집된 상품 목록")
                        for idx, row in df.iterrows():
                            col_img, col_info = st.columns([1, 4])
                            with col_img:
                                if row["image"]:
                                    st.image(row["image"], width=130)
                            with col_info:
                                st.markdown(f"""
                                **[{row['title_clean']}]({row['link']})**  
                                - 가격: `{int(row['lprice']):,}`원 | 판매몰: `{row['mallName']}`  
                                - 카테고리: `{row['category1']} > {row['category2']} > {row['category3']}`
                                """)
                            st.markdown("---")
                    else:
                        st.warning("상품 정보가 없습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")

def blog_page():
    st.markdown("<div class='main-title'>📝 네이버 블로그 검색 분석</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>네이버 블로그 포스트를 수집하여 최근 트렌드 언급량 및 소셜 반응 분포를 분석합니다.</div>", unsafe_allow_html=True)
    
    if check_api_keys():
        target_kw = st.selectbox("분석 대상 키워드 선택", keywords)
        sort_option = st.selectbox("정렬 옵션", ["sim", "date"], format_func=lambda x: {"sim":"유사도순", "date":"최신등록순"}[x])
        
        if st.button("블로그 데이터 분석 시작", type="primary"):
            with st.spinner("블로그 피드 분석 중..."):
                try:
                    data = api_client.search_blog(client_id, client_secret, target_kw, display=50, sort=sort_option)
                    items = data.get("items", [])
                    
                    if items:
                        df = pd.DataFrame(items)
                        df["title_clean"] = df["title"].str.replace(r"<[^>]*>", "", regex=True)
                        df["desc_clean"] = df["description"].str.replace(r"<[^>]*>", "", regex=True)
                        
                        df["postdate_dt"] = pd.to_datetime(df["postdate"], format="%Y%m%d", errors="coerce")
                        date_counts = df["postdate_dt"].value_counts().reset_index()
                        date_counts.columns = ["작성일", "글 개수"]
                        date_counts = date_counts.sort_values(by="작성일")
                        
                        fig_date = px.bar(date_counts, x="작성일", y="글 개수", title="일자별 블로그 글 발행 빈도 분포", template="plotly_white", color_discrete_sequence=["#1EC800"])
                        st.plotly_chart(fig_date, use_container_width=True)
                        
                        st.markdown("### 📄 수집된 블로그 피드 목록")
                        for idx, row in df.iterrows():
                            with st.expander(f"📌 {row['title_clean']} ({row['bloggername']} | {row['postdate']})"):
                                st.write(row["desc_clean"])
                                st.markdown(f"[블로그 포스트 원문 이동]({row['link']})")
                    else:
                        st.warning("데이터가 없습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")

def cafe_page():
    st.markdown("<div class='main-title'>👥 네이버 카페글 검색 분석</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>네이버 카페 게시판 공개글 검색을 통해 온라인 카페 반응을 분석합니다.</div>", unsafe_allow_html=True)
    
    if check_api_keys():
        target_kw = st.selectbox("분석 대상 키워드 선택", keywords)
        sort_option = st.selectbox("정렬 옵션", ["sim", "date"], format_func=lambda x: {"sim":"유사도순", "date":"최신등록순"}[x])
        
        if st.button("카페 데이터 분석 시작", type="primary"):
            with st.spinner("카페 게시글 분석 중..."):
                try:
                    data = api_client.search_cafe(client_id, client_secret, target_kw, display=50, sort=sort_option)
                    items = data.get("items", [])
                    
                    if items:
                        df = pd.DataFrame(items)
                        df["title_clean"] = df["title"].str.replace(r"<[^>]*>", "", regex=True)
                        df["desc_clean"] = df["description"].str.replace(r"<[^>]*>", "", regex=True)
                        
                        cafe_counts = df["cafename"].value_counts().reset_index().head(10)
                        cafe_counts.columns = ["카페명", "발행 수"]
                        fig_cafe = px.bar(cafe_counts, x="발행 수", y="카페명", orientation="h", title="주요 언급 카페 분포 (Top 10)", template="plotly_white")
                        st.plotly_chart(fig_cafe, use_container_width=True)
                        
                        st.markdown("### 📄 수집된 카페 게시글 목록")
                        for idx, row in df.iterrows():
                            with st.expander(f"💬 {row['title_clean']} ({row['cafename']})"):
                                st.write(row["desc_clean"])
                                st.markdown(f"[카페글 원문 이동]({row['link']})")
                    else:
                        st.warning("데이터가 없습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")

def news_page():
    st.markdown("<div class='main-title'>📰 네이버 뉴스 검색 데이터 분석</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>네이버 뉴스 검색 결과를 분석하여 일자별 보도량 추이, 주요 보도 매체(도메인) 및 연관 키워드를 시각화합니다.</div>", unsafe_allow_html=True)
    
    if check_api_keys():
        target_kw = st.selectbox("분석 대상 키워드 선택", keywords)
        sort_option = st.selectbox("뉴스 정렬 기준", ["sim", "date"], format_func=lambda x: {"sim":"정확도순", "date":"최신 보도순"}[x])
        
        if st.button("뉴스 데이터 분석 시작", type="primary"):
            with st.spinner("보도 기사 분석 중..."):
                try:
                    data = api_client.search_news(client_id, client_secret, target_kw, display=50, sort=sort_option)
                    items = data.get("items", [])
                    
                    if items:
                        df = pd.DataFrame(items)
                        df["title_clean"] = df["title"].str.replace(r"<[^>]*>", "", regex=True)
                        df["desc_clean"] = df["description"].str.replace(r"<[^>]*>", "", regex=True)
                        
                        df["pub_dt"] = pd.to_datetime(df["pubDate"], errors="coerce")
                        df["pub_day"] = df["pub_dt"].dt.date
                        news_trend = df["pub_day"].value_counts().reset_index()
                        news_trend.columns = ["보도일자", "기사수"]
                        news_trend = news_trend.sort_values("보도일자")
                        
                        fig_news = px.line(news_trend, x="보도일자", y="기사수", title="최근 일자별 언론 보도량 흐름", template="plotly_white", markers=True)
                        st.plotly_chart(fig_news, use_container_width=True)
                        
                        st.markdown("### 📰 최근 주요 뉴스 목록")
                        for idx, row in df.iterrows():
                            st.markdown(f"""
                            **[{row['title_clean']}]({row['link']})**  
                            _보도 시간: {row['pubDate']}_  
                            > {row['desc_clean']}  
                            ---
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("기사가 없습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")

# ----------------- 멀티페이지 네비게이션 정의 -----------------
pages = {
    "안내": [
        st.Page(intro_page, title="대시보드 소개", icon="🏠", url_path="intro")
    ],
    "데이터랩 트렌드 분석": [
        st.Page(trend_page, title="검색어 트렌드 분석", icon="📈", url_path="trend"),
        st.Page(shopping_trend_page, title="쇼핑 트렌드 분석", icon="🛍️", url_path="shopping_trend")
    ],
    "검색 데이터 다차원 분석": [
        st.Page(shop_page, title="쇼핑 검색 분석", icon="🛒", url_path="shop"),
        st.Page(blog_page, title="블로그 검색 분석", icon="📝", url_path="blog"),
        st.Page(cafe_page, title="카페글 검색 분석", icon="👥", url_path="cafe"),
        st.Page(news_page, title="뉴스 검색 분석", icon="📰", url_path="news")
    ]
}

# 네비게이션 및 앱 구동
pg = st.navigation(pages)
pg.run()

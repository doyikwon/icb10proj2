"""
기본 EDA(탐색적 데이터 분석) 페이지.
버거지수와 관련 브랜드 매장 수에 대한 기초 통계량, 
상위 지역 분포, 그리고 지역별 산점도를 Plotly를 활용해 시각화합니다.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EDA", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/dashboard_data.csv')
    return df

def main():
    st.title("📊 기본 EDA (탐색적 데이터 분석)")
    
    with st.spinner("데이터를 불러오는 중입니다..."):
        df = load_data()
        
    if df.empty:
        st.error("데이터를 불러오지 못했습니다. 데이터 전처리를 먼저 수행해주세요.")
        return

    st.markdown("### 1. 기본 데이터 확인")
    st.write("원본 데이터의 첫 5행을 보여줍니다.")
    st.dataframe(df.head())
    
    st.markdown("### 2. 버거지수 및 브랜드 매장 수 기술 통계")
    # 수치형 변수만 선택
    num_cols = ['KFC', '롯데리아', '맥도날드', '버거킹', '총계', '버거지수']
    desc = df[num_cols].describe()
    st.dataframe(desc)
    
    st.markdown("### 3. 버거지수 상위 20개 지역")
    # 상위 20개 지역
    top20 = df.nlargest(20, '버거지수')
    fig_bar = px.bar(
        top20, 
        x='시도시군구명', 
        y='버거지수', 
        color='버거지수',
        color_continuous_scale='Blues',
        title='버거지수 상위 20개 지역'
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("### 4. 지역별 버거지수 산점도 (합계 5 이상 지역)")
    # 필터링 조건: 총계 5 이상 (왜곡 방지)
    df_filtered = df[df['총계'] >= 5].copy()
    fig_scatter = px.scatter(
        df_filtered,
        x='경도',
        y='위도',
        size='버거지수',
        color='버거지수',
        color_continuous_scale='Reds',
        hover_name='시도시군구명',
        hover_data=['버거지수', '총계', 'KFC', '롯데리아', '맥도날드', '버거킹'],
        title='지역별 버거지수 산점도 (합계 5 이상 지역)'
    )
    
    fig_scatter.update_layout(
        xaxis_title="경도(Longitude)",
        yaxis_title="위도(Latitude)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

if __name__ == "__main__":
    main()

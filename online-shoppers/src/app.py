"""
이 스크립트는 Online Shoppers Purchasing Intention 데이터셋을 바탕으로
수치형 및 범주형 변수의 EDA 결과를 보여주는 Streamlit 대시보드 애플리케이션입니다.
Revenue(수익) 발생 여부에 따른 데이터 분포 시각화 및 통계 요약을 제공합니다.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Online Shoppers Intention EDA", layout="wide")

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "online_shoppers_intention.csv")
    df = pd.read_csv(data_path)
    
    # 범주형 변수의 타입을 명확히 설정
    categorical_cols = ['Month', 'OperatingSystems', 'Browser', 'Region', 
                        'TrafficType', 'VisitorType', 'Weekend', 'Revenue']
    for col in categorical_cols:
        df[col] = df[col].astype(str)
        
    return df

def main():
    st.title("Online Shoppers Purchasing Intention EDA 대시보드 🛒")
    st.markdown("이 대시보드는 쇼핑몰 방문자의 구매 의도 데이터셋을 바탕으로, `Revenue`(수익 발생 여부)에 따른 각 변수의 특성을 시각화하고 요약 통계를 제공합니다.")
    
    try:
        df = load_data()
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return
    
    with st.expander("데이터셋 미리보기 (원본 데이터)"):
        st.dataframe(df.head())
        st.caption(f"전체 데이터 건수: {len(df):,} 건")
    
    # 변수 목록 정의
    numeric_cols = ['Administrative', 'Administrative_Duration', 'Informational', 
                    'Informational_Duration', 'ProductRelated', 'ProductRelated_Duration', 
                    'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay']
    
    categorical_cols = ['Month', 'OperatingSystems', 'Browser', 'Region', 
                        'TrafficType', 'VisitorType', 'Weekend']
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 수치형 변수 탐색", "🥧 범주형 변수 탐색", "🌪️ 퍼널 분석", "🌐 외부 API 연동 데이터"])
    
    # --- 1. 수치형 변수 EDA ---
    with tab1:
        st.header("수치형 변수 탐색 (Revenue 여부 비교)")
        st.markdown("각 수치형 변수별로 Revenue(수익) 발생 여부에 따른 분포 차이를 Box Plot으로 확인하고, 하단에 그룹별 기초 통계량을 제공합니다.")
        
        # 2열 레이아웃으로 배치
        cols = st.columns(2)
        
        for i, col in enumerate(numeric_cols):
            with cols[i % 2]:
                st.subheader(f"📌 {col}")
                
                # 히스토그램 위에 박스플롯을 서브플롯으로 함께 시각화
                fig = px.histogram(df, x=col, color="Revenue", 
                                   marginal="box", # 상단 박스플롯 추가
                                   barmode="overlay", # 겹쳐서 분포 확인
                                   title=f"{col} 히스토그램 및 박스플롯",
                                   color_discrete_map={"True": "#2E86C1", "False": "#E74C3C"})
                st.plotly_chart(fig, use_container_width=True)
                
                # 기술 통계량 산출
                # Revenue가 str 타입으로 되어있으므로, 통계량 계산 시 그대로 사용
                # 단, 변수는 float로 캐스팅 후 계산 (pandas 버전 호환성)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                stat_df = df.groupby('Revenue')[col].agg(
                    Count='count',
                    Mean='mean',
                    Median='median',
                    Std='std',
                    Min='min',
                    Max='max'
                ).reset_index()
                
                # 보기 좋게 소수점 포맷팅
                for stat_col in ['Mean', 'Median', 'Std', 'Min', 'Max']:
                    stat_df[stat_col] = stat_df[stat_col].round(2)
                    
                st.dataframe(stat_df, use_container_width=True, hide_index=True)
                st.markdown("---")
                
    # --- 2. 범주형 변수 EDA ---
    with tab2:
        st.header("범주형 변수 탐색 (Revenue 여부 비교)")
        st.markdown("각 범주형 변수의 분포를 Revenue 발생 여부별로 Bar Chart로 확인하고, 하단에 각 항목별 수익 발생 빈도와 비율(%)을 표로 제공합니다.")
        
        cols = st.columns(2)
        
        for i, col in enumerate(categorical_cols):
            with cols[i % 2]:
                st.subheader(f"📌 {col}")
                
                # 그룹화된 빈도수 계산
                freq_df = df.groupby([col, 'Revenue']).size().reset_index(name='Count')
                
                # Bar Chart 시각화 (빈도수)
                fig_count = px.bar(freq_df, x=col, y='Count', color='Revenue', barmode='group',
                             title=f"{col} 항목별 빈도수",
                             color_discrete_map={"True": "#2E86C1", "False": "#E74C3C"})
                st.plotly_chart(fig_count, use_container_width=True)
                
                # 100% 누적 막대 그래프 서브플롯 시각화 (비율 비교)
                fig_ratio = px.histogram(df, x=col, color='Revenue', barnorm='percent',
                                         title=f"{col} 항목별 Revenue 비율(%)",
                                         color_discrete_map={"True": "#2E86C1", "False": "#E74C3C"})
                fig_ratio.update_layout(yaxis_title="비율(%)")
                st.plotly_chart(fig_ratio, use_container_width=True)
                
                # 교차표 (빈도 및 비율)
                crosstab = pd.crosstab(df[col], df['Revenue'], margins=True, margins_name='Total')
                
                # Revenue='True' 비율 계산
                if 'True' in crosstab.columns:
                    crosstab['Revenue_True_Ratio(%)'] = (crosstab['True'] / crosstab['Total'] * 100).round(2)
                else:
                    crosstab['Revenue_True_Ratio(%)'] = 0.0
                    
                # 컬럼 순서 정리 및 인덱스 리셋
                crosstab = crosstab.reset_index()
                
                st.dataframe(crosstab, use_container_width=True, hide_index=True)
                st.markdown("---")
                
    # --- 3. 퍼널 분석 ---
    with tab3:
        st.header("방문자 퍼널 분석 (Funnel Analysis)")
        st.markdown(
            "퍼널 분석은 웹사이트에 방문한 사용자가 최종 목표(구매)에 도달하기까지의 "
            "단계를 시각화하여 어느 단계에서 이탈이 많이 발생하는지 파악하는 기법입니다. "
            "이 데이터셋에서는 다음 4단계로 퍼널을 정의했습니다."
        )
        
        st.info(
            "**[퍼널 단계 정의]**\n"
            "1. **전체 방문 (Total Visits)**: 쇼핑몰에 접속한 전체 세션 수\n"
            "2. **상품 조회 (Product View)**: 상품 관련 페이지(ProductRelated)를 1회 이상 조회한 세션 수\n"
            "3. **결제 진행/장바구니 (High Intent)**: 페이지 가치(PageValues)가 0보다 큰 세션 수 (장바구니 추가, 결제 단계 진입 등 유의미한 행동)\n"
            "4. **최종 구매 (Purchase)**: Revenue가 True(수익 발생)인 세션 수"
        )
        
        # 데이터 계산 (Revenue 변수는 앞에서 str로 캐스팅됨)
        total_visits = len(df)
        product_views = len(df[pd.to_numeric(df['ProductRelated'], errors='coerce') > 0])
        high_intent = len(df[pd.to_numeric(df['PageValues'], errors='coerce') > 0])
        purchases = len(df[df['Revenue'] == 'True'])
        
        funnel_data = dict(
            number=[total_visits, product_views, high_intent, purchases],
            stage=["1. 전체 방문", "2. 상품 조회", "3. 결제 진행/장바구니", "4. 최종 구매"]
        )
        
        fig_funnel = px.funnel(funnel_data, x='number', y='stage',
                               title="온라인 쇼핑몰 방문자 전환 퍼널",
                               labels={'number': '방문자(세션) 수', 'stage': '단계'},
                               color_discrete_sequence=['#8E44AD'])
        fig_funnel.update_layout(yaxis_title="퍼널 단계", xaxis_title="세션 수")
        st.plotly_chart(fig_funnel, use_container_width=True)
        
        # 전환율 통계 표시
        st.markdown("### 주요 전환율 지표")
        col1, col2, col3 = st.columns(3)
        with col1:
            conv_view = (product_views / total_visits) * 100 if total_visits > 0 else 0
            st.metric("상품 조회 전환율", f"{conv_view:.1f}%", help="전체 방문자 중 상품을 조회한 비율")
        with col2:
            conv_intent = (high_intent / product_views) * 100 if product_views > 0 else 0
            st.metric("결제 진행 전환율", f"{conv_intent:.1f}%", help="상품 조회자 중 결제/장바구니 단계로 넘어간 비율")
        with col3:
            conv_purchase = (purchases / high_intent) * 100 if high_intent > 0 else 0
            st.metric("최종 구매 전환율", f"{conv_purchase:.1f}%", help="결제 단계 진입자 중 최종 구매를 완료한 비율")

    # --- 4. 외부 API 연동 데이터 ---
    with tab4:
        st.header("외부 공공 API 연동 데이터 대시보드")
        st.markdown("식약처 및 각종 공공기관 API를 통해 수집된 최신 건강기능식품, 식품영양성분, 의약품 관련 데이터를 확인합니다.")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        api_data_path = os.path.join(base_dir, "data", "integrated_api_data.json")
        if os.path.exists(api_data_path):
            import json
            with open(api_data_path, 'r', encoding='utf-8') as f:
                api_data = json.load(f)
            api_df = pd.DataFrame(api_data)
            
            st.subheader("📝 통합 정제 데이터세트")
            st.dataframe(api_df, use_container_width=True)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🏢 수집 기관(Source) 비율")
                fig_agency = px.pie(api_df, names='source_agency', hole=0.3, 
                                    color_discrete_sequence=px.colors.sequential.Teal)
                st.plotly_chart(fig_agency, use_container_width=True)
                
            with col2:
                st.subheader("🏷️ 카테고리(Category) 비율")
                fig_category = px.pie(api_df, names='category', hole=0.3,
                                      color_discrete_sequence=px.colors.sequential.Burg)
                st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.warning("API 데이터 파일을 찾을 수 없습니다. 연동 스크립트(`fetch_apis.py` 및 `process_apis.py`)를 먼저 실행해 주세요.")

if __name__ == "__main__":
    main()

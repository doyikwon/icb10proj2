"""
이 스크립트는 사전 집계된 SQLite DB를 활용한 서울 생활인구 데이터 심층 EDA 대시보드입니다.
py-streamlit 스킬의 30개 체크리스트를 준수하며, 파케이(Parquet) 대신 가벼운 DB 쿼리를
활용해 획기적으로 개선된 로딩 속도를 제공합니다.
작성자: Antigravity
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import skew, kurtosis
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import folium
from streamlit_folium import st_folium
import requests
import sqlite3
import copy

st.set_page_config(page_title="서울 생활인구 심층 EDA 대시보드", layout="wide", page_icon="📈")

@st.cache_data(show_spinner="지도 데이터를 불러오는 중입니다...")
def load_geojson(level):
    if level == "구별":
        url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"
    else:
        url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_submunicipalities_geo_simple.json"
    response = requests.get(url)
    return response.json()

@st.cache_data(show_spinner="DB에서 데이터를 가져오는 중입니다...")
def load_data_from_db(query, db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def generate_insights(total_pop, top_dong, top_time):
    insights = []
    insights.append(f"- 총 분석 대상 인구 누적합은 **{total_pop:,.0f}명**입니다.")
    insights.append(f"- 가장 많은 인구가 집중된 행정동 코드는 **{top_dong}** 입니다.")
    insights.append(f"- 생활인구가 가장 많은 시간대는 **{top_time}시** 부근입니다.")
    return insights

def main():
    st.title("📈 서울 생활인구 데이터 심층 EDA 대시보드 (DB 최적화)")
    st.markdown("SQLite 사전 집계(Pre-aggregation)를 통해 **초고속 렌더링**을 구현한 심층 분석 대시보드입니다.")
    
    db_path = "c:/Users/doyik/OneDrive/바탕 화면/icb10proj2/seoul-pops/data/dashboard.db"
    if not os.path.exists(db_path):
        st.error(f"DB 파일을 찾을 수 없습니다. 먼저 init_db.py를 실행하세요.")
        return
        
    try:
        # 날짜 필터 로드
        dates_df = load_data_from_db("SELECT DISTINCT 기준일ID FROM map_agg_gu ORDER BY 기준일ID", db_path)
        dates = dates_df['기준일ID'].tolist()
        default_dates = dates[:3] if len(dates) > 3 else dates
    except Exception as e:
        st.error(f"DB 쿼리 중 오류가 발생했습니다: {e}")
        return

    # 사이드바 필터
    st.sidebar.header("🔍 분석 필터 옵션")
    st.sidebar.info("💡 10% 샘플링 옵션 대신, 사전에 완벽히 집계된 고속 DB 뷰를 사용합니다.")
    selected_dates = st.sidebar.multiselect("분석할 기준일 선택", dates, default=default_dates)
    
    if not selected_dates:
        st.warning("선택된 기준일이 없습니다. 필터를 조정해주세요.")
        return
        
    # SQL WHERE IN 절을 위한 문자열
    dates_str = ", ".join([f"'{d}'" for d in selected_dates])
    where_clause = f"WHERE 기준일ID IN ({dates_str})"
        
    st.sidebar.markdown("---")
    
    # ---------------------------------------------------------
    # 최상단 KPI 카드 배치
    # ---------------------------------------------------------
    meta_df = load_data_from_db("SELECT * FROM meta_stats", db_path)
    kpi_query = f"SELECT SUM(생활인구수) as 총인구수 FROM map_agg_gu {where_clause}"
    kpi_df = load_data_from_db(kpi_query, db_path)
    cur_total_pop = kpi_df['총인구수'].iloc[0] if not pd.isna(kpi_df['총인구수'].iloc[0]) else 0
    
    st.markdown("### 🔑 핵심 요약 지표 (KPI)")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("전체 데이터 건수 (Raw 기준)", f"{meta_df['총데이터수'].iloc[0]:,} 건")
    kpi2.metric("전체 결측치 수", f"{meta_df['총결측치'].iloc[0]:,} 개")
    kpi3.metric("선택된 기간 총 생활인구", f"{cur_total_pop:,.0f} 명")
    kpi4.metric("메모리 효율 및 속도", f"⚡ DB 캐시 렌더링")
    st.markdown("---")

    # ---------------------------------------------------------
    # 탭 구성
    # ---------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 지도 시각화 (Folium)", "📋 품질 및 단일 분포", "🔗 상관성 및 다차원 분석", "🚀 고급 기법 및 시뮬레이션"])
    
    # ==========================================
    # TAB 1: 지도 시각화 (Folium Choropleth)
    # ==========================================
    with tab1:
        st.header("🗺️ 서울시 구/동별 생활인구 밀도 시각화")
        st.markdown("특정 시간대의 생활인구 밀도를 구(Gu) 또는 동(Dong) 단위로 코로플리스 맵을 통해 확인합니다.")
        
        map_level = st.radio("지도 표시 기준 선택", ["구별 (Gu)", "동별 (Dong)"], horizontal=True)
        selected_time = st.slider("시간대 선택 (0~23시)", 0, 23, 12, key="map_time")
        
        seoul_geo = load_geojson(map_level[:2])
        
        if map_level == "구별 (Gu)":
            query = f"SELECT 시구군코드 as 지역코드, SUM(생활인구수) as 생활인구수 FROM map_agg_gu {where_clause} AND 시간대구분 = {selected_time} GROUP BY 시구군코드"
            key_on = "feature.properties.SIG_CD"
        else:
            query = f"SELECT 지역코드, SUM(생활인구수) as 생활인구수 FROM map_agg_dong {where_clause} AND 시간대구분 = {selected_time} GROUP BY 지역코드"
            key_on = "feature.properties.code"
            
        map_data = load_data_from_db(query, db_path)
        
        if map_data.empty:
            st.warning("해당 시간대에 데이터가 없거나 매핑에 실패했습니다.")
        else:
            seoul_geo_copy = copy.deepcopy(seoul_geo)
            pop_dict = dict(zip(map_data['지역코드'], map_data['생활인구수']))
            
            for feature in seoul_geo_copy['features']:
                if map_level == "구별 (Gu)":
                    code = feature['properties'].get('SIG_CD', '')
                    name = feature['properties'].get('SIG_KOR_NM', '')
                else:
                    code = feature['properties'].get('code', '')
                    name = feature['properties'].get('name', '')
                
                pop = pop_dict.get(code, 0)
                feature['properties']['pop_str'] = f"{pop:,.0f} 명"
                feature['properties']['region_name'] = name

            m = folium.Map(location=[37.5665, 126.9780], zoom_start=11 if map_level == "구별 (Gu)" else 12)
            
            cp = folium.Choropleth(
                geo_data=seoul_geo_copy,
                name="choropleth",
                data=map_data,
                columns=["지역코드", "생활인구수"],
                key_on=key_on,
                fill_color="YlOrRd",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name=f"{selected_time}시 {map_level[:2]} 생활인구 합계"
            ).add_to(m)
            
            folium.GeoJsonTooltip(
                fields=['region_name', 'pop_str'],
                aliases=['지역명:', '생활인구수:'],
                localize=True
            ).add_to(cp.geojson)
            
            st_folium(m, width=1000, height=600)
            st.caption("* 지도의 각 구역에 마우스를 올리면 해당 지역명과 생활인구수를 확인할 수 있습니다.")

    # ==========================================
    # TAB 2: 품질 및 단일 분포
    # ==========================================
    with tab2:
        st.header("1. 데이터 품질 및 기술 통계")
        
        # 10% 샘플 데이터 로드
        raw_sample = load_data_from_db(f"SELECT * FROM raw_sample {where_clause}", db_path)
        
        col_type, col_miss = st.columns(2)
        with col_type:
            st.markdown("#### 🔹 데이터 타입 및 논리적 유효성 (Sample 10%)")
            dtypes_df = pd.DataFrame(raw_sample.dtypes, columns=['데이터 타입']).astype(str)
            st.dataframe(dtypes_df, use_container_width=True)
            
            # 데이터 범위 유효성 검증
            min_pop = raw_sample['생활인구수'].min() if not raw_sample.empty else 0
            if min_pop < 0:
                st.error(f"데이터 오류 감지: 생활인구수 최소값이 음수입니다 ({min_pop}).")
            else:
                st.success(f"데이터 범위 정상: 생활인구 최소값 {min_pop}명 (음수 없음)")
                
        with col_miss:
            st.markdown("#### 🔹 결측치 가시성 (Sample 10%)")
            if not raw_sample.empty:
                missing_df = pd.DataFrame(raw_sample.isnull().sum(), columns=['결측치 수'])
                missing_df['결측 비율(%)'] = (missing_df['결측치 수'] / len(raw_sample) * 100).round(2)
                st.dataframe(missing_df, use_container_width=True)
            
        st.markdown("#### 🔹 수치형 항목 정밀 통계 (분포 비대칭성 및 집중도)")
        num_df = raw_sample.select_dtypes(include=[np.number])
        if not num_df.empty:
            desc = num_df.describe(percentiles=[.10, .25, .50, .75, .90]).T
            desc['최빈값(Mode)'] = num_df.mode().iloc[0]
            desc['왜도(Skewness)'] = num_df.apply(lambda x: skew(x.dropna()))
            desc['첨도(Kurtosis)'] = num_df.apply(lambda x: kurtosis(x.dropna()))
            desc['변동계수(CV)'] = desc['std'] / desc['mean']
            
            st.dataframe(desc.round(3), use_container_width=True)
            
        st.markdown("#### 🔹 범주형 항목 균형 분석 (전체 데이터 기반 DB 집계)")
        col_cat1, col_cat2 = st.columns(2)
        
        cat_stats = load_data_from_db(f"SELECT 성별, 연령대, SUM(카운트) as 카운트 FROM cat_stats {where_clause} GROUP BY 성별, 연령대", db_path)
        
        with col_cat1:
            if not cat_stats.empty:
                sex_counts = cat_stats.groupby('성별')['카운트'].sum()
                sex_ratio = sex_counts / sex_counts.sum()
                fig_sex = px.pie(values=sex_counts.values, names=sex_counts.index, title="성별 분포 비율", hole=0.4)
                st.plotly_chart(fig_sex, use_container_width=True)
                if (sex_ratio > 0.8).any():
                    st.warning("특정 성별에 80% 이상 데이터가 쏠려 있습니다 (데이터 불균형).")
        with col_cat2:
            if not cat_stats.empty:
                age_counts = cat_stats.groupby('연령대')['카운트'].sum().reset_index()
                fig_age = px.bar(age_counts.sort_values('연령대'), x='연령대', y='카운트', title="연령대별 분포 수")
                st.plotly_chart(fig_age, use_container_width=True)
            
        st.markdown("#### 🔹 생활인구수 Box Plot (이상치 식별 - Sample 10%)")
        if not raw_sample.empty:
            fig_box = px.box(raw_sample, x='시간대구분', y='생활인구수', color='성별',
                             title="시간대별 생활인구수 이상치(Outlier) 분포", points="outliers")
            fig_box.update_layout(xaxis_type='category')
            st.plotly_chart(fig_box, use_container_width=True)

    # ==========================================
    # TAB 3: 상관성 및 다차원 분석
    # ==========================================
    with tab3:
        st.header("2. 항목 간 관계 및 상관성 분석")
        
        col_corr, col_scatter = st.columns(2)
        with col_corr:
            st.markdown("#### 🔹 수치형 항목 상관행렬 (Sample 10%)")
            if not num_df.empty:
                corr = num_df.corr(numeric_only=True)
                fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
                st.plotly_chart(fig_corr, use_container_width=True)
                
                high_corr = False
                for i in range(len(corr.columns)):
                    for j in range(i):
                        if abs(corr.iloc[i, j]) > 0.9:
                            st.warning(f"다중공선성 경고: '{corr.columns[i]}'와 '{corr.columns[j]}'의 상관계수가 0.9 이상입니다.")
                            high_corr = True
                if not high_corr:
                    st.success("상관계수가 0.9 이상인 변수 쌍이 없습니다 (다중공선성 위험 낮음).")
                
        # 행정동별 집계 (DB)
        dong_query = f"SELECT 행정동코드, AVG(평균시간대) as 평균시간대, SUM(총생활인구) as 총생활인구 FROM dong_stats {where_clause} GROUP BY 행정동코드"
        dong_stats = load_data_from_db(dong_query, db_path)

        with col_scatter:
            st.markdown("#### 🔹 산점도 시각화 (행정동별 시간대 평균 인구)")
            if not dong_stats.empty:
                fig_scatter = px.scatter(dong_stats, x='평균시간대', y='총생활인구', 
                                         hover_data=['행정동코드'], title="행정동별 평균 시간대 vs 총 인구수")
                st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("#### 🔹 파레토 분석 (행정동 인구 쏠림 현상)")
        if not dong_stats.empty:
            dong_pop = dong_stats.sort_values('총생활인구', ascending=False).reset_index(drop=True)
            dong_pop['누적비율(%)'] = (dong_pop['총생활인구'].cumsum() / dong_pop['총생활인구'].sum()) * 100
            dong_pop['순위'] = range(1, len(dong_pop) + 1)
            
            fig_pareto = go.Figure()
            fig_pareto.add_trace(go.Bar(x=dong_pop['행정동코드'].astype(str), y=dong_pop['총생활인구'], name='생활인구수'))
            fig_pareto.add_trace(go.Scatter(x=dong_pop['행정동코드'].astype(str), y=dong_pop['누적비율(%)'], 
                                            name='누적 비율(%)', yaxis='y2', mode='lines+markers'))
            fig_pareto.update_layout(
                title="행정동별 인구 파레토 차트",
                yaxis=dict(title="생활인구수"),
                yaxis2=dict(title="누적 비율(%)", overlaying='y', side='right', range=[0, 105]),
                xaxis=dict(title="행정동코드", type='category')
            )
            st.plotly_chart(fig_pareto, use_container_width=True)
            
            top20_percent_idx = int(len(dong_pop) * 0.2)
            if top20_percent_idx > 0:
                top20_pop_ratio = dong_pop.iloc[top20_percent_idx-1]['누적비율(%)']
                st.info(f"파레토 분석: 상위 20%의 행정동({top20_percent_idx}개)이 전체 인구의 **{top20_pop_ratio:.1f}%**를 차지하고 있습니다.")

    # ==========================================
    # TAB 4: 고급 기법 및 시뮬레이션
    # ==========================================
    with tab4:
        st.header("3. 고급 분석 및 시뮬레이션")
        
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            st.markdown("#### 🔹 K-Means 군집 분석 (행정동 클러스터링)")
            st.markdown("행정동별 '총 생활인구'와 '평균 활동 시간대'를 기준으로 지역을 3개 군집으로 분류합니다.")
            
            if len(dong_stats) >= 3:
                scaler = StandardScaler()
                scaled_features = scaler.fit_transform(dong_stats[['평균시간대', '총생활인구']])
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                dong_stats['Cluster'] = kmeans.fit_predict(scaled_features)
                dong_stats['Cluster'] = dong_stats['Cluster'].astype(str)
                
                fig_cluster = px.scatter(dong_stats, x='평균시간대', y='총생활인구', color='Cluster',
                                         hover_data=['행정동코드'], title="행정동 3-그룹 군집화 결과")
                st.plotly_chart(fig_cluster, use_container_width=True)
            else:
                st.warning("군집 분석을 수행하기에 데이터가 부족합니다.")
                
        with col_adv2:
            st.markdown("#### 🔹 PCA 차원 축소 시각화 (Sample Data)")
            st.markdown("수치형 데이터의 변동성을 가장 잘 설명하는 주성분 2개로 차원을 축소하여 분포를 확인합니다.")
            
            pca_features = num_df.dropna()
            pca_sample = pca_features.sample(n=min(1000, len(pca_features)), random_state=42)
            
            if pca_sample.shape[1] >= 2:
                pca = PCA(n_components=2)
                components = pca.fit_transform(StandardScaler().fit_transform(pca_sample))
                pca_df = pd.DataFrame(components, columns=['PC1', 'PC2'])
                fig_pca = px.scatter(pca_df, x='PC1', y='PC2', title="PCA 변환 (샘플 1,000건)")
                st.plotly_chart(fig_pca, use_container_width=True)
                st.caption(f"* 주성분 1, 2가 전체 데이터 분산의 {pca.explained_variance_ratio_.sum()*100:.1f}%를 설명합니다.")
            else:
                st.warning("PCA를 수행할 수치형 변수가 부족합니다.")
                
        st.markdown("---")
        st.markdown("#### 🔹 What-if 시뮬레이션")
        st.markdown("특정 조건(시간대)에 인구가 가상으로 증가/감소했을 때의 총합 변화를 시뮬레이션 합니다.")
        
        sim_time = st.slider("조절할 시간대 선택", 0, 23, 12, key='sim_time')
        sim_rate = st.slider(f"{sim_time}시의 인구 증감율(%) 설정", -50, 100, 20)
        
        time_query = f"SELECT 시간대구분, SUM(생활인구수) as 생활인구수 FROM time_stats {where_clause} GROUP BY 시간대구분"
        time_df = load_data_from_db(time_query, db_path)
        
        if not time_df.empty:
            orig_total = time_df['생활인구수'].sum()
            target_pop = time_df[time_df['시간대구분'] == sim_time]['생활인구수'].sum()
            diff = target_pop * (sim_rate / 100)
            sim_total = orig_total + diff
            
            col_sim1, col_sim2 = st.columns(2)
            col_sim1.metric("기존 총 인구합계", f"{orig_total:,.0f} 명")
            col_sim2.metric(f"시뮬레이션 후 총 인구합계", f"{sim_total:,.0f} 명", f"{diff:,.0f} 명 변화")
            
            # Insights
            st.markdown("#### 💡 보고서 자동 요약 (Key Findings)")
            if not dong_stats.empty and not time_df.empty:
                top_dong = dong_stats.loc[dong_stats['총생활인구'].idxmax(), '행정동코드']
                top_time = time_df.loc[time_df['생활인구수'].idxmax(), '시간대구분']
                insights = generate_insights(orig_total, top_dong, top_time)
                for insight in insights:
                    st.write(insight)

if __name__ == "__main__":
    main()

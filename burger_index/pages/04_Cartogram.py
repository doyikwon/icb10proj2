"""
버거지수 카토그램(블록맵) 시각화 페이지.
전국 시군구를 격자 모양의 블록 맵으로 변환하여 버거지수를 표현합니다.
Plotly의 Heatmap을 활용하여 대한민국 지도의 형상을 유지하며 시각화합니다.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Cartogram Map", page_icon="🧩", layout="wide")

@st.cache_data
def load_and_prepare_data():
    # 1. 원본 데이터 불러오기
    df = pd.read_csv('data/dashboard_data.csv')
    df = df[df['시도시군구명'] != '총계'] # 총계 제외
    
    # 2. 행정구역명을 카토그램 ID에 맞게 변환하는 함수
    def parse_region(name):
        if pd.isna(name): return name
        if '화성' in name: return '화성'
        
        parts = name.split()
        if len(parts) == 1: return name
        sido = parts[0]
        sigungu = parts[1]
        
        if sido.startswith('세종'): return '세종'
        
        sido_map = {
            '서울특별시': '서울', '부산광역시': '부산', '대구광역시': '대구',
            '인천광역시': '인천', '광주광역시': '광주', '대전광역시': '대전', '울산광역시': '울산'
        }
        
        if sido in sido_map:
            sido_short = sido_map[sido]
            gu = sigungu
            if gu == '미추홀구' and sido_short == '인천': gu = '남구'
            
            # 군 단위 처리 (달성군, 기장군 등)
            if gu.endswith('군'):
                return f'{sido_short} {gu[:-1]}'
            
            if len(gu) == 2 and gu.endswith('구'):
                return f'{sido_short} {gu}'
            elif gu.endswith('구'):
                return f'{sido_short} {gu[:-1]}'
            return f'{sido_short} {gu}'
        else:
            if len(parts) == 3:
                si = parts[1]
                gu = parts[2]
                if si == '창원시':
                    if gu == '마산합포구': return '창원 합포'
                    if gu == '마산회원구': return '창원 회원'
                    if gu == '성산구': return '창원 성산'
                    if gu == '의창구': return '창원 의창'
                    if gu == '진해구': return '창원 진해'
                if len(gu) == 2 and gu.endswith('구'):
                    return f'{si[:-1]} {gu}'
                elif gu.endswith('구'):
                    return f'{si[:-1]} {gu[:-1]}'
            
            sigungu_short = sigungu[:-1]
            if sigungu_short == '고성':
                if sido.startswith('강원'): return '고성(강원)'
                else: return '고성(경남)'
            return sigungu_short

    # ID 변환 및 그룹화 (화성시 등의 병합을 위해)
    df['ID'] = df['시도시군구명'].apply(parse_region)
    grouped = df.groupby('ID')[['KFC', '롯데리아', '맥도날드', '버거킹']].sum().reset_index()
    # 버거지수 재계산
    grouped['버거지수'] = (grouped['KFC'] + grouped['맥도날드'] + grouped['버거킹']) / grouped['롯데리아']
    # inf 처리
    grouped['버거지수'] = grouped['버거지수'].replace(np.inf, np.nan)
    
    # 3. 카토그램 맵 데이터 불러오기
    map_url = 'https://raw.githubusercontent.com/PinkWink/DataScience/master/data/05.%20draw_korea.csv'
    map_df = pd.read_csv(map_url, index_col=0)
    
    # 4. 데이터 병합
    merged_df = pd.merge(map_df, grouped, on='ID', how='left')
    return merged_df

def main():
    st.title("🧩 전국 시군구 블록맵 (Cartogram)")
    st.markdown("전국의 시군구를 격자 모양(Cartogram)으로 변환하여 버거지수를 시각화한 차트입니다. 각 격자는 지역의 상대적인 위치를 유지하며 면적을 통일하여 비교하기 쉽게 만들어졌습니다.")
    
    with st.spinner("블록맵 데이터를 구성하는 중입니다..."):
        df = load_and_prepare_data()
        
        # Plotly Heatmap을 활용한 카토그램 그리기
        fig = go.Figure(data=go.Heatmap(
            x=df['x'],
            y=df['y'],
            z=df['버거지수'],
            text=df['ID'],
            texttemplate='%{text}',
            textfont=dict(size=12),
            colorscale='Blues',
            showscale=True,
            xgap=2,
            ygap=2,
            hoverinfo='text+z',
            hovertemplate='<b>%{text}</b><br>버거지수: %{z:.2f}<extra></extra>',
            zmin=0,
            zmax=3.0 # 최대값을 3.0으로 제한하여 색상 대비 확보
        ))
        
        # 축 및 레이아웃 설정
        fig.update_yaxes(autorange='reversed', visible=False, scaleanchor="x", scaleratio=1)
        fig.update_xaxes(visible=False)
        fig.update_layout(
            width=800, 
            height=1000, 
            plot_bgcolor='white',
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
if __name__ == "__main__":
    main()

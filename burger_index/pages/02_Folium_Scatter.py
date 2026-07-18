"""
Folium 산점도 시각화 페이지.
위경도 좌표를 활용하여 전국의 버거지수를 원형 마커(CircleMarker)로 지도 위에 표현합니다.
버거지수가 높을수록 원의 크기가 커지고 붉은색에 가까워지도록 설정합니다.
"""
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Folium Scatter Map", page_icon="🗺️", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/dashboard_data.csv')
    # 위도 경도가 있는 데이터만 필터링
    df = df.dropna(subset=['위도', '경도'])
    return df

def get_color(index_value):
    """버거지수에 따라 색상을 반환합니다."""
    if index_value >= 3.0:
        return 'darkred'
    elif index_value >= 2.0:
        return 'red'
    elif index_value >= 1.0:
        return 'orange'
    elif index_value >= 0.5:
        return 'lightgreen'
    else:
        return 'lightblue'

def main():
    st.title("🗺️ Folium 산점도 (버거지수 분포)")
    st.markdown("전국 시군구의 위도, 경도 좌표를 기반으로 버거지수를 지도 위에 시각화합니다. 원의 크기와 색상 농도는 버거지수에 비례합니다.")
    
    with st.spinner("지도를 생성하는 중입니다..."):
        df = load_data()
        
        # 합계가 적은 지역 필터링 옵션
        min_total = st.slider("최소 패스트푸드 매장 수 필터", min_value=0, max_value=20, value=5, step=1)
        df_filtered = df[df['총계'] >= min_total].copy()
        
        # 지도 중심점 계산 (한국 중심)
        center_lat = df_filtered['위도'].median() if not df_filtered.empty else 36.5
        center_lon = df_filtered['경도'].median() if not df_filtered.empty else 127.5
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="CartoDB positron")
        
        for idx, row in df_filtered.iterrows():
            burger_idx = row['버거지수']
            
            # 버거지수가 무한대(inf)인 경우 처리 (크기 제한)
            radius_size = min(burger_idx * 3, 20) if pd.notna(burger_idx) else 3
            
            tooltip_html = f"""
            <b>{row['시도시군구명']}</b><br>
            버거지수: {burger_idx:.2f}<br>
            총 매장 수: {row['총계']}
            """
            
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=radius_size,
                popup=folium.Popup(tooltip_html, max_width=300),
                tooltip=row['시도시군구명'],
                color=get_color(burger_idx),
                fill=True,
                fill_color=get_color(burger_idx),
                fill_opacity=0.7
            ).add_to(m)
            
        # Streamlit 화면에 지도 출력
        st_folium(m, width=1000, height=700)

if __name__ == "__main__":
    main()

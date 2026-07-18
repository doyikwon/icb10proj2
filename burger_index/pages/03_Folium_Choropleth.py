"""
Folium 단계구분도(Choropleth) 시각화 페이지.
행정구역 GeoJSON 데이터를 기반으로, 각 시군구의 버거지수를 색상으로 구분하여 나타냅니다.
South Korea Maps의 데이터를 연동하여 활용합니다.
"""
import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import st_folium

st.set_page_config(page_title="Folium Choropleth Map", page_icon="🗺️", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/dashboard_data.csv')
    # 시군구코드가 문자열 형태(5자리)이므로 Z-fill 확인
    df = df.dropna(subset=['시군구코드'])
    df['시군구코드'] = df['시군구코드'].astype(int).astype(str).str.zfill(5)
    return df

@st.cache_data
def load_geojson():
    url = 'https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_municipalities_geo_simple.json'
    r = requests.get(url)
    return r.json()

def main():
    st.title("🗺️ Folium 단계구분도 (버거지수 Choropleth)")
    st.markdown("대한민국 행정구역(시군구) GeoJSON을 바탕으로 지역별 버거지수를 색상으로 시각화합니다.")
    
    with st.spinner("데이터와 지도를 불러오는 중입니다. 잠시만 기다려주세요..."):
        df = load_data()
        geojson_data = load_geojson()
        
        # 합계가 적은 지역 필터링 옵션 (너무 적으면 이상치로 인해 지도 색상이 왜곡됨)
        min_total = st.slider("최소 패스트푸드 매장 수 필터", min_value=0, max_value=20, value=5, step=1)
        df_filtered = df[df['총계'] >= min_total].copy()
        
        # Choropleth 생성을 위한 Map 초기화
        m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles="CartoDB positron")
        
        # 단계구분도 추가
        folium.Choropleth(
            geo_data=geojson_data,
            data=df_filtered,
            columns=['시군구코드', '버거지수'],
            key_on='feature.properties.code',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='버거지수 (Burger Index)',
            nan_fill_color='lightgray'
        ).add_to(m)
        
        st_folium(m, width=1000, height=700)

if __name__ == "__main__":
    main()

"""
전국 숙박업소 상권 데이터를 시각화하기 위한 Streamlit 대시보드 애플리케이션 파일입니다.
사이드바를 통한 지역 및 숙박 업종 필터링 기능을 제공하며, 필터링된 데이터에 기반하여
주요 지표(KPI), 업종/지역별 통계 시각화(Plotly), 그리고 Folium 마커 클러스터링 지도를 구현합니다.
"""
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
import os

# 페이지 기본 설정
st.set_page_config(page_title="전국 숙박업소 상권 대시보드", layout="wide", page_icon="🏨")

# ==========================================
# 1. 데이터 로드 및 전처리
# ==========================================
@st.cache_data
def load_data():
    # 파일 경로 (현재 스크립트 위치를 기준으로 절대 경로 구성)
    current_dir = os.path.dirname(__file__)
    file_paths = [
        os.path.join(current_dir, 'data', 'site_raw.csv'),
        os.path.join(current_dir, '숙박업소_통합.csv'),
        'Tour/data/site_raw.csv',
        'Tour/숙박업소_통합.csv'
    ]
    df = pd.DataFrame()
    for path in file_paths:
        if os.path.exists(path):
            df = pd.read_csv(path, low_memory=False)
            break
            
    if df.empty:
        st.error("데이터 파일을 찾을 수 없습니다. 올바른 경로에 데이터가 있는지 확인해 주세요.")
        return pd.DataFrame()
    
    # 실제 컬럼명을 대시보드에서 사용할 표준 컬럼명으로 매핑합니다.
    col_mapping = {
        '시도명': '시도',
        '시군구명': '시군구',
        '행정동명': '동',       # 행정동 단위까지 조회를 위해 '행정동명' 사용
        '상권업종소분류명': '업종명',
        '상호명': '상호명',
        '도로명주소': '주소',   # 도로명주소를 기본 주소로 사용
        '위도': '위도',
        '경도': '경도'
    }
    
    # 존재하는 컬럼만 딕셔너리로 매핑하여 이름 변경
    rename_dict = {k: v for k, v in col_mapping.items() if k in df.columns}
    df = df.rename(columns=rename_dict)
    
    # 도로명주소가 결측치일 경우 지번주소로 대체
    if '주소' in df.columns and '지번주소' in df.columns:
        df['주소'] = df['주소'].fillna(df['지번주소'])
        
    # 위도와 경도 결측치가 있는 데이터는 지도에 표시할 수 없으므로 제외
    if '위도' in df.columns and '경도' in df.columns:
        # 데이터가 숫자가 아닌 문자열로 입력된 경우가 있을 수 있으므로 float 변환
        df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
        df['경도'] = pd.to_numeric(df['경도'], errors='coerce')
        df = df.dropna(subset=['위도', '경도'])
        
    return df

# 데이터 로딩
df_raw = load_data()

# 데이터가 비어있다면 이후 코드 실행 중단
if df_raw.empty:
    st.stop()

# ==========================================
# 2. 사이드바 필터 (Sidebar Filters)
# ==========================================
st.sidebar.header("🔍 필터 설정")

# 2-1. 지역 선택 (시도)
sido_list = ['전체'] + sorted(df_raw['시도'].dropna().unique().tolist())
selected_sido = st.sidebar.selectbox("지역(시도) 선택", sido_list)

# 선택한 시도에 따라 데이터 필터링
if selected_sido != '전체':
    df_sido = df_raw[df_raw['시도'] == selected_sido]
else:
    df_sido = df_raw.copy()

# 2-2. 시군구 선택 (선택된 시도에 종속되어 동적으로 변경됨)
sigungu_list = ['전체'] + sorted(df_sido['시군구'].dropna().unique().tolist())
selected_sigungu = st.sidebar.selectbox("시군구 선택", sigungu_list)

# 선택한 시군구에 따라 데이터 필터링
if selected_sigungu != '전체':
    df_sigungu = df_sido[df_sido['시군구'] == selected_sigungu]
else:
    df_sigungu = df_sido.copy()

# 2-3. 동 선택 (서울시를 선택하고 특정 시군구를 선택한 경우에만 활성화)
df_filtered = df_sigungu.copy()
if selected_sido == '서울특별시' and selected_sigungu != '전체' and '동' in df_filtered.columns:
    dong_list = ['전체'] + sorted(df_sigungu['동'].dropna().unique().tolist())
    selected_dong = st.sidebar.selectbox("행정동 선택 (서울시 전용)", dong_list)
    
    # 선택된 동에 따라 데이터 필터링
    if selected_dong != '전체':
        df_filtered = df_sigungu[df_sigungu['동'] == selected_dong]
else:
    selected_dong = '전체'

# 2-4. 숙박 업종 선택 (멀티 선택)
업종_list = sorted(df_filtered['업종명'].dropna().unique().tolist())
selected_types = st.sidebar.multiselect(
    "숙박 업종 선택", 
    options=업종_list, 
    default=업종_list
)

# 선택한 업종으로 최종 필터링 적용
if selected_types:
    df_filtered = df_filtered[df_filtered['업종명'].isin(selected_types)]
else:
    st.sidebar.warning("최소 한 개의 업종을 선택해 주세요.")
    st.stop()

# ==========================================
# 3. 메인 화면 1: 주요 지표 (Key Metrics)
# ==========================================
st.title("🏨 전국 숙박업소 상권 대시보드")
st.markdown("---")

# 총 숙박업소 수 계산
total_count = len(df_filtered)

# 가장 많은 업종 계산
if total_count > 0:
    most_common_type = df_filtered['업종명'].mode().iloc[0]
else:
    most_common_type = "없음"

# 밀집도 표현 (필터링된 영역 내 업소 개수)
density_info = f"{total_count:,} 개소"

# 3개의 컬럼으로 나누어 주요 지표를 카드 형태로 배치
col1, col2, col3 = st.columns(3)
col1.metric("총 숙박업소 수", f"{total_count:,} 개")
col2.metric("가장 많은 숙박 업종", most_common_type)
col3.metric("선택 지역 내 업소 밀집도", density_info)

st.markdown("---")

# ==========================================
# 4. 메인 화면 2: 통계 시각화 (Charts)
# ==========================================
if total_count > 0:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 숙박 업종별 비율")
        
        # 업종별 개수 집계
        type_counts = df_filtered['업종명'].value_counts().reset_index()
        type_counts.columns = ['업종명', '업소 수']
        
        # Plotly 파이 차트 생성
        fig_pie = px.pie(
            type_counts, 
            names='업종명', 
            values='업소 수', 
            hole=0.4, 
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_layout(margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.subheader("📈 지역별 업소 현황 (Top 15)")
        
        # 집계할 기준 지역을 동적으로 결정 (동 -> 시군구 -> 시도 순서)
        if selected_sigungu != '전체' and '동' in df_filtered.columns:
            region_col = '동'
        elif selected_sido != '전체':
            region_col = '시군구'
        else:
            region_col = '시도'
            
        # 지역별 개수 집계 후 상위 15개 추출
        region_counts = df_filtered[region_col].value_counts().reset_index().head(15)
        region_counts.columns = ['지역', '업소 수']
        
        # Plotly 바 차트 생성
        fig_bar = px.bar(
            region_counts, 
            x='지역', 
            y='업소 수', 
            text='업소 수', 
            color='업소 수',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(margin=dict(t=30, b=10, l=10, r=10), xaxis_title="지역", yaxis_title="업소 수")
        st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 5. 메인 화면 3: 인터랙션 지도 (Interactive Map)
# ==========================================
st.markdown("---")
st.subheader("🗺️ 숙박업소 위치 지도 (네이버 지도 + 클러스터링 적용)")

if total_count > 0:
    import json
    import streamlit.components.v1 as components

    # ⚠️ 네이버 클라우드 플랫폼에서 발급받은 Client ID를 입력하세요.
    # localhost:8501 등 실행 환경 URL이 NCP Web 서비스 URL에 등록되어 있어야 합니다.
    NAVER_CLIENT_ID = "YOUR_CLIENT_ID" 

    center_lat = df_filtered['위도'].mean()
    center_lon = df_filtered['경도'].mean()
    
    max_markers = 3000
    df_map = df_filtered.head(max_markers)
    if total_count > max_markers:
        st.warning(f"⚠️ 렌더링 속도 저하를 방지하기 위해 상위 {max_markers}개의 마커만 표시됩니다.")
        
    # JS로 전달할 데이터를 리스트/딕셔너리 형태로 변환
    map_data = []
    for idx, row in df_map.iterrows():
        map_data.append({
            "lat": float(row['위도']),
            "lng": float(row['경도']),
            "name": str(row.get("상호명", "알수없음")).replace('"', '\\"'),
            "type": str(row.get("업종명", "알수없음")),
            "addr": str(row.get("주소", "알수없음")).replace('"', '\\"')
        })
    json_data = json.dumps(map_data)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ margin: 0; padding: 0; }}
            #map {{ width: 100%; height: 600px; }}
            .iw_inner {{ padding: 15px; font-size: 13px; font-family: 'Malgun Gothic', sans-serif; }}
            .iw_inner h4 {{ margin: 0 0 8px 0; font-size: 15px; color: #333; }}
            .iw_inner p {{ margin: 0; color: #666; line-height: 1.5; }}
        </style>
        <!-- 네이버 지도 API -->
        <script type="text/javascript" src="https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId={NAVER_CLIENT_ID}"></script>
        <!-- 마커 클러스터링 라이브러리 -->
        <script type="text/javascript" src="https://navermaps.github.io/MarkerClustering/src/MarkerClustering.js"></script>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var mapData = {json_data};
            
            if (typeof naver === 'undefined' || !naver.maps) {{
                document.getElementById('map').innerHTML = '<div style="padding:20px; color:red; font-weight:bold;">네이버 지도 API를 불러올 수 없습니다.<br>코드 내의 NAVER_CLIENT_ID를 실제 발급받은 ID로 변경해주세요.</div>';
            }} else {{
                var map = new naver.maps.Map("map", {{
                    center: new naver.maps.LatLng({center_lat}, {center_lon}),
                    zoom: 11,
                    maxZoom: 18
                }});

                var markers = [];
                var infoWindows = [];

                mapData.forEach(function(item, index) {{
                    var position = new naver.maps.LatLng(item.lat, item.lng);
                    var marker = new naver.maps.Marker({{
                        position: position,
                        title: item.name
                    }});
                    
                    var contentString = [
                        '<div class="iw_inner">',
                        '   <h4>' + item.name + '</h4>',
                        '   <p><b>업종:</b> ' + item.type + '<br />',
                        '   <b>주소:</b> ' + item.addr + '</p>',
                        '</div>'
                    ].join('');
                    
                    var infoWindow = new naver.maps.InfoWindow({{
                        content: contentString,
                        maxWidth: 300,
                        backgroundColor: "#fff",
                        borderColor: "#ccc",
                        borderWidth: 1,
                        anchorSize: new naver.maps.Size(10, 10),
                        anchorSkew: true,
                        pixelOffset: new naver.maps.Point(0, -10)
                    }});
                    
                    markers.push(marker);
                    infoWindows.push(infoWindow);
                }});
                
                // 네이버 지도 클러스터링 마커 아이콘 설정
                var htmlMarker1 = {{
                        content: '<div style="cursor:pointer;width:40px;height:40px;line-height:42px;font-size:10px;color:white;text-align:center;font-weight:bold;background:url(https://navermaps.github.io/MarkerClustering/images/cluster-marker-1.png);background-size:contain;"></div>',
                        size: N.Size(40, 40),
                        anchor: N.Point(20, 20)
                    }},
                    htmlMarker2 = {{
                        content: '<div style="cursor:pointer;width:40px;height:40px;line-height:42px;font-size:10px;color:white;text-align:center;font-weight:bold;background:url(https://navermaps.github.io/MarkerClustering/images/cluster-marker-2.png);background-size:contain;"></div>',
                        size: N.Size(40, 40),
                        anchor: N.Point(20, 20)
                    }},
                    htmlMarker3 = {{
                        content: '<div style="cursor:pointer;width:40px;height:40px;line-height:42px;font-size:10px;color:white;text-align:center;font-weight:bold;background:url(https://navermaps.github.io/MarkerClustering/images/cluster-marker-3.png);background-size:contain;"></div>',
                        size: N.Size(40, 40),
                        anchor: N.Point(20, 20)
                    }},
                    htmlMarker4 = {{
                        content: '<div style="cursor:pointer;width:40px;height:40px;line-height:42px;font-size:10px;color:white;text-align:center;font-weight:bold;background:url(https://navermaps.github.io/MarkerClustering/images/cluster-marker-4.png);background-size:contain;"></div>',
                        size: N.Size(40, 40),
                        anchor: N.Point(20, 20)
                    }},
                    htmlMarker5 = {{
                        content: '<div style="cursor:pointer;width:40px;height:40px;line-height:42px;font-size:10px;color:white;text-align:center;font-weight:bold;background:url(https://navermaps.github.io/MarkerClustering/images/cluster-marker-5.png);background-size:contain;"></div>',
                        size: N.Size(40, 40),
                        anchor: N.Point(20, 20)
                    }};

                var markerClustering = new MarkerClustering({{
                    minClusterSize: 2,
                    maxZoom: 13,
                    map: map,
                    markers: markers,
                    disableClickZoom: false,
                    gridSize: 120,
                    icons: [htmlMarker1, htmlMarker2, htmlMarker3, htmlMarker4, htmlMarker5],
                    indexGenerator: [10, 100, 200, 500, 1000],
                    stylingFunction: function(clusterMarker, count) {{
                        clusterMarker.getElement().querySelector('div:first-child').innerText = count;
                    }}
                }});

                // 마커 클릭 시 정보창 열기
                for (var i = 0; i < markers.length; i++) {{
                    naver.maps.Event.addListener(markers[i], 'click', getClickHandler(i));
                }}

                function getClickHandler(seq) {{
                    return function(e) {{
                        var marker = markers[seq],
                            infoWindow = infoWindows[seq];

                        if (infoWindow.getMap()) {{
                            infoWindow.close();
                        }} else {{
                            infoWindow.open(map, marker);
                        }}
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    # HTML 컴포넌트 렌더링
    components.html(html_code, height=600)
else:
    st.info("조건에 맞는 데이터가 없습니다.")

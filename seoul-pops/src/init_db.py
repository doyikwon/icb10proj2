"""
서울 생활인구 데이터 사전 집계 및 SQLite DB 생성 스크립트
이 스크립트는 원본 Parquet 파일을 로드하여 대시보드 표시를 위한 집계 데이터를 
계산하고, 결과를 'dashboard.db' 파일에 저장합니다.

작성자: Antigravity
"""

import pandas as pd
import sqlite3
import os

def init_db():
    print("데이터 로딩 중...")
    base_dir = "c:/Users/doyik/OneDrive/바탕 화면/icb10proj2/seoul-pops/data"
    parquet_path = os.path.join(base_dir, "LOCAL_PEOPLE_DONG_202606.parquet")
    mapping_path = os.path.join(base_dir, "행정동코드_매핑정보_20241218.xlsx")
    db_path = os.path.join(base_dir, "dashboard.db")
    
    df = pd.read_parquet(parquet_path)
    map_df = pd.read_excel(mapping_path, header=1)
    
    # DB 연결 (기존 파일이 있으면 덮어씁니다)
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    
    print("1. 구별 지도 집계 (map_agg_gu) 생성 중...")
    df['시구군코드'] = df['행정동코드'].astype(str).str[:5]
    map_agg_gu = df.groupby(['기준일ID', '시간대구분', '시구군코드'])['생활인구수'].sum().reset_index()
    map_agg_gu.to_sql('map_agg_gu', conn, if_exists='replace', index=False)
    
    print("2. 동별 지도 집계 (map_agg_dong) 생성 중...")
    map_df['H_DNG_CD'] = map_df['H_DNG_CD'].astype(str)
    map_df['H_SDNG_CD'] = map_df['H_SDNG_CD'].astype(str)
    df['행정동코드_str'] = df['행정동코드'].astype(str)
    
    merged = pd.merge(df, map_df, left_on='행정동코드_str', right_on='H_DNG_CD', how='inner')
    map_agg_dong = merged.groupby(['기준일ID', '시간대구분', 'H_SDNG_CD'])['생활인구수'].sum().reset_index()
    map_agg_dong.rename(columns={'H_SDNG_CD': '지역코드'}, inplace=True)
    map_agg_dong.to_sql('map_agg_dong', conn, if_exists='replace', index=False)
    
    print("3. 행정동별 통계 (dong_stats) 생성 중...")
    dong_stats = df.groupby(['기준일ID', '행정동코드']).agg(
        평균시간대=('시간대구분', 'mean'),
        총생활인구=('생활인구수', 'sum')
    ).reset_index()
    dong_stats.to_sql('dong_stats', conn, if_exists='replace', index=False)
    
    print("4. 시간대/성별 통계 (time_stats) 생성 중...")
    time_stats = df.groupby(['기준일ID', '시간대구분', '성별'])['생활인구수'].sum().reset_index()
    time_stats.to_sql('time_stats', conn, if_exists='replace', index=False)
    
    print("5. 연령대/성별 통계 (cat_stats) 생성 중...")
    cat_stats = df.groupby(['기준일ID', '연령대', '성별'])['생활인구수'].count().reset_index()
    cat_stats.rename(columns={'생활인구수': '카운트'}, inplace=True)
    cat_stats.to_sql('cat_stats', conn, if_exists='replace', index=False)
    
    print("6. 상관/분포 분석용 10% Raw 샘플링 데이터 저장 중...")
    raw_sample = df.sample(frac=0.1, random_state=42)
    # 메모리 절약을 위해 불필요한 임시 컬럼 제거
    if '시구군코드' in raw_sample.columns:
        raw_sample = raw_sample.drop(columns=['시구군코드'])
    if '행정동코드_str' in raw_sample.columns:
        raw_sample = raw_sample.drop(columns=['행정동코드_str'])
    raw_sample.to_sql('raw_sample', conn, if_exists='replace', index=False)
    
    print("7. 기초 통계량 (Describe & 결측치) 계산 중...")
    desc = raw_sample.describe(percentiles=[.10, .25, .50, .75, .90]).reset_index()
    desc.to_sql('describe_stats', conn, if_exists='replace', index=False)
    
    # 총 인구수 및 결측치 등 전역 메타데이터
    total_pop = df['생활인구수'].sum()
    total_rows = len(df)
    missing_sum = df.isnull().sum().sum()
    # 파이썬 원시 타입으로 변환 (numpy type -> int/float)
    total_pop = float(total_pop)
    total_rows = int(total_rows)
    missing_sum = int(missing_sum)
    
    meta_df = pd.DataFrame({
        '총인구수': [total_pop],
        '총데이터수': [total_rows],
        '총결측치': [missing_sum]
    })
    meta_df.to_sql('meta_stats', conn, if_exists='replace', index=False)
    
    conn.close()
    print("✅ 성공적으로 dashboard.db 생성 완료!")

if __name__ == "__main__":
    init_db()

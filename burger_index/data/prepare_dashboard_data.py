"""
대시보드 구현을 위한 데이터 전처리 스크립트.
burger.csv 파일에서 시군구코드 매핑 정보를 추출하여,
기존의 crosstab_region_brand.csv 파일에 병합한 뒤 dashboard_data.csv로 저장합니다.
생성된 시군구코드는 GeoJSON 매핑을 위해 5자리 문자열로 변환됩니다.
"""
import pandas as pd
import numpy as np

def main():
    # 1. Load original burger.csv to extract 시군구코드 mapping
    burger_df = pd.read_csv('burger.csv')
    
    # Create 시도시군구명
    burger_df['시도시군구명'] = burger_df['시도명'] + ' ' + burger_df['시군구명']
    
    # Get unique mapping of 시도시군구명 to 시군구코드
    # Note: 시군구코드 should be 5-digit string for GeoJSON mapping
    mapping_df = burger_df[['시도시군구명', '시군구코드']].dropna().drop_duplicates()
    mapping_df['시군구코드_str'] = mapping_df['시군구코드'].astype(int).astype(str).str.zfill(5)
    
    mapping_dict = dict(zip(mapping_df['시도시군구명'], mapping_df['시군구코드_str']))
    
    # 2. Load aggregated crosstab data
    crosstab_df = pd.read_csv('crosstab_region_brand.csv')
    
    # 3. Add 시군구코드 to crosstab_df
    crosstab_df['시군구코드'] = crosstab_df['시도시군구명'].map(mapping_dict)
    
    # 4. Save to dashboard_data.csv
    crosstab_df.to_csv('dashboard_data.csv', index=False)
    print("dashboard_data.csv generated successfully.")

if __name__ == "__main__":
    main()

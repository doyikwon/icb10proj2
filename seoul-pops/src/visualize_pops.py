"""
연남동과 성수동의 행정동코드를 추출하여
시간대별, 연령대별 생활인구수를 선그래프로 시각화하는 스크립트입니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    excel_path = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\data\행정동코드_매핑정보_20241218.xlsx"
    parquet_path = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\data\LOCAL_PEOPLE_DONG_202606.parquet"
    save_path = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\images\population_by_age_time.png"
    
    # 1. 매핑 테이블 로드
    df_map = pd.read_excel(excel_path)
    # 컬럼 이름을 명확하게 지정하고 첫 번째 행(영문명)을 제외
    df_map.columns = ['통계청동코드', '행자부동코드', '시도명', '시군구명', '행정동명']
    df_map = df_map.iloc[1:].copy()
    
    # 연남동, 성수동 필터링
    target_dongs = df_map[df_map['행정동명'].str.contains('연남|성수', na=False)].copy()
    target_dongs['행자부동코드'] = target_dongs['행자부동코드'].astype(int)
    
    print("--- 타겟 행정동 ---")
    print(target_dongs[['행정동명', '행자부동코드']])
    
    # 2. 파케이 데이터 로드
    df_pop = pd.read_parquet(parquet_path)
    
    # 3. 데이터 병합 (타겟 행정동만 추출)
    # 행정동코드는 파케이에서 category일 수 있으므로 int로 변환
    if pd.api.types.is_categorical_dtype(df_pop['행정동코드']) or isinstance(df_pop['행정동코드'].dtype, pd.CategoricalDtype):
        df_pop['행정동코드'] = df_pop['행정동코드'].astype(int)
    
    merged_df = pd.merge(
        df_pop, 
        target_dongs[['행자부동코드', '행정동명']], 
        left_on='행정동코드', 
        right_on='행자부동코드', 
        how='inner'
    )
    
    print(f"\n--- 병합된 데이터 건수: {len(merged_df)} ---")
    
    # 4. 데이터 집계
    # 성별은 제외하고 시간대, 행정동, 연령대별 생활인구 합계 계산
    grouped_df = merged_df.groupby(['행정동명', '시간대구분', '연령대'], observed=True)['생활인구수'].sum().reset_index()
    
    # 5. 시각화
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    g = sns.relplot(
        data=grouped_df,
        x='시간대구분',
        y='생활인구수',
        hue='행정동명',
        col='연령대',
        col_wrap=4,
        kind='line',
        marker='o',
        height=3.5,
        aspect=1.2,
        facet_kws={'sharey': False} # 연령대별로 인구 스케일이 다를 수 있으므로 y축 공유 해제
    )
    
    g.set_axis_labels("시간대", "생활인구수")
    g.fig.suptitle("연남동 및 성수동 연령대별/시간대별 생활인구수", y=1.02, fontsize=18, fontweight='bold')
    
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    print(f"\n시각화 이미지가 저장되었습니다: {save_path}")

if __name__ == '__main__':
    main()

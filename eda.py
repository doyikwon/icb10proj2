"""
서울시 생활인구 데이터(Parquet)에 대한 EDA 및 시각화를 수행하는 스크립트입니다.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import sys

def main():
    # Ensure UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    
    file_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
    df = pd.read_parquet(file_path)
    
    # 1. Initial Inspection
    print("=== INFO ===")
    df.info()
    print(f"\nTotal rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print("=== HEAD ===")
    print(df.head())
    print("=== TAIL ===")
    print(df.tail())
    
    # 2. Descriptive Statistics
    print("\n=== NUMERICAL DESC STATS ===")
    num_cols = ['시간대구분', '행정동코드', '생활인구수']
    print(df[num_cols].describe())
    
    print("\n=== CATEGORICAL DESC STATS ===")
    cat_cols = ['기준일ID', '성별', '연령대']
    print(df[cat_cols].astype(str).describe())
    
    # Generate Plots
    os.makedirs('images', exist_ok=True)
    
    # 1. 생활인구수 Histogram
    plt.figure(figsize=(10, 5))
    plt.hist(df['생활인구수'], bins=50, color='skyblue', edgecolor='black')
    plt.title('생활인구수 분포 (Histogram)')
    plt.xlabel('생활인구수')
    plt.ylabel('빈도')
    plt.savefig('images/plot1_hist.png', bbox_inches='tight')
    plt.close()
    
    # 2. 생활인구수 Boxplot
    plt.figure(figsize=(10, 5))
    plt.boxplot(df['생활인구수'], vert=False)
    plt.title('생활인구수 상자수염그림 (Boxplot)')
    plt.xlabel('생활인구수')
    plt.savefig('images/plot2_box.png', bbox_inches='tight')
    plt.close()
    
    # 3. 성별 총 생활인구수
    gender_pop = df.groupby('성별')['생활인구수'].sum().reset_index()
    print("\n=== 성별 생활인구수 ===")
    print(gender_pop)
    plt.figure(figsize=(8, 5))
    plt.bar(gender_pop['성별'], gender_pop['생활인구수'], color=['blue', 'red'])
    plt.title('성별 총 생활인구수')
    plt.ylabel('총 생활인구수')
    plt.savefig('images/plot3_gender.png', bbox_inches='tight')
    plt.close()
    
    # 4. 연령대별 총 생활인구수
    age_pop = df.groupby('연령대')['생활인구수'].sum().reset_index()
    # Sort ages reasonably if possible, but they are strings like '0세부터9세', '10세부터14세'
    print("\n=== 연령대별 생활인구수 ===")
    print(age_pop)
    plt.figure(figsize=(12, 6))
    plt.bar(age_pop['연령대'], age_pop['생활인구수'], color='green')
    plt.title('연령대별 총 생활인구수')
    plt.xticks(rotation=45)
    plt.ylabel('총 생활인구수')
    plt.savefig('images/plot4_age.png', bbox_inches='tight')
    plt.close()
    
    # 5. 시간대별 평균 생활인구수
    time_pop = df.groupby('시간대구분')['생활인구수'].mean().reset_index()
    print("\n=== 시간대별 평균 생활인구수 ===")
    print(time_pop)
    plt.figure(figsize=(10, 5))
    plt.plot(time_pop['시간대구분'], time_pop['생활인구수'], marker='o', linestyle='-')
    plt.title('시간대별 평균 생활인구수')
    plt.xlabel('시간대')
    plt.ylabel('평균 생활인구수')
    plt.xticks(range(0, 24))
    plt.grid(True, alpha=0.3)
    plt.savefig('images/plot5_time.png', bbox_inches='tight')
    plt.close()
    
    # 6. 시간대 & 성별 총 생활인구수
    time_gender = df.groupby(['시간대구분', '성별'])['생활인구수'].sum().unstack()
    print("\n=== 시간대 & 성별 총 생활인구수 ===")
    print(time_gender.head())
    plt.figure(figsize=(12, 6))
    for col in time_gender.columns:
        plt.plot(time_gender.index, time_gender[col], marker='o', label=col)
    plt.title('시간대 및 성별 총 생활인구수')
    plt.xlabel('시간대')
    plt.ylabel('총 생활인구수')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('images/plot6_time_gender.png', bbox_inches='tight')
    plt.close()
    
    # 7. 시간대 vs 연령대 히트맵 데이터
    time_age = df.groupby(['시간대구분', '연령대'])['생활인구수'].sum().unstack()
    print("\n=== 시간대 vs 연령대 (Heatmap Data) ===")
    print(time_age.iloc[:5, :5])
    plt.figure(figsize=(12, 8))
    plt.imshow(time_age, cmap='YlGnBu', aspect='auto')
    plt.colorbar(label='총 생활인구수')
    plt.title('시간대 및 연령대별 총 생활인구수 (Heatmap)')
    plt.xlabel('연령대')
    plt.ylabel('시간대')
    plt.yticks(range(0, 24))
    plt.xticks(range(len(time_age.columns)), time_age.columns, rotation=90)
    plt.savefig('images/plot7_heatmap_age.png', bbox_inches='tight')
    plt.close()
    
    # 8. 기준일자별 총 생활인구수 (Trend)
    date_pop = df.groupby('기준일ID')['생활인구수'].sum().reset_index()
    print("\n=== 일자별 총 생활인구수 ===")
    print(date_pop.head())
    plt.figure(figsize=(12, 5))
    plt.plot(date_pop['기준일ID'].astype(str), date_pop['생활인구수'], marker='s', color='purple')
    plt.title('일자별 총 생활인구수 추이')
    plt.xticks(rotation=45)
    plt.ylabel('총 생활인구수')
    plt.grid(True, alpha=0.3)
    plt.savefig('images/plot8_date.png', bbox_inches='tight')
    plt.close()
    
    # 9. Top 30 행정동코드
    dong_pop = df.groupby('행정동코드')['생활인구수'].sum().sort_values(ascending=False).head(30)
    print("\n=== Top 30 행정동 ===")
    print(dong_pop.head())
    plt.figure(figsize=(12, 6))
    dong_pop.plot(kind='bar', color='orange')
    plt.title('상위 30개 행정동별 총 생활인구수')
    plt.ylabel('총 생활인구수')
    plt.xticks(rotation=90)
    plt.savefig('images/plot9_dong.png', bbox_inches='tight')
    plt.close()
    
    # 10. 기준일자별 & 성별 총 생활인구수
    date_gender = df.groupby(['기준일ID', '성별'])['생활인구수'].sum().unstack()
    print("\n=== 일자 & 성별 총 생활인구수 ===")
    print(date_gender.head())
    plt.figure(figsize=(12, 6))
    for col in date_gender.columns:
        plt.plot(date_gender.index.astype(str), date_gender[col], marker='^', label=col)
    plt.title('일자별 및 성별 총 생활인구수 추이')
    plt.xticks(rotation=45)
    plt.ylabel('총 생활인구수')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('images/plot10_date_gender.png', bbox_inches='tight')
    plt.close()
    
    print("All plots generated successfully.")

if __name__ == "__main__":
    main()

"""
burger.csv 파일에서 상권업종대분류명이 '과학·기술', '교육'인 데이터를 제외하고 
다시 CSV 파일로 덮어쓰는 스크립트입니다.
"""
import pandas as pd
import os

file_path = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\data\burger.csv"

# 데이터 불러오기
df = pd.read_csv(file_path, encoding='utf-8')

# 제외할 카테고리
exclude_categories = ['과학·기술', '교육']

# 필터링 (해당 카테고리가 아닌 데이터만 남김)
df_filtered = df[~df['상권업종대분류명'].isin(exclude_categories)]

# 결과를 기존 파일에 덮어쓰기
df_filtered.to_csv(file_path, encoding='utf-8', index=False)

print(f"제외 전 데이터 수: {len(df)}")
print(f"제외 후 데이터 수: {len(df_filtered)}")
print(f"제외된 데이터 수: {len(df) - len(df_filtered)}")
print("CSV 파일이 성공적으로 업데이트되었습니다.")

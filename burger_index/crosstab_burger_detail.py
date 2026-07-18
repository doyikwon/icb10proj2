"""
버거 프랜차이즈 데이터 중 상권업종대분류명이 '과학·기술', '교육', '소매'에 
해당하는 업체 리스트를 추출하여 마크다운 형태로 저장하는 스크립트입니다.
"""
import pandas as pd
import os

file_path = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\data\burger.csv"
output_txt = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\detail_list.md"

# 데이터 불러오기
df = pd.read_csv(file_path, encoding='utf-8')

# 필터링 조건
categories = ['과학·기술', '교육', '소매']
filtered_df = df[df['상권업종대분류명'].isin(categories)]

# 필요한 컬럼 선택 (상호명, 지점명, 상권업종대분류명, 도로명주소)
result_df = filtered_df[['상권업종대분류명', '상호명', '지점명', '도로명주소']].copy()

# 지점명이 결측치인 경우 빈 문자열로 대체
result_df['지점명'] = result_df['지점명'].fillna('')

# 정렬 (대분류명, 상호명 순)
result_df = result_df.sort_values(by=['상권업종대분류명', '상호명'])

# 마크다운 표 형태로 저장
with open(output_txt, "w", encoding="utf-8") as f:
    f.write(f"총 {len(result_df)}건의 데이터가 발견되었습니다.\n\n")
    f.write(result_df.to_markdown(index=False))

print(f"저장 완료: {output_txt}")

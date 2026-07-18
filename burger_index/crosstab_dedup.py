"""
burger.csv에서 상호명, 지점명, 도로명주소가 동일한 실질적 중복 데이터를 제거하고,
남은 데이터에 대해 브랜드명과 상권업종대분류명 교차표를 작성하는 스크립트입니다.
"""
import pandas as pd
import os

file_path = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\data\burger.csv"
output_md = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\crosstab_dedup_result.md"

# 1. 데이터 불러오기
df = pd.read_csv(file_path, encoding='utf-8')

# 2. 중복 제거 (상호명, 지점명, 도로명주소 기준)
# 지점명이 NaN인 경우도 동일하게 처리하기 위해 잠시 빈 문자열로 치환해서 중복 제거 후 복구할 수도 있으나,
# drop_duplicates는 기본적으로 NaN을 서로 같은 것으로 취급하므로 그대로 진행해도 무방합니다.
subset_cols = ['상호명', '지점명', '도로명주소']
df_dedup = df.drop_duplicates(subset=subset_cols, keep='first').copy()

print(f"중복 제거 전: {len(df)}건")
print(f"중복 제거 후: {len(df_dedup)}건")

# 3. 덮어쓰기 (중복이 제거된 데이터로 업데이트)
df_dedup.to_csv(file_path, encoding='utf-8', index=False)
print("중복이 제거된 데이터로 burger.csv 파일을 업데이트했습니다.")

# 4. 브랜드명 파생변수 생성
def get_brand(name):
    name = str(name).lower().replace(" ", "")
    if "버거킹" in name or "burgerking" in name:
        return "버거킹"
    elif "맥도날드" in name or "mcdonald" in name:
        return "맥도날드"
    elif "kfc" in name:
        return "KFC"
    elif "롯데리아" in name or "lotteria" in name:
        return "롯데리아"
    else:
        return "기타"

df_dedup['브랜드명'] = df_dedup['상호명'].apply(get_brand)

# 5. 브랜드명 vs 상권업종대분류명 교차표(빈도수) 작성
cross_tab = pd.crosstab(df_dedup['브랜드명'], df_dedup['상권업종대분류명'], margins=True, margins_name="총계")

# 파일로 저장
with open(output_md, "w", encoding="utf-8") as f:
    f.write(cross_tab.to_markdown())

print(f"교차표 작성 완료. 결과가 {output_md} 에 저장되었습니다.")

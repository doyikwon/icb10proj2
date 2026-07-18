"""
상호명을 기반으로 프랜차이즈 브랜드명 파생변수를 생성하고,
브랜드명과 상권업종대분류명 간의 교차표(빈도수)를 작성하는 스크립트입니다.
"""
import pandas as pd
import os

file_path = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\data\burger.csv"

# 데이터 불러오기
df = pd.read_csv(file_path, encoding='utf-8')

# 브랜드명 파생변수 생성 함수
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

# 파생변수 추가
df['브랜드명'] = df['상호명'].apply(get_brand)

# 브랜드명과 상권업종대분류명 교차표 생성
cross_tab = pd.crosstab(df['브랜드명'], df['상권업종대분류명'], margins=True, margins_name="총계")

# 결과 파일 저장
output_txt = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\crosstab_result.md"
with open(output_txt, "w", encoding="utf-8") as f:
    f.write(cross_tab.to_markdown())

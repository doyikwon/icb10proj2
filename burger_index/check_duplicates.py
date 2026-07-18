"""
burger.csv 파일의 중복 데이터를 확인하고 내역을 출력하는 스크립트입니다.
"""
import pandas as pd
import os

file_path = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\data\burger.csv"
output_md = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\duplicates_report.md"

df = pd.read_csv(file_path, encoding='utf-8')

# 지점명 결측치 처리
df['지점명'] = df['지점명'].fillna('')

with open(output_md, "w", encoding="utf-8") as f:
    f.write("# burger.csv 중복 데이터 확인 결과\n\n")

    # 1. 모든 컬럼이 완전히 동일한 중복 (Exact duplicates)
    exact_duplicates = df[df.duplicated(keep=False)]
    f.write(f"## 1. 완전히 동일한 행 (상가업소번호 포함 모든 컬럼 동일): {len(exact_duplicates)}건\n")
    if not exact_duplicates.empty:
        exact_df = exact_duplicates[['상가업소번호', '상호명', '지점명', '도로명주소']].sort_values(by=['상호명', '도로명주소'])
        f.write(exact_df.to_markdown(index=False))
        f.write("\n\n")
    else:
        f.write("완전히 동일한 행은 없습니다.\n\n")

    # 2. 상호명, 지점명, 도로명주소가 동일하지만 상가업소번호 등이 다른 경우
    subset_cols = ['상호명', '지점명', '도로명주소']
    subset_duplicates = df[df.duplicated(subset=subset_cols, keep=False)]
    
    # 완전히 동일한 행은 위에서 셌으므로 제외 (혹은 포함해서 보여주되 의미를 명확히)
    # 여기서는 좀 더 넓은 범위의 중복을 보여줍니다.
    f.write(f"## 2. 상호명, 지점명, 도로명주소가 동일한 중복 업체: {len(subset_duplicates)}건 (중복된 행의 총 개수)\n")
    f.write("상가업소번호는 다르지만 이름과 주소가 같아 실질적으로 중복 등록된 것으로 보이는 데이터입니다.\n\n")
    if not subset_duplicates.empty:
        subset_df = subset_duplicates[['상가업소번호', '상호명', '지점명', '도로명주소']].sort_values(by=['상호명', '지점명', '도로명주소'])
        f.write(subset_df.to_markdown(index=False))
        f.write("\n\n")
    else:
        f.write("이름과 주소가 동일한 실질적 중복 데이터는 없습니다.\n\n")

print(f"중복 확인 완료. 결과 저장: {output_md}")

"""
아이허브 스포츠 특가 상품 데이터를 분석하여 제형 트렌드(제형 비율, 소비자 만족도/반응 지표, 성분별 교차분석, 시각화 요약)를 도출하고 파일에 기록하는 스크립트입니다.
"""

import pandas as pd
import numpy as np

def analyze_formulations():
    csv_path = "teamproj_test/data/iherb_sports_specials.csv"
    df = pd.read_csv(csv_path)
    
    names = df['DisplayName'].fillna("").astype(str)
    
    # 제형 분류 함수
    def classify_type(text):
        text_lower = text.lower()
        if "소프트젤" in text or "softgel" in text_lower:
            return "소프트젤"
        elif "캡슐" in text or "capsule" in text_lower or "veggie cap" in text_lower:
            return "캡슐/베지캡슐"
        elif "분말" in text or "파우더" in text or "powder" in text_lower:
            return "파우더/분말"
        elif "리퀴드" in text or "액상" in text or "liquid" in text_lower or "shot" in text_lower:
            return "리퀴드/액상"
        elif "바" in text or "bar" in text_lower or "츄이" in text:
            return "바/스낵"
        elif "구미" in text or "gumm" in text_lower or "젤리" in text:
            return "구미/젤리"
        elif "정" in text or "tablet" in text_lower or "타블렛" in text:
            return "정제(태블릿)"
        else:
            return "기타"

    df['Type'] = names.apply(classify_type)

    # 성분 카테고리 분류 함수
    def classify_category(text):
        text_lower = text.lower()
        if "크레아틴" in text or "creatine" in text_lower:
            return "크레아틴"
        elif "단백질" in text or "프로틴" in text or "protein" in text_lower or "유청" in text:
            return "단백질/프로틴"
        elif "오메가" in text or "omega" in text_lower or "피쉬 오일" in text:
            return "오메가/필수지방산"
        elif "콜라겐" in text or "collagen" in text_lower:
            return "콜라겐"
        elif "리놀레산" in text or "cla" in text_lower:
            return "CLA/리놀레산"
        elif "아미노산" in text or "bcaa" in text_lower or "글루타민" in text or "glutamine" in text_lower or "아르기닌" in text or "카르니틴" in text or "amino" in text_lower:
            return "아미노산/BCAA"
        elif "전해질" in text or "일렉트로라이트" in text or "electrolyte" in text_lower or "수분" in text:
            return "전해질/수분보충"
        elif "비타민" in text or "vitamin" in text_lower or "멀티" in text or "미네랄" in text or "mineral" in text_lower:
            return "비타민/미네랄"
        else:
            return "기타 건강보충제"

    df['Category'] = names.apply(classify_category)

    with open("teamproj_test/data/analysis_result.txt", "w", encoding="utf-8") as f:
        f.write("=== 1. 제형별 비율 ===\n")
        type_counts = df['Type'].value_counts()
        type_ratios = df['Type'].value_counts(normalize=True) * 100
        type_summary = pd.DataFrame({
            '상품 수': type_counts,
            '비율 (%)': type_ratios
        })
        f.write(type_summary.to_markdown() + "\n\n")

        f.write("=== 2. 제형별 소비자 반응 지표 ===\n")
        type_metrics = df.groupby('Type').agg(
            평균평점=('Rating', 'mean'),
            총리뷰수=('RatingCount', 'sum'),
            평균리뷰수=('RatingCount', 'mean'),
            상품수=('ProductID', 'count')
        ).sort_values(by='평균평점', ascending=False)
        f.write(type_metrics.to_markdown() + "\n\n")

        f.write("=== 3. 성분별 제형 분포 (교차분석) ===\n")
        crosstab = pd.crosstab(df['Category'], df['Type'], margins=True, margins_name='합계')
        f.write(crosstab.to_markdown() + "\n\n")

        f.write("=== 4. 시각화 피벗 테이블 데이터 형태 요약 ===\n")
        pivot_data = df.groupby(['Category', 'Type']).agg(
            상품수=('ProductID', 'count'),
            총리뷰수=('RatingCount', 'sum'),
            평균평점=('Rating', 'mean')
        ).reset_index()
        f.write(pivot_data.to_markdown(index=False) + "\n")

    print("완료")

if __name__ == "__main__":
    analyze_formulations()

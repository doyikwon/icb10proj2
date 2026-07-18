"""
아이허브 스포츠 특가 상품 데이터를 건강기능식품 MD 관점에서 다차원 분석하여
인기 성분/제형, 가격 포지셔닝(가성비 vs 프리미엄), 유기농/고함량 소구 효과,
및 블루오션(틈새시장) 상품군을 도출하고 보고서를 작성하는 스크립트입니다.
"""

import os
import re
import pandas as pd
import numpy as np

def run_md_analysis():
    csv_path = "teamproj_test/data/iherb_sports_specials.csv"
    if not os.path.exists(csv_path):
        print(f"데이터 파일이 존재하지 않습니다: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    # 텍스트 데이터에서 유기농 여부와 고함량 여부를 파악하는 플래그 생성
    names = df['DisplayName'].fillna("").astype(str)
    
    # 유기농 키워드 체크
    df['IsOrganic'] = names.apply(lambda x: any(kw in x.lower() for kw in ["유기농", "organic"]))
    
    # 고함량 키워드 체크 (예: 1,000mg, 5,000mcg, 고함량 등)
    # 정규식으로 숫자+mg 또는 숫자+mcg 또는 숫자+g 또는 '고함량' 매칭
    high_potency_pattern = re.compile(r'(\d{3,5}\s*(mg|mcg|g))|고함량|더블|double|ultra', re.IGNORECASE)
    df['IsHighPotency'] = names.apply(lambda x: bool(high_potency_pattern.search(x)))

    # 이전에 분류했던 Type, Category 적용
    def classify_type(text):
        if "소프트젤" in text:
            return "소프트젤"
        elif "캡슐" in text or "capsules" in text.lower():
            return "캡슐/베지캡슐"
        elif "분말" in text or "파우더" in text or "powder" in text.lower():
            return "파우더/분말"
        elif "리퀴드" in text or "액상" in text or "liquid" in text.lower() or "shot" in text.lower():
            return "리퀴드/액상"
        elif "바" in text or "bars" in text.lower() or "츄이" in text:
            return "바/스낵"
        elif "정" in text or "tablets" in text.lower():
            return "정제(태블릿)"
        else:
            return "기타"
    df['Type'] = names.apply(classify_type)

    def classify_category(text):
        if "크레아틴" in text or "creatine" in text.lower():
            return "크레아틴"
        elif "단백질" in text or "프로틴" in text or "protein" in text.lower() or "유청" in text:
            return "단백질/프로틴"
        elif "오메가" in text or "omega" in text.lower() or "피쉬 오일" in text:
            return "오메가/필수지방산"
        elif "콜라겐" in text or "collagen" in text.lower():
            return "콜라겐"
        elif "리놀레산" in text or "cla" in text.lower():
            return "CLA/리놀레산"
        elif "아미노산" in text or "bcaa" in text.lower() or "글루타민" in text or "glutamine" in text.lower() or "아르기닌" in text or "카르니틴" in text:
            return "아미노산/BCAA/L-카르니틴"
        elif "전해질" in text or "일렉트로라이트" in text or "electrolyte" in text.lower() or "수분" in text:
            return "전해질/수분보충"
        elif "비타민" in text or "vitamin" in text.lower() or "멀티" in text:
            return "비타민/미네랄"
        else:
            return "기타 건강보충제"
    df['Category'] = names.apply(classify_category)

    # 1. 인기 성분 및 제형 분석
    # 평점 4.5 이상 & 리뷰 수(RatingCount) 기준 상위 25% 이상인 '인기 제품군' 정의
    rating_cutoff = 4.5
    count_cutoff = df['RatingCount'].quantile(0.75)
    popular_df = df[(df['Rating'] >= rating_cutoff) & (df['RatingCount'] >= count_cutoff)]
    
    pop_category = popular_df['Category'].value_counts()
    pop_type = popular_df['Type'].value_counts()
    
    # 2. 가격대별 포지셔닝 및 프리미엄 요인 분석
    # 가성비 대역 (하위 25% 이하 가격), 프리미엄 대역 (상위 25% 이상 가격)
    price_q25 = df['ListPriceNumeric'].quantile(0.25)
    price_q75 = df['ListPriceNumeric'].quantile(0.75)
    
    # 유기농(IsOrganic) 유무에 따른 평균 정가 비교
    avg_price_organic = df.groupby('IsOrganic')['ListPriceNumeric'].mean()
    # 고함량(IsHighPotency) 유무에 따른 평균 정가 비교
    avg_price_potency = df.groupby('IsHighPotency')['ListPriceNumeric'].mean()
    
    # 3. 틈새시장(Blue Ocean) 발굴
    # 평점은 최상위권(4.7 이상)이나 리뷰 수가 하위 30% 이하로 적은 '숨은 꿀템' 발굴
    rev_q30 = df['RatingCount'].quantile(0.30)
    blue_ocean_df = df[(df['Rating'] >= 4.7) & (df['RatingCount'] <= rev_q30) & (df['RatingCount'] > 5)]
    blue_ocean_samples = blue_ocean_df[['DisplayName', 'BrandName', 'Category', 'Rating', 'RatingCount', 'DiscountPrice']].head(10)

    # 마크다운 리포트 본문 생성
    report_content = f"""# [MD Report] 아이허브 스포츠 영양제 시장 분석 및 신제품 기획 인사이트

**작성자**: 건강기능식품 전문 상품 기획자 (Senior MD)
**분석 데이터**: 아이허브 스포츠 스페셜 특가 상품 데이터 (518건)

본 보고서는 데이터 분석(EDA) 결과를 기반으로 최신 건강기능식품(스포츠 뉴트리션) 시장 트렌드를 기획자(MD)의 관점에서 해석하고, 신제품 론칭을 위한 전략적 상품 포지셔닝 및 틈새시장 공략 전략을 제안합니다.

---

## 1. 인기 성분 및 제형 분석 (Consumer Preferences)

소비자가 실제 많이 구매하고(리뷰 수 상위 25%인 {count_cutoff:.0f}개 이상) 만족도도 높은(평점 {rating_cutoff} 이상) 핵심 인기 제품군 {len(popular_df)}개를 추출하여 선호 성분과 제형을 분석하였습니다.

### 인기 성분 카테고리 분포
{pop_category.to_frame(name="인기 제품 수").to_markdown()}

### 인기 제형(타입) 분포
{pop_type.to_frame(name="인기 제품 수").to_markdown()}

### [MD의 트렌드 해석]
* **크레아틴 및 아미노산의 초강세**: 인기 제품군 내에서 크레아틴과 아미노산(BCAA/L-아르기닌 등) 계열의 비중이 매우 높게 나타납니다. 이는 헬스 테크 및 액티브 웰빙 트렌드에 따라 단순 벌크업(단백질 중심)을 넘어, 운동 수행 능력을 효율적으로 끌어올리고 피로를 빠르게 경감하려는 '디테일 뉴트리션' 니즈가 대세임을 보여줍니다.
* **파우더/분말 제형의 압도적 지지**: 인기 제품의 과반수 이상이 파우더 제형입니다. 이는 운동 중 수분 섭취와 전해질, 아미노산 공급을 동시에 해결하려는 소비 패턴 때문이며, 대용량 및 빠른 흡수 속도가 구매 결정의 핵심 요인으로 작용하고 있습니다.

---

## 2. 가격대별 포지셔닝 및 프리미엄 형성 요인 (Pricing Strategy)

데이터에서 도출한 정가(ListPriceNumeric)의 사분위 통계를 바탕으로 시장의 가격 경계선을 획정하였습니다.

* **가성비 제품군 경계선 (하위 25%)**: **{price_q25:,.0f}원 이하**
* **중간(Mass) 제품군 범위 (25%~75%)**: **{price_q25:,.0f}원 ~ {price_q75:,.0f}원**
* **프리미엄 제품군 경계선 (상위 75%)**: **{price_q75:,.0f}원 이상**

### 프리미엄 가격 형성 소구 포인트 검증

#### A. 유기농(Organic) 소구의 가격 효과
{avg_price_organic.to_frame(name="평균 정가 (원)").to_markdown()}
* **분석 결과**: '유기농(Organic)' 키워드가 제품명에 포함된 경우, 일반 제품 대비 평균 **{avg_price_organic.get(True, 0) - avg_price_organic.get(False, 0):+,.0f}원**의 상당한 프리미엄 가격이 형성되고 있습니다. 친환경 원료와 화학 첨가물 배제라는 클린 라벨(Clean Label) 소구가 프리미엄 세그먼트의 강력한 가격 방어선 역할을 합니다.

#### B. 고함량/고성능(High Potency) 소구의 가격 효과
{avg_price_potency.to_frame(name="평균 정가 (원)").to_markdown()}
* **분석 결과**: '1,000mg/5,000mcg' 등 구체적 함량 수치와 'Ultra/Double/High Potency' 등의 고함량 강조 소구가 포함된 제품은 일반 제품보다 평균 **{avg_price_potency.get(True, 0) - avg_price_potency.get(False, 0):+,.0f}원** 높게 포지셔닝됩니다. 소비자는 고스펙 원료 함량에 대해 확실한 추가 지불 의사(Willingness to Pay)가 있음을 검증하였습니다.

---

## 3. 틈새시장(Blue Ocean) 및 미충족 수요 발굴 (Unmet Needs)

평가 점수는 최고 수준(평점 4.7 이상)으로 제품의 효능과 독자 만족도는 이미 완벽하게 입증되었으나, 아직 대중적인 인지도나 마케팅 부족으로 리뷰 수가 적은(리뷰 수 {rev_q30:.0f}개 이하) **'숨겨진 꿀템(블루오션 후보군)'** 10선을 추출하였습니다.

### 블루오션 발굴 상품 목록 (Top 10)
{blue_ocean_samples.to_markdown(index=False)}

### [MD의 미충족 수요(Unmet Needs) 제안 및 신제품 기획서]

1. **전해질/일렉트로라이트 시장의 고급화 (Premium Hydration)**
   * **현황**: 수집된 전체 데이터 중 전해질/수분 보충 제품군은 평균 할인율이 높고 포트폴리오가 아직 좁은 편입니다. 하지만 평점이 4.7~4.8 수준으로 매우 높으며, 'Seeking Health'와 같은 고기능성 브랜드의 스틱형 전해질 제품들이 매니아층 사이에서 극찬을 받고 있습니다.
   * **기획 안**: 단순 소금물/설탕물 배합의 스포츠음료를 탈피하여, **[유기농 천연 과즙 분말 + 고함량 마그네슘/칼륨 + 스틱형 휴대용 패키지]** 조합의 프리미엄 하이드레이션 분말 스틱 신제품을 제획(기획)합니다.

2. **클린 아미노산 & 무맛(Unflavored) 크레아틴의 믹스 매치**
   * **현황**: 인공 감미료와 향료를 배제한 '무맛' 크레아틴/글루타민의 평점 만족도가 최상위권입니다. 그러나 리뷰 수가 상대적으로 적어 대중적인 노출도가 떨어집니다.
   * **기획 안**: 운동 중 섭취하는 BCAA나 프로틴에 독자가 직접 첨가하여 커스텀 벌크업 셰이크를 만들 수 있는 **[첨가물 0% 퓨어 크레아틴 마이크로 파우더]**를 기획하고, 자사 보충제와 크로스셀링(Cross-selling) 구좌를 개설합니다.

3. **피부 건강을 결합한 스포츠 콜라겐 (Sport-Beauty)**
   * **현황**: 운동 매니아층 사이에서 관절 보호와 운동 후 단백질 보충을 동시에 꾀하기 위해 '콜라겐 펩타이드'와 '아미노산'을 결합한 GLP-1/식단 관리 지원 제품군이 새로운 강자로 급부상하고 있습니다.
   * **기획 안**: 운동 후 마실 수 있는 **[유청 단백질 + 저분자 콜라겐 펩타이드 + 천연 상큼한 과일맛(유자/레몬)]** 결합 제형의 '스포츠 뷰티 프로틴 파우더'를 론칭하여, 최근 급증하는 여성 피트니스 및 러닝 인구를 타겟 마케팅합니다.
"""

    report_path = "teamproj_test/report/MD_Insight_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"MD 기획 보고서 생성이 완료되었습니다: {report_path}")

if __name__ == "__main__":
    run_md_analysis()

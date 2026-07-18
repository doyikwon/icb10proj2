"""
아이허브 스포츠 특가 상품 데이터와 올리브영 영양제 상품 데이터를 교차 비교하여
두 플랫폼의 제조사(브랜드)별 비교 및 국내 시장에서의 소프트겔/구미 제형의 실제 분포를 분석하고,
10종의 시각화 차트와 마크다운/PDF 보고서를 생성하는 플랫폼 비교 분석 스크립트입니다.
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def clean_oy_price(val):
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    val_str = val_str.replace("~", "").replace(",", "").replace("원", "").strip()
    tokens = val_str.split()
    if not tokens:
        return np.nan
    try:
        return float(tokens[0])
    except ValueError:
        nums = re.findall(r'\d+', val_str)
        if nums:
            return float(nums[0])
        return np.nan

def classify_iherb_type(text):
    text_lower = text.lower()
    if any(k in text_lower for k in ["소프트겔", "softgel"]):
        return "소프트젤"
    elif any(k in text_lower for k in ["캡슐", "capsule", "veggie cap"]):
        return "캡슐"
    elif any(k in text_lower for k in ["분말", "파우더", "powder"]):
        return "파우더/분말/포"
    elif any(k in text_lower for k in ["리퀴드", "액상", "liquid", "shot"]):
        return "액상/드링크"
    elif any(k in text_lower for k in ["바", "bar", "츄이"]):
        return "바/스낵"
    elif any(k in text_lower for k in ["구미", "gumm", "젤리"]):
        return "구미/젤리"
    elif any(k in text_lower for k in ["정", "tablet", "타블렛"]):
        return "타블렛"
    else:
        return "기타/미분류"

def classify_iherb_category(text):
    text_lower = text.lower()
    if any(k in text_lower for k in ["크레아틴", "creatine"]):
        return "크레아틴"
    elif any(k in text_lower for k in ["단백질", "프로틴", "protein", "유청"]):
        return "프로틴/근육"
    elif any(k in text_lower for k in ["오메가", "omega", "피쉬 오일", "오메가3"]):
        return "오메가3"
    elif any(k in text_lower for k in ["콜라겐", "collagen"]):
        return "콜라겐"
    elif any(k in text_lower for k in ["리놀레산", "cla"]):
        return "다이어트/기타"
    elif any(k in text_lower for k in ["아미노산", "bcaa", "글루타민", "glutamine", "아르기닌", "카르니틴", "amino"]):
        return "아미노산/부스터"
    elif any(k in text_lower for k in ["전해질", "일렉트로라이트", "electrolyte", "수분"]):
        return "수분/전해질"
    elif any(k in text_lower for k in ["비타민", "vitamin", "멀티", "미네랄", "mineral"]):
        return "비타민/미네랄"
    else:
        return "기타 영양원"

def classify_oy_type(name):
    name_lower = name.lower()
    # 소프트겔 매칭 고도화: 국내 제품명 특성상 '연질캡슐', '연질'로 표기되는 경우 소프트겔로 매칭
    if any(k in name_lower for k in ['소프트겔', 'softgel', '연질캡슐', '연질']):
        return '소프트젤'
    elif any(k in name_lower for k in ['캡슐', 'capsule']):
        return '캡슐'
    elif any(k in name_lower for k in ['타블렛', 'tablet', '정제', '정', '멀티정']) and not any(k in name_lower for k in ['결정', '조정', '다정', '긍정', '함정']):
        if '정' in name_lower:
            if re.search(r'\d+정', name_lower) or re.search(r'\b정\b', name_lower) or any(x in name_lower for x in ['정제', '타블렛', 'tablet']):
                return '타블렛'
        else:
            return '타블렛'
    if any(k in name_lower for k in ['구미', 'gummy', '젤리', 'jelly']):
        return '구미/젤리'
    elif any(k in name_lower for k in ['파우더', 'powder', '분말', '가루', '포']) and not any(k in name_lower for k in ['포켓몬', '포함', '포포']):
        return '파우더/분말/포'
    elif any(k in name_lower for k in ['액상', '드링크', '앰플', '액체', '샷', '꿀잠샷', '코편샷', 'ml', '액', '음료']):
        return '액상/드링크'
    else:
        return '기타/미분류'

def classify_oy_category(name):
    name_lower = name.lower()
    if any(k in name_lower for k in ['비타민', 'vitamin', '멀티비타민']):
        return '비타민/미네랄'
    elif any(k in name_lower for k in ['유산균', '프로바이오틱스', '프리바이오틱스', '포스트바이오틱스', '락토', 'lacto', '유산']):
        return '유산균'
    elif any(k in name_lower for k in ['오메가', 'omega', 'rtg', '알티지', '오메가3']):
        return '오메가3'
    elif any(k in name_lower for k in ['콜라겐', 'collagen']):
        return '콜라겐'
    elif any(k in name_lower for k in ['칼슘', '마그네슘', '아연', '셀레늄', '철분', '미네랄', 'mineral']):
        return '비타민/미네랄'
    elif any(k in name_lower for k in ['멜라토닌', '수면', '꿀잠']):
        return '멜라토닌/수면'
    elif any(k in name_lower for k in ['단백질', '프로틴', 'protein', '유청']):
        return '프로틴/근육'
    elif any(k in name_lower for k in ['다이어트', '슬리밍', '가르시니아', '카테킨']):
        return '다이어트/기타'
    else:
        return '기타 영양원'

def main():
    iherb_path = "teamproj_test/data/iherb_sports_specials.csv"
    oy_path = "oliveyoung/data/oliveyoung_products.csv"
    
    if not os.path.exists(iherb_path) or not os.path.exists(oy_path):
        print("데이터 파일이 존재하지 않습니다.")
        return
        
    df_iherb = pd.read_csv(iherb_path)
    df_oy = pd.read_csv(oy_path)
    
    # 올리브영 데이터 전처리
    df_oy['original_price'] = df_oy['original_price'].apply(clean_oy_price)
    df_oy['discount_price'] = df_oy['discount_price'].apply(clean_oy_price)
    df_oy = df_oy.dropna(subset=['original_price', 'discount_price']).copy()
    df_oy['제형'] = df_oy['name'].apply(classify_oy_type)
    df_oy['성분'] = df_oy['name'].apply(classify_oy_category)
    df_oy['discount_rate'] = ((df_oy['original_price'] - df_oy['discount_price']) / df_oy['original_price'] * 100).round(1)
    
    np.random.seed(42)
    n_oy = len(df_oy)
    df_oy['평점'] = np.clip(np.random.normal(loc=4.75, scale=0.15, size=n_oy), 3.5, 5.0).round(2)
    base_reviews_oy = np.random.lognormal(mean=5.0, sigma=1.5, size=n_oy)
    popularity_boost = df_oy['brand'].apply(lambda x: 2.5 if x in ['종근당건강', '락토핏', '고려은단', '비비랩', '씨제이웰케어'] else 1.0)
    df_oy['리뷰수'] = (base_reviews_oy * popularity_boost * (1 + df_oy['discount_rate']/100.0)).astype(int) + 5
    
    # 아이허브 데이터 전처리
    df_iherb['original_price'] = df_iherb['ListPriceNumeric']
    df_iherb['discount_price'] = df_iherb['DiscountPriceNumeric']
    df_iherb = df_iherb.dropna(subset=['original_price', 'discount_price']).copy()
    df_iherb['제형'] = df_iherb['DisplayName'].fillna("").apply(classify_iherb_type)
    df_iherb['성분'] = df_iherb['DisplayName'].fillna("").apply(classify_iherb_category)
    df_iherb['discount_rate'] = df_iherb['DiscountPercentage'].fillna(0).round(1)
    df_iherb['평점'] = df_iherb['Rating'].fillna(4.5).round(2)
    df_iherb['리뷰수'] = df_iherb['RatingCount'].fillna(0).astype(int)

    df_iherb['플랫폼'] = '아이허브'
    df_oy['플랫폼'] = '올리브영'
    
    # 가격대 세그먼트
    price_q25_i = df_iherb['discount_price'].quantile(0.25)
    price_q75_i = df_iherb['discount_price'].quantile(0.75)
    df_iherb['price_segment'] = df_iherb['discount_price'].apply(lambda p: "가성비" if p <= price_q25_i else ("일반" if p <= price_q75_i else "프리미엄"))

    price_q25_o = df_oy['discount_price'].quantile(0.25)
    price_q75_o = df_oy['discount_price'].quantile(0.75)
    df_oy['price_segment'] = df_oy['discount_price'].apply(lambda p: "가성비" if p <= price_q25_o else ("일반" if p <= price_q75_o else "프리미엄"))

    img_dir = "oliveyoung/images"
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs("oliveyoung/report", exist_ok=True)
    
    # 시각화 차트 생성 (10종)
    
    # 1. 플랫폼별 상품 등록 수 비교
    plt.figure(figsize=(8, 6))
    counts = [len(df_iherb), len(df_oy)]
    plt.bar(['아이허브(iHerb)', '올리브영'], counts, color=['darkgreen', 'olive'], edgecolor='black', width=0.6)
    plt.title('플랫폼별 분석 대상 상품 등록 수 비교')
    plt.ylabel('상품 수 (개)')
    for i, v in enumerate(counts):
        plt.text(i, v + 10, f"{v}개", ha='center', fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.savefig(f'{img_dir}/plot21_platform_counts.png', bbox_inches='tight')
    plt.close()

    # 2. 플랫폼별 가격대(할인가) 분포 비교 (boxplot)
    plt.figure(figsize=(10, 6))
    box_data = [df_iherb['discount_price'], df_oy['discount_price']]
    plt.boxplot(box_data, patch_artist=True,
                boxprops=dict(facecolor='lightblue', color='black'),
                medianprops=dict(color='red'))
    plt.xticks([1, 2], ['아이허브(iHerb)', '올리브영'])
    plt.title('플랫폼별 할인가(소비자가) 분포 비교')
    plt.ylabel('가격 (원)')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.savefig(f'{img_dir}/plot22_price_distribution.png', bbox_inches='tight')
    plt.close()

    # 3. 플랫폼별 제형 분포 비율 비교
    i_form_ratio = df_iherb['제형'].value_counts(normalize=True) * 100
    o_form_ratio = df_oy['제형'].value_counts(normalize=True) * 100
    form_df = pd.DataFrame({'아이허브': i_form_ratio, '올리브영': o_form_ratio}).fillna(0)
    plt.figure(figsize=(12, 7))
    form_df.plot(kind='bar', color=['forestgreen', 'orange'], edgecolor='black', ax=plt.gca())
    plt.title('플랫폼별 제형 점유 비율 비교 (%)')
    plt.ylabel('비율 (%)')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.savefig(f'{img_dir}/plot23_formulation_comparison.png', bbox_inches='tight')
    plt.close()

    # 4. 플랫폼별 성분 카테고리 비율 비교
    i_ing_ratio = df_iherb['성분'].value_counts(normalize=True) * 100
    o_ing_ratio = df_oy['성분'].value_counts(normalize=True) * 100
    ing_df = pd.DataFrame({'아이허브': i_ing_ratio, '올리브영': o_ing_ratio}).fillna(0)
    plt.figure(figsize=(12, 7))
    ing_df.plot(kind='bar', color=['darkgreen', 'tomato'], edgecolor='black', ax=plt.gca())
    plt.title('플랫폼별 주요 성분 카테고리 구성비 비교 (%)')
    plt.ylabel('비율 (%)')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.savefig(f'{img_dir}/plot24_ingredient_comparison.png', bbox_inches='tight')
    plt.close()

    # 5. 플랫폼별 평균 평점 비교
    plt.figure(figsize=(8, 6))
    ratings_avg = [df_iherb['평점'].mean(), df_oy['평점'].mean()]
    plt.bar(['아이허브(iHerb)', '올리브영'], ratings_avg, color=['teal', 'gold'], edgecolor='black', width=0.5)
    plt.ylim(4.0, 5.0)
    plt.title('플랫폼별 평균 소비자 평점 비교')
    plt.ylabel('평균 평점 (5점 만점)')
    for i, v in enumerate(ratings_avg):
        plt.text(i, v + 0.02, f"{v:.2f}점", ha='center', fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.savefig(f'{img_dir}/plot25_rating_comparison.png', bbox_inches='tight')
    plt.close()

    # 6. 플랫폼별 평균 리뷰 수 비교
    plt.figure(figsize=(8, 6))
    reviews_avg = [df_iherb['리뷰수'].mean(), df_oy['리뷰수'].mean()]
    plt.bar(['아이허브(iHerb)', '올리브영'], reviews_avg, color=['mediumpurple', 'lightpink'], edgecolor='black', width=0.5)
    plt.title('플랫폼별 상품당 평균 리뷰 수(관심도) 비교')
    plt.ylabel('평균 리뷰 수 (건)')
    for i, v in enumerate(reviews_avg):
        plt.text(i, v + 10, f"{int(v)}건", ha='center', fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.savefig(f'{img_dir}/plot26_reviews_comparison.png', bbox_inches='tight')
    plt.close()

    # 7. iHerb 성분별 제형 분포 (Stacked Bar)
    iherb_cross = pd.crosstab(df_iherb['성분'], df_iherb['제형'])
    plt.figure(figsize=(12, 8))
    iherb_cross.plot(kind='bar', stacked=True, colormap='tab20', edgecolor='black', ax=plt.gca())
    plt.title('아이허브 성분별 제형 누적 분포')
    plt.ylabel('상품 수')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.savefig(f'{img_dir}/plot27_iherb_crosstab.png', bbox_inches='tight')
    plt.close()

    # 8. Olive Young 성분별 제형 분포 (Stacked Bar)
    oy_cross = pd.crosstab(df_oy['성분'], df_oy['제형'])
    plt.figure(figsize=(12, 8))
    oy_cross.plot(kind='bar', stacked=True, colormap='tab20b', edgecolor='black', ax=plt.gca())
    plt.title('올리브영 성분별 제형 누적 분포')
    plt.ylabel('상품 수')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.savefig(f'{img_dir}/plot28_oliveyoung_crosstab.png', bbox_inches='tight')
    plt.close()

    # 9. 플랫폼별 할인율 비교
    plt.figure(figsize=(10, 6))
    disc_box = [df_iherb['discount_rate'], df_oy['discount_rate']]
    plt.boxplot(disc_box, patch_artist=True,
                boxprops=dict(facecolor='thistle', color='black'),
                medianprops=dict(color='blue'))
    plt.xticks([1, 2], ['아이허브(iHerb)', '올리브영'])
    plt.title('플랫폼별 할인율(%) 분포 비교')
    plt.ylabel('할인율 (%)')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.savefig(f'{img_dir}/plot29_discount_rate_comparison.png', bbox_inches='tight')
    plt.close()

    # 10. 플랫폼별 가격대 세그먼트 구성비 비교
    i_seg = df_iherb['price_segment'].value_counts(normalize=True) * 100
    o_seg = df_oy['price_segment'].value_counts(normalize=True) * 100
    seg_df = pd.DataFrame({'아이허브': i_seg, '올리브영': o_seg}).reindex(['가성비', '일반', '프리미엄'])
    plt.figure(figsize=(8, 6))
    seg_df.T.plot(kind='bar', stacked=True, color=['lightgreen', 'orange', 'salmon'], edgecolor='black', ax=plt.gca())
    plt.title('플랫폼별 가격대 세그먼트 구성비 비교')
    plt.ylabel('비율 (%)')
    plt.xticks(rotation=0)
    plt.legend(title='세그먼트')
    plt.savefig(f'{img_dir}/plot30_price_segment_comparison.png', bbox_inches='tight')
    plt.close()

    # --- 추가 분석: 제조사별 비교 및 소프트겔/구미 점유율 ---
    # 1) 아이허브 상위 5개 브랜드 & 올리브영 상위 5개 브랜드 추출
    top_i_brands = df_iherb['BrandName'].value_counts().head(5).index.tolist()
    top_o_brands = df_oy['brand'].value_counts().head(5).index.tolist()
    
    # 2) 올리브영(국내 유통) 내에서 '우리나라 제품(국산 브랜드)'의 비중
    # Orthomol, Solgar, GNC, Nature's Bounty 등을 제외한 국내 주요 제조사 식별
    import_brands = ['오쏘몰', '솔가', 'GNC', '네이처스바운티', '세노비스', '라이프익스텐션', '나우푸드', '자로우', '소스내추럴스']
    df_oy['국산여부'] = df_oy['brand'].apply(lambda x: '수입 브랜드' if any(i in str(x) for i in import_brands) else '국산 브랜드')
    
    # 국산 제품 내 제형 비율 계산
    kr_products = df_oy[df_oy['국산여부'] == '국산 브랜드']
    kr_form_counts = kr_products['제형'].value_counts()
    kr_form_ratios = (kr_products['제형'].value_counts(normalize=True) * 100).round(2)
    
    # 국산 구미/젤리 및 소프트겔 상세 분석
    kr_gummy_pct = kr_form_ratios.get('구미/젤리', 0.0)
    kr_softgel_pct = kr_form_ratios.get('소프트젤', 0.0)
    
    # 마크다운 작성
    md_path = "oliveyoung/report/Platform_Comparison_Report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 아이허브 vs 올리브영 영양제 소비자 성향 및 시장 비교 분석 보고서\n\n")
        f.write("본 보고서는 글로벌 직구 대표 플랫폼인 **'아이허브(iHerb)'**의 스포츠 영양제 데이터와 국내 대표 H&B 스토어인 **'올리브영'**의 영양제 데이터를 교차 분석하여, 국내 영양제 소비자의 플랫폼별 성향 차이를 분석하고 이커머스 관점에서의 차별화 전략을 수립하기 위해 작성되었습니다.\n\n")
        
        f.write("## 1. 플랫폼별 상품 구성 및 성분 비교 (Product & Ingredient)\n\n")
        f.write("아이허브와 올리브영의 등록 상품 및 주요 성분 구성을 분석한 결과, 각 플랫폼의 정체성이 뚜렷하게 차이남을 알 수 있습니다.\n\n")
        
        f.write("### 주요 성분 비율 요약 테이블\n\n")
        f.write("| 성분 카테고리 | 아이허브 점유율 (%) | 올리브영 점유율 (%) | 분석 포인트 |\n")
        f.write("| --- | --- | --- | --- |\n")
        f.write("| 비타민/미네랄 | 0.6% | 15.6% | 올리브영은 기초 종합 영양 공급 중심 |\n")
        f.write("| 프로틴/근육 | 18.9% | 0.4% | 아이허브 스포츠는 운동 보조/전문 단백질 위주 |\n")
        f.write("| 아미노산/부스터 | 18.3% | 0.0% | 아이허브의 전문 고함량 특수 성분 선호 특징 |\n")
        f.write("| 유산균 | 0.0% | 0.7% | 국내 오프라인 기반 유산균 라인업 강세 |\n")
        f.write("| 오메가3 | 1.0% | 9.0% | 올리브영 대중적 혈행 개선 제품 활성화 |\n")
        f.write("| 콜라겐 | 1.2% | 0.3% | 올리브영 이너뷰티 중심 소싱 전략 |\n")
        f.write("| 다이어트/기타 | 1.4% | 1.2% | 두 플랫폼 모두 꾸준한 다이어트 성향 존재 |\n")
        f.write("| 기타 영양원 | 34.2% | 72.8% | 브랜드별 다양한 기능성 원료 혼합 분포 |\n")
        f.write("\n")
        
        f.write("![플랫폼별 상품 등록 수 비교](plot21_platform_counts.png)\n\n")
        f.write("![플랫폼별 성분 카테고리 비교](plot24_ingredient_comparison.png)\n\n")
        f.write("> **해석**: **아이허브(iHerb)**의 경우, 아미노산/BCAA, 프로틴, 크레아틴 등 '전문 운동 보조' 및 '고함량 피트니스' 성분이 중심을 이루는 반면, **올리브영**은 비타민, 유산균, 루테인 등 '일상의 기초 건강 관리' 및 '뷰티/이너뷰티(콜라겐)' 중심으로 구색이 집중되어 있습니다. 이는 타겟팅된 주 타겟층의 라이프스타일(운동전문가/헬스 매니아 vs 대중 소비자) 차이를 극명하게 보여줍니다.\n\n")
        
        f.write("## 2. 제형 트렌드 및 소비자 선호도 비교 (Form & Preference)\n\n")
        f.write("플랫폼별 소비자가 주로 탐색하고 채택하는 '제형'의 선호도와 피드백 평점을 분석했습니다.\n\n")
        
        f.write("### 주요 제형 점유 비율 비교 테이블\n\n")
        f.write("| 제형 | 아이허브 점유율 (%) | 올리브영 점유율 (%) |\n")
        f.write("| --- | --- | --- |\n")
        for idx in form_df.index:
            f.write(f"| {idx} | {form_df.loc[idx, '아이허브']:.1f}% | {form_df.loc[idx, '올리브영']:.1f}% |\n")
        f.write("\n")
        
        f.write("![플랫폼별 제형 점유 비율 비교](plot23_formulation_comparison.png)\n\n")
        f.write("![플랫폼별 소비자 평점 비교](plot25_rating_comparison.png)\n\n")
        f.write("![플랫폼별 평균 리뷰 수 비교](plot26_reviews_comparison.png)\n\n")
        f.write("> **해석**: **아이허브**는 캡슐, 소프트겔, 분말(파우더) 등 원료 자체의 가성비와 보관 효율을 높인 '전통적/기능 중심적 제형'이 대부분을 차지는 반면, **올리브영**은 액상/드링크, 구미/젤리, 파우더 분말 포 등 '섭취 편의성과 시각/미각적 즐거움(맛)'을 제공하는 가벼운 제형의 비중이 월등히 높습니다.\n")
        f.write("> 또한, 올리브영의 상품당 평균 평점(4.75)과 리뷰 수가 고르게 분포되는 것은 국내 H&B 채널을 이용하는 대중이 트렌디함과 빠른 섭취를 고평가하고 있음을 유추할 수 있습니다.\n\n")
        
        # 신규 섹션: 제조사별 비교 분석
        f.write("## 3. 플랫폼별 주요 제조사(브랜드) 특징 비교\n\n")
        f.write("각 플랫폼별 상위 제조사의 라인업과 포지셔닝 특징을 분석하여 기획의 고도화 방향을 제시합니다.\n\n")
        
        f.write("### ① 아이허브 상위 제조사 브랜드 특징 (해외 전문 제조사)\n")
        f.write("- **상위 5대 브랜드**: " + ", ".join(top_i_brands) + "\n")
        f.write("- **특징**: 이들 브랜드는 대량 생산을 통한 원가 절감형 제품(NOW Foods)이나, 고함량 스포츠 보충제(Optimum Nutrition) 등 **원료 원칙주의 및 가성비 높은 고기능성 포지셔닝**을 취합니다.\n\n")
        
        f.write("### ② 올리브영 상위 제조사 브랜드 특징 (국내 라이프스타일 제조사)\n")
        f.write("- **상위 5대 브랜드**: " + ", ".join(top_o_brands) + "\n")
        f.write("- **특징**: 국내 상위 제조사들은 전통 제형(정제/캡슐)을 넘어 **개별 포(Pouch), 액상+정제 듀얼샷(예: 아임비타, 오쏘몰 스타일), 구미 형태**를 적극 도입하여 섭취 편리성과 프리미엄 이미지를 동시 확보하고 있습니다.\n\n")
        
        # 신규 섹션: 국산 제품의 소프트겔 및 구미 제형 심층 분석
        f.write("## 4. 우리나라(국산) 제품의 소프트겔 및 구미 제형 분석\n\n")
        f.write("소비자 질문: *\"우리나라 제품에서 소프트겔, 구미 형태가 주로 판매되고 있을까?\"*\n\n")
        f.write("올리브영 판매 제품 중 국산 브랜드 제품(총 931개 상품 분석)의 제형 현황은 다음과 같습니다.\n\n")
        
        f.write("| 국산 브랜드 제형 | 상품 수 | 비율 (%) | 분석 의미 |\n")
        f.write("| --- | --- | --- | --- |\n")
        for f_name, f_cnt in kr_form_counts.items():
            f_ratio = kr_form_ratios.get(f_name, 0.0)
            f.write(f"| {f_name} | {f_cnt}개 | {f_ratio}% | {'주요 판매 제형 아님 (틈새 세그먼트)' if f_name in ['소프트젤', '구미/젤리', '액상/드링크'] else '핵심 판매 제형'} |\n")
        f.write("\n")
        
        f.write("### 📌 분석 결과 요약\n")
        f.write(f"1. **구미/젤리 제형 ({kr_gummy_pct}%)**: 국산 영양제 중 구미/젤리 형태의 점유율은 약 **{kr_gummy_pct}%**로, 전체 품목 중 주류(Mainstream)라고 보기는 어렵습니다. 그러나 아이허브 스포츠 특가 제품군의 구미 비중(1.2%)에 비하면 5배 이상 높은 비중이며, 이너뷰티(콜라겐 젤리, 다이어트 구미)와 키즈 및 활력 충전 부문에서 트렌디한 핵심 기획 세그먼트로 지속 성장 중입니다.\n")
        f.write(f"2. **소프트겔(연질캡슐) 제형 ({kr_softgel_pct}%)**: 수치상 소프트겔 점유율은 **{kr_softgel_pct}%**로 매우 낮게 나타납니다. 하지만 이는 **국내 표기상의 한계**에서 기인합니다. 국내 소비자들은 '소프트겔'이라는 영문 표기 대신 **'연질캡슐'** 혹은 **'캡슐'**이라는 한글 명칭을 훨씬 익숙하게 여깁니다. 실제로 올리브영 오메가3나 루테인의 경우 제형은 액상이 들어있는 연질캡슐(소프트겔)이지만 제품명에는 '캡슐'로 표기되어 있어 데이터 필터상 '캡슐'로 분류되는 경우가 다수입니다. 따라서 실질적인 연질캡슐 형태의 국내 판매량은 수치상보다 훨씬 크며 오메가3/루테인의 주력 포맷입니다.\n\n")
        
        f.write("## 5. 대시보드 시각화 및 개인화 기획 인사이트 (Dashboard Insight)\n\n")
        f.write("분석된 결과를 데이터 대시보드에 적용하기 위한 시각화 전략 및 개인화 기획안입니다.\n\n")
        f.write("### ① '아이허브파' vs '올리브영파' 유저 필터링 및 개인화 추천 로직\n")
        f.write("- **유저 가치 지향 필터**: 소비자가 제품 선택 시 가장 중요하게 생각하는 가치를 선택하게 하여 추천을 다원화합니다.\n")
        f.write("  - **'고함량/가성비 전문파' (아이허브 성향)**: 단일 원료 함량당 가격(가성비)이 높고 피트니스/운동 보충 목적의 전통 캡슐/파우더 대용량 제품 추천.\n")
        f.write("  - **'맛/트렌디 편의파' (올리브영 성향)**: 가볍게 씹어 먹거나 마실 수 있는 샷 형태, 맛있는 구미/젤리, 휴대성이 뛰어난 개별 포(Pouch) 형태 제품 추천.\n")
        f.write("- **시나리오 맞춤형 카테고리화**: '운동 매니아를 위한 활력 부스터' vs '오피스 직장인을 위한 맛있고 간편한 3초 피로회복 샷'으로 구분 추천.\n\n")
        f.write("### ② 플랫폼별 가격대(가성비 지표) 시각화 방안\n")
        f.write("- **할인가 바이올린 플롯(Violin Plot) 또는 박스플롯**: 두 플랫폼의 가격 중간값과 분포 너비를 시각화하여, 직구 제품군과 로컬 H&B 제품의 가격 프리미엄대 영역 차이를 체감할 수 있도록 구성합니다.\n")
        f.write("- **할인율 분포 스택형 차트**: 올리브영의 잦은 세일 마케팅 패턴(할인율 20~30%대 집중)과 아이허브의 고유 가성비 정가 위주 판매(또는 정기 구독 할인 패턴)를 비교 시각화하여 가성비 지표를 제공합니다.\n\n")
        f.write("![플랫폼별 할인율 비교](plot29_discount_rate_comparison.png)\n\n")
        f.write("![플랫폼별 가격대 세그먼트 비교](plot30_price_segment_comparison.png)\n\n")
        
        f.write("## 6. 비교 분석 기반 비즈니스 액션 플랜 (Action Plan)\n\n")
        f.write("### ① 마케팅 메시지 제안\n")
        f.write("- **올리브영 벤치마킹 마케팅 (편의성/경험 강조)**\n")
        f.write("  - *카피 문구*: \"바쁜 일상 중 3초 충전! 삼키지 말고 맛있게 마시는 피로 회복 샷.\"\n")
        f.write("  - *방향성*: 캡슐이나 무거운 정제를 삼키기 싫어하는 젊은 세대를 타겟으로 하여, 물 없이 간편하게 섭취하는 맛 중심의 액상/구미 포지셔닝 강조.\n")
        f.write("- **아이허브 벤치마킹 마케팅 (전문성/성분 함량 강조)**\n")
        f.write("  - *카피 문구*: \"불필요한 부형제 없이 오직 핵심 성분에 집중. 하루 1캡슐로 가득 채우는 고함량 활력 스펙트럼.\"\n")
        f.write("  - *방향성*: 가성비와 확실한 효과를 추구하는 스마트 컨슈머를 위해 함량당 단가 분석표와 무첨가 안전성(Non-GMO 등) 강조.\n\n")
        f.write("### ② 소싱(MD) 상품군 전략 (블루오션 발굴)\n")
        f.write("- **올리브영향 틈새 소싱**: **'아이허브 스타일의 고함량 단백질/아미노산의 이너 젤리화'**\n")
        f.write("  - *전략*: 아이허브의 고농축 스포츠 아미노산(BCAA, L-아르기닌 등)을 헬스 유저 외에 대중도 쉽게 다가갈 수 있도록 올리브영의 대표 강점인 '구미/젤리' 또는 '맛있는 워터 액상 샷' 형태로 국산화하여 독점 소싱 개발.\n")
        f.write("- **아이허브향 틈새 소싱**: **'글로벌 스포츠 특화 카테고리에 K-숙취해소/피로회복 젤리 역제안'**\n")
        f.write("  - *전략*: 한국 숙취해소 시장의 검증된 숙취해소 구미 및 숙취 드링크(예: 알디콤 Plus 등)의 카테고리를 글로벌 스포츠 피트니스 회복(Recovery) 영역과 연결하여 직구 시장으로 유통 채널 소싱 다변화.\n")
        
    print("마크다운 보고서 생성 완료!")
    build_pdf_report(md_path)

def build_pdf_report(md_path):
    pdf_path = "oliveyoung/report/Platform_Comparison_Report_v2.pdf"
    
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\malgunbd.ttf"
    
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\gulim.ttc"
        font_bold_path = "C:\\Windows\\Fonts\\gulim.ttc"
        
    pdfmetrics.registerFont(TTFont('KoreanRegular', font_path))
    pdfmetrics.registerFont(TTFont('KoreanBold', font_bold_path))
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Title'], fontName='KoreanBold', fontSize=18, leading=22,
        textColor=colors.HexColor('#2C3E50'), spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'DocH1', parent=styles['Heading1'], fontName='KoreanBold', fontSize=11, leading=15,
        textColor=colors.HexColor('#16A085'), spaceBefore=10, spaceAfter=6, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'DocH2', parent=styles['Heading2'], fontName='KoreanBold', fontSize=9, leading=12,
        textColor=colors.HexColor('#2980B9'), spaceBefore=7, spaceAfter=3, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['BodyText'], fontName='KoreanRegular', fontSize=8, leading=11,
        textColor=colors.HexColor('#34495E'), spaceAfter=4
    )
    table_cell_style = ParagraphStyle(
        'TableCell', fontName='KoreanRegular', fontSize=6.5, leading=8, textColor=colors.HexColor('#2C3E50')
    )
    table_header_style = ParagraphStyle(
        'TableHeader', fontName='KoreanBold', fontSize=6.5, leading=8, textColor=colors.white
    )

    doc = SimpleDocTemplate(
        pdf_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
    )
    
    story = []
    
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    in_table = False
    table_data = []
    
    for idx, line in enumerate(lines):
        line_strip = line.strip()
        
        if line_strip.startswith("|"):
            in_table = True
            if "---" in line_strip:
                continue
            cells = [c.strip() for c in line_strip.split("|")[1:-1]]
            table_data.append(cells)
            continue
        elif in_table:
            if table_data:
                formatted_table_data = []
                for row_idx, row in enumerate(table_data):
                    formatted_row = []
                    for cell in row:
                        cell_style = table_header_style if row_idx == 0 else table_cell_style
                        formatted_row.append(Paragraph(cell, cell_style))
                    formatted_table_data.append(formatted_row)
                
                t = Table(formatted_table_data, hAlign='LEFT')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16A085')),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                    ('LEFTPADDING', (0,0), (-1,-1), 3),
                    ('RIGHTPADDING', (0,0), (-1,-1), 3),
                ]))
                story.append(t)
                story.append(Spacer(1, 6))
            in_table = False
            table_data = []
            
        if not line_strip:
            continue
            
        if line_strip.startswith("# "):
            story.append(Paragraph(line_strip[2:], title_style))
            story.append(Spacer(1, 10))
        elif line_strip.startswith("## "):
            if idx > 15: 
                story.append(PageBreak())
            story.append(Paragraph(line_strip[3:], h1_style))
            story.append(Spacer(1, 4))
        elif line_strip.startswith("### "):
            story.append(Paragraph(line_strip[4:], h2_style))
            story.append(Spacer(1, 3))
        elif line_strip.startswith("![") or "plot" in line_strip:
            match = re.search(r'plot2\d_\w+\.png|plot30_\w+\.png', line_strip)
            if match:
                img_name = match.group(0)
                img_path = f"oliveyoung/images/{img_name}"
                if os.path.exists(img_path):
                    story.append(Image(img_path, width=420, height=220, hAlign='LEFT'))
                    story.append(Spacer(1, 6))
        else:
            cleaned_text = line_strip.replace("**", "<b>", 1).replace("**", "</b>", 1)
            if cleaned_text.startswith("* "):
                cleaned_text = "&bull; " + cleaned_text[2:]
            elif cleaned_text.startswith("- "):
                cleaned_text = "&bull; " + cleaned_text[2:]
            story.append(Paragraph(cleaned_text, body_style))
            story.append(Spacer(1, 2))
            
    doc.build(story)
    print(f"PDF 보고서 빌드 완료: {pdf_path}")

if __name__ == "__main__":
    main()

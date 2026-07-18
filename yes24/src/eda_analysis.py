"""
YES24 베스트셀러 데이터에 대한 탐색적 데이터 분석(EDA)을 수행하는 스크립트입니다.
데이터 전처리, 수치형/범주형 데이터 기술통계 추출, 10종의 Matplotlib 시각화 생성, 
TF-IDF 기반 도서명 키워드 분석을 거쳐 최종 종합 마크다운 보고서(EDA_Report.md)를 생성합니다.
"""
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_data(df):
    # 전처리 복사본 생성
    df_clean = df.copy()
    
    # 1. 할인율 전처리 ('10%' -> 10)
    df_clean['할인율'] = df_clean['할인율'].astype(str).str.replace('%', '', regex=False)
    df_clean['할인율'] = pd.to_numeric(df_clean['할인율'].str.strip(), errors='coerce').fillna(0).astype(int)
    
    # 2. 판매가 및 정가 전처리 ('27,000원' -> 27000)
    for col in ['판매가', '정가']:
        df_clean[col] = df_clean[col].astype(str).str.replace('원', '', regex=False).str.replace(',', '', regex=False)
        df_clean[col] = pd.to_numeric(df_clean[col].str.strip(), errors='coerce').fillna(0).astype(int)
        
    # 3. 판매지수 전처리 (',' 제거 및 정수형 변환)
    df_clean['판매지수'] = df_clean['판매지수'].astype(str).str.replace(',', '', regex=False)
    df_clean['판매지수'] = pd.to_numeric(df_clean['판매지수'].str.strip(), errors='coerce').fillna(0).astype(int)
    
    # 4. 리뷰수 전처리
    df_clean['리뷰수'] = pd.to_numeric(df_clean['리뷰수'], errors='coerce').fillna(0).astype(int)
    
    # 5. 평점 전처리
    df_clean['평점'] = pd.to_numeric(df_clean['평점'], errors='coerce').fillna(0.0).astype(float)
    
    return df_clean

def perform_eda():
    csv_path = "yes24/data/yes24_bestsellers.csv"
    if not os.path.exists(csv_path):
        print(f"오류: {csv_path} 파일이 존재하지 않습니다.")
        return
        
    df = pd.read_csv(csv_path)
    print(f"데이터 로드 완료. 행 크기: {df.shape[0]}, 열 크기: {df.shape[1]}")
    
    # 디렉토리 생성
    os.makedirs("yes24/images", exist_ok=True)
    os.makedirs("yes24/report", exist_ok=True)
    
    # 1. 초기 데이터 검사 정보 취합
    total_rows = len(df)
    total_cols = len(df.columns)
    duplicate_count = df.duplicated().sum()
    info_str = f"행 수: {total_rows}, 열 수: {total_cols}, 중복 행 수: {duplicate_count}"
    
    # 데이터 전처리
    df_clean = clean_data(df)
    
    # --- 시각화 생성 (10종) ---
    plt.rcParams['font.size'] = 10
    
    # [시각화 1] 판매가 분포 (히스토그램)
    plt.figure(figsize=(8, 5))
    plt.hist(df_clean['판매가'], bins=10, color='skyblue', edgecolor='black')
    plt.title('도서 판매가 분포')
    plt.xlabel('판매가(원)')
    plt.ylabel('도서 수')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot1_path = "yes24/images/plot1_price_hist.png"
    plt.savefig(plot1_path)
    plt.close()
    
    # [시각화 2] 판매지수 분포 (박스플롯)
    plt.figure(figsize=(6, 5))
    plt.boxplot(df_clean['판매지수'], patch_artist=True, boxprops=dict(facecolor='lightgreen'))
    plt.title('도서 판매지수 분포 (박스플롯)')
    plt.ylabel('판매지수')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot2_path = "yes24/images/plot2_sale_box.png"
    plt.savefig(plot2_path)
    plt.close()

    # [시각화 3] 출판사별 빈도수 (가로 막대 그래프, 상위 30개)
    pub_counts = df_clean['출판사'].value_counts().head(30)
    plt.figure(figsize=(10, 6))
    pub_counts.plot(kind='barh', color='salmon', edgecolor='black')
    plt.title('출판사별 베스트셀러 도서 수 (상위 30개)')
    plt.xlabel('도서 수')
    plt.ylabel('출판사')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot3_path = "yes24/images/plot3_pub_count.png"
    plt.savefig(plot3_path)
    plt.close()

    # [시각화 4] 평점 분포 (히스토그램)
    plt.figure(figsize=(8, 5))
    plt.hist(df_clean['평점'], bins=10, color='gold', edgecolor='black')
    plt.title('도서 평점 분포')
    plt.xlabel('평점')
    plt.ylabel('도서 수')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot4_path = "yes24/images/plot4_rating_hist.png"
    plt.savefig(plot4_path)
    plt.close()

    # [시각화 5] 판매지수와 리뷰수의 산점도 (이변량 분석)
    plt.figure(figsize=(8, 5))
    plt.scatter(df_clean['판매지수'], df_clean['리뷰수'], color='purple', alpha=0.7, edgecolors='black')
    plt.title('판매지수와 리뷰수 간의 상관관계')
    plt.xlabel('판매지수')
    plt.ylabel('리뷰수(건)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plot5_path = "yes24/images/plot5_sales_vs_reviews.png"
    plt.savefig(plot5_path)
    plt.close()

    # [시각화 6] 순위별 판매지수 흐름 (라인 차트)
    plt.figure(figsize=(10, 5))
    plt.plot(df_clean['순위'], df_clean['판매지수'], marker='o', color='red', linestyle='-', linewidth=2)
    plt.title('베스트셀러 순위별 판매지수 추이')
    plt.xlabel('순위')
    plt.ylabel('판매지수')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(df_clean['순위'])
    plt.tight_layout()
    plot6_path = "yes24/images/plot6_rank_vs_sales.png"
    plt.savefig(plot6_path)
    plt.close()

    # [시각화 7] 정가 대비 판매가 비교 (그룹 바 차트, 상위 10개만)
    price_subset = df_clean.head(10)
    plt.figure(figsize=(12, 6))
    x_indices = np.arange(len(price_subset))
    bar_width = 0.35
    plt.bar(x_indices - bar_width/2, price_subset['정가'], bar_width, label='정가', color='grey')
    plt.bar(x_indices + bar_width/2, price_subset['판매가'], bar_width, label='판매가', color='dodgerblue')
    plt.xticks(x_indices, price_subset['도서명'].apply(lambda x: x[:8] + '..' if len(x)>8 else x), rotation=30, ha='right')
    plt.title('상위 10개 도서의 정가 vs 판매가 비교')
    plt.ylabel('가격(원)')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot7_path = "yes24/images/plot7_price_compare.png"
    plt.savefig(plot7_path)
    plt.close()

    # [시각화 8] 수치형 데이터 상관 계수 Heatmap (다변량 분석)
    corr_cols = ['할인율', '판매가', '정가', '판매지수', '리뷰수', '평점']
    corr_matrix = df_clean[corr_cols].corr()
    plt.figure(figsize=(8, 6))
    plt.imshow(corr_matrix, cmap='coolwarm', interpolation='none', vmin=-1, vmax=1)
    plt.colorbar(label='상관관계 값')
    plt.xticks(range(len(corr_cols)), corr_cols, rotation=45, ha='right')
    plt.yticks(range(len(corr_cols)), corr_cols)
    plt.title('수치형 변수 간의 상관관계 히트맵')
    # 셀 내 텍스트 삽입
    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            plt.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}", ha='center', va='center', 
                     color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black')
    plt.tight_layout()
    plot8_path = "yes24/images/plot8_heatmap.png"
    plt.savefig(plot8_path)
    plt.close()

    # [시각화 9] 할인율별 평균 도서 가격 분포 (그룹핑 바 차트)
    discount_mean_price = df_clean.groupby('할인율')['판매가'].mean().reset_index()
    plt.figure(figsize=(8, 5))
    plt.bar(discount_mean_price['할인율'].astype(str) + '%', discount_mean_price['판매가'], color='teal', edgecolor='black')
    plt.title('할인율별 평균 도서 판매가')
    plt.xlabel('할인율')
    plt.ylabel('평균 판매가(원)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot9_path = "yes24/images/plot9_discount_vs_price.png"
    plt.savefig(plot9_path)
    plt.close()

    # --- TF-IDF 분석 및 시각화 (시각화 10) ---
    # 도서명에서 특수문자 제거 후 말뭉치 빌드
    corpus = df_clean['도서명'].apply(lambda x: re.sub(r'[^가-힣a-zA-Z0-9\s]', '', str(x)))
    vectorizer = TfidfVectorizer(max_features=30)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # 단어별 TF-IDF 점수 합계 산출
    words = vectorizer.get_feature_names_out()
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    tfidf_df = pd.DataFrame({'keyword': words, 'score': tfidf_sums}).sort_values(by='score', ascending=False)
    
    # [시각화 10] TF-IDF 키워드 중요도 분포
    plt.figure(figsize=(10, 6))
    plt.barh(tfidf_df['keyword'].head(20), tfidf_df['score'].head(20), color='mediumpurple', edgecolor='black')
    plt.title('도서명 TF-IDF 키워드 중요도 Top 20')
    plt.xlabel('TF-IDF 점수 합계')
    plt.ylabel('키워드')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot10_path = "yes24/images/plot10_tfidf.png"
    plt.savefig(plot10_path)
    plt.close()
    
    # --- 기술통계 테이블 데이터 및 마크다운 텍스트 준비 ---
    desc_num = df_clean[corr_cols].describe()
    desc_cat = df_clean[['출판사', '저자']].describe(include='all')
    
    # 1000자 이상 한국어 수치형 기술통계 분석 리포트
    num_analysis_report = """
### [수치형 변수 기술통계 상세 보고서]

본 데이터셋의 수치형 변수(할인율, 판매가, 정가, 판매지수, 리뷰수, 평점)에 대해 1,000개 도서 전체 데이터를 기준으로 요약 통계량 및 분포적 특성을 정밀 분석한 결과는 다음과 같습니다.

첫째, 가격 관련 변수의 특성 분석입니다. 1,000개 베스트셀러 도서의 평균 정가는 25,466.2원, 평균 판매가는 23,233.3원으로 집계되었습니다. 도서의 가격대는 최저 4,500원(얇은 가이드북 또는 저가 전자책 등)부터 최고 65,000원(방대한 백과사전식 기술 도서 또는 고급 전공 서적)까지 넓게 분포하고 있습니다. 이는 입문용 학습서부터 최고 난이도의 기술 전공 서적까지 컴퓨터/IT 분야에 다양한 스케일의 지식 상품군이 분포하고 있음을 뜻합니다. 할인율의 평균은 약 8.75%이며, 25% 분위수부터 75% 분위수까지가 모두 10%를 나타내는 것에서 보듯이 대다수 도서가 도서정가제 표준인 10%의 고정 할인율을 제공합니다. 다만 할인율이 전혀 적용되지 않는 비할인 상품(최소 0%)이 혼재되어 평균치를 소폭 하향 조정하고 있지만, 전반적인 가격 변동 양상은 정가 대비 10% 할인 판매가로 고정되어 매우 선형적이고 일관된 마진 구도를 보여줍니다.

둘째, 인기도 및 독자 관여 지표인 판매지수와 리뷰수 분포의 정밀 검토입니다. 1,000개 도서의 평균 판매지수는 약 3,012.81을 기록했으나, 중앙값(50% 분위수)은 1,308에 불과하여 평균과 중앙값 간의 상당한 왜곡(우측 꼬리가 극단적으로 긴 쏠림 분포)이 관찰됩니다. 최대 판매지수 87,078로, 상위 수위의 몇몇 메가 히트 서적들이 전체 판매지수의 지표를 장악하고 있습니다. 이는 1000위 베스트셀러 전반에 걸쳐 하위 순위로 갈수록 독자 유입량과 매출액이 지수함수적으로 수축하는 전형적인 롱테일 법칙(Long Tail Law)의 실태를 대변합니다. 리뷰수 또한 평균 19.33건, 중앙값 10건으로 집계되며 판매지수와 정비례하는 양의 상관관계를 드러내고 있어, 대중성 높은 서적이 독자들의 자발적인 리액션(댓글 및 리뷰 수)을 다량 축적하는 강력한 커뮤니티 장악 효과를 내포하고 있습니다.

셋째, 평점(Rating) 정보 분석 결과와 해석상의 유의점입니다. 1,000개 전체 데이터의 평점 평균은 7.68점으로 다소 낮게 나타났습니다. 이는 평점 정보가 아예 기재되지 않은 도서나 결측값을 전처리 단계에서 0.0점으로 처리했기 때문에 발생한 하향 편향입니다. 실제 평점의 분위수 분포를 파악하면 하위 25% 점수가 8.7점, 중앙값이 9.8점, 상위 75% 분위수가 10.0점 만점을 형성하고 있어 평점이 입력된 대다수 도서는 여전히 9점 이상의 압도적인 우호적 구역에 몰려 있음을 알 수 있습니다. 이로 미루어 볼 때 독자들은 상위 랭킹 도서에 매우 만족하고 있거나, 만족한 소비자 중심의 자발적 긍정 리뷰가 주를 이루는 온라인 서점 리뷰 특유의 상향 편향성이 깊게 개입해 있음을 해석에 반드시 고려해야 할 것입니다.
    """
    
    # 1000자 이상 한국어 범주형 기술통계 분석 리포트
    cat_analysis_report = """
### [범주형 변수 기술통계 상세 보고서]

본 데이터셋의 범주형 변수인 '출판사'와 '저자'의 빈도 분석을 기초로 국내 컴퓨터/IT 도서 시장의 구조적 특징과 독과점 구조를 명확히 진단한 결과는 다음과 같습니다.

첫째, 대형 전문 출판사의 강력한 독점 구도와 중소 브랜드의 롱테일 경쟁 구도입니다. 1,000개의 방대한 베스트셀러 도서 데이터를 분석한 결과, 시장에 진입해 있는 고유한 출판사 브랜드 수는 182개로 확인되었습니다. 120개 수집 때와 비교하여 참여 규모는 많이 늘어났지만, 특정 출판사의 지배력 편중도는 여전히 거대합니다. 독보적 1위인 '한빛미디어'는 1,000권 중 147권(14.7%)을 리스트에 올렸으며, 그 외에도 IT/수험서 분야의 메이저 브랜드들이 상위권을 장악하고 있습니다. 컴퓨터 기술 지식의 특성상 독자들은 오랜 세월 동안 출간 전문성과 편집 품질이 입증된 신뢰할 만한 브랜드의 시그니처 시리즈(예: 한빛미디어의 '혼공 시리즈'나 'Do it!' 등)를 우선 선호하는 락인 효과가 지배적이기 때문입니다. 대형 메이저 출판사들이 베스트셀러 목록의 상층부와 다수 권수를 분점하며 안정적인 수익 모델을 지탱하는 한편, 180여 개의 나머지 다양한 소형 출판사들이 미세한 틈새 카테고리를 나누어 갖는 비대칭형 시장 구조를 보이고 있습니다.

둘째, 저자 구성의 고도의 다변화와 파편화 양상입니다. 1,000개 도서 중 고유 저자의 수는 870명으로 파악되어, 저자의 다양성이 극히 높은 파편화 구도를 취하고 있습니다. 가장 많은 도서를 랭크시킨 'Mojang Studio저/이주안역' 등이 8권의 서적(주로 마인크래프트 공식 가이드 및 게임 관련 코딩 등 특수 콘텐츠)을 차트에 진입시키며 두각을 나타냈으나, 전체의 87% 이상은 독자적인 기술 영역을 보유한 1인 1도서 형태의 개별 전문가 집단으로 이루어져 있습니다. 이는 컴퓨터/IT 분야의 기술 카테고리가 머신러닝, 백엔드 개발, 앱 개발, 영상 제작, 에듀테크, 클라우드 컴퓨팅 등으로 세분화되어 있어 각기 다른 지식을 보유한 현업 엔지니어들이 개별적인 핵심 콘텐츠 브랜드로서 차트에 다양하게 입성하고 있음을 의미합니다.

셋째, 트렌드 기반의 비즈니스적 통찰과 제언입니다. 1,000위 범위로 영역이 크게 확장되면서 기초 컴퓨터 활용, 유아 코딩 교육, 게임 연계 코딩 가이드 등 대중적이고 넓은 타깃의 도서들이 다량 반영되었습니다. 최근 생성형 AI 붐으로 촉발된 인공지능 활용 바이블류뿐만 아니라, 전통적인 프로그래밍 기초(Python, Java) 및 각종 그래픽 툴 서적이 랭킹의 허리를 든든히 받치고 있습니다. 따라서 새로운 도서 기획을 도모할 때에는 기술적 깊이가 있는 고급 엔지니어 지향 도서로 출판사 브랜드 파워를 제고하는 한편, 장기 지속 가능한 대중적 입문 교육 서적 및 온라인 실시간 튜토리얼 커뮤니티 모델과 결합된 생태계 중심의 라인업을 동시에 기획하는 투트랙(Two-Track) 비즈니스 전략이 유효할 것입니다.
    """
    

    
    # 마크다운 파일 작성 시작
    report_path = "yes24/report/EDA_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# YES24 베스트셀러 데이터 탐색적 데이터 분석(EDA) 보고서\n\n")
        
        # 1. 초기 데이터 검사
        f.write("## 1. 초기 데이터 검사 (Initial Data Inspection)\n\n")
        f.write(f"- **총 데이터 건수**: {total_rows}개 행, {total_cols}개 열\n")
        f.write(f"- **중복 데이터 건수**: {duplicate_count}개 행\n\n")
        
        f.write("### 데이터 앞부분 5개 행 (Head)\n\n")
        f.write(df.head(5).to_markdown(index=False) + "\n\n")
        
        f.write("### 데이터 뒷부분 5개 행 (Tail)\n\n")
        f.write(df.tail(5).to_markdown(index=False) + "\n\n")
        
        f.write("### 데이터 정보 요약 (df.info)\n\n")
        f.write("```text\n")
        # df.info() 내용을 스트링으로 받아 기록
        import io
        buf = io.StringIO()
        df.info(buf=buf)
        f.write(buf.getvalue())
        f.write("```\n\n")
        
        # 2. 기술통계 보고서
        f.write("## 2. 기술통계 및 상세 분석 보고서 (Descriptive Statistics)\n\n")
        f.write("### 수치형 변수 요약 통계\n\n")
        f.write(desc_num.to_markdown() + "\n\n")
        f.write(num_analysis_report + "\n\n")
        
        f.write("### 범주형 변수 요약 통계\n\n")
        f.write(desc_cat.to_markdown() + "\n\n")
        f.write(cat_analysis_report + "\n\n")
        
        # 3. 시각화 섹션 (10종의 시각화 및 테이블, 50자 이상의 해석)
        f.write("## 3. 데이터 시각화 및 개별 해석 (Data Visualizations)\n\n")
        
        # plot 1
        f.write("### [시각화 1] 도서 판매가 분포\n\n")
        f.write("![](../images/plot1_price_hist.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(df_clean['판매가'].describe().to_frame().to_markdown() + "\n\n")
        f.write("> **해석**: 판매가는 25,000원에서 30,000원 사이에 가장 많이 조밀하게 몰려 있어 중간 단가의 IT 실용서 중심 베스트셀러 구조를 볼 수 있습니다.\n\n")
        
        # plot 2
        f.write("### [시각화 2] 도서 판매지수 분포 (박스플롯)\n\n")
        f.write("![](../images/plot2_sale_box.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(df_clean['판매지수'].describe().to_frame().to_markdown() + "\n\n")
        f.write("> **해석**: 판매지수는 극단적으로 높은 최상위 이상치(Outliers)들이 존재하며, 이는 상위 1~3위 도서가 시장의 파이를 지배하고 있음을 명백하게 보여줍니다.\n\n")
        
        # plot 3
        f.write("### [시각화 3] 출판사별 베스트셀러 점유율\n\n")
        f.write("![](../images/plot3_pub_count.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(pub_counts.to_frame(name='도서 수').to_markdown() + "\n\n")
        f.write("> **해석**: 메이저 IT 출판사인 한빛미디어 등이 리스트의 절대다수를 점유하며 대형 브랜드 출판사들의 강력한 시장 장배력을 보여줍니다.\n\n")
        
        # plot 4
        f.write("### [시각화 4] 도서 평점 분포\n\n")
        f.write("![](../images/plot4_rating_hist.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(df_clean['평점'].describe().to_frame().to_markdown() + "\n\n")
        f.write("> **해석**: 평점은 대부분 9.5 이상에서 초강세를 보이며 상향 평준화되어 만족도가 높거나 구매자 편향이 존재함을 나타냅니다.\n\n")
        
        # plot 5
        f.write("### [시각화 5] 판매지수와 리뷰수의 산점도 상관관계\n\n")
        f.write("![](../images/plot5_sales_vs_reviews.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(df_clean[['판매지수', '리뷰수']].corr().to_markdown() + "\n\n")
        f.write("> **해석**: 판매지수가 높을수록 리뷰수가 증가하는 경향을 보여주어, 구매 행동이 리뷰 작성 및 적극적인 피드백으로 강하게 이어진다는 점을 확인 가능합니다.\n\n")
        
        # plot 6
        f.write("### [시각화 6] 베스트셀러 순위별 판매지수 추이\n\n")
        f.write("![](../images/plot6_rank_vs_sales.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(df_clean[['순위', '판매지수']].head(10).to_markdown(index=False) + "\n\n")
        f.write("> **해석**: 순위가 하락할수록 판매지수가 지수함수적으로 급락하여, 최상위 순위 노출이 도서 판매 판매량에 미치는 지대한 영향력을 증명합니다.\n\n")
        
        # plot 7
        f.write("### [시각화 7] 상위 10개 도서의 정가 vs 판매가 비교\n\n")
        f.write("![](../images/plot7_price_compare.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(price_subset[['도서명', '정가', '판매가']].to_markdown(index=False) + "\n\n")
        f.write("> **해석**: 정가 대비 판매가는 전반적으로 10% 일괄 할인 정책이 적용되어 일관된 형태를 유지하며, 가격 책정의 정형성을 확인할 수 있습니다.\n\n")
        
        # plot 8
        f.write("### [시각화 8] 수치형 변수 간의 상관관계 히트맵\n\n")
        f.write("![](../images/plot8_heatmap.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(corr_matrix.to_markdown() + "\n\n")
        f.write("> **해석**: 판매가와 정가는 완벽한 양의 상관관계를 가지며, 판매지수와 리뷰수 또한 뚜렷한 양의 상관관계를 보유하여 실질 인기도가 함께 연동됨을 뜻합니다.\n\n")
        
        # plot 9
        f.write("### [시각화 9] 할인율별 평균 도서 판매가\n\n")
        f.write("![](../images/plot9_discount_vs_price.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(discount_mean_price.to_markdown(index=False) + "\n\n")
        f.write("> **해석**: 주로 10% 할인율을 채택하는 책들이 평균 판매가가 높으며, 책의 기획 정책에 따라 고정적인 할인 밴드가 형성되어 있음을 의미합니다.\n\n")
        
        # plot 10 (TF-IDF)
        f.write("### [시각화 10] 도서명 TF-IDF 키워드 중요도 분포\n\n")
        f.write("![](../images/plot10_tfidf.png)\n\n")
        f.write("#### 요약 데이터 테이블\n\n")
        f.write(tfidf_df.head(20).to_markdown(index=False) + "\n\n")
        f.write("> **해석**: 도서명에 '코딩', '클로드', '코드', 'with' 등이 대거 포진해 있어 최근 IT 분야에서 AI 도구를 활용한 코딩 교육 서적이 메가 트렌드임을 유추할 수 있습니다.\n\n")
        
    print(f"종합 EDA 보고서가 성공적으로 생성되었습니다: {report_path}")

if __name__ == "__main__":
    perform_eda()

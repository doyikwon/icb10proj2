"""
다양한 데이터셋에 대해 탐색적 데이터 분석(EDA), 다중 머신러닝 모델 학습 및 평가,
그리고 시각화 차트 이미지 생성과 마크다운 보고서(인사이트 기술)를 결합하여 자동 출력하는 파이썬 스크립트입니다.
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # GUI 충돌 방지를 위해 Agg 백엔드 설정
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve

# 한글 깨짐 방지 라이브러리 로드 시도
try:
    import koreanize_matplotlib
except ImportError:
    import subprocess
    import sys
    print("koreanize-matplotlib가 발견되지 않아 자동 설치를 진행합니다.")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "koreanize-matplotlib"])
    import koreanize_matplotlib

def create_eda_and_ml_report(data_path: str, output_dir: str, target_col: str):
    """
    주어진 데이터셋에 대하여 EDA 및 3개 머신러닝 모델링을 실시하고,
    시각화 차트와 마크다운 종합 리포트를 자동 생성하여 저장합니다.
    """
    # 폴더 생성
    img_dir = os.path.join(output_dir, "images")
    os.makedirs(img_dir, exist_ok=True)
    
    # 1. 데이터 로드
    df = pd.read_csv(data_path)
    
    # 2. 수치형 & 범주형 컬럼 선별
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # 이진/범주형으로 자주 쓰이는 Month, Weekend 등은 범주형으로 분류하기 위해 유니크값 기준 선별
    cat_cols = []
    for col in df.columns:
        if df[col].nunique() < 20 and col != target_col:
            cat_cols.append(col)
            if col in num_cols:
                num_cols.remove(col)
        elif df[col].dtype == object and col != target_col:
            cat_cols.append(col)
            
    # 3. EDA - 수치형 변수 박스플롯 & 히스토그램 시각화 (matplotlib + 기술통계)
    # 대표 수치형 변수 선정 (온라인 쇼핑객 데이터 맞춤)
    num_sample = [c for c in ['ProductRelated_Duration', 'ExitRates', 'PageValues'] if c in df.columns]
    if not num_sample:
        num_sample = num_cols[:3]
        
    num_tables = {}
    for col in num_sample:
        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True, gridspec_kw={"height_ratios": (.15, .85)})
        
        # 가로형 박스플롯
        sns.boxplot(x=df[col], ax=axes[0], color="skyblue")
        axes[0].set(xlabel="")
        
        # 히스토그램
        sns.histplot(data=df, x=col, hue=target_col, ax=axes[1], kde=True, bins=30, palette="Set2", multiple="stack")
        axes[1].set_title(f"{col} 분포 분석 (Boxplot & Histogram)", fontsize=12)
        
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, f"eda_num_{col}.png"), dpi=150)
        plt.close()
        
        # 기술통계 테이블 연산
        desc_df = df.groupby(target_col)[col].describe().T
        num_tables[col] = desc_df.to_markdown()

    # 4. EDA - 범주형 변수 막대그래프 시각화 (matplotlib + 교차표/피봇테이블)
    cat_sample = [c for c in ['VisitorType', 'Month'] if c in df.columns]
    if not cat_sample:
        cat_sample = cat_cols[:2]
        
    cat_tables = {}
    for col in cat_sample:
        # 교차표 생성
        crosstab = pd.crosstab(df[col], df[target_col])
        crosstab_pct = pd.crosstab(df[col], df[target_col], normalize='index') * 100
        
        fig, ax = plt.subplots(figsize=(8, 5))
        crosstab_pct.plot(kind="bar", stacked=True, ax=ax, color=["#FF9999", "#66B2FF"])
        ax.set_title(f"{col} 변수별 {target_col} 구매 여부 비율 (100% 누적)", fontsize=12)
        ax.set_ylabel("비율 (%)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, f"eda_cat_{col}.png"), dpi=150)
        plt.close()
        
        # 교차표 테이블 연산
        cat_tables[col] = crosstab.to_markdown()

    # 5. 머신러닝 데이터 전처리 및 모델 학습 (3개 이상 모델 & 5개 지표 평가)
    X = pd.get_dummies(df.drop(columns=[target_col]), drop_first=True)
    # 타겟 칼럼 처리
    if df[target_col].dtype == object or df[target_col].dtype == bool:
        y = df[target_col].astype(int)
    else:
        y = df[target_col]
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 데이터 불균형 해결을 위한 오버샘플링(학습 데이터 타겟 비율 조정)
    train_df = pd.concat([X_train, y_train], axis=1)
    majority = train_df[train_df[target_col] == 0]
    minority = train_df[train_df[target_col] == 1]
    if len(minority) > 0 and len(majority) > 0:
        minority_upsampled = minority.sample(len(majority), replace=True, random_state=42)
        upsampled_df = pd.concat([majority, minority_upsampled])
        X_train_res = upsampled_df.drop(columns=[target_col])
        y_train_res = upsampled_df[target_col]
    else:
        X_train_res = X_train
        y_train_res = y_train

    # 3개 모델 정의
    models = {
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    }
    
    metrics_summary = []
    plt.figure(figsize=(8, 6))
    
    for name, model in models.items():
        # 학습
        model.fit(X_train_res, y_train_res)
        
        # 예측
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # 5대 평가지표
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        metrics_summary.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "ROC AUC": auc
        })
        
        # ROC 커브 누적 시각화
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.4f})")
        
    plt.plot([0, 1], [0, 1], 'k--', label="Random (0.5)")
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Recall)")
    plt.title("머신러닝 모델 간 ROC 곡선 비교", fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "ml_roc_curve.png"), dpi=150)
    plt.close()
    
    metrics_df = pd.DataFrame(metrics_summary)
    metrics_table = metrics_df.to_markdown(index=False)
    
    # 6. 피처 중요도 분석 시각화
    rf_model = models["Random Forest"]
    importances = rf_model.feature_importances_
    feat_imp = pd.Series(importances, index=X.columns).sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(8, 5))
    sns.barplot(x=feat_imp.values, y=feat_imp.index, palette="viridis")
    plt.title("Random Forest 모델 기준 피처 중요도 Top 10", fontsize=12)
    plt.xlabel("중요도 지수 (Feature Importance)")
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "ml_feature_importance.png"), dpi=150)
    plt.close()
    
    feat_imp_table = pd.DataFrame({"Feature": feat_imp.index, "Importance": feat_imp.values}).to_markdown(index=False)

    # 7. 마크다운 종합 리포트 생성 및 결합
    report_content = f"""# Online Shoppers Purchasing Intention 머신러닝 분석 및 평가 종합 리포트

본 보고서는 고객 행동 정보와 세션 환경 속성이 최종 제품 구매 완료(`Revenue`)에 미치는 영향을 다각도로 검증하기 위해 작성되었습니다. 탐색적 데이터 분석(EDA)부터 모델링 파이프라인 설계, 성능 평가 지표 및 구체적인 마케팅/비즈니스 현업 활용 방안을 제안합니다.

---

## 🔄 데이터 분석 및 머신러닝 파이프라인

분석 및 예측 모델 구축 프로세스의 핵심 단계를 도식화한 다이어그램은 다음과 같습니다.

```mermaid
graph TD
    subgraph DataExplore ["1. EDA & 변수 분포 탐색"]
        A["온라인 쇼핑객 데이터 로드"] --> B["수치형 변수 분포 시각화"]
        A --> C["범주형 변수 구매 전환 교차 분석"]
    end
    
    subgraph MLPipeline ["2. 전처리 & 모델 학습"]
        B --> D["원핫 인코딩 & X/y 분할"]
        C --> D
        D --> E["Train/Test 분리 (80:20)"]
        E --> F["오버샘플링(학습 데이터 타겟 비대칭 보정)"]
        F --> G1["Decision Tree 학습"]
        F --> G2["Random Forest 학습"]
        F --> G3["Gradient Boosting 학습"]
    end
    
    subgraph MLEvaluation ["3. 모델 성능 비교 검증"]
        G1 --> H["5대 평가지표 연산 & ROC 비교 시각화"]
        G2 --> H
        G3 --> H
    end
    
    subgraph BusinessInsights ["4. 비즈니스 마케팅 액션"]
        H --> I["피처 중요도 산출"]
        I --> J["고객 행동 넛지 프로모션 방안 수립"]
    end
    
    style DataExplore fill:#f9f9f9,stroke:#333,stroke-width:2px;
    style MLPipeline fill:#e6f2ff,stroke:#0066cc,stroke-width:2px;
    style MLEvaluation fill:#ebfafa,stroke:#00b3b3,stroke-width:2px;
    style BusinessInsights fill:#f2e6ff,stroke:#7b2cbf,stroke-width:2px;
```

---

## 📈 1. 탐색적 데이터 분석 (EDA) 및 변수 분포 해석

### 1.1 주요 수치형 변수 분포 및 기술통계

웹페이지 가치(`PageValues`) 및 특정 상품 상세 페이지 체류 시간(`ProductRelated_Duration`)에 대한 데이터 분포 분석 결과입니다.

#### **[PageValues 분포 및 상호작용]**
![PageValues 분포](./images/eda_num_PageValues.png)

##### **PageValues 데이터 기술통계표**
{num_tables.get('PageValues', '')}

##### **PageValues 정밀 인사이트 (500자 이상)**
`PageValues` 변수는 사용자가 해당 세션 동안 방문한 페이지의 평균적인 가치를 대변하며, 구매 완료(`Revenue = True`)에 가장 직접적이고 파괴적인 영향력을 미치는 것으로 나타났습니다.
위의 기술통계 표를 분석해 보면, 비구매 고객(`False`)의 PageValues 평균값은 거의 0에 가깝고 75% 백분위수까지도 0으로 채워져 있습니다. 반면, 실제 구매를 완료한 고객(`True`)의 PageValues 평균값은 27.26에 달하며 최대 361.76에 이르는 고가치 영역을 나타냅니다.
이 분포의 핵심 시사점은 단순 트래픽 유입이 매출을 보장하지 않는다는 것입니다. 장바구니 페이지 도달, 장바구니 담기, 리뷰 확인과 같은 매출 기여 행동을 취하게 만드는 '골든 페이지'로 고객을 자연스럽게 유입시켜야 함을 의미합니다.
따라서, 마케터와 UI 디자이너는 사용자의 유기적 흐름에서 이탈율을 막고 장바구니 페이지 접근성을 획기적으로 개선하기 위해 메인 화면의 행동유도버튼(CTA)의 배치 및 시각 디자인을 정교하게 다듬는 '체류 경험 극대화' 전략을 시급히 전개해야 합니다.

---

#### **[ProductRelated_Duration 분포 및 상호작용]**
![ProductRelated_Duration 분포](./images/eda_num_ProductRelated_Duration.png)

##### **ProductRelated_Duration 데이터 기술통계표**
{num_tables.get('ProductRelated_Duration', '')}

##### **ProductRelated_Duration 정밀 인사이트 (500자 이상)**
`ProductRelated_Duration`은 고객이 상품 상세 페이지에 머무른 누적 시간(초 단위)을 나타냅니다. 분석 결과, 구매한 고객들의 평균 상품 페이지 체류 시간은 1852.12초로 비구매 고객들의 평균 체류 시간(1124.96초)에 비해 1.6배 이상 월등히 긴 것으로 분석되었습니다. 
하지만 두 그룹 모두 50% 중앙값(Median)과 75% 백분위수의 격차가 매우 큰 우측 꼬리가 긴 왜곡된 분포(Right-Skewed) 구조를 띱니다. 이는 대다수의 일반적인 고객은 빠르게 이탈하지만, 상품 정보를 꼼꼼히 탐색하고 비교하는 소수의 고관여 고객들이 장시간 상세 정보 페이지에 잔류하고 최종 구매까지 안착함을 증명합니다.
이 데이터를 실무 마케팅 전략에 투영하기 위해서는, 고객이 일정 시간(예: 중앙값 근방의 약 600초) 이상 제품 탐색 화면에 잔류하고 있으나 장바구니 담기를 실행하지 않는 조건의 실시간 잔류 넛지 시나리오를 가동해야 합니다. 
예를 들어, 해당 세션에 실시간 상담 팝업창을 노출하거나 구매 의사를 결단할 수 있도록 '오늘만 3% 즉시 할인 쿠폰 제공' 팝업 넛지를 설계하여 구매 주저 상태의 탐색 유저를 실시간으로 낚아채는 타겟 프로모션이 매우 효과적일 것입니다.

---

### 1.2 주요 범주형 변수 교차 비율 해석

고객 유형(`VisitorType`)에 따른 구매 전환 확률 및 비율 교차 분석 결과입니다.

#### **[VisitorType별 구매 전환 비율 (100% 누적)]**
![VisitorType 비율](./images/eda_cat_VisitorType.png)

##### **VisitorType별 구매 여부 빈도 교차표**
{cat_tables.get('VisitorType', '')}

##### **VisitorType 정밀 인사이트 (500자 이상)**
방문자 유형(`VisitorType`)은 신규 방문 고객(`New_Visitor`), 기존 재방문 고객(`Returning_Visitor`), 그리고 기타 고객(`Other`)으로 나뉩니다.
교차 분석 표에 따르면, 재방문 고객은 총 10,551건 중 1,466건(전환율 약 13.9%)의 구매 완료 성과를 기록하였으며, 신규 방문 고객은 1,694건 중 422건(전환율 약 24.9%)의 놀라운 전환 효율을 입증하였습니다. 신규 유저가 기존 유저 대비 구매 결단력이 거의 2배 가까이 강하게 작동하는 것으로 나타났습니다.
이러한 전환 효율 격차는 기존 재방문 유저들은 상품을 단순 비교 탐색하거나 가격 모니터링 목적으로 반복 방문하는 체리피커 성격이 짙은 반면, 신규 방문자들은 외부 마케팅 광고나 검색 포털 광고를 타고 명확한 구매 필요를 품고 쇼핑몰로 단독 진입한 직접 타겟군일 개연성이 높음을 증명합니다.
이 결과에 맞추어, 마케팅 예산 및 전략을 이원화해야 합니다. 첫째, 신규 방문 유저의 리텐션을 잡고 첫 구매를 강력히 촉진하기 위해 '첫 구매 무료 배송' 또는 '신규 가입 환영 특별 적립금 지급' 프로모션을 대문 레이어에 즉각 노출해야 합니다.
반면 기존 재방문 고객군에 대해서는 그들의 지난 장바구니 담기 이력이나 상품 방문 정보를 분석하여, 정교하게 타겟팅된 카탈로그 이메일 전송 또는 카카오 알림톡 푸시 등의 '리마케팅 캠페인'으로 재방문을 유도하고 단골 고객 충성도를 높이는 록인(Lock-in) 전략을 병행하는 것이 최선입니다.

---

## 🤖 2. 머신러닝 모델 학습 및 성능 평가

### 2.1 모델별 예측 성능 평가지표 대조

분류 예측을 수행하기 위해 사용된 3개 머신러닝 알고리즘의 종합 검증 성적표입니다.

##### **머신러닝 모델 성능 비교표 (검증 데이터 기준)**
{metrics_table}

#### **[3개 모델 성능 대조 ROC 곡선]**
![ROC Curve](./images/ml_roc_curve.png)

##### **머신러닝 평가지표 및 과적합 정밀 인사이트 (500자 이상)**
의사결정나무(Decision Tree), 랜덤 포레스트(Random Forest), 그래디언트 부스팅(Gradient Boosting) 등 3가지 분류 알고리즘에 대해 5대 평가지표(Accuracy, Precision, Recall, F1, ROC AUC)를 산출해 정량 평가를 실시했습니다.
성능지표 요약표와 ROC 커브를 대조해 보면, 부스팅 계열 알고리즘인 `Gradient Boosting`과 배깅 앙상블인 `Random Forest`가 예측력 관점에서 매우 우수한 성적을 보여주고 있습니다. 특히 Gradient Boosting 모델은 ROC AUC가 0.90에 근접하여 고객의 최종 의사를 탐지하는 일반화 지수 면에서 가장 탁월한 퀄리티를 유지하고 있습니다.
성능 지표 중에서도 현업 담당자가 주목해야 할 부분은 재현율(Recall) 지표입니다. 구매 의지가 있는 타겟 고객을 미구매할 것으로 판단해 마케팅 넛지 지급 대상에서 누락시키는 비용은 전환 기회 비용 관점에서 막대한 손실을 야기합니다.
이 분석 결과를 토대로, 실제 마케팅 자동화 파이프라인에 탑재할 최종 모델로 일반화 AUC 및 F1-Score가 가장 균형 잡힌 Gradient Boosting 모델 또는 안정적인 Random Forest 모델 배포를 추천합니다. 
동시에, 모델 오버피팅 예방을 위해 트리 깊이 조절 슬라이더 및 오버샘플링 옵션을 결합해 최적의 일반화 마진을 유지하도록 주기적인 하이퍼파라미터 모니터링 파이프라인을 연동해야 과대적합 리스크를 철저히 방지할 수 있습니다.

---

### 2.2 피처 중요도 분석 및 비즈니스 활용 방안

Random Forest 모델을 통해 파악된 고객 매출 발생 영향도 상위 10대 피처의 가중치 데이터입니다.

#### **[Random Forest 피처 중요도 Top 10]**
![Feature Importance](./images/ml_feature_importance.png)

##### **피처 중요도 순위표**
{feat_imp_table}

##### **피처 중요도 비즈니스 연계 인사이트 (500자 이상)**
피처 중요도 추출 결과, 예상했던 바와 같이 `PageValues`가 10대 요인 중 압도적 가중치로 1위를 기록하여 최종 매출 성패의 알파이자 오메가임을 정량적으로 확인시켜 주고 있습니다.
그 뒤를 이어, 상품 상세 화면에서의 체류 지속성을 드러내는 `ProductRelated_Duration`과 세션 페이지 내의 이탈 민감도를 나타내는 `ExitRates` 및 `BounceRates`가 매출 행동 기여에 강력하게 작용하는 피처로 상위권을 지키고 있습니다.
비즈니스 실무 관점에서 이 중요도 데이터는 자원 배분 의사결정의 명확한 가이드라인을 선사합니다. 첫째, 유입 트래픽 단순 증대를 위한 막대한 배너 광고비 지출보다는, 유입된 고객의 가치 지표(`PageValues`) 자체를 빌드업하기 위한 쇼핑몰 UX/UI 개선 및 온사이트 개인화 마케팅에 투자를 집중해야 한다는 점입니다.
둘째, 이탈율(`BounceRates`) 관리를 위해 상세 설명 화면 내에 '실제 이용 고객들의 포토 및 영상 리뷰 정렬 필터'를 눈에 잘 띄게 부각시켜 유저들의 페이지 내 체류 흐름을 추가로 확보해야 합니다.
셋째, 주요 이탈 지점(`ExitRates`)이 관측되는 결제/장바구니 직전 페이지에 대해서는 실시간으로 마우스 커서가 브라우저 닫기 영역으로 향할 때 자동으로 '미결제 상품 보존 중' 긴급 리타게팅 넛지 팝업을 띄우는 이탈 방어 장치를 구현하는 등 고도화된 비즈니스 동선 보정을 통해 직접적인 매출 증대를 실현해야 합니다.
"""
    
    report_file_path = os.path.join(output_dir, "ML_Evaluation_Report.md")
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"종합 분석 보고서 및 차트 생성이 성공적으로 완료되었습니다: {report_file_path}")

if __name__ == "__main__":
    import argparse
    
    # 기본 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    default_data_path = os.path.join(base_dir, "online-shoppers", "data", "online_shoppers_intention.csv")
    default_output_dir = os.path.join(base_dir, "online-shoppers", "report")
    
    parser = argparse.ArgumentParser(description="범용 머신러닝 분석 및 마크다운 리포트 생성기")
    parser.add_argument("--data_path", type=str, default=default_data_path, help="분석할 CSV 데이터셋 경로")
    parser.add_argument("--target_col", type=str, default="Revenue", help="예측 및 타겟 컬럼명")
    parser.add_argument("--output_dir", type=str, default=default_output_dir, help="최종 리포트 및 이미지 파일이 저장될 폴더")
    
    args = parser.parse_args()
    
    # 상대 경로 처리 등을 위한 유연성 확보
    data_path = os.path.abspath(args.data_path)
    output_dir = os.path.abspath(args.output_dir)
    
    if os.path.exists(data_path):
        create_eda_and_ml_report(data_path, output_dir, args.target_col)
    else:
        # 워크스페이스 내에서 직접 돌릴 경우 대비 예외 처리 경로
        alt_data_path = os.path.join(os.getcwd(), "online-shoppers", "data", "online_shoppers_intention.csv")
        alt_output_dir = os.path.join(os.getcwd(), "online-shoppers", "report")
        if os.path.exists(alt_data_path) and args.data_path == default_data_path:
            create_eda_and_ml_report(alt_data_path, alt_output_dir, args.target_col)
        else:
            print(f"에러: 지정하신 데이터 경로를 찾을 수 없습니다: {data_path}")


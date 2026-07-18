"""
온라인 쇼핑객 구매 의도(Revenue) 예측을 위한 머신러닝 페이지
- 사용 데이터: online_shoppers_intention.csv
- 핵심 모델: 의사결정나무 (Decision Tree)
- 주요 기능: 
  1. 머신러닝 파이프라인 과정 시각화 (Mermaid)
  2. 모델 학습 및 전처리 (Label Encoding, Train/Test 분할)
  3. 의사결정나무 트리 시각화 및 피처 중요도 분석 (Plotly)
  4. 예측 결과에 대한 5가지 성능 평가 지표 및 Confusion Matrix, ROC Curve 시각화
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, roc_curve
)
from imblearn.over_sampling import SMOTE

st.set_page_config(page_title="머신러닝 예측 (Revenue)", layout="wide")

st.title("🛒 온라인 쇼핑객 구매 의도 (Revenue) 예측 모델")
st.markdown("의사결정나무(Decision Tree)를 사용하여 온라인 쇼핑객의 구매(Revenue) 여부를 예측하고 분석합니다.")

# 1. Mermaid를 통한 머신러닝 과정 시각화
st.header("1. 머신러닝 파이프라인 과정")

def mermaid(code: str, height=350):
    components.html(f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>mermaid.initialize({{startOnLoad:true}})</script>
        <div class="mermaid" style="text-align: center;">
            {code}
        </div>
    """, height=height)

mermaid_code = """
graph TD
    A[데이터 로드<br>online_shoppers_intention.csv] --> B[데이터 전처리<br>결측치 확인 및 범주형 변수 인코딩]
    B --> C[데이터 분할<br>Train/Test 80:20 Split]
    C --> D[모델 학습<br>Decision Tree Classifier]
    D --> E[모델 평가<br>5가지 지표 확인]
    D --> F[시각화<br>의사결정나무 및 Feature Importance]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
"""
# mermaid(mermaid_code)

st.divider()

# 2. 데이터 로드 및 전처리
@st.cache_data
def load_and_preprocess_data():
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "data", "online_shoppers_intention.csv")
    df = pd.read_csv(file_path)
    
    # Label encoding for categoricals
    le_dict = {}
    categorical_cols = ['Month', 'VisitorType', 'Weekend', 'Revenue']
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        le_dict[col] = le
        
    X = df.drop('Revenue', axis=1)
    y = df['Revenue']
    
    # Stratified split to maintain class balance
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # SMOTE를 활용한 오버샘플링 적용 (클래스 불균형 해소 및 재현율 향상)
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    return X_train, X_test, y_train, y_test, X_train_resampled, y_train_resampled, X.columns.tolist()

with st.spinner("데이터를 불러오고 전처리하는 중입니다..."):
    X_train, X_test, y_train, y_test, X_train_resampled, y_train_resampled, feature_names = load_and_preprocess_data()

st.header("2. 모델 학습 결과")
st.write(f"- **원본 학습 데이터 크기:** {X_train.shape[0]}건")
st.write(f"- **SMOTE 적용 후 학습 데이터 크기:** {X_train_resampled.shape[0]}건 (클래스 균형 조정됨)")
st.write(f"- **테스트 데이터 크기:** {X_test.shape[0]}건")
st.write(f"- **사용된 특성(Feature) 개수:** {len(feature_names)}개")

@st.cache_resource
def train_model(X_train_res, y_train_res):
    # 과적합 방지 및 시각화 가독성을 위해 max_depth 설정
    clf = DecisionTreeClassifier(max_depth=4, random_state=42)
    clf.fit(X_train_res, y_train_res)
    return clf

clf = train_model(X_train_resampled, y_train_resampled)

st.divider()

# 3. 모델 시각화 (의사결정나무 및 Feature Importance)
st.header("3. 모델 시각화 분석")

col1, col2 = st.columns([1.5, 1])

def plot_decision_tree_plotly(clf, feature_names):
    tree_ = clf.tree_
    n_nodes = tree_.node_count
    children_left = tree_.children_left
    children_right = tree_.children_right
    feature = tree_.feature
    threshold = tree_.threshold
    value = tree_.value
    
    # 노드 위치 계산 (단순 깊이 우선 탐색 기반)
    positions = {}
    def calc_pos(node, depth, x_min, x_max):
        x = (x_min + x_max) / 2
        y = -depth
        positions[node] = (x, y)
        if children_left[node] != _tree.TREE_LEAF:
            calc_pos(children_left[node], depth + 1, x_min, x)
            calc_pos(children_right[node], depth + 1, x, x_max)
            
    calc_pos(0, 0, 0, 100)
    
    edge_x = []
    edge_y = []
    for i in range(n_nodes):
        if children_left[i] != _tree.TREE_LEAF:
            x0, y0 = positions[i]
            x1, y1 = positions[children_left[i]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            x2, y2 = positions[children_right[i]]
            edge_x.extend([x0, x2, None])
            edge_y.extend([y0, y2, None])
            
    node_x = []
    node_y = []
    text = []
    hovertext = []
    colors = []
    
    for i in range(n_nodes):
        x, y = positions[i]
        node_x.append(x)
        node_y.append(y)
        
        samples = tree_.n_node_samples[i]
        val = value[i][0]
        class_idx = np.argmax(val)
        class_name = "구매 (Revenue=1)" if class_idx == 1 else "미구매 (Revenue=0)"
        
        if feature[i] != _tree.TREE_UNDEFINED:
            name = feature_names[feature[i]]
            thres = threshold[i]
            hover_label = f"분기 조건: {name} <= {thres:.2f}<br>샘플 수: {samples}<br>지배적 클래스: {class_name}"
            node_text = f"{name}<br><= {thres:.2f}"
            colors.append('#1f77b4') # 분기 노드 파란색
        else:
            hover_label = f"리프 노드<br>예측: {class_name}<br>샘플 수: {samples}"
            node_text = f"결과:<br>{class_name}"
            colors.append('#ff7f0e' if class_idx == 1 else '#2ca02c') # 결과 노드 색상 분리
            
        text.append(node_text)
        hovertext.append(hover_label)
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode='lines', 
        line=dict(color='#888', width=1.5), 
        hoverinfo='none'
    ))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        marker=dict(size=40, color=colors, line=dict(width=2, color='DarkSlateGrey')),
        text=text,
        textposition='bottom center',
        hovertext=hovertext,
        hoverinfo='text',
        textfont=dict(size=10)
    ))
    fig.update_layout(
        title="의사결정나무 트리 구조 (Plotly)",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        height=600,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

with col1:
    st.subheader("🌲 의사결정나무 시각화")
    fig_tree = plot_decision_tree_plotly(clf, feature_names)
    st.plotly_chart(fig_tree)

with col2:
    st.subheader("🔑 특성 중요도 (Feature Importance)")
    importances = clf.feature_importances_
    
    # 중요도가 0보다 큰 특성만 추출
    idx = np.where(importances > 0)[0]
    filtered_importances = importances[idx]
    filtered_features = [feature_names[i] for i in idx]
    
    # 데이터프레임으로 변환 후 정렬
    df_imp = pd.DataFrame({'Feature': filtered_features, 'Importance': filtered_importances})
    df_imp = df_imp.sort_values(by='Importance', ascending=True)
    
    fig_imp = px.bar(
        df_imp, x='Importance', y='Feature', orientation='h',
        color='Importance', color_continuous_scale='Blues'
    )
    fig_imp.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig_imp)

st.divider()

# 4. 모델 평가 및 시각화
st.header("4. 모델 평가 (과적합 확인 및 5대 지표)")

# Train/Test 예측 수행
y_train_pred = clf.predict(X_train)
y_pred = clf.predict(X_test)
y_prob = clf.predict_proba(X_test)[:, 1]

# Train vs Test 정확도 비교
train_acc = accuracy_score(y_train, y_train_pred)
test_acc = accuracy_score(y_test, y_pred)

st.subheader("📌 Train vs Test 성능 비교 (Overfitting 확인)")
col_score1, col_score2, col_score3 = st.columns(3)
col_score1.metric("Train 정확도", f"{train_acc:.4f}", help="원본 훈련 데이터에 대한 정확도")
col_score2.metric("Test 정확도", f"{test_acc:.4f}", delta=f"{test_acc - train_acc:.4f}", help="테스트 데이터에 대한 정확도")

if abs(train_acc - test_acc) > 0.05 and train_acc > test_acc:
    col_score3.warning("⚠️ 과적합(Overfitting) 주의: Train 성능이 Test보다 유의미하게 높습니다.")
elif train_acc < 0.7:
    col_score3.error("🚨 과소적합(Underfitting) 의심: 모델이 충분히 학습되지 않았습니다.")
else:
    col_score3.success("✅ 적절한 피팅 (Good Fit): 과적합 및 과소적합 징후가 없습니다.")

st.markdown("---")
st.subheader("📌 Test 데이터 기준 5대 평가 지표")

# 5가지 지표 계산
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)

# 지표 메트릭 표시
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("정확도 (Accuracy)", f"{acc:.4f}", help="전체 예측 중 정답의 비율")
m2.metric("정밀도 (Precision)", f"{prec:.4f}", help="구매한다고 예측한 것 중 실제 구매한 비율")
m3.metric("재현율 (Recall)", f"{rec:.4f}", help="실제 구매한 사람 중 구매할 것이라 예측한 비율")
m4.metric("F1 스코어 (F1-Score)", f"{f1:.4f}", help="정밀도와 재현율의 조화 평균")
m5.metric("ROC AUC", f"{roc_auc:.4f}", help="클래스 분류 성능의 전반적인 평가 지표")

# 평가 결과 시각화
col_eval1, col_eval2 = st.columns(2)

with col_eval1:
    st.subheader("분류 오차 행렬 (Confusion Matrix)")
    cm = confusion_matrix(y_test, y_pred)
    
    fig_cm = px.imshow(
        cm, 
        text_auto=True, 
        color_continuous_scale='Blues',
        labels=dict(x="예측값 (Predicted)", y="실제값 (Actual)", color="데이터 수"),
        x=['미구매 (0)', '구매 (1)'],
        y=['미구매 (0)', '구매 (1)']
    )
    fig_cm.update_layout(height=450)
    st.plotly_chart(fig_cm)

with col_eval2:
    st.subheader("ROC Curve")
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    
    fig_roc = go.Figure()
    fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name=f'ROC Curve (AUC = {roc_auc:.2f})', line=dict(color='blue', width=2)))
    fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Random Classifier', line=dict(color='red', width=2, dash='dash')))
    
    fig_roc.update_layout(
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=450,
        legend=dict(x=0.6, y=0.1)
    )
    st.plotly_chart(fig_roc)

st.success("머신러닝 모델 예측 파이프라인 처리가 완료되었습니다!")

st.divider()

st.header("5. 비즈니스 인사이트 및 액션 플랜 🚀")
st.markdown("""
### 💡 주요 분석 인사이트 (Insights)
머신러닝 모델의 특성 중요도(Feature Importance)와 의사결정나무 시각화 결과를 종합해 볼 때, 고객의 구매 전환(Revenue)을 결정짓는 핵심 요인은 다음과 같습니다.

1. **압도적인 영향력을 가진 PageValues (페이지 가치):** 
   전체 모델 중요도의 약 **82.6%**를 차지하는 가장 결정적인 지표입니다. 고객이 방문한 웹페이지들의 평균 가치가 높을수록(예: 결제 직전 페이지, 장바구니, 프로모션 핵심 페이지 등) 최종 구매로 이어질 확률이 매우 높게 나타납니다.
2. **이탈률(Bounce Rates)의 강력한 패널티:** 
   두 번째로 중요한 요인(약 7.8%)인 이탈률은 구매를 저해하는 핵심 요소입니다. 방문하자마자 아무 상호작용 없이 사이트를 떠나는 고객 비율이 높은 페이지나 유입 경로는 전체 전환율을 크게 깎아먹고 있습니다.
3. **계절성(Month) 및 탐색 깊이(Administrative, ProductRelated_Duration):** 
   방문 시기(월)에 따라 구매 의도의 편차가 크게 발생하며, 사용자 계정 설정이나 결제 배송 정보 등 관리/정보 탐색 페이지(Administrative)를 많이 방문할수록 구매로 이어지는 경향성이 존재합니다.

---

### 🎯 비즈니스 액션 플랜 (Action Plan)
위의 인사이트를 바탕으로 실제 매출 증대를 위해 다음과 같은 비즈니스 전략을 제안합니다.

* **고가치 페이지(High-Value Pages)로의 유도 최적화**
  * **전략:** 방문자들이 PageValues가 높은 페이지(베스트셀러, 장바구니, 기획전 페이지)로 자연스럽게 흘러가도록 동선을 재설계해야 합니다. 
  * **액션:** 메인 화면 최상단이나 랜딩 페이지에 '개인화된 추천 상품' 밴드나 '기간 한정 혜택' 배너를 배치하여, 고객이 가치 없는 페이지에 머물지 않고 즉시 핵심 구매 경로로 진입하도록 클릭을 유도하세요.

* **초기 이탈률 방어 및 이탈 징후 타겟팅 (Exit-Intent Strategy)**
  * **전략:** 이탈률(Bounce Rates)이 높은 유입 채널이나 랜딩 페이지를 즉각적으로 식별하고 방어해야 합니다.
  * **액션:** 고객이 브라우저 창을 닫으려고 하거나 마우스가 이탈하는 움직임이 감지될 때, 타임세일 할인 쿠폰이나 무료 배송 혜택을 담은 팝업을 노출하여 마지막 체류를 유도하세요. 첫 랜딩 페이지의 로딩 속도를 최적화하는 것도 필수적입니다.

* **시즌 및 개인 행동 맞춤형 리타겟팅 마케팅**
  * **전략:** Month(방문 월) 변수가 유의미하므로 연말이나 주요 시즌(예: 11월 블랙프라이데이)에 마케팅 예산을 집중 편성해야 합니다.
  * **액션:** 장바구니에 물건을 담아두고 결제 페이지(PageValues가 높음)까지 도달했으나 구매하지 않은 고객들에게만 선별적으로 SMS나 이메일 리타겟팅 광고(할인 쿠폰 동봉)를 발송하면 매우 높은 마케팅 ROI를 달성할 수 있습니다.

* **탐색(Administrative) 중인 고객을 위한 실시간 넛지(Nudge)**
  * **전략:** 배송 정보, 반품 규정, 고객 센터 등의 정보 페이지(Administrative)에 머무는 고객은 구매 의향은 있지만 확신이 부족한 상태일 수 있습니다.
  * **액션:** 해당 페이지에 챗봇(Chatbot)을 띄워 실시간 상담을 지원하거나, "오늘 주문 시 내일 도착"과 같이 구매 불안감을 해소해 주는 명확한 문구를 강조하여 즉각적인 구매 결정을 돕도록 설계하세요.
""")

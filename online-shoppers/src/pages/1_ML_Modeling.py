"""
이 스크립트는 Online Shoppers Purchasing Intention 데이터셋을 바탕으로
랜덤포레스트와 부스팅 알고리즘을 사용해 구매 여부(Revenue)를 예측하고
모델의 성능을 평가하는 Streamlit 페이지입니다.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

st.set_page_config(page_title="ML 모델링 - 구매 예측", layout="wide")

@st.cache_data
def load_data():
    # 현재 파일 위치: src/pages/1_ML_Modeling.py
    # 따라서 상위의 상위 폴더인 online-shoppers 폴더를 base_dir로 설정합니다.
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "data", "online_shoppers_intention.csv")
    df = pd.read_csv(data_path)
    return df

def preprocess_data(df):
    # 결측치 제거
    df = df.dropna()
    
    # 입력(X)과 출력(y) 분리
    X = df.drop('Revenue', axis=1)
    
    # Revenue는 불리언 값이 문자열 'True'/'False'로 되어있거나 bool 형태일 수 있음
    if X.empty:
        return X, []
        
    # 문자열인 경우 매핑, 부울인 경우 int로 변환
    if df['Revenue'].dtype == 'object':
        y = df['Revenue'].astype(str).map({'True': 1, 'False': 0, 'True ': 1, 'False ': 0})
        if y.isnull().any():
            y = df['Revenue'].astype(bool).astype(int)
    else:
        y = df['Revenue'].astype(int)
    
    # 범주형 변수 원핫인코딩 적용
    categorical_cols = X.select_dtypes(include=['object', 'bool']).columns
    X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    
    return X, y

def main():
    st.title("🤖 머신러닝 모델 학습 및 평가")
    st.markdown("이 페이지에서는 방문자의 데이터를 바탕으로 **수익 발생(Revenue)** 여부를 예측하기 위해 **랜덤 포레스트(Random Forest)**와 **부스팅(Gradient Boosting)** 알고리즘을 학습하고 성능을 비교 평가합니다.")
    
    try:
        df = load_data()
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return
        
    X, y = preprocess_data(df)
    
    # 사이드바에서 모델 학습 파라미터 설정
    st.sidebar.header("모델 학습 설정")
    test_size = st.sidebar.slider("테스트 데이터 비율", 0.1, 0.5, 0.2, 0.05)
    random_state = st.sidebar.number_input("랜덤 시드 (Random State)", min_value=0, max_value=9999, value=42)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    
    # 스케일링
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    st.markdown("### 📊 데이터 준비")
    st.write(f"- **전체 데이터 수**: {len(X):,} 개")
    st.write(f"- **학습 데이터 수**: {len(X_train):,} 개 (비율: {1-test_size:.2f})")
    st.write(f"- **테스트 데이터 수**: {len(X_test):,} 개 (비율: {test_size:.2f})")
    st.write(f"- **사용된 특성(Feature) 수**: {X_train.shape[1]} 개 (원핫인코딩 적용됨)")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌲 랜덤 포레스트 (Random Forest)")
        rf_n_estimators = st.slider("트리 개수 (n_estimators) - RF", 10, 200, 100, 10, key='rf_n')
        
        if st.button("랜덤 포레스트 학습", key='btn_rf'):
            with st.spinner("학습 중..."):
                rf_model = RandomForestClassifier(n_estimators=rf_n_estimators, random_state=random_state)
                rf_model.fit(X_train_scaled, y_train)
                rf_pred = rf_model.predict(X_test_scaled)
                
                rf_acc = accuracy_score(y_test, rf_pred)
                rf_prec = precision_score(y_test, rf_pred)
                rf_rec = recall_score(y_test, rf_pred)
                rf_f1 = f1_score(y_test, rf_pred)
                rf_cm = confusion_matrix(y_test, rf_pred)
                
                st.success("학습 완료!")
                
                # 평가지표 출력
                metrics_df = pd.DataFrame({
                    "지표": ["정확도 (Accuracy)", "정밀도 (Precision)", "재현율 (Recall)", "F1 Score"],
                    "점수": [rf_acc, rf_prec, rf_rec, rf_f1]
                })
                st.table(metrics_df.style.format({"점수": "{:.4f}"}))
                
                # 혼동행렬 시각화
                fig_rf_cm = px.imshow(rf_cm, text_auto=True, color_continuous_scale='Blues',
                                      labels=dict(x="예측값", y="실제값"),
                                      x=['False (0)', 'True (1)'], y=['False (0)', 'True (1)'],
                                      title="랜덤 포레스트 혼동 행렬")
                st.plotly_chart(fig_rf_cm, use_container_width=True)
                
                # 피처 중요도
                feature_importances = pd.DataFrame({'Feature': X.columns, 'Importance': rf_model.feature_importances_})
                feature_importances = feature_importances.sort_values('Importance', ascending=False).head(10)
                
                fig_rf_fi = px.bar(feature_importances, x='Importance', y='Feature', orientation='h',
                                   title="Top 10 피처 중요도 (Random Forest)")
                fig_rf_fi.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_rf_fi, use_container_width=True)

    with col2:
        st.subheader("🚀 그래디언트 부스팅 (Gradient Boosting)")
        gb_n_estimators = st.slider("트리 개수 (n_estimators) - GB", 10, 200, 100, 10, key='gb_n')
        
        if st.button("부스팅 모델 학습", key='btn_gb'):
            with st.spinner("학습 중..."):
                gb_model = GradientBoostingClassifier(n_estimators=gb_n_estimators, random_state=random_state)
                gb_model.fit(X_train_scaled, y_train)
                gb_pred = gb_model.predict(X_test_scaled)
                
                gb_acc = accuracy_score(y_test, gb_pred)
                gb_prec = precision_score(y_test, gb_pred)
                gb_rec = recall_score(y_test, gb_pred)
                gb_f1 = f1_score(y_test, gb_pred)
                gb_cm = confusion_matrix(y_test, gb_pred)
                
                st.success("학습 완료!")
                
                # 평가지표 출력
                metrics_df2 = pd.DataFrame({
                    "지표": ["정확도 (Accuracy)", "정밀도 (Precision)", "재현율 (Recall)", "F1 Score"],
                    "점수": [gb_acc, gb_prec, gb_rec, gb_f1]
                })
                st.table(metrics_df2.style.format({"점수": "{:.4f}"}))
                
                # 혼동행렬 시각화
                fig_gb_cm = px.imshow(gb_cm, text_auto=True, color_continuous_scale='Oranges',
                                      labels=dict(x="예측값", y="실제값"),
                                      x=['False (0)', 'True (1)'], y=['False (0)', 'True (1)'],
                                      title="그래디언트 부스팅 혼동 행렬")
                st.plotly_chart(fig_gb_cm, use_container_width=True)
                
                # 피처 중요도
                feature_importances_gb = pd.DataFrame({'Feature': X.columns, 'Importance': gb_model.feature_importances_})
                feature_importances_gb = feature_importances_gb.sort_values('Importance', ascending=False).head(10)
                
                fig_gb_fi = px.bar(feature_importances_gb, x='Importance', y='Feature', orientation='h',
                                   title="Top 10 피처 중요도 (Gradient Boosting)")
                fig_gb_fi.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_gb_fi, use_container_width=True)

if __name__ == "__main__":
    main()

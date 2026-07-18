"""
총생활인구수 컬럼을 제거하고 결과를 덮어쓰는 스크립트입니다.
세부 생활인구수의 합으로 구할 수 있으므로 불필요한 데이터를 제거하여 최적화합니다.
"""

import pandas as pd

def main():
    parquet_file_path = r'c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\data\LOCAL_PEOPLE_DONG_202606.parquet'
    
    print("--- 1. 데이터 로드 ---")
    df = pd.read_parquet(parquet_file_path)
    
    print("\n--- 2. '총생활인구수' 컬럼 제거 ---")
    if '총생활인구수' in df.columns:
        df = df.drop(columns=['총생활인구수'])
        print("'총생활인구수' 컬럼이 성공적으로 제거되었습니다.")
    else:
        print("이미 '총생활인구수' 컬럼이 존재하지 않습니다.")
        
    print("\n--- 3. 최종 Info 확인 ---")
    df.info()
    
    print("\n--- 4. Parquet 덮어쓰기 ---")
    df.to_parquet(parquet_file_path, index=False)
    print("저장 완료!")

if __name__ == '__main__':
    main()

"""
데이터를 추가로 다운캐스팅하고 기술통계 및 info() 결과를 출력하는 스크립트입니다.
기준일ID와 행정동코드를 카테고리형으로 변환하고, 실수형 데이터를 최적화합니다.
"""

import pandas as pd
import io

def main():
    parquet_file_path = r'c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\data\LOCAL_PEOPLE_DONG_202606.parquet'
    
    print("--- 1. 데이터 로드 ---")
    df = pd.read_parquet(parquet_file_path)
    
    print("\n--- 2. 기준일ID, 행정동코드 카테고리 변환 ---")
    df['기준일ID'] = df['기준일ID'].astype('category')
    df['행정동코드'] = df['행정동코드'].astype('category')
    
    print("\n--- 3. 기술 통계 확인 (수치형) ---")
    print(df.describe().to_markdown())
    
    print("\n--- 4. 기술 통계 확인 (범주형) ---")
    print(df.describe(include=['category']).to_markdown())
    
    print("\n--- 5. 추가 다운캐스팅 ---")
    # float64 -> float32 로 다운캐스팅 시도
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype('float32')
        
    print("\n--- 6. 최종 Info 확인 ---")
    df.info()
    
    print("\n--- 7. Parquet 덮어쓰기 ---")
    df.to_parquet(parquet_file_path, index=False)
    print("저장 완료!")

if __name__ == '__main__':
    main()

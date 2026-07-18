"""
데이터의 상하위 5개 행 및 기술통계를 마크다운 형태로 추출하는 스크립트입니다.
"""
import pandas as pd

def main():
    file_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
    df = pd.read_parquet(file_path)
    
    with open('tables_output.md', 'w', encoding='utf-8') as f:
        f.write("### 데이터 상위 5개 행 (Head)\n")
        f.write(df.head().to_markdown(index=False))
        f.write("\n\n### 데이터 하위 5개 행 (Tail)\n")
        f.write(df.tail().to_markdown(index=False))
        
        f.write("\n\n### 수치형 변수 기술통계 (Numerical Descriptive Statistics)\n")
        num_cols = ['시간대구분', '행정동코드', '생활인구수']
        f.write(df[num_cols].describe().to_markdown())
        
        f.write("\n\n### 범주형 변수 기술통계 (Categorical Descriptive Statistics)\n")
        cat_cols = ['기준일ID', '성별', '연령대']
        f.write(df[cat_cols].astype(str).describe().to_markdown())

if __name__ == "__main__":
    main()

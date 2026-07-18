"""
서울시 생활인구 데이터를 전처리하는 스크립트입니다.
zip 파일 형태의 csv를 판다스로 읽어와서 성별, 연령대를 tidy 형태로 변환하고
다운캐스팅을 적용하여 parquet 포맷으로 저장합니다.
"""

import pandas as pd
import io

def main():
    zip_file_path = r'c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\data\LOCAL_PEOPLE_DONG_202606.zip'
    parquet_file_path = r'c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\data\LOCAL_PEOPLE_DONG_202606.parquet'
    report_file_path = r'c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\report\info_report.txt'
    
    # 1. Read data
    df = pd.read_csv(zip_file_path, encoding='utf-8', index_col=False)
    
    # Save original info
    buf_orig = io.StringIO()
    df.info(buf=buf_orig)
    orig_info = buf_orig.getvalue()
    
    # Save head
    head_str = df.head().to_markdown()
    
    # 2. Tidy data transformation
    id_vars = list(df.columns[:4])
    value_vars = list(df.columns[4:])
    
    df_melt = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='성별_연령대', value_name='생활인구수')
    
    # Extract 성별 and 연령대
    # '남자10세부터14세생활인구수' -> 성별: 남자 (2글자), 연령대: 10세부터14세, 제외할부분: 생활인구수 (5글자)
    df_melt['성별'] = df_melt['성별_연령대'].str[:2]
    df_melt['연령대'] = df_melt['성별_연령대'].str[2:-5]
    df_melt.drop(columns=['성별_연령대'], inplace=True)
    
    # 3. Downcast to reduce size
    for col in df_melt.select_dtypes(include=['int']).columns:
        df_melt[col] = pd.to_numeric(df_melt[col], downcast='integer')
    for col in df_melt.select_dtypes(include=['float']).columns:
        df_melt[col] = pd.to_numeric(df_melt[col], downcast='float')
        
    df_melt['성별'] = df_melt['성별'].astype('category')
    df_melt['연령대'] = df_melt['연령대'].astype('category')
    
    # 4. Save to parquet
    df_melt.to_parquet(parquet_file_path, index=False)
    
    # 5. Read back parquet to get info
    df_parquet = pd.read_parquet(parquet_file_path)
    buf_parq = io.StringIO()
    df_parquet.info(buf=buf_parq)
    parq_info = buf_parq.getvalue()
    
    # Save everything to a text file so the agent can read it
    with open(report_file_path, 'w', encoding='utf-8') as f:
        f.write("=== HEAD ===\n")
        f.write(head_str)
        f.write("\n\n=== ORIGINAL INFO ===\n")
        f.write(orig_info)
        f.write("\n\n=== PARQUET INFO ===\n")
        f.write(parq_info)

if __name__ == '__main__':
    main()

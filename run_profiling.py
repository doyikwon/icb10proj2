"""
데이터 프로파일링 스크립트입니다.
"""
import pandas as pd
from ydata_profiling import ProfileReport
import os

def main():
    file_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
    df = pd.read_parquet(file_path)
    
    # 850만 개의 데이터는 프로파일링에 너무 오랜 시간이 걸리므로 10만 개로 샘플링
    df_sample = df.sample(n=100000, random_state=42)
    
    profile = ProfileReport(df_sample, title="Seoul POPS Data Profiling Report", minimal=True)
    
    output_dir = 'seoul-pops/report'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'profile_report.html')
    profile.to_file(output_file)
    print(f"Profile report generated at: {output_file}")

if __name__ == "__main__":
    main()

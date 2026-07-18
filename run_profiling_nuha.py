"""
누하동(청운효자동, 행정동코드: 11110515) 생활인구 데이터만 필터링하여 데이터 프로파일링을 수행하는 스크립트입니다.
"""
import pandas as pd
from ydata_profiling import ProfileReport
import os

def main():
    file_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
    print("데이터 로딩 중...")
    df = pd.read_parquet(file_path)
    
    # 누하동은 법정동이며, 행정동으로는 '청운효자동'(코드: 11110515)에 속함
    # 따라서 행정동코드 11110515로 필터링
    print("누하동(청운효자동) 데이터 필터링 중...")
    df_nuha = df[df['행정동코드'] == 11110515]
    
    print(f"필터링된 데이터 개수: {len(df_nuha)}건")
    
    print("프로파일링 리포트 생성 중...")
    # 필터링된 데이터는 약 20,160건(30일 * 24시간 * 2성별 * 14연령대)이므로 전체 데이터 프로파일링 가능
    profile = ProfileReport(df_nuha, title="Nuha-dong (Cheongunhyoja-dong) POPS Data Profiling", minimal=True)
    
    output_dir = 'seoul-pops/report'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'nuha_profile_report.html')
    profile.to_file(output_file)
    print(f"Profile report generated at: {output_file}")

if __name__ == "__main__":
    main()

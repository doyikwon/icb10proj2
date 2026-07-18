"""
전국 상가(상권)정보 CSV 파일들에서 특정 버거 프랜차이즈(버거킹, 맥도날드, KFC, 롯데리아) 
상호명 데이터를 추출하여 하나의 burger.csv 파일로 병합하는 스크립트입니다.
"""
import csv
import os
import glob

data_dir = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\burger_index\data"
output_file = os.path.join(data_dir, "burger.csv")

# 찾을 상호명 키워드들 (영문 포함)
keywords = ["버거킹", "맥도날드", "KFC", "롯데리아", "BURGER KING", "BURGERKING", "MCDONALD", "LOTTERIA"]
keywords_lower = [k.lower() for k in keywords]

files = glob.glob(os.path.join(data_dir, "*.csv"))
# 기존 출력 파일이 있으면 제외
files = [f for f in files if not f.endswith("burger.csv")]

header_written = False

print(f"처리할 총 파일 수: {len(files)}")

with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
    writer = csv.writer(out_f)
    
    for file_path in files:
        print(f"처리 중: {os.path.basename(file_path)}")
        try:
            with open(file_path, 'r', encoding='utf-8') as in_f:
                reader = csv.reader(in_f)
                header = next(reader)
                
                if not header_written:
                    writer.writerow(header)
                    header_written = True
                
                # '상호명' 컬럼 인덱스 찾기
                if '상호명' in header:
                    name_idx = header.index('상호명')
                else:
                    print(f"경고: {os.path.basename(file_path)}에서 '상호명' 컬럼을 찾을 수 없습니다.")
                    continue
                
                count = 0
                for row in reader:
                    if len(row) > name_idx:
                        name = row[name_idx].lower()
                        # 공백 제거하여 BURGER KING과 BURGERKING 모두 매칭 등 편의성 제공
                        name_no_space = name.replace(" ", "")
                        
                        match = False
                        for kw in keywords_lower:
                            kw_no_space = kw.replace(" ", "")
                            if kw_no_space in name_no_space:
                                match = True
                                break
                        
                        if match:
                            writer.writerow(row)
                            count += 1
                print(f"  발견된 데이터 수: {count}")
        except Exception as e:
            print(f"{os.path.basename(file_path)} 처리 중 오류 발생: {e}")

print(f"데이터 추출 완료! 저장 위치: {output_file}")

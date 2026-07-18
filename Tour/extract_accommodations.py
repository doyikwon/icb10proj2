"""
Tour/data 폴더에 있는 모든 CSV 상권정보 파일을 읽어서
'상권업종대분류명'이 '숙박'인 데이터만 추출하여 
하나의 CSV 파일(숙박업소_통합.csv)로 저장하는 스크립트입니다.
"""
import os
import glob
import csv

def main():
    data_dir = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\Tour\data"
    output_file = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\Tour\숙박업소_통합.csv"

    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    header_written = False
    total_found = 0

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f_out:
        writer = csv.writer(f_out)
        
        for file in csv_files:
            if os.path.basename(file) == "숙박업소_통합.csv":
                continue
                
            print(f"Processing {os.path.basename(file)}...")
            with open(file, 'r', encoding='utf-8', newline='') as f_in:
                reader = csv.reader(f_in)
                try:
                    header = next(reader)
                except StopIteration:
                    continue
                    
                if not header_written:
                    writer.writerow(header)
                    header_written = True
                    
                try:
                    cat_idx = header.index("상권업종대분류명")
                except ValueError:
                    cat_idx = 4
                    
                count = 0
                for row in reader:
                    if len(row) > cat_idx and row[cat_idx] == "숙박":
                        writer.writerow(row)
                        count += 1
                        total_found += 1
                        
            print(f"  -> Found {count} records.")

    print(f"\nComplete. Total {total_found} records saved to {output_file}")

if __name__ == '__main__':
    main()

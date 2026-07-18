import pyarrow.parquet as pq

def main():
    parquet_file_path = r'c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\data\LOCAL_PEOPLE_DONG_202606.parquet'
    meta = pq.read_metadata(parquet_file_path)
    
    print("--- Parquet Metadata ---")
    print(meta)
    
    print("\n--- Schema ---")
    print(meta.schema)
    
    print("\n--- Row Groups ---")
    print(f"Num Row Groups: {meta.num_row_groups}")
    for i in range(min(meta.num_row_groups, 1)): # print first row group to keep it concise
        print(meta.row_group(i))

if __name__ == '__main__':
    main()

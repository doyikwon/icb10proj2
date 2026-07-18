import pandas as pd
import io

zip_file_path = r'c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\data\LOCAL_PEOPLE_DONG_202606.zip'

print("--- Reading Zip ---")
df = pd.read_csv(zip_file_path, encoding='utf-8', index_col=False)
print("\n--- Columns ---")
print(df.columns.tolist())
print("\n--- Head ---")
print(df.head())
print("\n--- Info ---")
buffer = io.StringIO()
df.info(buf=buffer)
print(buffer.getvalue())

import pandas as pd

file_path = r"c:\Users\doyik\OneDrive\바탕 화면\icb10proj2\seoul-pops\data\행정동코드_매핑정보_20241218.xlsx"
df = pd.read_excel(file_path, nrows=10)
print(df.head())
print(df.columns)

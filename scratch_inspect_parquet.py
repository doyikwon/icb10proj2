import pandas as pd

df = pd.read_parquet('c:/Users/doyik/OneDrive/바탕 화면/icb10proj2/seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet')
print("--- INFO ---")
df.info()
print("\n--- HEAD ---")
print(df.head())
print("\n--- DESCRIBE ---")
print(df.describe(include='all'))
print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

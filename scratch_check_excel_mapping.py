import pandas as pd
df = pd.read_excel('c:/Users/doyik/OneDrive/바탕 화면/icb10proj2/seoul-pops/data/행정동코드_매핑정보_20241218.xlsx')
# Check Daebang-dong or Gil-dong
gil_dong = df[df['H_DNG_NM'] == '길동']
print("Gil-dong:")
print(gil_dong[['H_SDNG_CD', 'H_DNG_CD', 'H_DNG_NM']])

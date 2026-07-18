import pandas as pd
import json

df = pd.read_parquet('c:/Users/doyik/OneDrive/바탕 화면/icb10proj2/seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet')

info = {
    'columns': list(df.columns),
    'dtypes': {k: str(v) for k, v in df.dtypes.items()},
    'head': df.head().to_dict(orient='records'),
    'missing': df.isnull().sum().to_dict()
}

with open('c:/Users/doyik/OneDrive/바탕 화면/icb10proj2/seoul-pops/data/info.json', 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=4)

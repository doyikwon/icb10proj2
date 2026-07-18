"""
파일 목적: 원본 API JSON 응답 데이터를 파싱하여 통합 스키마로 변환.
주요 기능:
- `api_raw_responses.json` 파일 읽기
- 각 소스별 항목 추출 및 매핑
- `integrated_api_data.json` 파일 생성
생성일: 2026-07-13
"""
import json
import os
from datetime import datetime

def main():
    raw_path = os.path.join("online-shoppers", "data", "api_raw_responses.json")
    out_path = os.path.join("online-shoppers", "data", "integrated_api_data.json")
    
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    integrated_list = []
    
    for item in raw_data:
        source = item.get("source")
        if "error" in item:
            continue
            
        data = item.get("data", {})
        body = data.get("body", {})
        
        # 식품안전나라 API 2, 3, 4 모두 body.items 안에 리스트가 있음
        items = body.get("items", [])
        
        for idx, row in enumerate(items):
            # 식약처_건강기능식품
            if source == "식약처_건강기능식품":
                obj = row.get("item", {})
                integrated_list.append({
                    "id": f"MFDS-HF-{idx+1}",
                    "source_agency": source,
                    "category": "건강기능식품",
                    "product_name": obj.get("PRDUCT", "").strip(),
                    "main_ingredient": obj.get("SUNGSANG", "").split(" ")[0],
                    "efficacy": obj.get("MAIN_FNCTN", ""),
                    "updated_at": obj.get("REGIST_DT", datetime.today().strftime('%Y-%m-%d'))
                })
            
            # 식약처_식품영양성분
            elif source == "식약처_식품영양성분":
                obj = row
                integrated_list.append({
                    "id": f"MFDS-FN-{idx+1}",
                    "source_agency": source,
                    "category": obj.get("FOOD_CAT1_NM", ""),
                    "product_name": obj.get("FOOD_NM_KR", ""),
                    "main_ingredient": "탄수화물,단백질,지방",
                    "efficacy": "영양공급",
                    "updated_at": obj.get("UPDATE_DATE", datetime.today().strftime('%Y-%m-%d'))
                })
            
            # 식약처_e약은요
            elif source == "식약처_e약은요":
                obj = row.get("item", row)
                integrated_list.append({
                    "id": f"MFDS-DR-{idx+1}",
                    "source_agency": source,
                    "category": "일반의약품",
                    "product_name": obj.get("ITEM_NAME", ""),
                    "main_ingredient": "의약성분",
                    "efficacy": obj.get("EFCY_QESITM", ""),
                    "updated_at": datetime.today().strftime('%Y-%m-%d')
                })
                
    # 가상의 질병관리청 데이터 1개 추가
    integrated_list.append({
        "id": "MOCK-001",
        "source_agency": "국민건강보험공단(가상)",
        "category": "질병통계",
        "product_name": "감기/호흡기 질환",
        "main_ingredient": "N/A",
        "efficacy": "해당 계절 유행",
        "updated_at": datetime.today().strftime('%Y-%m-%d')
    })
                
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(integrated_list, f, ensure_ascii=False, indent=2)
        
if __name__ == "__main__":
    main()

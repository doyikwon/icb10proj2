"""
아이허브(iHerb) 스포츠 스페셜 카테고리 API를 통해 
할인 판매 중인 스포츠 제품 전체 페이지 데이터를 수집하고 CSV 파일로 저장하는 스크립트입니다.
응답의 totalSize가 실제 전체 개수가 아닌 페이지당 개수로 반환되는 한계를 극복하기 위해,
데이터가 더 이상 반환되지 않을 때까지 페이징을 계속 수행합니다.
"""

import os
import time
import requests
import pandas as pd

def scrape_iherb_specials_all():
    url = "https://catalog.app.iherb.com/category/sports/specials"
    base_params = {
        "isMobile": "false",
        "pageSize": 18
    }
    headers = {
        "referer": "https://kr.iherb.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    }

    parsed_products = []
    page = 1
    page_size = 18

    print("아이허브 스포츠 스페셜 전체 데이터 수집 시작...")

    while True:
        print(f"페이지 {page} 수집 중...")
        params = base_params.copy()
        params["page"] = page

        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code != 200:
                print(f"{page}페이지 HTTP 요청 실패. 상태 코드: {response.status_code}")
                break
            
            data = response.json()
            products_list = data.get("products", [])
            
            # 반환된 상품 목록이 없으면 수집 종료
            if not products_list:
                print(f"{page}페이지에 상품 데이터가 없습니다. 수집을 종료합니다.")
                break
                
            print(f"  - {len(products_list)}개의 상품 발견")
            
            for prod in products_list:
                prod_id = prod.get("productId")
                display_name = prod.get("displayName")
                prod_url = prod.get("url")
                part_number = prod.get("partNumber")
                list_price = prod.get("listPrice")
                discount_price = prod.get("discountPrice")
                is_out_of_stock = prod.get("isOutOfStock")
                rating = prod.get("rating")
                rating_count = prod.get("ratingCount")
                discount_percentage = prod.get("salesDiscountPercentage")
                brand_code = prod.get("brandCode")
                brand_name = prod.get("brandName")
                name = prod.get("name")
                product_name = prod.get("productName")
                potency = prod.get("potency")
                package_quantity = prod.get("packageQuantity")
                
                # 금액 정제
                def clean_price(price_str):
                    if not price_str:
                        return None
                    try:
                        cleaned = price_str.replace("₩", "").replace(",", "").strip()
                        return float(cleaned)
                    except ValueError:
                        return None
                
                numeric_list_price = clean_price(list_price)
                numeric_discount_price = clean_price(discount_price)

                parsed_products.append({
                    "ProductID": prod_id,
                    "DisplayName": display_name,
                    "URL": prod_url,
                    "PartNumber": part_number,
                    "ListPrice": list_price,
                    "DiscountPrice": discount_price,
                    "ListPriceNumeric": numeric_list_price,
                    "DiscountPriceNumeric": numeric_discount_price,
                    "IsOutOfStock": is_out_of_stock,
                    "Rating": rating,
                    "RatingCount": rating_count,
                    "DiscountPercentage": discount_percentage,
                    "BrandCode": brand_code,
                    "BrandName": brand_name,
                    "Name": name,
                    "ProductName": product_name,
                    "Potency": potency,
                    "PackageQuantity": package_quantity
                })
                
            page += 1
            # 서버 부하 조절을 위한 딜레이
            time.sleep(0.5)
            
        except Exception as e:
            print(f"에러 발생 (페이지 {page}): {e}")
            break

    # 수집 완료 후 데이터 프레임 변환 및 저장
    if parsed_products:
        df = pd.DataFrame(parsed_products)
        
        # 중복 상품 제거 (혹시 페이징 중 데이터 밀림 등으로 발생할 수 있는 중복 방지)
        df_unique = df.drop_duplicates(subset=["ProductID"])
        
        output_dir = "teamproj_test/data"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "iherb_sports_specials.csv")
        df_unique.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"전체 데이터 수집 완료! 총 {len(df_unique)}개의 고유 상품 정보를 '{output_path}'에 저장했습니다. (수집 데이터 수: {len(df)}개)")
    else:
        print("수집된 상품 데이터가 없습니다.")

if __name__ == "__main__":
    scrape_iherb_specials_all()

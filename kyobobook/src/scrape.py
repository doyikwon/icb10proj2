"""
교보문고 베스트셀러 API를 사용하여 컴퓨터/IT 분야(분류 코드 33)의 
온라인 베스트셀러 전체 페이지 데이터를 수집하고 CSV 파일로 저장하는 스크립습니다.
"""

import os
import time
import requests
import pandas as pd

def scrape_kyobo_bestseller_all():
    url = "https://store.kyobobook.co.kr/api/gw/best/v2/best-seller/online"
    base_params = {
        "per": 20,
        "saleCmdtClstCode": "33",
        "soldOutExcludeYn": "N",
        "saleCmdtDsplDvsnCode": "KOR",
        "period": "002",
        "dsplDvsnCode": "001",
        "dsplTrgtDvsnCode": "004"
    }
    
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "x-api-gw-key": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..i35xkkCOngvXqCRx.0CqToQel6sj5d0qOS2ftoDu37jRwb0vtQwMBd1e_G1ynl7KUrTrH_qPJnygVpkc0tExt4BUX_pJ4RepB5QsxWmKLjC8tEuMELKG8SvRLEVn6ambMnSmDaJ85mLbGtHcM-zFiDBzi.3y1-RnxGHFxeLNMK2dWZoQ"
    }

    parsed_books = []
    page = 1
    total_pages = 1  # 루프 시작을 위한 초기값
    per_page = 20

    print("교보문고 베스트셀러 데이터 수집 시작...")

    while page <= total_pages:
        print(f"페이지 {page}/{total_pages} 수집 중...")
        params = base_params.copy()
        params["page"] = page
        headers["referer"] = f"https://store.kyobobook.co.kr/category/domestic/33/best?page={page}"

        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code != 200:
                print(f"{page}페이지 HTTP 요청 실패. 상태 코드: {response.status_code}")
                break
            
            json_data = response.json()
            data_content = json_data.get("data", {})
            bestsellers = data_content.get("bestSeller", [])
            
            # 첫 페이지 요청 시 전체 총 아이템 개수를 확인하여 총 페이지 수 계산
            if page == 1:
                total_items = data_content.get("total", 0)
                if total_items > 0:
                    import math
                    total_pages = math.ceil(total_items / per_page)
                    print(f"전체 검색 건수: {total_items}건 (총 {total_pages}페이지)")
                else:
                    print("검색 결과가 없습니다.")
                    break
            
            if not bestsellers:
                print(f"{page}페이지에 도서 데이터가 없습니다. 수집을 종료합니다.")
                break
                
            for item in bestsellers:
                prstRnkn = item.get("prstRnkn")
                frmrRnkn = item.get("frmrRnkn")
                ymw = item.get("ymw")
                
                product = item.get("product", {})
                prod_info = product.get("productInfo", {})
                price_info = product.get("priceInfo", {})
                review_info = product.get("reviewInfo", {})
                
                # 도서 정보 추출
                book_id = prod_info.get("saleCmdtid")
                title = prod_info.get("cmdtName")
                subtitle = prod_info.get("sbttName1")
                isbn = prod_info.get("isbn")
                cmdtcode = prod_info.get("cmdtcode")
                release_date = prod_info.get("rlseDate")
                publisher = prod_info.get("pbcmName")
                author = prod_info.get("chrcName")
                
                # 가격 정보
                price = price_info.get("saleCmdtPrce")
                sale_price = price_info.get("saleCmdtSapr")
                discount_rate = price_info.get("saleCmdtPrceDscnRate")
                
                # 평점 정보
                score = review_info.get("score")
                review_count = review_info.get("count")
                
                parsed_books.append({
                    "Rank": prstRnkn,
                    "PreviousRank": frmrRnkn,
                    "Period": ymw,
                    "BookID": book_id,
                    "Title": title,
                    "Subtitle": subtitle,
                    "ISBN": isbn,
                    "CmdtCode": cmdtcode,
                    "ReleaseDate": release_date,
                    "Publisher": publisher,
                    "Author": author,
                    "Price": price,
                    "SalePrice": sale_price,
                    "DiscountRate": discount_rate,
                    "Score": score,
                    "ReviewCount": review_count
                })
                
            page += 1
            # 서버 부하 방지를 위한 딜레이 추가
            time.sleep(0.5)
            
        except Exception as e:
            print(f"에러 발생 (페이지 {page}): {e}")
            break

    # 수집 완료 후 데이터 프레임 변환 및 저장
    if parsed_books:
        df = pd.DataFrame(parsed_books)
        output_dir = "kyobobook/data"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "best_seller_all.csv")
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"전체 데이터 수집 완료! 총 {len(df)}개의 도서 정보를 '{output_path}'에 저장했습니다.")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    scrape_kyobo_bestseller_all()

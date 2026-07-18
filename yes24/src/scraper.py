"""
YES24 베스트셀러 페이지의 도서 정보를 수집하고 CSV 파일로 저장하는 스크립트입니다.
BeautifulSoup과 requests 라이브러리를 사용하여 웹 데이터를 스크래핑한 후, 
pandas를 사용하여 데이터프레임으로 변환하고 UTF-8-sig 인코딩의 CSV 파일로 저장합니다.
전체 페이지(1~5페이지, 총 120위)를 순회하며 데이터를 수집합니다.
"""
import os
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

def scrape_yes24_bestsellers():
    url = "https://www.yes24.com/product/category/BestSellerContents"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.yes24.com/"
    }
    
    book_list = []
    global_rank = 1
    
    # 1페이지부터 42페이지까지 순회하며 수집 (최대 1008개 도서, 1000권 목표)
    for page in range(1, 43):
        print(f"YES24 베스트셀러 {page}페이지 데이터를 요청 중입니다...")
        
        # Payload/Query parameters
        params = {
            "categoryNumber": "001001003",
            "sumGb": "06",
            "sex": "A",
            "age": "255",
            "goodsTp": "0",
            "addOptionTp": "0",
            "excludeTp": "2",
            "pageNumber": str(page),
            "pageSize": "24",
            "goodsStatGb": "06",
            "eBookTp": "0",
            "bestType": "YES24_BESTSELLER",
            "type": "",
            "saleYear": "0",
            "saleMonth": "0",
            "weekNo": "0",
            "saleDts": "",
            "viewMode": "",
            "freeYn": ""
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code != 200:
                print(f"{page}페이지 요청 중 오류 발생: HTTP 상태 코드 {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 각 도서 항목(itemUnit class가 포함된 요소 또는 li) 검색
            items = soup.select('div.itemUnit')
            if not items:
                items = soup.select('li')
                items = [item for item in items if item.find('div', class_='itemUnit')]
                
            if not items:
                print(f"{page}페이지에서 도서 데이터를 더 이상 찾을 수 없어 수집을 중단합니다.")
                break
                
            print(f"{page}페이지에서 발견된 도서 수: {len(items)}개")
            
            for item in items:
                try:
                    # 도서 번호 (data-goods-no) - 부모 li 또는 본인 요소에서 탐색
                    goods_no = ""
                    parent_li = item.find_parent('li')
                    if parent_li and parent_li.has_attr('data-goods-no'):
                        goods_no = parent_li['data-goods-no']
                    elif item.has_attr('data-goods-no'):
                        goods_no = item['data-goods-no']
                    
                    # 도서 제목
                    title_el = item.select_one('a.gd_name')
                    title = title_el.get_text(strip=True) if title_el else ""
                    
                    # 부제목
                    subtitle_el = item.select_one('span.gd_nameE')
                    subtitle = subtitle_el.get_text(strip=True) if subtitle_el else ""
                    
                    # 저자
                    author_el = item.select_one('span.info_auth')
                    author = ""
                    if author_el:
                        author = author_el.get_text(strip=True)
                        author = re.sub(r'\s*저$', '', author)
                    
                    # 출판사
                    pub_el = item.select_one('span.info_pub')
                    publisher = pub_el.get_text(strip=True) if pub_el else ""
                    
                    # 출판일
                    date_el = item.select_one('span.info_date')
                    pub_date = date_el.get_text(strip=True) if date_el else ""
                    
                    # 할인율
                    discount_el = item.select_one('span.txt_sale em.num')
                    discount_rate = discount_el.get_text(strip=True) + "%" if discount_el else ""
                    
                    # 판매가
                    sale_price_el = item.select_one('strong.txt_num em.yes_b')
                    sale_price = sale_price_el.get_text(strip=True) + "원" if sale_price_el else ""
                    
                    # 정가
                    original_price_el = item.select_one('span.txt_num.dash em.yes_m')
                    original_price = original_price_el.get_text(strip=True) + "원" if original_price_el else ""
                    
                    # 판매지수
                    sale_num_el = item.select_one('span.saleNum')
                    sale_num = ""
                    if sale_num_el:
                        sale_num_text = sale_num_el.get_text(strip=True)
                        sale_num = sale_num_text.replace("판매지수", "").strip()
                    
                    # 리뷰 수
                    review_count_el = item.select_one('span.rating_rvCount em.txC_blue')
                    review_count = review_count_el.get_text(strip=True) if review_count_el else "0"
                    
                    # 평점
                    rating_el = item.select_one('span.rating_grade em.yes_b')
                    rating = rating_el.get_text(strip=True) if rating_el else ""
                    
                    book_list.append({
                        "순위": global_rank,
                        "상품번호": goods_no,
                        "도서명": title,
                        "부제목": subtitle,
                        "저자": author,
                        "출판사": publisher,
                        "출판일": pub_date,
                        "할인율": discount_rate,
                        "판매가": sale_price,
                        "정가": original_price,
                        "판매지수": sale_num,
                        "리뷰수": review_count,
                        "평점": rating
                    })
                    global_rank += 1
                    
                    if len(book_list) >= 1000:
                        break
                except Exception as e:
                    print(f"항목 파싱 중 오류 발생: {e}")
                    
            if len(book_list) >= 1000:
                print("수집 목표치(1000권)에 도달하여 수집을 중료합니다.")
                break
        except Exception as e:
            print(f"{page}페이지 요청 중 실패: {e}")
            
        # 요청 대기 시간 (서버 부하 경감 및 차단 방지)
        time.sleep(0.5)
            
    if not book_list:
        print("수집된 데이터가 없습니다.")
        return
        
    df = pd.DataFrame(book_list)
    
    # 저장 경로 설정
    output_dir = "yes24/data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "yes24_bestsellers.csv")
    
    # UTF-8-sig 인코딩으로 CSV 저장 (Excel 한글 깨짐 방지)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"데이터 수집 완료! 총 {len(df)}개 도서 수집됨.")
    print(f"저장 경로: {output_path}")
    print(df.head(5))

if __name__ == "__main__":
    scrape_yes24_bestsellers()


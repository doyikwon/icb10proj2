"""
모바일 올리브영 HTML 덤프에서 상품 리스트 요소를 정밀 분석하여 상품명, 브랜드명, 가격 등을 추출하는 테스트 스크립트입니다.
"""

from bs4 import BeautifulSoup

def parse_dump():
    file_path = "oliveyoung/data/mobile_dump.html"
    
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # <li> 태그 중 goods-list 클래스를 가진 요소를 찾습니다.
    products = soup.select("li.goods-list")
    print(f"li.goods-list 상품 개수: {len(products)}")
    
    if len(products) == 0:
        # 대체 패턴으로 div나 li의 다른 클래스 탐색
        products = soup.select(".jq_molocoGoods")
        print(f"jq_molocoGoods 상품 개수: {len(products)}")
        
    for idx, prd in enumerate(products[:10]):
        print(f"\n--- Product {idx+1} ---")
        # 브랜드명은 보통 span.bname 이나 p.iname 안의 브랜드 텍스트
        brand_elem = prd.select_one("span.bname")
        brand = brand_elem.get_text(strip=True) if brand_elem else "N/A"
        
        # 상품명은 보통 p.iname 이나 p.jq_goodsNm
        name_elem = prd.select_one("p.iname, p.jq_goodsNm")
        name = name_elem.get_text(strip=True) if name_elem else "N/A"
        
        # 가격 정보 (정가, 할인가)
        # .tx_org (정가), .tx_cur (할인가) 또는 jq_priceToPay 등
        price_elem = prd.select_one(".price")
        price_text = price_elem.get_text(strip=True) if price_elem else "N/A"
        
        # 개별 가격 요소를 정교하게 선택
        cur_price_elem = prd.select_one(".price .cur, .price .tx_cur")
        cur_price = cur_price_elem.get_text(strip=True) if cur_price_elem else "N/A"
        
        org_price_elem = prd.select_one(".price .org, .price .tx_org")
        org_price = org_price_elem.get_text(strip=True) if org_price_elem else "N/A"
        
        print(f"Brand: {brand}")
        print(f"Name: {name}")
        print(f"Price Text: {price_text}")
        print(f"Current Price: {cur_price} | Org Price: {org_price}")

if __name__ == "__main__":
    parse_dump()

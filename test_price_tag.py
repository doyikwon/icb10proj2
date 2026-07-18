import sys
from bs4 import BeautifulSoup
import re

html = open('playwright_page2_real.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')
product_links = soup.find_all('a', href=lambda x: x and '/vp/products/' in x)

for a in product_links[:5]:
    price_tag = a.find(class_=re.compile('price-value'))
    if price_tag:
        print(f"Price tag: {price_tag.text}")
    else:
        print("No price tag found!")
        print(a.get_text(separator='|', strip=True))

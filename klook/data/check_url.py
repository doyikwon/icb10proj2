"""
klook_products.db 에서 상위 10개의 상품 ID와 deep_link를 확인하는 스크립트.
"""
import sqlite3

def check_urls():
    conn = sqlite3.connect('klook_products.db')
    c = conn.cursor()
    c.execute("SELECT product_id, deep_link FROM products LIMIT 10;")
    rows = c.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, URL: {row[1]}")

if __name__ == "__main__":
    check_urls()

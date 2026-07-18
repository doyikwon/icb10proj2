"""
DB 확인 및 파일 저장 스크립트.
"""
import sqlite3
import json

def verify():
    conn = sqlite3.connect('klook_products.db')
    c = conn.cursor()
    
    with open('verify_output.txt', 'w', encoding='utf-8') as f:
        c.execute("SELECT COUNT(*) FROM product_details")
        count = c.fetchone()[0]
        f.write(f"Total rows in product_details: {count}\n")
        
        f.write("\nSample joined data (products + product_details):\n")
        c.execute('''
            SELECT p.product_id, p.title, d.page_title, d.main_description
            FROM products p
            JOIN product_details d ON p.product_id = d.product_id
            LIMIT 10
        ''')
        for row in c.fetchall():
            f.write(f"ID: {row[0]}\n")
            f.write(f"Title (products): {row[1]}\n")
            f.write(f"Page Title (details): {row[2]}\n")
            desc = row[3] if row[3] else ""
            f.write(f"Desc Snippet: {desc[:200]}...\n")
            f.write("-" * 40 + "\n")
        
if __name__ == "__main__":
    verify()

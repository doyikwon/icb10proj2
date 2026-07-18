import sqlite3

def check_db():
    conn = sqlite3.connect('klook_products.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print('Tables:', tables)
    for t in tables:
        table_name = t[0]
        print(f'\nSchema for {table_name}:')
        c.execute(f"PRAGMA table_info({table_name});")
        for col in c.fetchall():
            print(col)
        print(f'\nSample data from {table_name}:')
        try:
            c.execute(f"SELECT * FROM {table_name} LIMIT 2;")
            for row in c.fetchall():
                print(row)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    check_db()

import os
import sqlite3

def init_db():
    # 設定 instance 路徑與 db 檔名
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'expense_management.db')

    # 調整 SQL 檔案路徑
    sql_path = os.path.join(os.path.dirname(__file__), 'sql')
    schema_file = os.path.join(sql_path, 'schema.sql')

    # 讀取 SQL 腳本
    with open(schema_file) as f:
        schema = f.read()

    # 初始化資料庫
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()

    print("資料庫已建立在 instance/expense_management.db")
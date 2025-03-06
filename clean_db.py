import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def clean_database():
    # SSL証明書のパス
    ssl_ca = os.path.abspath(os.path.join(os.path.dirname(__file__), os.getenv('MYSQL_SSL_CA')))
    
    # データベース接続設定
    db_config = {
        'host': os.getenv('MYSQL_HOST'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'ssl': {'ca': ssl_ca}
    }
    
    try:
        # データベースに接続
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 不要なデータベースを削除
        cursor.execute('DROP DATABASE IF EXISTS flask_auth_db')
        print("Cleaned up flask_auth_db")
        
        # my_flask_dbのテーブルを確認
        cursor.execute('USE my_flask_db')
        cursor.execute('SHOW TABLES')
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Current tables in my_flask_db: {tables}")
        
        # 変更を確定
        conn.commit()
        print("Database cleanup completed successfully!")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    clean_database()

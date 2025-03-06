import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def migrate_data():
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
        # 古いデータベースに接続
        old_conn = pymysql.connect(**db_config, database='my_flask_db')
        old_cursor = old_conn.cursor(pymysql.cursors.DictCursor)
        
        # 新しいデータベースに接続
        new_conn = pymysql.connect(**db_config, database='flask_auth_db')
        new_cursor = new_conn.cursor()
        
        # ユーザーデータの移行
        old_cursor.execute('SELECT * FROM user')
        users = old_cursor.fetchall()
        for user in users:
            # メールアドレスはユーザー名から生成
            email = f"{user['username']}@example.com"
            
            new_cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, phone_number, is_admin)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                username=VALUES(username),
                email=VALUES(email),
                password_hash=VALUES(password_hash),
                phone_number=VALUES(phone_number),
                is_admin=VALUES(is_admin)
            ''', (user['id'], user['username'], email, 
                  user['password_hash'], 
                  user.get('phone_number', '08015652205'), 
                  user.get('is_admin', False)))
        print("Users migrated successfully!")

        # verification_codeテーブルを作成
        new_cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_code (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                code VARCHAR(6) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                is_used TINYINT(1) DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')
        print("Verification code table created successfully!")

        # verification_codeデータの移行
        old_cursor.execute('SELECT * FROM verification_code')
        codes = old_cursor.fetchall()
        for code in codes:
            new_cursor.execute('''
                INSERT INTO verification_code (id, user_id, code, created_at, expires_at, is_used)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                user_id=VALUES(user_id),
                code=VALUES(code),
                created_at=VALUES(created_at),
                expires_at=VALUES(expires_at),
                is_used=VALUES(is_used)
            ''', (code['id'], code['user_id'], code['code'],
                  code['created_at'], code['expires_at'], code['is_used']))
        print("Verification codes migrated successfully!")
        
        # 変更を確定
        new_conn.commit()
        print("All data migrated successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        if 'new_conn' in locals():
            new_conn.rollback()
    
    finally:
        if 'old_cursor' in locals():
            old_cursor.close()
        if 'new_cursor' in locals():
            new_cursor.close()
        if 'old_conn' in locals():
            old_conn.close()
        if 'new_conn' in locals():
            new_conn.close()

if __name__ == '__main__':
    migrate_data()

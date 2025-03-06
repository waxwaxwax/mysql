import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def create_database():
    # SSL証明書のパス
    ssl_ca = os.path.abspath(os.path.join(os.path.dirname(__file__), os.getenv('MYSQL_SSL_CA')))
    
    # データベースなしで接続
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        ssl={'ca': ssl_ca}
    )
    
    try:
        with connection.cursor() as cursor:
            # データベースを作成
            cursor.execute('CREATE DATABASE IF NOT EXISTS flask_auth_db;')
            print("Database 'flask_auth_db' created successfully!")
            
            # データベースを選択
            cursor.execute('USE flask_auth_db;')
            
            # usersテーブルを作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE
                );
            ''')
            print("Table 'users' created successfully!")

            # threadsテーブルを作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threads (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    creator_id INT,
                    FOREIGN KEY (creator_id) REFERENCES users(id)
                );
            ''')
            print("Table 'threads' created successfully!")

            # messagesテーブルを作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    thread_id INT,
                    user_id INT,
                    FOREIGN KEY (thread_id) REFERENCES threads(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            ''')
            print("Table 'messages' created successfully!")
            
            # 管理者ユーザーが存在しない場合は作成
            cursor.execute("SELECT * FROM users WHERE username = 'admin';")
            if not cursor.fetchone():
                from werkzeug.security import generate_password_hash
                admin_password_hash = generate_password_hash('admin')
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, phone_number, is_admin)
                    VALUES ('admin', 'admin@example.com', %s, '08015652205', TRUE);
                ''', (admin_password_hash,))
                print("Admin user created successfully!")

                # サンプルスレッドとメッセージを作成
                cursor.execute('''
                    INSERT INTO threads (title, creator_id) 
                    SELECT 'Welcome to the Chat', id FROM users WHERE username = 'admin';
                ''')
                thread_id = cursor.lastrowid

                cursor.execute('''
                    INSERT INTO messages (content, thread_id, user_id)
                    SELECT 'Welcome to our chat system! Feel free to start conversations.', %s, id 
                    FROM users WHERE username = 'admin';
                ''', (thread_id,))
                print("Sample thread and message created successfully!")
            
        connection.commit()
        print("All database operations completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        connection.close()

if __name__ == '__main__':
    create_database()

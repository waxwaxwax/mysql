import os
from dotenv import load_dotenv
from pathlib import Path

# .env ファイルから環境変数を読み込む（既存の値を上書き）
load_dotenv(override=True)

# SSL証明書の絶対パスを取得
SSL_CA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.getenv('MYSQL_SSL_CA')))

# データベース設定
MYSQL_DB = 'my_flask_db'  # 元のデータベース名に戻す
SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{MYSQL_DB}"
    f"?ssl_ca={SSL_CA_PATH}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

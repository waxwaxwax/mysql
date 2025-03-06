import pymysql
import os
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む（既存の値を上書き）
load_dotenv(override=True)

# 環境変数の値を確認
print("環境変数の値:")
print(f"MYSQL_HOST: {os.getenv('MYSQL_HOST')}")
print(f"MYSQL_USER: {os.getenv('MYSQL_USER')}")
print(f"MYSQL_PASSWORD: {os.getenv('MYSQL_PASSWORD')}")
print(f"MYSQL_PORT: {os.getenv('MYSQL_PORT')}")
print(f"MYSQL_SSL_CA: {os.getenv('MYSQL_SSL_CA')}")

try:
    print(f"\n接続を試みます...")

    # データベースに接続
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        port=int(os.getenv('MYSQL_PORT', '3306')),
        ssl={
            'ca': os.path.abspath(os.path.join(os.path.dirname(__file__), os.getenv('MYSQL_SSL_CA')))
        }
    )

    print("データベースに接続しました！")

    # 接続を確認
    with connection.cursor() as cursor:
        # データベース一覧を表示
        cursor.execute("SHOW DATABASES")
        print("\n利用可能なデータベース:")
        for db in cursor:
            print(f"- {db[0]}")

except Exception as err:
    print("接続エラー:")
    print(err)

finally:
    if 'connection' in locals() and connection.open:
        connection.close()
        print("\nデータベース接続を閉じました")

# MySQL Database Reviewer

このアプリケーションは、MySQLデータベースの管理と監視を行うためのWebアプリケーションです。2段階認証を使用したセキュアなログイン機能と、データベーステーブルの閲覧・管理機能を提供します。

## 主な機能

- 2段階認証によるセキュアなログイン
- データベーステーブルの閲覧と管理
- 管理者向けユーザー管理機能
- キャッシュシステムによる高速なレスポンス

## 技術スタック

- **バックエンド**: Python/Flask
- **データベース**: MySQL (Azure Database for MySQL)
- **認証**: Twilio Verify API
- **キャッシュ**: Flask-Caching
- **セッション管理**: Flask-Session
- **デプロイ環境**: Azure Web Apps

## セットアップ方法

1. 必要なパッケージのインストール:
```bash
pip install -r requirements.txt
```

2. 環境変数の設定:
```env
MYSQL_HOST=your-mysql-host
MYSQL_USER=your-username
MYSQL_PASSWORD=your-password
MYSQL_DB=your-database
MYSQL_PORT=3306
MYSQL_SSL_CA=DigiCertGlobalRootCA.crt.pem

# Twilio設定
TWILIO_API_KEY_SID=your-api-key-sid
TWILIO_API_KEY_SECRET=your-api-key-secret
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_VERIFY_SERVICE_ID=your-service-id
TWILIO_VERIFY_SERVICE_NAME=your-service-name
```

3. データベースの初期化:
```bash
python create_db.py
```

4. アプリケーションの起動:
```bash
python app.py
```

## デプロイ方法 (Azure Web Apps)

1. Azureポータルでリソースを作成

2. 環境変数の設定:
```bash
az webapp config appsettings set --name your-app-name --resource-group your-resource-group --settings KEY=VALUE
```

3. デプロイ:
```bash
az webapp deployment source config-zip --resource-group your-resource-group --name your-app-name --src path/to/your/code.zip
```

## 主要な機能の説明

### ログイン認証
- 2段階認証（SMS認証）を使用
- Twilioサービスによる電話番号認証
- セッション管理による安全なユーザー認証

### データベース管理
- テーブル一覧の表示
- テーブル構造の閲覧
- データの閲覧と管理

### 管理者機能
- ユーザーの追加・削除
- ユーザー権限の管理
- システム設定の管理

## セキュリティ機能

- 2段階認証
- パスワードハッシュ化
- セッション管理
- SSL/TLS暗号化（MySQL接続）

## トラブルシューティング

データベース接続のテスト:
```bash
python test_connection.py
```

データベースのクリーンアップ:
```bash
python clean_db.py
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能改善の提案は、Issueを通じて行ってください。
# mysql

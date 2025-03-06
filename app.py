import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
from database import db, init_db
from flask_caching import Cache
from functools import wraps

# アプリケーションの初期化
app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# キャッシュの設定
app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = 'flask_cache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600  # 60分
cache = Cache(app)

# Twilioの設定
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_API_KEY_SID = os.getenv('TWILIO_API_KEY_SID')
TWILIO_API_KEY_SECRET = os.getenv('TWILIO_API_KEY_SECRET')
TWILIO_VERIFY_SERVICE_ID = os.getenv('TWILIO_VERIFY_SERVICE_ID')
TWILIO_VERIFY_SERVICE_NAME = os.getenv('TWILIO_VERIFY_SERVICE_NAME')

# Twilioクライアントの初期化
twilio_client = Client(
    TWILIO_API_KEY_SID,
    TWILIO_API_KEY_SECRET,
    TWILIO_ACCOUNT_SID
)

# データベースの初期化
init_db(app)

# ログインマネージャーの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# セッション設定
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 60分
app.config['SESSION_FILE_DIR'] = 'flask_session'
app.config['SESSION_FILE_THRESHOLD'] = 500  # セッションファイルの最大数
Session(app)

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()

def send_verification_code(phone_number, code):
    try:
        # 国際電話番号形式に変換（日本の場合）
        if phone_number.startswith('0'):
            phone_number = '+81' + phone_number[1:]
        elif not phone_number.startswith('+'):
            phone_number = '+81' + phone_number

        # 認証コードを送信
        verification = twilio_client.verify \
            .v2 \
            .services(TWILIO_VERIFY_SERVICE_ID) \
            .verifications \
            .create(to=phone_number, channel='sms')
        
        logger.info(f"Verification sent: {verification.status}")
        return True
    except TwilioRestException as e:
        logger.error(f"Failed to send verification: {str(e)}")
        return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # セッションを永続化
            session.permanent = True
            
            # 最後の認証時刻をキャッシュ
            last_auth_key = f'last_auth_{user.id}'
            last_auth = cache.get(last_auth_key)
            
            if last_auth and (datetime.now() - last_auth).total_seconds() < 3600:
                # 60分以内に認証済みの場合、SMS認証をスキップ
                login_user(user)
                return redirect(url_for('index'))
            
            # 認証コードを生成
            verification_code = VerificationCode(
                user_id=user.id,
                code=VerificationCode.generate_code(),
                expires_at=datetime.now() + timedelta(minutes=10)
            )
            db.session.add(verification_code)
            db.session.commit()
            
            # 認証コードを送信
            if send_verification_code(user.phone_number, verification_code.code):
                session['user_id'] = user.id
                session['verification_code'] = verification_code.code
                return redirect(url_for('verify'))
            else:
                db.session.delete(verification_code)
                db.session.commit()
                return redirect(url_for('login'))

        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        code = request.form['code']
        stored_code = session.get('verification_code')

        # 国際電話番号形式に変換
        phone_number = user.phone_number
        if phone_number.startswith('0'):
            phone_number = '+81' + phone_number[1:]
        elif not phone_number.startswith('+'):
            phone_number = '+81' + phone_number

        try:
            # Twilioで認証コードを検証
            verification_check = twilio_client.verify \
                .v2 \
                .services(TWILIO_VERIFY_SERVICE_ID) \
                .verification_checks \
                .create(to=phone_number, code=code)

            if verification_check.status == 'approved':
                # 認証成功時に最後の認証時刻をキャッシュ
                last_auth_key = f'last_auth_{user.id}'
                cache.set(last_auth_key, datetime.now())
                
                login_user(user)
                session.pop('verification_code', None)
                return redirect(url_for('index'))
            else:
                return redirect(url_for('verify'))
        except TwilioRestException as e:
            logger.error(f"Verification check failed: {str(e)}")
            return redirect(url_for('verify'))

    return render_template('verify.html')

@app.route('/resend-code')
def resend_code():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return redirect(url_for('login'))

    if send_verification_code(user.phone_number, None):
        return redirect(url_for('verify'))
    else:
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/tables')
@login_required
def get_tables():
    try:
        cursor = db.session.connection().connection.cursor()
        
        # データベース一覧を取得
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        result = {}
        for db_name in databases:
            db_name = db_name[0]
            if db_name not in ['information_schema', 'performance_schema', 'mysql', 'sys']:
                try:
                    # データベースを選択
                    cursor.execute(f"USE {db_name}")
                    
                    # テーブル一覧を取得
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    
                    db_info = {'tables': {}}
                    
                    for table in tables:
                        table_name = table[0]
                        try:
                            # テーブルの列情報を取得
                            cursor.execute(f"DESCRIBE {table_name}")
                            columns = [column[0] for column in cursor.fetchall()]
                            
                            # テーブルのデータを取得
                            cursor.execute(f"SELECT * FROM {table_name}")
                            rows = cursor.fetchall()
                            
                            # 行データを辞書形式に変換
                            table_data = []
                            for row in rows:
                                row_dict = {}
                                for i, column in enumerate(columns):
                                    row_dict[column] = str(row[i]) if row[i] is not None else None
                                table_data.append(row_dict)
                            
                            db_info['tables'][table_name] = {
                                'columns': columns,
                                'rows': table_data
                            }
                        except Exception as e:
                            db_info['tables'][table_name] = {'error': str(e)}
                    
                    result[db_name] = db_info
                except Exception as e:
                    result[db_name] = {'error': str(e)}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/admin/add_user', methods=['POST'])
@login_required
@admin_required
def admin_add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    phone_number = request.form.get('phone_number')
    is_admin = request.form.get('is_admin') == 'on'

    if not username or not password or not phone_number:
        return redirect(url_for('admin'))

    # 電話番号を国際形式に変換
    if phone_number.startswith('0'):
        phone_number = '+81' + phone_number[1:]
    elif not phone_number.startswith('+'):
        phone_number = '+81' + phone_number

    # 既存ユーザーチェック
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return redirect(url_for('admin'))

    # 新規ユーザー作成
    new_user = User(
        username=username,
        phone_number=phone_number,
        is_admin=is_admin
    )
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create user: {str(e)}")

    return redirect(url_for('admin'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get(user_id)
    if user and user.id != current_user.id:  # 自分自身は削除できない
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete user: {str(e)}")

    return redirect(url_for('admin'))

@app.route('/admin')
@login_required
@admin_required
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

# モデルのインポート
from models import User, VerificationCode

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

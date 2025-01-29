from flask import Flask
# dbモデル
from flask_app.models import db
# ルーティングファイル
from flask_app.routes.auth import auth_bp
from flask_app.routes.music import music_bp

def create_app():
    app = Flask(__name__)

    #SQLite3を使うように、MySQL等ならIPアドレス等を記述
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'
    #セッション利用に秘密鍵が必要
    app.config['SECRET_KEY'] = 'dev'

    db.init_app(app)
    #ルーティングファイルをエンドポイントとして登録
    app.register_blueprint(auth_bp)
    app.register_blueprint(music_bp)

    return app

app = create_app()

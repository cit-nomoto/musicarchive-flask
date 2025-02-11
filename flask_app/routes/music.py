import os
from flask import current_app, Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_app.models import db, Music
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename


music_bp = Blueprint('music', __name__)

def login_required(f):
    """ログインを必須にする"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
@music_bp.route('/recorder', methods=['GET', 'POST'])
@login_required #ログイン状態でないとアクセス不可にする
def recorder():
    """楽曲の登録を行う"""
    if request.method == 'POST':
        song_name = request.form.get('song_name')
        artist_name = request.form.get('artist_name')
        category = request.form.get('category')
        music_file = request.files['music_file']
        
        if music_file and allowed_file(music_file.filename):
          filename=secure_filename(music_file.filename)
          file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
          music_file.save(file_path)

        music = Music(
            song_name=song_name,
            artist_name=artist_name,
            category=category,
            music_file_path=file_path,
            music_user_id=session['user_id']
        )

        try:
            db.session.add(music)
            db.session.commit()
            flash('楽曲が正常に登録されました','success')
            return redirect(url_for('music.list'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'データベースエラーが発生しました: {str(e)}', 'error')
        
        finally:
            db.session.close()

    return render_template('recorder.html')

@music_bp.route('/list', methods=['GET', 'POST'])
@login_required #ログイン済でないとアクセス不可にする
def list(): #listは組み込みの再定義になってしまうが、PHP版に準拠
    """楽曲の一覧を表示する"""
    user_id = session['user_id']
    musics = []
    
    if request.method == 'POST':
        music_id = request.form.get('music_id')
        if not music_id:
            flash('削除する楽曲を選択してください','error')
            return redirect(url_for('music.list'))
        try:
            music = Music.query.filter_by(id=music_id, music_user_id=user_id).first()
            if not music:
                flash('楽曲が1件も登録されていません','error')
                return redirect(url_for('music.list'))

            db.session.delete(music)
            db.session.commit()
            flash('楽曲が正常に削除されました','success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'データベースエラーが発生しました: {str(e)}', 'error')

    try:
        musics = Music.query.filter_by(music_user_id=user_id).all()
        
    
    except SQLAlchemyError as e:
        flash(f'データベースエラーが発生しました: {str(e)}', 'error')
    
    finally:
        db.session.close()

    #値やリストを付加した状態でHTMLのレンダリング（HTML側で利用可能）
    return render_template('list.html', musics=musics, login_user_id=user_id)

@music_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
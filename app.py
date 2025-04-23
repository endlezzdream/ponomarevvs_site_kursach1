from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(150), unique=True)
  password = db.Column(db.String(200))

class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/')
def index():
  posts = Post.query.order_by(Post.id.desc()).all()
  return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    user = User(username=request.form['username'], password=generate_password_hash(request.form['password']))
    db.session.add(user)
    db.session.commit()
    return redirect('/login')
  return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    user = User.query.filter_by(username=request.form['username']).first()
    if user and check_password_hash(user.password, request.form['password']):
      session['user_id'] = user.id
      return redirect('/')
  return render_template('login.html')

@app.route('/logout')
def logout():
  session.pop('user_id', None)
  return redirect('/')

@app.route('/create_post', methods=['POST'])
def create_post():
  if 'user_id' in session:
    post = Post(content=request.form['content'], user_id=session['user_id'])
    db.session.add(post)
    db.session.commit()
  return redirect('/')


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.id.desc()).all()
    return render_template('profile.html', username=user.username, posts=posts)

@app.route('/delete_post', methods=['POST'])
def delete_post():
    if 'user_id' not in session:
        return redirect('/login')
    post = Post.query.get(request.form['post_id'])
    if post and post.user_id == session['user_id']:
        db.session.delete(post)
        db.session.commit()
    return redirect('/profile')

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    Post.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    session.clear()
    return redirect('/')



@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    if 'user_id' not in session:
        return redirect('/login')
    comment = Comment.query.get(request.form['comment_id'])
    if comment and comment.user_id == session['user_id']:
        db.session.delete(comment)
        db.session.commit()
    return redirect('/')


if __name__ == '__main__':
  with app.app_context():
    db.create_all()
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
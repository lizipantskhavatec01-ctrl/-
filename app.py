from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,current_user
import os

app = Flask(__name__)

# კონფიგურაცია
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# მოდელები
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ბაზის შექმნა
with app.app_context():
    db.create_all()

# მარშრუტები (Routes)
@app.route('/')
@app.route('/home')
def home():
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('ეს იმეილი უკვე დაკავებულია!', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        flash('არასწორი სახელი ან პაროლი!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
@login_required
def profile():
    # აქ Subject-ის მოდელი უნდა გვქონდეს
    user_subjects = Subject.query.all()
    return render_template('profile.html', subjects=user_subjects)

@app.route('/admin')
@login_required
def admin():
    if current_user.username != 'admin':
        flash('ამ გვერდზე წვდომა მხოლოდ ადმინს აქვს!', 'danger')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin.html', users=users)


@app.route('/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        new_subject = Subject(name=name)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('add_subject.html')

if __name__ == '__main__':
    app.run(debug=True)
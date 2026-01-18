import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    subjects = db.relationship('Subject', backref='author', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)

@app.route('/about') # ეს ფუნქცია აკლდა და იწვევდა BuildError-ს
def about():
    return render_template('about.html')

@app.route('/profile')
@login_required
def profile():
    # მხოლოდ მიმდინარე მომხმარებლის მასალები
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', subjects=subjects)

@app.route('/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    if request.method == 'POST':
        title = request.form.get('title')
        file = request.files.get('file')
        if file and title:
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # შეცვალე ეს ხაზი:
            new_sub = Subject(title=title, image_file=filename, user_id=current_user.id)
            db.session.add(new_sub)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('add_subject.html')

@app.route('/delete_subject/<int:id>')
@login_required
def delete_subject(id):
    if current_user.username == 'admin':
        subject = Subject.query.get_or_404(id)
        db.session.delete(subject)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
    if current_user.username != 'admin':
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            login_user(user)
            return redirect(url_for('profile'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # თუ პაროლი 3 სიმბოლოზე მეტია, არ გაატაროს
        if len(password) > 3:
            flash('პაროლი არ უნდა აღემატებოდეს 3 სიმბოლოს!', 'danger')
            return redirect(url_for('register'))

        if not User.query.filter_by(username=username).first():
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
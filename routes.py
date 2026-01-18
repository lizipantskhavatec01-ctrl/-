from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from ext import db
from models import User, Subject
# აუცილებლად ეს იმპორტი
from app import app


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
    user_subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', subjects=user_subjects)
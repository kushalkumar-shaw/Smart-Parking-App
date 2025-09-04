from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        
        flash('Wrong username or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        address = request.form['address']
        pin_code = request.form['pin_code']

        if User.query.filter_by(username=username).first():
            flash('Username taken.', 'danger')
        else:
            new_user = User(
                username=username,
                password=generate_password_hash(password),
                full_name=full_name,
                address=address,
                pin_code=pin_code
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registered. You can log in now.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

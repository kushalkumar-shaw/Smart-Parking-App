from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models.models import db, User
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp
from werkzeug.security import generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gzth3r3s3cr3tk3y'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')

@app.route('/')
def index():
    return render_template('index.html')

def create_admin_user():
    existing_admin = User.query.filter_by(is_admin=True).first()
    if not existing_admin:
        new_admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            is_admin=True,
            full_name='System Admin',
            address='Admin Office, Main Campus',
            pin_code='123456'
        )
        db.session.add(new_admin)
        db.session.commit()
        print("Admin created successfully.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    app.run(debug=True)

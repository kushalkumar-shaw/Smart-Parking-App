from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models.models import db, User, ParkingLot, ParkingSpot
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp
from werkzeug.security import generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gzth3r3s3cr3tk3y'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_MAPS_API_KEY'] = 'AIzaSyA0H5SzwC0e3vlQglnCY9neAQfhVPzFHYs'  # Replace with your actual API key

db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/parking-lots')
def get_parking_lots():
    """API endpoint to return parking lot data with GPS coordinates for map view"""
    lots = ParkingLot.query.all()
    lots_data = []
    
    for lot in lots:
        available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
        lots_data.append({
            'id': lot.id,
            'name': lot.prime_location_name,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'price': lot.price,
            'latitude': lot.latitude,
            'longitude': lot.longitude,
            'total_spots': lot.maximum_number_of_spots,
            'available_spots': available_spots
        })
    
    return jsonify({'lots': lots_data})

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
    app.run(host='0.0.0.0', debug=True)

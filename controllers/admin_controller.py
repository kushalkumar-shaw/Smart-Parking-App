from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models.models import db, ParkingLot, ParkingSpot, User, Reservation

admin_bp = Blueprint('admin', __name__)

def admin_required():
    return session.get('is_admin', False)

@admin_bp.route('/dashboard')
def dashboard():
    if not admin_required():
        return redirect(url_for('auth.login'))
    
    lots = ParkingLot.query.all()
    users = User.query.filter_by(is_admin=False).all()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    
    return render_template('admin/admin_dashboard.html', 
                           lots=lots, users=users, 
                           total_spots=total_spots, 
                           occupied_spots=occupied_spots)

@admin_bp.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if not admin_required():
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        lot = ParkingLot(
            prime_location_name=request.form['location'],
            price=float(request.form['price']),
            address=request.form['address'],
            pin_code=request.form['pin_code'],
            latitude=float(request.form['latitude']) if request.form.get('latitude') else None,
            longitude=float(request.form['longitude']) if request.form.get('longitude') else None,
            maximum_number_of_spots=int(request.form['spots'])
        )
        db.session.add(lot)
        db.session.commit()

        for _ in range(lot.maximum_number_of_spots):
            db.session.add(ParkingSpot(lot_id=lot.id))
        db.session.commit()
        
        flash('New lot added.', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/add_lot.html', 
                         google_maps_api_key=current_app.config.get('GOOGLE_MAPS_API_KEY'))

@admin_bp.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if not admin_required():
        return redirect(url_for('auth.login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        lot.prime_location_name = request.form['location']
        lot.price = float(request.form['price'])
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.latitude = float(request.form['latitude']) if request.form.get('latitude') else None
        lot.longitude = float(request.form['longitude']) if request.form.get('longitude') else None
        new_total = int(request.form['spots'])
        
        if new_total > lot.maximum_number_of_spots:
            for _ in range(new_total - lot.maximum_number_of_spots):
                db.session.add(ParkingSpot(lot_id=lot.id))
        elif new_total < lot.maximum_number_of_spots:
            to_remove = new_total - lot.maximum_number_of_spots
            free_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(abs(to_remove)).all()
            for spot in free_spots:
                db.session.delete(spot)
        
        lot.maximum_number_of_spots = new_total
        db.session.commit()
        flash('Lot updated.', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_lot.html', lot=lot,
                         google_maps_api_key=current_app.config.get('GOOGLE_MAPS_API_KEY'))

@admin_bp.route('/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    lot = ParkingLot.query.get_or_404(lot_id)

    spot_ids = [spot.id for spot in lot.spots]
    has_reservations = Reservation.query.filter(Reservation.spot_id.in_(spot_ids)).count()

    if has_reservations > 0:
        flash('Lot has existing reservations.', 'danger')
        return redirect(url_for('admin.dashboard'))

    for spot in lot.spots:
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()
    flash('Lot deleted.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/view_spots/<int:lot_id>')
def view_spots(lot_id):
    if not admin_required():
        return redirect(url_for('auth.login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    
    spot_data = []
    for spot in spots:
        reservation = Reservation.query.filter_by(spot_id=spot.id, is_active=True).first()
        spot_data.append({
            'spot': spot,
            'reservation': reservation
        })
    
    return render_template('admin/view_spots.html', lot=lot, spot_details=spot_data)

@admin_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not admin_required():
        return redirect(url_for('auth.login'))

    admin = User.query.filter_by(is_admin=True).first()

    if request.method == 'POST':
        admin.full_name = request.form['full_name']
        admin.username = request.form['username']
        admin.address = request.form['address']
        admin.pin_code = request.form['pin_code']
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_profile.html', admin=admin)

@admin_bp.route('/users')
def view_users():
    if not admin_required():
        return redirect(url_for('auth.login'))

    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/summary')
def admin_summary():
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))

    total_users = User.query.filter_by(is_admin=False).count()
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied = ParkingSpot.query.filter_by(status='O').count()
    total_reservations = Reservation.query.count()

    data = db.session.query(Reservation, ParkingLot)\
        .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)\
        .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id)\
        .filter(Reservation.is_active == False)\
        .all()

    revenue = 0
    for reservation, lot in data:
        if reservation.parking_cost:
            revenue += reservation.parking_cost
        elif reservation.parking_timestamp and reservation.leaving_timestamp:
            diff = reservation.leaving_timestamp - reservation.parking_timestamp
            hours = max(diff.total_seconds() / 3600, 1)
            revenue += lot.price * hours

    return render_template("admin/summary.html",
                           total_users=total_users,
                           total_lots=total_lots,
                           total_spots=total_spots,
                           occupied_spots=occupied,
                           total_reservations=total_reservations,
                           total_revenue=round(revenue, 2))

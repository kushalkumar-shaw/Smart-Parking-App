from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from models.models import db, ParkingLot, ParkingSpot, Reservation, User
from datetime import datetime

user_bp = Blueprint('user', __name__)

def user_required():
    return 'user_id' in session and not session.get('is_admin', False)

@user_bp.route('/dashboard')
def dashboard():
    if not user_required():
        return redirect(url_for('auth.login'))

    lots = ParkingLot.query.all()
    active = Reservation.query.filter_by(user_id=session['user_id'], is_active=True).all()
    past = Reservation.query.filter_by(user_id=session['user_id'], is_active=False).all()
    user = User.query.get(session['user_id'])

    return render_template(
        'user/user_dashboard.html',
        lots=lots,
        active_reservations=active,
        past_reservations=past,
        user=user,
        google_maps_api_key=current_app.config.get('GOOGLE_MAPS_API_KEY')
    )

@user_bp.route('/map')
def map_view():
    if not user_required():
        return redirect(url_for('auth.login'))
    
    active = Reservation.query.filter_by(user_id=session['user_id'], is_active=True).all()
    return render_template('user/map_view.html', 
                         active_reservations=active,
                         google_maps_api_key=current_app.config.get('GOOGLE_MAPS_API_KEY'))

@user_bp.route('/book_spot/<int:lot_id>')
def book_spot(lot_id):
    if not user_required():
        return redirect(url_for('auth.login'))

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

    if not spot:
        flash('Lot full. Try another.', 'danger')
        return redirect(url_for('user.dashboard'))

    existing = Reservation.query.filter_by(user_id=session['user_id'], is_active=True).first()
    if existing:
        flash('You already have a booking.', 'warning')
        return redirect(url_for('user.dashboard'))

    reservation = Reservation(
        spot_id=spot.id,
        user_id=session['user_id'],
        parking_timestamp=datetime.utcnow()
    )
    spot.status = 'O'

    db.session.add(reservation)
    db.session.commit()

    flash('Spot booked.', 'success')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/release_spot/<int:reservation_id>')
def release_spot(reservation_id):
    if not user_required():
        return redirect(url_for('auth.login'))

    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != session['user_id']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('user.dashboard'))

    if reservation.parking_timestamp:
        duration = datetime.utcnow() - reservation.parking_timestamp
        hours = duration.total_seconds() / 3600
        lot = ParkingLot.query.get(reservation.spot.lot_id)
        cost = hours * lot.price

        reservation.leaving_timestamp = datetime.utcnow()
        reservation.parking_cost = round(cost, 2)
        reservation.is_active = False
        reservation.spot.status = 'A'

        db.session.commit()
        flash(f'Spot released. ₹{reservation.parking_cost:.2f} charged.', 'success')

    return redirect(url_for('user.dashboard'))

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Login required.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)

    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.username = request.form['username']
        user.address = request.form['address']
        user.pin_code = request.form['pin_code']
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for('user.dashboard'))

    return render_template('user/edit_profile.html', user=user)

@user_bp.route('/summary')
def summary():
    if not user_required():
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    reservations = Reservation.query.filter_by(user_id=user_id).all()

    total_bookings = len(reservations)
    total_hours = 0
    total_cost = 0
    date_wise_data = {}

    for res in reservations:
        if res.parking_timestamp and res.leaving_timestamp:
            duration = res.leaving_timestamp - res.parking_timestamp
            hours = duration.total_seconds() / 3600
            total_hours += hours
            total_cost += res.parking_cost or 0

            date = res.parking_timestamp.date().isoformat()
            if date not in date_wise_data:
                date_wise_data[date] = 0
            date_wise_data[date] += hours

    return render_template('user/user_summary.html',
                           total_bookings=total_bookings,
                           total_hours=round(total_hours, 2),
                           total_cost=round(total_cost, 2),
                           date_labels=list(date_wise_data.keys()),
                           hours_data=list(date_wise_data.values()))

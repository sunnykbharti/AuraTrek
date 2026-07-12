from flask import Blueprint, request, jsonify, current_app
from models import db, Users, Treks, TrekApplications, Trekker
import jwt
from datetime import datetime
from extension import cache

user_bp = Blueprint('user', __name__)

# Authentication Decorator for User-only access
def user_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "No token present"}), 401
        
        try:
            if "Bearer" in token:
                token = token.split(" ")[1]
            
            # Fixed: Removed the global keyword to keep it safe for concurrent requests
            decoded_data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])

            if decoded_data.get('role') != 'trekker':
                return jsonify({"message": "User Access only"}), 403
            
            request.user_id = decoded_data.get('user.id')
            request.user_email = decoded_data.get('name')
        except Exception as e:
            return jsonify({"message": "Invalid token or token is expired!"}), 401
        
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

# Fetching & Updating User Profile
# Fixed: Added 'PUT' method to the route array wrap
@user_bp.route('/api/user/profile', methods=['GET', 'PUT'])
@user_required
def handle_profile():
    profile = Trekker.query.filter_by(u_email=request.user_email).first()

    if request.method == 'GET':
        if not profile:
            return jsonify({"name": "", "phone": "", "age": "", "city": ""}), 200
        
        return jsonify({
            "name": profile.u_name,
            "phone": profile.u_phone,
            "age": profile.u_age,
            "city": profile.u_city
        }), 200
    
    if request.method == "PUT":
        data = request.get_json()
        try:
            # Fixed: Added structural safety pattern if a new profile doesn't exist yet
            if not profile:
                profile = Trekker(
                    u_id=request.user_id,
                    u_name=data.get('name', ''),
                    u_phone=int(data.get('phone', 0)) if data.get('phone') else 0,
                    u_email=request.user_email,
                    u_age=int(data.get('age', 0)) if data.get('age') else 0,
                    u_city=data.get('city', '')
                )
                db.session.add(profile)
            else:
                profile.u_name = data.get('name', profile.u_name)
                profile.u_phone = int(data.get('phone', profile.u_phone)) if data.get('phone') else profile.u_phone
                profile.u_age = int(data.get('age', profile.u_age)) if data.get('age') else profile.u_age
                profile.u_city = data.get('city', profile.u_city)
            
            db.session.commit()
            return jsonify({"message": "Profile updated successfully!"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Profile update failed: {str(e)}"}), 500

# Book slot for a trek
@user_bp.route('/api/user/book/<int:trek_id>', methods=['POST'])
@user_required
def book_trek(trek_id):
    try:
        trek = Treks.query.get(trek_id)
        if not trek:
            return jsonify({"message": "Trek route not found"}), 404
        
        if trek.t_slots <= 0:
            return jsonify({"message": "No slots remaining on this trail!"}), 400
        
        # Check for pre-existing application 
        existing_application = TrekApplications.query.filter_by(u_id=request.user_id, s_id=trek.t_id).first()
        if existing_application:
            return jsonify({"message": "Already Applied for this route"}), 400
        
        # Creating new application in db
        new_application = TrekApplications(
            s_id=trek.t_id,
            u_id=request.user_id,
            a_date=datetime.now(),
            a_status="applied"
        )

        # Updating slot count
        trek.t_slots -= 1

        db.session.add(new_application)
        db.session.commit()

        from routes.admin import get_treks_cached
        cache.delete_memoized(get_treks_cached)

        return jsonify({"message": "Your slot is successfully booked"}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Booking failed: {str(e)}"}), 500

# Get Booking History Logs
@user_bp.route('/api/user/bookings', methods=['GET'])
@user_required
def get_my_bookings():
    try:
        applications = db.session.query(TrekApplications, Treks).\
            join(Treks, TrekApplications.s_id == Treks.t_id).\
            filter(TrekApplications.u_id == request.user_id).all()
        
        history_data = []
        for app, trek in applications:
            history_data.append({
                "a_id": app.a_id,
                "trek_name": trek.t_name,
                "date_applied": app.a_date.strftime('%Y-%m-%d %H:%M') if app.a_date else "Recent",
                "status": app.a_status
            })

        return jsonify(history_data), 200
    except Exception as e:
        return jsonify({"message": f"Server processing error: {str(e)}"}), 500

# User Triggered Async Job: Export Booking History as CSV
@user_bp.route('/api/user/export-history', methods=['GET','POST'])
@user_required
def trigger_history_export():
    try : 
        from tasks import export_booking_history_csv

        # Triggers task cleanly through Celery context stack
        export_booking_history_csv.delay(request.user_id, request.user_email)

        return jsonify({
            "message": "CSV Compilation Batch Job triggered successfully!"
        }), 202
    except Exception as e:
        return jsonify({"message": f"Server processing error: {str(e)}"}), 500
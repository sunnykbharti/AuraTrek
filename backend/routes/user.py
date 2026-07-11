from flask import Blueprint, request, jsonify, current_app
from models import db, Users, Treks, TrekApplications, Trekker
import jwt
from datetime import datetime

user_bp = Blueprint('user', __name__)

# Authentication Decorator for USer only access
def user_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "No token present"}), 401
        
        try:
            if "Bearer" in token:
                token = token.split(" ")[1]
            global data
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])

            if data.get('role') != 'trekker':
                return jsonify({"message": "User Access only"}), 403
            
            request.user_id = data.get('user.id')
            request.user_email = data.get('name')
        except Exception as e:
            return jsonify({"message": "Invalid token or token is expired!"}), 401
        
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated
# fetching user profile
@user_bp.route('/api/user/profile', methods=['GET', 'POST'])
@user_required
def handle_profile():
    profile = Trekker.query.filter_by(u_email=request.user_email).first()

    if request.method == 'GET':
        if not profile :
            return jsonify({"name" : "", "phone" : "", "age" : "", "city" : ""}), 200
        
        return jsonify({
            "name" : profile.u_name,
            "phone" : profile.u_phone,
            "age" : profile.u_age,
            "city" : profile.u_city
        }), 200
    
    if request.method == "PUT":
        data =request.get_json()
        try:
            profile.u_name = data.get('name', profile.u_name)
            profile.u_phone = int(data.get('phone', profile.u_phone))
            profile.u_age = int(data.get('age', profile.u_age))
            profile.u_city = data.get('city', profile.u_city)
            
            db.session.commit()
            return jsonify({"message" : "Profile updated!"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"message" : f"Profile update failed: {str(e)}"}), 500

# Book slot for a trek
@user_bp.route('/api/user/book/<int:trek_id>', methods=['POST'])
@user_required
def book_trek(trek_id):
    try:
        trek = Treks.query.get(trek_id)
        if not trek:
            return jsonify({"message" : "Trek route not found"}), 404
        
        if trek.t_slots <=0:
            return jsonify({"message" : "No slots remaining on this trail!"}), 400
        
        # Check for pre-existing application 
        existing_application = TrekApplications.query.filter_by(u_id=request.user_id, s_id=trek.t_id).first()
        if existing_application:
            return jsonify({"message" : "Already Applied for this route"}), 400
        
        # creating new apication in db
        new_application = TrekApplications(
            s_id = trek.t_id,
            u_id = request.user_id,
            a_date = datetime.now(),
            a_status="applied"
        )

        # updating slot count
        trek.t_slots -= 1

        db.session.add(new_application)
        db.session.commit()
        return jsonify({"message" : "Your slot is successfully booked"}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message" : f"Booking failed :{str(e)}"}), 500

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
                "a_id" : app.a_id,
                "trek_name" : trek.t_name,
                "date_applied" : app.a_date.strftime('%Y-%m-%d %H:%M'),
                "status" : app.a_status
            })

        return jsonify(history_data), 200
    except Exception as e:
        return jsonify({"message" : f"Server processing error : {str(e)}"}), 500
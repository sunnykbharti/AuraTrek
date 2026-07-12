from flask import Blueprint, request, jsonify, current_app
from models import db, Users, Treks
import jwt

staff_bp = Blueprint('staff', __name__)

# Authentication Decorator for staff only access
def staff_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "No token present"}), 401
        
        try:
            if "Bearer" in token:
                token = token.split(" ")[1]
            global data
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])

            if data.get('role') != 'staff':
                return jsonify({"message": "Staff Access only"}), 403
        except Exception as e:
            return jsonify({"message": "Invalid token or token is expired!"}), 401
        
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@staff_bp.route('/api/staff/treks', methods=['GET'])
@staff_required
def staff_treks():
    try:
        #pulling all thge assigned treks to the staff member
        assigned_trek =Treks.query.filter_by(t_staff=data.get('user_id')).all()

        treks_data = [{
            "t_id": t.t_id,
            "t_name": t.t_name,
            "t_location": t.t_location,
            "t_difficulty": t.t_difficulty,
            "t_duration": t.t_duration,
            "t_slots": t.t_slots
        } for t in assigned_trek]

        return jsonify(treks_data), 200
    except Exception as e:
        return jsonify({"message" : f"Token invalid or server error: {str(e)}"}), 401
    
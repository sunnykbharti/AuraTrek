from flask import Blueprint, request, jsonify, current_app
from models import db, Users, Treks
import jwt

admin_bp = Blueprint('admin', __name__)

# Authentication Decorator
def admin_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        
        try:
            if "Bearer" in token:
                token = token.split(" ")[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])

            if data.get('role') != 'admin':
                return jsonify({"message": "Access Denied"}), 403
        except Exception as e:
            return jsonify({"message": "Invalid token or token is expired!"}), 401
        
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

# 1. Main Stats Dashboard Metrics
@admin_bp.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    try:
        total_trekkers = Users.query.filter_by(u_role='trekker').count()
        total_staff = Users.query.filter_by(u_role='staff').count()
        
        return jsonify({
            "app_data": {
                "totalTrekkers": total_trekkers,
                "totalStaff": total_staff
            },
            "message": "Dashboard data fetched"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500

# 2. Get All User/Staff Accounts
@admin_bp.route('/api/admin/accounts', methods=['GET'])
@admin_required
def get_accounts():
    try:
        users = Users.query.filter(Users.u_role != 'admin').all()
        accounts_data = [{
            "u_id": u.u_id,
            "username": u.username,
            "u_role": u.u_role,
            "u_status": u.u_status.lower()
        } for u in users]
        return jsonify(accounts_data), 200
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

# 3. Toggle Account Status (Activate / Blacklist)
@admin_bp.route('/api/admin/accounts/toggle/<int:user_id>', methods=['POST'])
@admin_required
def toggle_account_status(user_id):
    try:
        user = Users.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Simple flip switch validation
        if user.u_status.lower() == 'active':
            user.u_status = 'inactive'
        else:
            user.u_status = 'active'
            
        db.session.commit()
        return jsonify({"message": f"User status updated to {user.u_status}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Server error: {str(e)}"}), 500

# 4. Get & Create Trek Routes (CRUD - Get & Post)
@admin_bp.route('/api/admin/treks', methods=['GET', 'POST'])
@admin_required
def handle_treks():
    if request.method == 'GET':
        try:
            treks = Treks.query.all()
            treks_data = [{
                "t_id": t.t_id,
                "t_name": t.t_name,
                "t_location": t.t_location,
                "t_difficulty": t.t_difficulty,
                "t_duration": t.t_duration,
                "t_slots": t.t_slots,
                "t_staff": t.t_staff
            } for t in treks]
            return jsonify(treks_data), 200
        except Exception as e:
            return jsonify({"message": f"Server error: {str(e)}"}), 500

    if request.method == 'POST':
        data = request.get_json()
        try:
            new_trek = Treks(
                t_name=data.get('t_name'),
                t_location=data.get('t_location'),
                t_difficulty=data.get('t_difficulty', 'Easy'),
                t_duration=int(data.get('t_duration', 1)),
                t_slots=int(data.get('t_slots', 10))
            )
            db.session.add(new_trek)
            db.session.commit()
            return jsonify({"message": "New Trek Route Created Successfully!"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Failed to create route: {str(e)}"}), 500

# 5. Update & Delete Specific Trek Route (CRUD - Put & Delete)
@admin_bp.route('/api/admin/treks/<int:trek_id>', methods=['PUT', 'DELETE'])
@admin_required
def modify_trek(trek_id):
    trek = Treks.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek route not found"}), 404

    if request.method == 'PUT':
        data = request.get_json()
        try:
            trek.t_name = data.get('t_name', trek.t_name)
            trek.t_location = data.get('t_location', trek.t_location)
            trek.t_difficulty = data.get('t_difficulty', trek.t_difficulty)
            trek.t_duration = int(data.get('t_duration', trek.t_duration))
            trek.t_slots = int(data.get('t_slots', trek.t_slots))
            trek.t_staff = data.get('t_staff') # <--- Explicitly handle staff assignment updates
            
            db.session.commit()
            return jsonify({"message": "Trek route details modified successfully!"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Update failed: {str(e)}"}), 500

    if request.method == 'DELETE':
        try:
            db.session.delete(trek)
            db.session.commit()
            return jsonify({"message": "Trek route deleted completely"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Deletion failed: {str(e)}"}), 500

# 6. Admin Action: Directly Register a New Staff Member
@admin_bp.route('/api/admin/staff/register', methods=['POST'])
@admin_required
def register_staff_member():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and temporary password are required!"}), 400

    try:
        # Check if user already exists
        existing_user = Users.query.filter_by(username=email).first()
        if existing_user:
            return jsonify({"message": "An account with this email already exists!"}), 400

        from werkzeug.security import generate_password_hash
        # Create user entry
        new_staff_user = Users(
            username=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            u_role="staff",
            u_status="active"
        )
        
        db.session.add(new_staff_user)
        db.session.commit()
        return jsonify({"message": f"Staff account {email} registered successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500
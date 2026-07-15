from functools import wraps
from flask import Blueprint, request, jsonify, current_app, g
from models import db, Treks, TrekApplications, Users
import jwt
from extension import cache

staff_bp = Blueprint('staff_api', __name__)

def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            if "Bearer" in token:
                token = token.split(" ")[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])

            if data.get('role') != 'staff':
                return jsonify({"message": "Staff Access only"}), 403

            staff_id = data.get('user.id')
            if not staff_id:
                return jsonify({"message": "Invalid token payload"}), 401

            g.staff_id = staff_id
        except Exception:
            return jsonify({"message": "Invalid token or token is expired!"}), 401

        return f(*args, **kwargs)
    return decorated


# 1. Fetch assigned treks along with dynamic participant registration numbers
@staff_bp.route('/api/staff/treks', methods=['GET'])
@staff_required
def get_assigned_treks():
    try:
        # Fetch treks explicitly assigned to this staff member
        treks = Treks.query.filter_by(t_staff=g.staff_id).all()

        treks_data = []
        for t in treks:
            # Dynamically count valid registered users for this trek
            registered_count = TrekApplications.query.filter_by(t_id=t.t_id).count()

            treks_data.append({
                "t_id": t.t_id,
                "t_name": t.t_name,
                "t_location": t.t_location,
                "t_difficulty": t.t_difficulty,
                "t_duration": t.t_duration,
                "t_slots": t.t_slots,
                "t_status": t.t_status,
                "registered_users": registered_count
            })
        return jsonify(treks_data), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500

# 2. Update slots, status
@staff_bp.route('/api/staff/treks/<int:trek_id>', methods=['PUT'])
@staff_required
def update_trek_details(trek_id):
    trek = Treks.query.filter_by(t_id=trek_id, t_staff=g.staff_id).first()
    if not trek:
        return jsonify({"message": "Trek not found or unauthorized"}), 404

    data = request.get_json()
    try:
        if 't_slots' in data:
            trek.t_slots = int(data.get('t_slots'))
        if 't_status' in data:
            trek.t_status = data.get('t_status')

        db.session.commit()

        # Evict the general cache so admins and trekåkers see the new counts/states instantly
        cache.delete('all_treks_data')
        return jsonify({"message": "Trek updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Update failed: {str(e)}"}), 500

# 3. View and manage participant list for a specific trek
@staff_bp.route('/api/staff/treks/<int:trek_id>/participants', methods=['GET'])
@staff_required
def get_trek_participants(trek_id):
    trek = Treks.query.filter_by(t_id=trek_id, t_staff=g.staff_id).first()
    if not trek:
        return jsonify({"message": "Unauthorized or route non-existent"}), 404

    try:
        # Join applications with users to get clear email/username data profiles
        apps = db.session.query(TrekApplications, Users).join(Users, TrekApplications.u_id == Users.u_id).filter(TrekApplications.t_id == trek_id).all()

        participants = [{
            "a_id": a.a_id,
            "username": u.username,
            "a_status": a.a_status,
            "a_date": a.a_date.strftime('%Y-%m-%d') if a.a_date else 'N/A'
        } for a, u in apps]

        return jsonify(participants), 200
    except Exception as e:
        return jsonify({"message": f"Failed to load participant matrix: {str(e)}"}), 500
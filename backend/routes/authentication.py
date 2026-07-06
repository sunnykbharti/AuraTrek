from flask import Blueprint, request, jsonify, current_app
from models import db, Users
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from datetime import datetime, timedelta
# import app
auth_bp = Blueprint("authentication", __name__)

# app.config['SECRET_KEY'] = 'auratrek_secret_key_2026'

@auth_bp.route('/api/auth/login', methods=['GET','POST'])
def login():
    data = request.get_json()
    user = Users.query.filter_by(username=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"message" : "Inavalid email or password"}), 401
    
    if user.u_status == "inactive":
        return jsonify({"message" : "Your Admin Approval is Pending"}), 403
    
    token = jwt.encode({
        "user.id" : user.u_id,
        "role" : user.u_role,
        "exp" : datetime.utcnow() + timedelta(days=1)
    }, current_app.config['SECRET_KEY'], algorithm = "HS256")

    return jsonify({
        "token" : token,
        "role" : user.u_role,
        "name" : user.username,
        "message" : f"Welcome back to AuraTrek, {user.username}!"
    }), 200

#============== registration route ==============
@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"message":"No field can be left empty!!!"}), 400
    
    existing_user = Users.query.filter_by(username=data['email']).first()
    if existing_user:
        return jsonify({"message":"User already exits, kindly check the credentials and login"}), 400
    
    try:
        new_user = Users(
            username=data.get('email'),
            password=generate_password_hash(data.get('password'), method='pbkdf2:sha256'),
            u_role="trekker",
            u_status="active"
        )

        # new_trekker = Trekker(
        #     name=data['name'],
        #     email=data['email'],
        #     phone=data.get('phone'),
        #     address=data.get('address'),
        #     registration_status="INACTIVE"
        # )


        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message":"User registered successfully, please wait for admin approval"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database processing failure: {str(e)}"}), 500
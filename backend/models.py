from flask_sqlalchemy import SQLAlchemy
import flask_login

db = SQLAlchemy()

#================== Authentication details of all users of the application ================================
class Users(flask_login.UserMixin, db.Model):
    u_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(200), nullable = False)
    u_role = db.Column(db.String(100), nullable = False)
    u_status = db.Column(db.String(50), nullable = False, default = "active")

#==================== Staff Profile details ===========================================
class Staff(db.Model):
    s_id = db.Column(db.Integer, primary_key = True)
    s_name = db.Column(db.String(100), nullable = False)
    s_phone = db.Column(db.Integer, unique = True, nullable = False)
    s_email = db.Column(db.String(200), unique = True, nullable = False)
    s_age = db.Column(db.Integer, nullable = False)
    s_city = db.Column(db.String(200), nullable = False)
    s_treks = db.Column(db.JSON, default = "[]")
    # s_assign = db.relationship('Treks', backref="manager", lazy = True)
    s_status = db.Column(db.String(200), default = "active")

#==================== Users who will opt for trkking Details =====================================
class Trekker(db.Model):
    u_id = db.Column(db.Integer, primary_key = True)
    u_name = db.Column(db.String(100), nullable = False)
    u_phone = db.Column(db.Integer, unique = True, nullable = False)
    u_email = db.Column(db.String(200), unique = True, nullable = False)
    u_age = db.Column(db.Integer, nullable = False)
    u_city = db.Column(db.String(200), nullable = False)
    u_treks = db.Column(db.JSON, default = "[]")
    u_status = db.Column(db.String(200), default = "active")

#==================== Details of treks =============================================
class Treks(db.Model):
    t_id = db.Column(db.Integer, primary_key = True)
    t_name = db.Column(db.String(200), nullable = False, unique = True)
    t_location = db.Column(db.String(200), nullable = False)
    t_difficulty = db.Column(db.String(200), nullable = False)
    t_duration = db.Column(db.Integer, nullable = False)
    t_slots = db.Column(db.Integer, nullable = False)
    t_staff = db.Column(db.Integer, db.ForeignKey('staff.s_id'), nullable = True)
    t_status = db.Column(db.String(100), default = "open")
    applications = db.relationship(
        'TrekApplications', 
        backref='trek', 
        cascade="all, delete-orphan",
        lazy=True
    )

#==================== Applications for trek details =============================
class TrekApplications(db.Model):
    a_id = db.Column(db.Integer, primary_key = True)
    t_id = db.Column(db.Integer, db.ForeignKey('treks.t_id'), nullable = True)
    u_id = db.Column(db.Integer, db.ForeignKey('trekker.u_id'), nullable = True)
    a_date = db.Column(db.DateTime)
    a_status = db.Column(db.String(100), default = "applied")
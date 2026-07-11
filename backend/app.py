import os
from flask import Flask, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Users, Staff, Trekker, Treks
from werkzeug.security import generate_password_hash
from flask_caching import Cache
from celery import Celery


# ============= Database configuration =========================

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auratrek.sqlite'
app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)

# ============ CORS configuration =====================

from flask_cors import CORS

CORS(app)

#  ================== importing & Registering routes =====================

from routes.authentication import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.user import user_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(user_bp)

# ============== Registering superuser i.e. admin ==========
with app.app_context():
    db.create_all()
    admin = Users.query.filter_by(username="admin@gmail.com").first()
    if not admin:
        admin = Users(username="admin@gmail.com", password=generate_password_hash("admin@auratrek", method='pbkdf2:sha256'), u_role="admin", u_status="active")
        db.session.add(admin)
        db.session.commit()

# ============ Flask-caching setup configuration ================

app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6397
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

cache = Cache(app)

# ============ Integerating Celery and configuration ================

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/1'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/2'

# ================ tieing celery context to flask's db appl ===========
def make_celery(app):
    celery = Celery(
        app.import_name,
        broker = app.config['CELERY_BROKER_URL'],
        backend = app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

celery_app = make_celery(app)

# =============== default route ================
@app.route('/')
def home():
    return jsonify({"status": "healthy", "message": "AuraTrek RESTful API is active."})

# ============== Running app ===================
if __name__ == "__main__":
    app.run( debug=True, port = 5000)
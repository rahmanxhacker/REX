from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.session_protection = 'strong'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp
    from app.routes.sms_monitor import monitor_bp
    from app.routes.developer import dev_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(monitor_bp)
    app.register_blueprint(dev_bp)

    with app.app_context():
        db.create_all()

        # ── Auto-migrate: add new columns if they don't exist ──────────────
        try:
            from sqlalchemy import text, inspect as sa_inspect
            inspector = sa_inspect(db.engine)
            tables = inspector.get_table_names()

            if 'sms_ranges' in tables:
                range_cols = [c['name'] for c in inspector.get_columns('sms_ranges')]
                if 'application' not in range_cols:
                    db.session.execute(text("ALTER TABLE sms_ranges ADD COLUMN application VARCHAR(50)"))
                    db.session.commit()

            if 'sms_cdr' in tables:
                cdr_cols = [c['name'] for c in inspector.get_columns('sms_cdr')]
                if 'caller_id' not in cdr_cols:
                    db.session.execute(text("ALTER TABLE sms_cdr ADD COLUMN caller_id VARCHAR(50)"))
                    db.session.commit()
        except Exception:
            pass
        # ────────────────────────────────────────────────────────────────────

        from app.models.user import User, Role
        from app.models.sms import SMDRange
        from app.models.developer import StaticAsset

        for role_name, display in [('admin','Administrator'),('agent','Agent'),
                                    ('client','Client'),('developer','Developer')]:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name, display_name=display))
        db.session.commit()

        # Fetch roles after committing so they are available below
        admin_role = Role.query.filter_by(name='admin').first()
        agent_role = Role.query.filter_by(name='agent').first()

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='Rahman',
                email='abdulkhan6655687@gmail.com',
                password_hash=bcrypt.generate_password_hash('Rahman').decode('utf-8'),
                role=admin_role,
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()

        agent = User.query.filter_by(username='GHOST1').first()
        if not agent:
            agent = User(
                username='GHOST1',
                email='ghost1@abyss.sms',
                password_hash=bcrypt.generate_password_hash('GHOSTSCRIPT').decode('utf-8'),
                role=agent_role,
                is_active=True,
                api_token='WGZuZGVPSkJETlhJ'
            )
            db.session.add(agent)
            db.session.commit()

        if SMDRange.query.count() == 0:
            sample_ranges = [
                SMDRange(prefix='1', country='United States', operator='AT&T',
                         network_type='GSM', mcc='310', mnc='410',
                         currency='USD', rate=0.005, cost_per_sms=0.0050,
                         memo='United States SMS', test_number='12025551234', is_active=True),
                SMDRange(prefix='44', country='United Kingdom', operator='Vodafone',
                         network_type='GSM', mcc='234', mnc='15',
                         currency='GBP', rate=0.004, cost_per_sms=0.0045,
                         memo='UK SMS', test_number='447911123456', is_active=True),
                SMDRange(prefix='49', country='Germany', operator='Deutsche Telekom',
                         network_type='GSM', mcc='262', mnc='1',
                         currency='EUR', rate=0.004, cost_per_sms=0.0048,
                         memo='Germany SMS', test_number='4915112345678', is_active=True),
                SMDRange(prefix='33', country='France', operator='Orange',
                         network_type='GSM', mcc='208', mnc='1',
                         currency='EUR', rate=0.004, cost_per_sms=0.0045,
                         memo='France SMS', test_number='33612345678', is_active=True),
                SMDRange(prefix='39', country='Italy', operator='TIM',
                         network_type='GSM', mcc='222', mnc='1',
                         currency='EUR', rate=0.005, cost_per_sms=0.0052,
                         memo='Italy SMS', test_number='39312345678', is_active=True),
            ]
            for r in sample_ranges:
                db.session.add(r)
            db.session.commit()

    return app

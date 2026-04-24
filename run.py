#!/usr/bin/env python3
"""
REX SMS - IPRN Billing and Softswitch
Run script for the application
"""

from app import create_app, db
from app.models.user import User, Role
from app.models.sms import SMDRange, SMSNumber, SMSCDR
from app.models.activity import ActivityLog, News

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()

        # Initialize default roles
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', display_name='Administrator')
            db.session.add(admin_role)

        agent_role = Role.query.filter_by(name='agent').first()
        if not agent_role:
            agent_role = Role(name='agent', display_name='Agent')
            db.session.add(agent_role)

        client_role = Role.query.filter_by(name='client').first()
        if not client_role:
            client_role = Role(name='client', display_name='Client')
            db.session.add(client_role)

        db.session.commit()

        # Create default admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='Rahman',
                email='abdulkhan6655687@gmail.com',
                role=admin_role,
                is_active=True
            )
            admin_user.set_password('Rahman')
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin / admin123")

        # Create sample agent if not exists
        agent = User.query.filter_by(username='agent1').first()
        if not agent:
            agent = User(
                username='Rahman1',
                email='abdulkhan6655687@gmail.com',
                role=agent_role,
                is_active=True
            )
            agent.set_password('Rahman1')
            db.session.add(agent)
            db.session.commit()
            print("Sample agent created: agent1 / agent123")

        # Add sample SMS ranges if empty
        if SMDRange.query.count() == 0:
            sample_ranges = [
                SMDRange(prefix='1', country='United States', operator='AT&T', network_type='GSM', hlr_lookup=True, mcc='310', mnc='410', cost_per_sms=0.0050),
                SMDRange(prefix='44', country='United Kingdom', operator='Vodafone', network_type='GSM', hlr_lookup=True, mcc='234', mnc='15', cost_per_sms=0.0045),
                SMDRange(prefix='49', country='Germany', operator='Deutsche Telekom', network_type='GSM', hlr_lookup=True, mcc='262', mnc='1', cost_per_sms=0.0048),
                SMDRange(prefix='33', country='France', operator='Orange', network_type='GSM', hlr_lookup=True, mcc='208', mnc='1', cost_per_sms=0.0045),
                SMDRange(prefix='39', country='Italy', operator='TIM', network_type='GSM', hlr_lookup=True, mcc='222', mnc='1', cost_per_sms=0.0052),
                SMDRange(prefix='34', country='Spain', operator='Movistar', network_type='GSM', hlr_lookup=True, mcc='214', mnc='3', cost_per_sms=0.0048),
                SMDRange(prefix='61', country='Australia', operator='Telstra', network_type='GSM', hlr_lookup=True, mcc='505', mnc='1', cost_per_sms=0.0060),
                SMDRange(prefix='55', country='Brazil', operator='Vivo', network_type='GSM', hlr_lookup=True, mcc='724', mnc='6', cost_per_sms=0.0055),
                SMDRange(prefix='52', country='Mexico', operator='Telcel', network_type='GSM', hlr_lookup=True, mcc='334', mnc='20', cost_per_sms=0.0048),
                SMDRange(prefix='91', country='India', operator='Airtel', network_type='GSM', hlr_lookup=True, mcc='404', mnc='40', cost_per_sms=0.0030),
            ]
            for r in sample_ranges:
                db.session.add(r)
            db.session.commit()
            print(f"{len(sample_ranges)} sample SMS ranges added")

        print("REX SMS is ready!")
        print(f"Starting server on http://0.0.0.0:5000")

    # Run the application
    app.run(host='0.0.0.0', port=20190, debug=True)

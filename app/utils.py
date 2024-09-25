from .models import db, User
from werkzeug.security import generate_password_hash


def create_default_admin():
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        hashed_password = generate_password_hash(
            'adminpassword', method='pbkdf2:sha256', salt_length=8)
        new_admin = User(
            username='admin',
            email='admin@example.com',  # Dummy email
            phone='0000000000',
            matricule='ADMIN0001',
            fonction='root',
            prenom='root',
            shift='shift',
            password=hashed_password,
            is_admin=True,
            is_super_admin=True  # Mark as super admin

        )
        try:
            db.session.add(new_admin)
            db.session.commit()
            print("Admin user created successfully.")
        except Exception as e:
            print(f"There was an issue creating the admin user: {e}")

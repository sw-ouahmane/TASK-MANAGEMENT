from flask_login import current_user
from flask import Flask, render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import db, User, Todo
import os
from datetime import datetime
from flask import Blueprint
from flask import current_app
from flask_login import logout_user, login_user, current_user

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if not user.is_admin and not user.is_approved:
                return 'Your account is awaiting admin approval.'

            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.admin'))
            else:
                return redirect(url_for('main.index'))
        else:
            return 'Invalid credentials'

    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        prenom = request.form['prenom']
        fonction = request.form['fonction']
        email = request.form['email']
        phone = request.form['phone']
        matricule = request.form['matricule']
        password = request.form['password']
        profile_image = request.files['profile_image'] if 'profile_image' in request.files else None
        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=8)

        # Check if the username, email, phone, or matricule already exists
        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email) |
            (User.phone == phone) |
            (User.matricule == matricule)
        ).first()

        if existing_user:
            return 'Username, email, matricule, or phone already exists. Please choose another.'

        # Handle image upload if provided
        image_filename = None
        if profile_image:
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            if not upload_folder:
                raise ValueError(
                    "UPLOAD_FOLDER configuration is missing or not set.")

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            image_filename = secure_filename(profile_image.filename)
            file_path = os.path.join(upload_folder, image_filename)
            profile_image.save(file_path)

        # Automatically approve admin accounts, but set normal users to pending approval
        is_admin = request.form.get('is_admin', 'off') == 'on'
        is_approved = True if is_admin else False

        # Since shift will be set by the admin, assign a default value here (e.g., 'Pending')
        default_shift = 'Pending'  # Or None if it is nullable in the database

        # Create a new user with the provided details
        new_user = User(
            username=username,
            prenom=prenom,
            fonction=fonction,
            shift=default_shift,  # Default value or admin-set later
            email=email,
            phone=phone,
            matricule=matricule,
            password=hashed_password,
            profile_image=image_filename,
            is_admin=is_admin,
            is_approved=is_approved
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            if is_admin:
                return redirect(url_for('auth.login'))
            else:
                return 'Your account is awaiting admin approval.'
        except Exception as e:
            return f'There was an issue creating your account: {e}'

    return render_template('register.html')


@bp.route('/logout')
def logout():
    # Clear the session
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('is_admin', None)

    # Log out the user using Flask-Login
    logout_user()

    # Redirect to login page
    return redirect(url_for('auth.login'))


@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if user:
            # Normally you would send a password reset email with a token here
            # For simplicity, we'll redirect to a password reset form
            return redirect(url_for('auth.reset_password', username=username))
        else:
            return 'No account found with that username.'

    return render_template('forgot_password.html')


@bp.route('/reset_password/<username>', methods=['GET', 'POST'])
def reset_password(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return 'Invalid request.'

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = generate_password_hash(
            new_password, method='pbkdf2:sha256', salt_length=8)
        user.password = hashed_password

        try:
            db.session.commit()
            return redirect(url_for('auth.login'))
        except:
            return 'There was an issue resetting your password.'

    return render_template('reset_password.html', username=username)

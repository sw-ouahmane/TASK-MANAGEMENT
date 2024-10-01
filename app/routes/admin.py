from flask import send_file, Blueprint
import openpyxl
from openpyxl import load_workbook
from flask import Blueprint, render_template
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from flask import send_file, abort
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask import send_from_directory, current_app
import pandas as pd
from flask import request, flash, redirect, url_for
from app.models import db
from app.models import Todo, User
from flask import request, render_template, url_for
from flask_login import current_user, login_required
from flask import Flask, render_template, url_for, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import db, User, Todo
import os
from datetime import datetime
from flask import Blueprint
from flask import current_app
from flask_login import login_required, current_user
from flask import send_file
from flask import Flask, render_template
import xlrd
import openpyxl  # For .xlsx files


bp = Blueprint('admin', __name__)


@bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    pending_users = User.query.filter_by(
        is_admin=False, is_approved=False).all()
    normal_users = User.query.filter_by(is_admin=False, is_approved=True).all()
    admins = User.query.filter_by(is_admin=True).all()

    # Get search parameter
    prenom = request.args.get('prenom', '')

    # Get current page and set tasks per page
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Start with the base query
    query = Todo.query.join(User).filter(Todo.user_id == User.id)

    # Filter by prenom (from User model)
    if prenom:
        query = query.filter(User.prenom.ilike(f'%{prenom}%'))

    # Paginate the query
    tasks = query.paginate(page=page, per_page=per_page)

    return render_template('admin/admin.html', pending_users=pending_users, normal_users=normal_users, admins=admins, tasks=tasks)


@bp.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    # Ensure that only admins can delete users
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin

    user_to_delete = User.query.get_or_404(id)

    try:
        # Option 1: Delete all tasks associated with the user
        Todo.query.filter_by(user_id=id).delete()

        # Option 2: Reassign tasks to another user or set to null if allowed
        # Todo.query.filter_by(user_id=id).update({Todo.user_id: None})

        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('admin.admin'))
    except Exception as e:
        return f'There was a problem deleting the user: {e}'


@bp.route('/delete_admin/<int:id>')
@login_required
def delete_admin(id):
    # Check if the current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin

    # Fetch the admin to be deleted
    admin_user = User.query.get_or_404(id)

    # Check if the user to be deleted is an admin
    if not admin_user.is_admin:
        return 'The user is not an admin.'

    # Prevent deletion of the super admin
    if admin_user.is_super_admin:
        return 'You cannot delete the super admin.'

    # Proceed with deletion
    try:
        db.session.delete(admin_user)
        db.session.commit()
        return redirect(url_for('admin.admin'))
    except Exception as e:
        return f'There was a problem deleting the admin user: {e}'


@bp.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    # Check if the current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Verify the current password
        if not check_password_hash(current_user.password, current_password):
            return 'Current password is incorrect.'

        # Check if new passwords match
        if new_password != confirm_password:
            return 'New passwords do not match.'

        # Hash the new password and update the user
        current_user.password = generate_password_hash(
            new_password, method='pbkdf2:sha256', salt_length=8
        )

        try:
            db.session.commit()  # Save the updated password to the database
            return 'Password changed successfully.'
        except Exception as e:
            return f'There was an issue changing your password: {e}'

    return render_template('admin/admin_change_password.html')


@bp.route('/admin/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    # Check if the current user is an admin and a super admin
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin
    if not current_user.is_super_admin:
        return "You do not have permission to add a new admin."

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        shift = request.form['shift']
        prenom = request.form['prenom']
        matricule = request.form['matricule']
        fonction = request.form['fonction']
        password = request.form['password']
        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=8
        )

        # Check for existing user by username, email, or phone
        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email) |
            (User.phone == phone) |
            (User.matricule == matricule)
        ).first()

        if existing_user:
            return 'Username, email, or phone already exists. Please choose another.'

        # Create new admin
        new_admin = User(
            username=username,
            email=email,
            matricule=matricule,
            shift=shift,
            phone=phone,
            fonction=fonction,
            prenom=prenom,
            password=hashed_password,
            is_admin=True
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            return redirect(url_for('admin.admin'))
        except Exception as e:
            return f'There was an issue creating the admin: {e}'

    return render_template('admin/add_admin.html')


@bp.route('/admin/approve_user/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)

    if request.form['action'] == 'approve':
        # Assign the shift only if the user is approved
        shift = request.form.get('shift')
        if shift in ['A', 'B', 'C']:
            user.shift = shift
            user.is_approved = True
            user.is_pending = False  # Ensure the user is no longer pending
            db.session.commit()
            flash(
                f'User {user.username} approved and assigned to Shift {shift}.', 'success')
        else:
            flash('Invalid shift selection.', 'danger')

    elif request.form['action'] == 'reject':
        # If the user is rejected, remove them from the database
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been rejected.', 'info')

    # Redirect back to the pending users page
    return redirect(url_for('admin.view_pending_users'))


@bp.route('/view_admins')
def view_admins():
    admins = User.query.filter_by(is_admin=True).all()
    return render_template('admin/admin_list.html', admins=admins)


@bp.route('/view_pending_users')
@login_required
def view_pending_users():
    # Ensure query only gets pending, unapproved users
    pending_users = User.query.filter_by(
        is_admin=False, is_approved=False, is_pending=True).all()
    return render_template('admin/pending_users.html', pending_users=pending_users)


@bp.route('/view_normal_users', methods=['GET', 'POST'])
@login_required
def view_normal_users():
    search_query = request.args.get('search', '')  # Get search query from URL
    page = request.args.get('page', 1, type=int)  # Get the current page

    # Base query for normal users
    query = User.query.filter_by(is_admin=False, is_approved=True)

    # Apply search filter if query is present
    if search_query:
        query = query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.matricule.ilike(f'%{search_query}%'))
        )

    # Paginate the results
    pagination = query.paginate(page=page, per_page=10)

    # Pass both normal_users and pagination to the template
    return render_template(
        'admin/normal_users.html',
        normal_users=pagination.items,
        search_query=search_query,
        pagination=pagination
    )


"""
@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # This uses current_app.root_path to access the main app directory
    uploads_directory = os.path.join(current_app.root_path, '..', 'uploads')
    return send_from_directory(uploads_directory, filename)
"""


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')


@bp.route('/load_conference', methods=['GET', 'POST'])
@login_required
def load_conference():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part. Please choose a file to upload.')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file. Please choose a file to upload.')
            return redirect(request.url)

        if file and file.filename.lower().endswith(('.xlsx', '.xls')):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            uploaded_files = session.get('uploaded_files', [])
            uploaded_files.append(
                {'filename': filename, 'filepath': file_path,
                    'upload_time': upload_time}
            )
            session['uploaded_files'] = uploaded_files

            flash('File successfully uploaded and processed.')
            return redirect(url_for('admin.load_conference'))

        flash(
            'Invalid file type. Please upload an Excel file with .xlsx or .xls extension.')

    uploaded_files = session.get('uploaded_files', [])
    return render_template('admin/load_conference.html', user=current_user, uploaded_files=uploaded_files)


@bp.route('/open_file/<filename>', methods=['GET'])
@login_required
def open_file(filename):
    # Construct the file path
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Check if file exists
    if not os.path.exists(file_path):
        flash(f'File {filename} not found.')
        return redirect(url_for('admin.load_conference'))

    # Return the file for download
    try:
        return send_file(file_path)
    except Exception as e:
        flash(f'Error opening file: {str(e)}')
        return redirect(url_for('admin.load_conference'))


@bp.route('/conference', methods=['GET'])
@login_required
def conference():
    # Get the list of uploaded files from the session
    uploaded_files = session.get('uploaded_files', [])
    if not uploaded_files:
        flash('No uploaded conference files found.')

    # Render the 'conference.html' to list uploaded files
    return render_template('conference.html', user=current_user, uploaded_files=uploaded_files)


@bp.route('/download_conference/<filename>', methods=['GET'])
def download_conference(filename):
    # Construct the file path
    file_path = os.path.join(os.getcwd(), 'uploads', filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        return "File not found", 404

    # Check the file extension and send the file as an attachment
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            print(f"Error sending file: {e}")
            return "Error sending file", 500
    else:
        return "Unsupported file format", 400

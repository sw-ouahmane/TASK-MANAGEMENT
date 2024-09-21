from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, User
from functools import wraps
from flask import session
from flask_login import login_required, current_user

bp = Blueprint('user', __name__, url_prefix='/user')


@login_required
def profile():
    user_id = current_user.id
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form['username']
        # Add additional fields as needed
        user.username = username
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', user=user)

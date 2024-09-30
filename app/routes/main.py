from flask_login import current_user, login_required
from flask import Flask, render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import db, User, Todo
import os
from datetime import datetime
from flask import Blueprint
from flask import current_app
from flask_login import login_required, current_user
bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/index')
@login_required  # Ensure the user is logged in
def index():
    return render_template('index.html', user=current_user)


@bp.route('/task_master', methods=['GET', 'POST'])
@login_required
def task_master():
    if request.method == 'POST':
        # Task creation logic
        task_date = request.form.get('date')
        task_shift = request.form.get('shift')
        task_poste = request.form.get('poste')
        task_grue = request.form.get('grue')
        task_navire = request.form.get('navire')
        task_marchandise = request.form.get('marchandise')
        task_nb_cs_pcs = request.form.get('nb_cs_pcs')
        task_unite = request.form.get('unite')
        task_raclage = request.form.get('raclage')
        task_comentaire = request.form.get('comentaire')

        # Validate required fields
        if not all([task_date, task_shift, task_poste, task_navire, task_marchandise, task_nb_cs_pcs, task_unite, task_raclage]):
            return 'All fields are required.'

        new_task = Todo(
            content=task_date,  # Modify as needed
            shift=task_shift,
            poste=task_poste,
            grue=task_grue,
            navire=task_navire,
            marchandise=task_marchandise,
            nb_cs_pcs=task_nb_cs_pcs,
            unite=task_unite,
            raclage=task_raclage,
            comentaire=task_comentaire,
            user_id=current_user.id
        )

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('main.task_master'))
        except Exception as e:
            return f'There was an issue adding your task: {e}'

    else:
        # Handle GET request for filtering tasks
        page = request.args.get('page', 1, type=int)
        year = request.args.get('year')
        month = request.args.get('month')

        # Start with a base query for the user's tasks
        query = Todo.query.filter_by(user_id=current_user.id)

        # Filter by year and month if provided
        if year and month:
            query = query.filter(
                db.extract('year', Todo.date_created) == year,
                db.extract('month', Todo.date_created) == month
            )

        # Paginate the results
        tasks = query.order_by(Todo.date_created).paginate(
            page=page, per_page=10  # Adjust per_page as needed
        )

        return render_template('task_master.html', tasks=tasks, user=current_user)

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


@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        task_date = request.form.get('date')
        task_shift = request.form.get('shift')
        task_poste = request.form.get('poste')
        task_navire = request.form.get('navire')
        task_marchandise = request.form.get('marchandise')
        task_nb_cs_pcs = request.form.get('nb_cs_pcs')
        task_unite = request.form.get('unite')
        task_raclage = request.form.get('raclage')

        if not task_date or not task_shift or not task_poste or not task_navire or not task_marchandise or not task_nb_cs_pcs or not task_unite or not task_raclage:
            return 'All fields are required.'

        new_task = Todo(
            content=task_date,  # Example, modify as needed
            shift=task_shift,
            poste=task_poste,
            navire=task_navire,
            marchandise=task_marchandise,
            nb_cs_pcs=task_nb_cs_pcs,
            unite=task_unite,
            raclage=task_raclage,
            user_id=current_user.id
        )

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('main.index'))
        except Exception as e:
            return f'There was an issue adding your task: {e}'

    else:
        page = request.args.get('page', 1, type=int)
        year = request.args.get('year')
        month = request.args.get('month')

        query = Todo.query.filter_by(user_id=current_user.id)

        # Filter by year and month if provided
        if year and month:
            query = query.filter(
                db.extract('year', Todo.date_created) == year,
                db.extract('month', Todo.date_created) == month
            )

        tasks = query.order_by(Todo.date_created).paginate(
            page=page, per_page=10)  # Adjust per_page as needed
        return render_template('index.html', tasks=tasks, user=current_user)

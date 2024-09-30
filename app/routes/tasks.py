from flask import request
from flask_login import login_required, current_user
from flask import Flask, render_template, url_for, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import db, User, Todo
from flask_login import current_user, login_required
from datetime import datetime
from flask import Blueprint
from flask import current_app


bp = Blueprint('tasks', __name__)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    # Use current_user instead of querying User from session
    user = current_user

    # Check if the task is validated and validated by another admin
    if task_to_delete.status == 'Validated' and task_to_delete.validated_by != user.username:
        return 'You cannot delete a validated task validated by another admin.'

    # Ensure the current user owns the task or is allowed to delete it
    if task_to_delete.user_id != user.id:
        return 'You are not authorized to delete this task.'

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('main.task_master'))
    except Exception as e:
        return f'There was a problem deleting that task: {e}'


@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    task = Todo.query.get_or_404(id)

    # Check if the task is validated and if another admin validated it
    if task.status == 'Validated' and task.validated_by != current_user.username:
        return 'You cannot update a validated task validated by another admin.'

    # Ensure the current user owns the task or is allowed to update it
    if task.user_id != current_user.id:
        return 'You are not authorized to update this task.'

    if request.method == 'POST':
        task.date = request.form['date']
        task.shift = request.form['shift']
        task.poste = request.form['poste']
        task.grue = request.form['grue']  # Match the HTML field name
        task.navire = request.form['navire']
        task.marchandise = request.form['marchandise']
        task.nb_cs_pcs = request.form['nb_cs_pcs']
        task.unite = request.form['unite']
        task.raclage = request.form['raclage']
        task.comentaire = request.form['comentaire']

        try:
            db.session.commit()
            return redirect(url_for('main.task_master'))  # Redirect to 'index'
        except Exception as e:
            return f'There was an issue updating your task: {e}'

    return render_template('update.html', task=task)


@bp.route('/add_affectation', methods=['GET', 'POST'])
@login_required
def add_affectation():
    if request.method == 'POST':
        try:
            # Retrieve form data
            date_str = request.form.get('date')
            shift = request.form.get('shift')
            poste = request.form.get('poste')
            grue = request.form.get('grue')
            navire = request.form.get('navire')
            marchandise = request.form.get('marchandise')
            nb_cs_pcs = request.form.get('nb_cs_pcs')
            unite = request.form.get('unite')
            raclage = request.form.get('raclage')
            comentaire = request.form.get('comentaire')

            # Ensure 'current_user' is used
            user_id = current_user.id

            # Convert date string to datetime object
            date_created = datetime.strptime(date_str, '%d/%m/%Y')

            # Create a new Todo object
            new_task = Todo(
                content=None,  # Adjust this as needed
                shift=shift,
                poste=poste,
                grue=grue,
                navire=navire,
                marchandise=marchandise,
                nb_cs_pcs=nb_cs_pcs,
                unite=unite,
                raclage=raclage,
                comentaire=comentaire,
                date_created=date_created,
                user_id=user_id
            )

            # Add to the database
            db.session.add(new_task)
            db.session.commit()

            return redirect(url_for('main.task_master'))

        except Exception as e:
            # Print the error for debugging
            print(f"An error occurred: {e}")
            return "There was a problem adding the affectation."

    return render_template('add_affectation.html')


@bp.route('/view_user_tasks/<int:user_id>', methods=['GET', 'POST'])
@login_required
def view_user_tasks(user_id):
    user = User.query.get_or_404(user_id)

    # Get the current page number from the query string or default to 1
    page = request.args.get('page', 1, type=int)

    # Retrieve search parameters (year and month) from query string
    search_year = request.args.get('year', type=int)
    search_month = request.args.get('month', type=int)

    # Start building the query for tasks
    query = Todo.query.filter_by(user_id=user_id)

    # Apply search filters if year and month are provided
    if search_year and search_month:
        query = query.filter(db.extract('year', Todo.date_created) == search_year,
                             db.extract('month', Todo.date_created) == search_month)

    # Paginate the tasks
    tasks = query.paginate(page=page, per_page=10)

    # Handle POST request (validation/rejection of tasks)
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        action = request.form.get('action')
        remark = request.form.get('remark')

        task = Todo.query.get(task_id)
        if not task:
            flash('Task not found.', 'danger')
            return redirect(url_for('tasks.view_user_tasks', user_id=user_id, page=page))

        # Check task status and apply actions
        if task.status == 'Rejected' and task.validated_by != current_user.username:
            flash(
                'This task has already been rejected by another admin. You cannot modify it.', 'danger')
        else:
            if action == 'validate':
                task.status = 'Validated'
                task.validated_by = current_user.username
                task.remark = remark
                flash('Task validated successfully.', 'success')
            elif action == 'reject':
                task.status = 'Rejected'
                task.validated_by = current_user.username
                task.remark = remark
                flash('Task rejected successfully.', 'success')
            else:
                flash('Invalid action.', 'danger')

        # Commit changes to the database
        db.session.commit()

        # Redirect to the same page to reflect the changes, keeping the pagination
        return redirect(url_for('tasks.view_user_tasks', user_id=user_id, page=page))

    # Render the template with the user, paginated tasks, and search values
    return render_template('view_tasks.html', user=user, tasks=tasks, search_year=search_year, search_month=search_month)


@bp.route('/validate_task/<int:task_id>/<string:action>', methods=['POST'])
@login_required
def validate_task(task_id, action):
    # Ensure only admins can validate or reject tasks
    if not current_user.is_admin:
        return redirect(url_for('tasks.view_user_tasks', user_id=current_user.id))

    task = Todo.query.get_or_404(task_id)
    # Get the Escale input from the form
    escale = request.form.get('Escale', '')
    remark = request.form.get('remark', '')

    # Update the task with the Escale value
    if escale:
        task.Escale = escale

    # Identify the initial admin created at app startup
    initial_admin_matricule = 'ADMIN0001'

    # If the task was processed by another admin, no further action is allowed unless it's the initial admin
    if task.is_validated and task.validated_by != current_user.username and current_user.matricule != initial_admin_matricule:
        return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))

    if task.status == 'Rejected' and task.validated_by != current_user.username and current_user.matricule != initial_admin_matricule:
        return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))

    # Handle task validation
    if action == 'validate':
        if task.is_validated and task.validated_by == current_user.username:
            pass  # No further action needed
        elif task.status == 'Rejected' and (task.validated_by == current_user.username or current_user.matricule == initial_admin_matricule):
            # Allow the same admin who rejected the task or the initial admin to reverse their decision
            task.status = 'Validated'
            task.is_validated = True
            task.remark = remark
            task.validated_by = current_user.username
        elif task.is_validated or task.status == 'Rejected':
            pass  # No action allowed if processed by another admin
        else:
            task.status = 'Validated'
            task.is_validated = True
            task.validated_by = current_user.username  # Store current admin's username
            task.remark = remark

    # Handle task rejection
    elif action == 'reject':
        if task.status == 'Rejected' and task.validated_by == current_user.username:
            pass  # No further action needed
        elif task.is_validated and (task.validated_by == current_user.username or current_user.matricule == initial_admin_matricule):
            # Allow the same admin who validated the task or the initial admin to reverse their decision
            task.status = 'Rejected'
            task.is_validated = False  # Set to False if rejected
            task.remark = remark
            task.validated_by = current_user.username
        elif task.is_validated or task.status == 'Rejected':
            pass  # No action allowed if processed by another admin
        else:
            task.status = 'Rejected'
            task.is_validated = False  # Set to False if rejected
            task.validated_by = current_user.username  # Store current admin's username
            task.remark = remark

    else:
        return "Invalid action", 400

    db.session.commit()
    return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))


@bp.route('/add_escale/<int:task_id>', methods=['POST'])
def add_escale(task_id):
    task = Todo.query.get_or_404(task_id)

    # Check if the user is an admin using the `is_admin` attribute
    if not current_user.is_admin:
        flash("You do not have permission to add an Escale.", "danger")
        return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))

    # Process form data
    escale = request.form.get('Escale')
    if escale:
        task.Escale = escale
        db.session.commit()
        flash('Escale added successfully!', 'success')
    else:
        flash('Please enter a valid Escale.', 'danger')

    return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))

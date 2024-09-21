"""
@bp.route('/validate_task/<int:task_id>/<string:action>', methods=['POST'])
@login_required
def validate_task(task_id, action):
    # Ensure only admins can validate or reject tasks
    if not current_user.is_admin:
        return redirect(url_for('tasks.view_user_tasks', user_id=current_user.id))

    task = Todo.query.get_or_404(task_id)
    remark = request.form.get('remark', '')

    # If the task was processed by another admin, no further action is allowed
    if task.is_validated and task.validated_by != current_user.username:
        return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))

    if task.status == 'Rejected' and task.validated_by != current_user.username:
        return redirect(url_for('tasks.view_user_tasks', user_id=task.user_id))

    # Handle task validation
    if action == 'validate':
        if task.is_validated and task.validated_by == current_user.username:
            pass  # No further action needed
        elif task.status == 'Rejected' and task.validated_by == current_user.username:
            # Allow the same admin who rejected the task to reverse their decision
            task.status = 'Validated'
            task.is_validated = True
            task.remark = remark
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
        elif task.is_validated and task.validated_by == current_user.username:
            # Allow the same admin who validated the task to reverse their decision
            task.status = 'Rejected'
            task.is_validated = False  # Set to False if rejected
            task.remark = remark
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
"""

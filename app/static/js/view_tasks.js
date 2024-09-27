$('#remarkModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var action = button.data('action'); // Extract info from data-* attributes
    var taskId = button.data('task-id');

    var modal = $(this);
    modal.find('#action').val(action);
    modal.find('#task-id').val(taskId);
    modal.find('#remarkForm').attr('action', `/validate_task/${taskId}/${action}`);
});


$('#remarkModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var taskId = button.data('task-id'); // Extract task ID
    var action = button.data('action'); // Extract action (validate/reject)

    var modal = $(this);
    modal.find('#task-id').val(taskId); // Set the task ID in hidden input
    modal.find('#action').val(action); // Set the action in hidden input
});

document.getElementById('Escale').addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();  // Prevent default form submission
        document.getElementById('escale-form').submit();  // Submit the form automatically
    }
});
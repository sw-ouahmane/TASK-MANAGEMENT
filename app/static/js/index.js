// When the modal is about to be shown
$('#viewRemarkModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var remark = button.data('remark'); // Extract remark from data-* attributes
    var admin = button.data('admin'); // Extract admin name from data-* attributes

    // Update the modal's content
    var modal = $(this);
    modal.find('#modal-admin').text(admin);
    modal.find('#modal-remark').text(remark);
});



$('#addRemarkModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var action = button.data('action') // Extract action info
    var taskId = button.data('task-id')

    var modal = $(this)
    modal.find('#modalAction').val(action)
    modal.find('#modalTaskId').val(taskId)
    modal.find('#remarkForm').attr('action', `/validate_task/${taskId}/${action}`)
})

$('#viewRemarkModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var remark = button.data('remark');
    var admin = button.data('admin');

    var modal = $(this);
    modal.find('#modal-remark').text(remark);
    modal.find('#modal-admin').text(admin);
});
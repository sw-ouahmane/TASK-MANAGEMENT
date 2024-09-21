document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('.delete-button'); // More specific class

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const confirmed = confirm('Are you sure you want to delete this?');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});

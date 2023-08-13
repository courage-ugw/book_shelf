document.addEventListener("DOMContentLoaded", function () {
    // Get the alert element by its ID
    var alertElement = document.getElementById("alert");

    // Hide the alert after 3 seconds
    setTimeout(function () {
        alertElement.style.display = "none";
    }, 3000);

});

$(document).ready(function () {
    // Show modal when delete button is clicked
    $('.btn-danger').click(function () {
        var modalId = $(this).data('bs-target');
        $(modalId).modal('show');
    });

});
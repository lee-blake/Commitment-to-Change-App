$(document).ready(function() {
    $('#submit-create-template').click(function(e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: $('#create-commitment-template-form').attr('action'),
            data: $('#create-commitment-template-form').serialize(),
            success: function() {
                window.location.reload();
            },
            error: function(){
                alert("Failed to create new template");
            }
        });
    });
});
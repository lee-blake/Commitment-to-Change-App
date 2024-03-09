// JQuery event listener. Listens for submit once document is ready
$(document).ready(function() {
    $('#create-commitment-template-form').submit(function(e) {
        e.preventDefault();
        createObjectFromForm('#create-commitment-template-form', 'Failed to create new template');
    });
});

function createObjectFromForm(form_id, error_message) {
    $.ajax({
        type: "POST",
        url: $(form_id).attr('action'),
        data: $(form_id).serialize(),
        success: function() {
            window.location.reload();
        },
        error: function(){
            alert(error_message);
        }
    });
}
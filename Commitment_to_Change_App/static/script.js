function copyToClipboard (id) {
    var text_to_copy = document.getElementById(id).innerHTML;

    if (!navigator.clipboard){ //Check to see if browser supports clipboard API

        // If not, use execCommand, an outdated method of copying. 
        // The clipboard API is still newer, and some browsers still
        // do not fully support it, so leaving this here just in case.
        
        var r = document.createRange();
        r.selectNode(document.getElementById(id));
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(r);
        document.execCommand('copy');
        window.getSelection().removeAllRanges();
    } else {
    navigator.clipboard.writeText(text_to_copy).then(
        function(){
            alert("Copied Successfully");
        })
      .catch(
         function() {
            alert("Copy Failed");
      });
    }
}
function showPassword (id) {
    var selected_password_field = document.getElementById(id);
  if (selected_password_field.type === "password") {
    selected_password_field.type = "text";
  } else {
    selected_password_field.type = "password";
  }
}
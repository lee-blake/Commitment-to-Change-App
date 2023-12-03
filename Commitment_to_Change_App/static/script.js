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
function showPassword (id_password, id_showPassword1, id_showPassword2) {
    const passwordInput = document.getElementById(id_showPassword);
    const passwordInput1 = document.getElementById(id_showPassword1);
    const passwordInput2 = document.getElementById(id_showPassword2);

    const showPasswordBox = document.getElementById('showPassword');
    const isPasswordVisible  = showPasswordBox.checked;

    if (isPasswordVisible) {
        passwordInput.type = 'text';
        passwordInput1.type = 'text';
        passwordInput2.type = 'text';
    } else {
        passwordInput.type = 'text';
        passwordInput1.type = 'password';
        passwordInput2.type = 'password';
    }
}
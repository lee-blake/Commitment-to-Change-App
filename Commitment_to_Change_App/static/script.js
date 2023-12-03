function copyToClipBoard (id) {
    const copyInput = document.getElementById('copyInput');
    copyInput.select();
    copyInput.setSelectionRange(0, 9999);

    document.execCommand('copy');
    copyInput.blur();
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
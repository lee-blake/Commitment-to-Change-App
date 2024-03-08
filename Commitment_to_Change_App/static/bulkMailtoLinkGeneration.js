document.addEventListener('DOMContentLoaded', function () {
    const submitBtn = document.getElementById('modal-bulk-email-submit-button');
    submitBtn.addEventListener('click', function () {
      const selectedEmails = [];
      const checkboxes = document.querySelectorAll('.email-checkbox');
      checkboxes.forEach(function (checkbox) {
        if (checkbox.checked) {
          selectedEmails.push(checkbox.getAttribute('data-email'));
        }
      });
  
      const mailtoLink = 'mailto:' + selectedEmails.join(',');
      window.location.href = mailtoLink;
    });
  });

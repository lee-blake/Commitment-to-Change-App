$(document).ready(function () {
  $('#modal-bulk-email-submit-button').click(function () {
    const selectedEmails = [];
    $('.email-checkbox:checked').each(function () {
      selectedEmails.push($(this).data('email'));
    });

    const mailtoLink = 'mailto:' + selectedEmails.join(',');
    window.location.href = mailtoLink;
  });
});
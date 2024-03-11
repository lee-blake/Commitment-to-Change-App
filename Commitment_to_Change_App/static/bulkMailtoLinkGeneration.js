$(document).ready(function() {
  $('#modal-bulk-email-submit-button').click(generateMailtoLink);
});

function generateMailtoLink() {
  const selectedEmails = [];
  $('.email-checkbox:checked').each(function() {
    selectedEmails.push($(this).data('email'));
  });
  const mailtoLink = 'mailto:' + selectedEmails.join(',');
  redirectToMailtoLink(mailtoLink);
}

function redirectToMailtoLink(mailtoLink) {
  window.location.href = mailtoLink;
}
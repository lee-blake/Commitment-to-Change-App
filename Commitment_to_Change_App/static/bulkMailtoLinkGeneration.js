$(document).ready(function() {
  $('#select-all-checkbox').click(selectAllCheckboxes);
  $('#modal-bulk-email-submit-button').click(generateMailtoLink);
});

function selectAllCheckboxes() {
  $('.email-checkbox').prop('checked', this.checked);
} 

function generateMailtoLink() {
  const selectedEmails = getSelectedEmails();
  const mailtoLink = 'mailto:' + selectedEmails.join(',');
  redirectToMailtoLink(mailtoLink);
}

function getSelectedEmails() {
  const selectedEmails = [];
  $('.email-checkbox:checked').each(function() {
    selectedEmails.push($(this).data('email'));
  });
  return selectedEmails;
}

function redirectToMailtoLink(mailtoLink) {
  window.location.href = mailtoLink;
}
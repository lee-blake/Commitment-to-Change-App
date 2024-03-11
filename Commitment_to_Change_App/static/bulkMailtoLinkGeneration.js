$(document).ready(function() {
  $('#select-all-emails-checkbox').click(selectOrUnselectAllCheckboxes);
  $('#modal-bulk-email-submit-button').click(generateMailtoLink);
});

function selectOrUnselectAllCheckboxes() {
  $('.select-email-checkbox').prop('checked', this.checked);
} 

function generateMailtoLink() {
  const selectedEmails = getSelectedEmails();
  const mailtoLink = 'mailto:' + selectedEmails.join(',');
  redirectToMailtoLink(mailtoLink);
}

function getSelectedEmails() {
  const selectedEmails = [];
  $('.select-email-checkbox:checked').each(function() {
    selectedEmails.push($(this).data('email'));
  });
  return selectedEmails;
}

function redirectToMailtoLink(mailtoLink) {
  window.location.href = mailtoLink;
}
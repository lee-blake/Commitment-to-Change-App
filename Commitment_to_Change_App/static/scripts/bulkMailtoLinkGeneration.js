$(document).ready(function () {
  $("#select-all-emails-checkbox").click(selectOrUnselectAllCheckboxes);
});

function selectOrUnselectAllCheckboxes() {
  $(".select-email-checkbox").prop("checked", this.checked);
}

function generateMailtoLink(defaultBodyText, defaultSubjectText) {
  const selectedEmails = getSelectedEmails();
  const encodedDefaultSubject = encodeURIComponent(defaultBodyText);
  const encodedDefaultBody = encodeURIComponent(defaultSubjectText);
  const mailtoLink = "mailto:" + selectedEmails.join(",") + "?subject=" + encodedDefaultSubject + "&body=" + encodedDefaultBody;
  redirectToMailtoLink(mailtoLink);
}

function getSelectedEmails() {
  const selectedEmails = [];
  $(".select-email-checkbox:checked").each(function () {
    selectedEmails.push($(this).data("email"));
  });
  return selectedEmails;
}

function redirectToMailtoLink(mailtoLink) {
  window.location.href = mailtoLink;
}

$(document).ready(function () {
  $("#select-all-emails-checkbox").click(selectOrUnselectAllCheckboxes);
});

function selectOrUnselectAllCheckboxes() {
  $(".select-email-checkbox").prop("checked", this.checked);
}

function generateMailtoLink(courseTitle, courseInstitution) {
  const selectedEmails = getSelectedEmails();
  const defaultSubject = encodeURIComponent(courseTitle + " - " + courseInstitution);
  const defaultBody = encodeURIComponent("You are receiving this email because you are enrolled in the following course: " + 
  courseTitle + ", created by: " + courseInstitution);
  const mailtoLink = "mailto:" + selectedEmails.join(",") + "?subject=" + defaultSubject + "&body=" + defaultBody;
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

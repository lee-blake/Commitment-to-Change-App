$(document).ready(function () {
  createStandardDataTable("#provider-course-datatable");
  createStandardDataTable("#provider-commitment-template-datatable");
  createStudentListDataTable("#clinician-course-student-datatable");
  createStudentListDataTable("#provider-course-student-datatable");
  createBulkEmailDataTable("#provider-course-student-datatable-bulk-email");
});

function createStandardDataTable(table_id) {
  $(table_id).DataTable({
    // autoWidth scales onlyon page refresh. Disabling allows us to use bootstrap class scaling
    autoWidth: false,
    // Disable pagination; Always displays everything in the list
    paging: false,
    // Remove pagination information ("Showing 1 to N of N entries")
    bInfo: false,
    // Adds dt-center (DataTables class) to all columns to center column content
    columnDefs: [{ className: "dt-center", targets: "_all" }],
  });
}

function createStudentListDataTable(table_id) {
  $(table_id).DataTable({
    // autoWidth scales onlyon page refresh. Disabling allows us to use bootstrap class scaling
    autoWidth: false,
    // Disable pagination; Always displays everything in the list
    paging: false,
    // Remove pagination information ("Showing 1 to N of N entries")
    bInfo: false,
    // Wrap search bar element in "text-center" div
    dom: '<"text-center"f>i',
    // Select status-column and sort by data-sort value if it exists
    // This is necessary because the status column has no text to sort by default
    columnDefs: [
      {
        targets: 'status-column',
        orderable: true,
        render: function (data, type) {
          if (type === 'sort' || type === 'type') {
            var element = $(data);
            var sortValue = element.data('sort');
            return sortValue !== undefined ? sortValue : data;
          }
          return data;
        }
      }
    ]
  });
}

function createBulkEmailDataTable(table_id) {
  $(table_id).DataTable({
    // autoWidth scales onlyon page refresh. Disabling allows us to use bootstrap class scaling
    autoWidth: false,
    // Disable pagination; Always displays everything in the list
    paging: false,
    // Remove pagination information ("Showing 1 to N of N entries")
    bInfo: false,
    // Set default column to sort by
    order: [[1, "asc"]],
    // Wrap search bar element in "text-center" div
    dom: '<"text-center"f>i',
    // Set width and disable sorting of 'select' checkbox column
    columnDefs: [
      { width: "16px", targets: "datatable-select-column" },
      { orderable: false, targets: "datatable-select-column" },
    ],
  });
}

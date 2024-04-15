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
    // Replace any empty, null, or undefined values with "——"
    columnDefs: [
      { 
        targets: "_all",
        render: function ( data ) {
          if(data === "" || data === null || data === undefined) {
            return "——";
          } else {
            return data;
          }
        }
      }
    ]
  });
}

function createBulkEmailDataTable(table_id) {
  $(table_id).DataTable({
    // autoWidth scales only on page refresh. Disabling allows us to use bootstrap class scaling
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
      { 
        targets: "_all",
        render: function ( data ) {
          if(data === "" || data === null || data === undefined) {
            return "——";
          } else {
            return data;
          }
        }
      },
    ],
  });
}

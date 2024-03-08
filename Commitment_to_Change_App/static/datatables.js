$(document).ready(function() {
    createStandardDataTable('#provider-course-datatable');
    createStandardDataTable('#provider-commitment-template-datatable');
    createStudentListDataTable('#clinician-course-student-datatable');
    createStudentListDataTable('#provider-course-student-datatable');
    createStudentListDataTable('#provider-course-student-datatable-bulk-email');

    // Trigger toggleVisibilityBasedOnDivWidth on document ready
    toggleVisibilityBasedOnDivWidth(400, '#course-student-datatable-container');
    // Trigger toggleVisibilityBasedOnDivWidth on window "resize"
    $(window).on("resize", function() {
        toggleVisibilityBasedOnDivWidth(400, '#course-student-datatable-container');
    });
});

// Toggle whether button or email link is shown
function toggleVisibilityBasedOnDivWidth(containerBreakpoint, parentContainerID) {
    var parentContainerWidth = $(parentContainerID).width();
    $(".hide-when-smaller").toggle(parentContainerWidth >= containerBreakpoint);
    $(".show-when-smaller").toggle(parentContainerWidth < containerBreakpoint);
}

function createStandardDataTable(table_id){
    $(table_id).DataTable({
        // autoWidth scales onlyon page refresh. Disabling allows us to use bootstrap class scaling
        "autoWidth": false,
        // Disable pagination; Always displays everything in the list
        "paging": false,
        // Remove pagination information ("Showing 1 to N of N entries")
        "bInfo" : false,
        // Adds dt-center (DataTables class) to all columns to center column content
        "columnDefs": [
            {"className": "dt-center", "targets": "_all"}
        ],
    });
}

function createStudentListDataTable(table_id){
    $(table_id).DataTable({
        // autoWidth scales onlyon page refresh. Disabling allows us to use bootstrap class scaling
        "autoWidth": false,
        // Disable pagination; Always displays everything in the list
        "paging": false,
        // Remove pagination information ("Showing 1 to N of N entries")
        "bInfo" : false,
        // Wrap search bar element in "text-center" div
        "dom": '<"text-center"f>i'
    });
}

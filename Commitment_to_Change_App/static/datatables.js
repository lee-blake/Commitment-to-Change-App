$(document).ready(function() {
    createStandardDataTable('#provider-course-datatable');
    createStandardDataTable('#provider-commitment-template-datatable');
    createStudentListDataTable('#clinician-course-student-datatable');
    createStudentListDataTable('#provider-course-student-datatable');

    // Trigger toggleBasedOnScreenSize on document ready
    toggleBasedOnScreenSize(400, '#course-student-datatable-container');
    // Trigger toggleBasedOnScreenSize on window "resize"
    $(window).on("resize", function() {
        toggleBasedOnScreenSize(400, '#course-student-datatable-container');
    });
});

// Toggle whether button or email link is shown
function toggleBasedOnScreenSize(tableWidthBreakpoint, container_id) {
    var containerWidth = $(container_id).width();
    $(".hide-when-smaller").toggle(containerWidth >= tableWidthBreakpoint);
    $(".show-when-smaller").toggle(containerWidth < tableWidthBreakpoint);
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

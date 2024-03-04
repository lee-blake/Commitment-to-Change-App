$(document).ready(function() {
    createStandardDataTable('#provider-course-datatable');
    createStandardDataTable('#provider-commitment-template-datatable');
    createStudentListDataTable('#clinician-course-view-datatable');
    createStudentListDataTable('#provider-course-view-datatable');
});

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
        // Allows DataTables to hide columns with a higher data-priority tag, based on screensize at generation
        "responsive": true,
        // Adds dt-center (DataTables class) to the mailto button column
        "columnDefs": [
            {"className": "dt-center", "targets": "#mailto-button-column"},
            { "orderable": false, "targets": "#mailto-button-column" }
        ],
    });
}


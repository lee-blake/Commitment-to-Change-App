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
        // Wrap search bar element in "text-center" div
        "dom": '<"text-center"f>i',
        // Allows DataTables to hide columns with a higher data-priority tag, based on screensize at generation
        "responsive": true,
        
        "columnDefs": [
            // Adds dt-center (DataTables class) to the mailto button column
            {"className": "dt-center", "targets": "#mailto-button-column"},
            // Remove sortability and sort arrow from mailto button column
            { "orderable": false, "targets": "#mailto-button-column" }
        ],
    });
}


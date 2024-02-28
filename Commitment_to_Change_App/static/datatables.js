$(document).ready(function() {
    $('#myTable').DataTable( {
        "autoWidth": false,
        "paging": false,
        "bInfo" : false,
        "columnDefs": [
        {"className": "dt-center", "targets": "_all"}
        ],
      });
});
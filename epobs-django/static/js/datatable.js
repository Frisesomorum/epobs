$(document).ready(function() {
  $('#datatable').DataTable( {
    columnDefs: [
      { targets: 'datatable-date', type: "date" },
      { targets: 'datatable-nondata', orderable: false, width:"1px", autoWidth: false }
    ],
    pageLength: 50,
    dom: "ftpB",
    buttons: [
      { extend: 'excel', className: 'btn-sm' },
      { extend: 'pdf', className: 'btn-sm' },
      { extend: 'csv', className: 'btn-sm' },
      { extend: 'copy', className: 'btn-sm' },
      { extend: 'print', className: 'btn-sm' },
    ]
  });
} );

$(document).ready(function() {
  $('#datatable-secondary').DataTable( {
    columnDefs: [
      { targets: 'datatable-nondata', orderable: false, width:"1px", autoWidth: false }
    ],
    paging: false,
    dom: "ftB",
    buttons: [
      { extend: 'excel', className: 'btn-sm' },
      { extend: 'pdf', className: 'btn-sm' },
      { extend: 'csv', className: 'btn-sm' },
      { extend: 'copy', className: 'btn-sm' },
      { extend: 'print', className: 'btn-sm' },
    ]
  });
} );

$(document).ready(function() {
  $('table.datatable-report').DataTable( {
    columnDefs: [
      { targets: 'datatable-nondata', width:"1px", autoWidth: false }
    ],
    ordering: false,
    paging: false,
    dom: "tB",
    buttons: [
      { extend: 'excel', className: 'btn-sm' },
      { extend: 'pdf', className: 'btn-sm' },
      { extend: 'csv', className: 'btn-sm' },
      { extend: 'copy', className: 'btn-sm' },
      { extend: 'print', className: 'btn-sm' },
    ]
  });
} );

$('table.datatable-report tbody').on('click', 'td.report-summary-toggle', function () {
    var parentId = this.id;
    var category = parentId.slice(parentId.lastIndexOf("-")+1);
    var childClass = 'report-child-row-' + category;
    var childRows = document.getElementsByClassName(childClass);
    if ( this.classList.contains('collapsed') ) {
      for (var i = 0; i < childRows.length; i++){
        childRows[i].style.display = 'table-row';
      }
      this.innerHTML = '<i class="fas fa-angle-down"></i>';
    }
    else {
      for (var i = 0; i < childRows.length; i++){
        childRows[i].style.display = 'none';
      }
      this.innerHTML = '<i class="fas fa-angle-right"></i>';
    }
    this.classList.toggle('collapsed');
} );

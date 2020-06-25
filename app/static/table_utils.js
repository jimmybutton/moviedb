window.operateEvents = {
  'click .like': function (e, value, row, index) {
    alert('You clicked like movie: ' + row.title)
  },
  'click .remove': function (e, value, row, index) {
    $table.bootstrapTable('remove', {
      field: 'id',
      values: [row.id]
    })
  }
}

$(document).ready(function () {

  var $table = $('#table')
  var $btnGetSelected = $('#btnGetSelected')

  // get selected rows and alert movie titles
  $btnGetSelected.click(function () {
    var list_of_names = $table.bootstrapTable('getSelections').map(
      function (element) { return element.title; }
    );
    // alert('getSelections: ' + JSON.stringify($table.bootstrapTable('getSelections')))
    alert('getSelections: ' + list_of_names)
  })

  // remove vertical borders
  $table.bootstrapTable('refreshOptions', {
    classes: 'table table-hover bg-white table-sm'
  })

  // adjust table height
  function adjustTableHeight() {
    let viewportHeight = $(window).height();
    let tableHeight = viewportHeight - 140;
    if (tableHeight < 480) {
      tableHeight = 480
    }
    $('#table').bootstrapTable('resetView', { height: tableHeight });
  }

  // if you want to apply the table height adjustment, copy this code into the html script of the page
  // adjustTableHeight();
  // $(window).resize(function () {
  //   adjustTableHeight();
  // });
});
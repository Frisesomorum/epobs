function initAll() {
  var amounts = {};
  $(".budget-item-amount").each(function( index ) {
    var id = this.id.split("-");
    var category = id[2];
    if (amounts[category]) {
      amounts[category] += Number(this.innerHTML);
    } else {
      amounts[category] = Number(this.innerHTML);
    }
  } );
  var totalExpenses = 0;
  var totalRevenues = 0;
  Object.keys(amounts).forEach(function (category) {
    var totalAmount = amounts[category].toFixed(2);
    var name = 'total-amount-' + category;
    var totals = document.getElementsByClassName(name);
    for (var i = 0; i < totals.length; i++){
      totals[i].innerHTML = totalAmount;
    }
    if (category !== 'rev'){
      totalExpenses += amounts[category];
    } else {
      totalRevenues = amounts[category];
    }
  } );
  document.getElementById('total-amount-exp').innerHTML = totalExpenses.toFixed(2);
  document.getElementById('total-amount-balance').innerHTML = (totalRevenues - totalExpenses).toFixed(2);
}

initAll();

$('.category-toggle').on('click', function () {
    var parentId = this.id;
    var category = parentId.slice(parentId.lastIndexOf("-")+1);
    var childClass = 'budget-item-' + category;
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

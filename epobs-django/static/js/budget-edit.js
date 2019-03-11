$('.budget-item-amount').change(function() {
  var category = this.name.split("-")[0];
  update(category);
  updateSummaries();
});
$('.budget-item-amount').on('keyup', function() {
  var category = this.name.split("-")[0];
  update(category);
  updateSummaries();
});

function update(category) {
  var total = 0;
  $( ".budget-item-amount-" + category ).each(function( index ) {
    total += Number(this.value);
  } );
  document.getElementById('total-amount-' + category).innerHTML = total.toFixed(2);
}

function updateAll() {
  $( ".total-amount" ).each(function( index ) {
    var id = this.id;
    var category = id.slice(id.lastIndexOf("-")+1);
    update(category);
  } );
  updateSummaries();
}

function updateSummaries() {
  var totalExpenses = 0;
  var totalRevenues = 0;
  $( ".total-amount" ).each(function( index ) {
    var id = this.id;
    var category = id.slice(id.lastIndexOf("-")+1);
    if (category !== 'rev'){
      totalExpenses += Number(this.innerHTML);
    } else {
      totalRevenues = Number(this.innerHTML);
    }
  } );
  document.getElementById('summary-exp').innerHTML = totalExpenses.toFixed(2);
  document.getElementById('summary-rev').innerHTML = totalRevenues.toFixed(2);
  document.getElementById('summary-balance').innerHTML = (totalRevenues - totalExpenses).toFixed(2);
}

updateAll();

$('.category-toggle').on('click', function () {
    var parentId = this.id;
    var cat_id = parentId.slice(parentId.lastIndexOf("-")+1);
    var childDiv = document.getElementById('budget-items-' + cat_id);
    if ( this.classList.contains('collapsed') ) {
      childDiv.style.display = 'block';
      this.innerHTML = '<i class="fas fa-angle-down"></i>';
    }
    else {
      childDiv.style.display = 'none';
      this.innerHTML = '<i class="fas fa-angle-right"></i>';
    }
    this.classList.toggle('collapsed');
} );

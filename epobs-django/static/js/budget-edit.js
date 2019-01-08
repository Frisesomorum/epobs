$('.budget-item-amount').change(function() {
  var category = this.name.split("-")[0];
  update(category);
});
$('.budget-item-amount').on('keyup', function() {
  var category = this.name.split("-")[0];
  update(category);
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

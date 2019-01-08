$('#id_category').change(function() {
  filterLedgerAccountsByCategory(this.value);
});
$('#id_category').on('keyup', function() {
  filterLedgerAccountsByCategory(this.value);
});

function filterLedgerAccountsByCategory(category) {
  var sortedOptions = [];

  if (category) {
    var restOfOptions = [];
    $('#id_ledger_account > option').each(function() {
      if ($(this).attr('la_category') == category) {
        $(this).css("color", "black");
        sortedOptions.push($(this));
      } else {
        $(this).css("color", "silver");
        restOfOptions.push($(this));
      }
    });
    restOfOptions.sort(function(a,b){
        return a.val()-b.val();
    });
    sortedOptions = sortedOptions.concat(restOfOptions);
  } else {
    $('#id_ledger_account > option').each(function() {
      $(this).css("color", "black");
      sortedOptions.push($(this));
    });
    sortedOptions.sort(function(a,b){
        return a.val()-b.val();
    });
  }

  var selectedOption = $('#id_ledger_account').val();
  $("#id_ledger_account").empty().append(sortedOptions);
  $('#id_ledger_account').val(selectedOption);
}

$('.amount-factor').change(function() {
    update();
});
$('.amount-factor').on('keyup', function() {
    update();
});

function update() {
  var quantity = Number($('#id_quantity').val());
  var unit_cost = Number($('#id_unit_cost').val());
  var discount = Number($('#id_discount').val());
  var tax = Number($('#id_tax').val());
  var amount = (quantity * unit_cost) - discount + tax;
  document.getElementById('total-amount').innerHTML = amount;
}

update();

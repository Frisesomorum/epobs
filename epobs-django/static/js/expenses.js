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

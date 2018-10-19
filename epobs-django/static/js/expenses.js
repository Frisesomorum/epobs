$('#id_quantity').change(function() {
    update();
});
$('#id_unit_cost').change(function() {
    update();
});
$('#id_discount').change(function() {
    update();
});
$('#id_tax').change(function() {
    update();
});
$('#id_quantity').on('keyup', function() {
    update();
});
$('#id_unit_cost').on('keyup', function() {
    update();
});
$('#id_discount').on('keyup', function() {
    update();
});
$('#id_tax').on('keyup', function() {
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

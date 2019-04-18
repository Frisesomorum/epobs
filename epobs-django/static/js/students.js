$('#id_graduating_class').change(function() {
  setGraduatingYear($(this).find(':selected').attr('graduating_year'));
});
$('#id_graduating_class').on('keyup', function() {
  setGraduatingYear($(this).find(':selected').attr('graduating_year'));
});

function setGraduatingYear(graduatingClass) {
  if (graduatingClass) {
    $('#id_graduating_year').val(graduatingClass);
  }
}

$('#id_graduating_year').change(function() {
  setGraduatingClass(this.value);
});

function setGraduatingClass(graduatingYear) {
  if (graduatingYear) {
    foundMatch = false;
    $('#id_graduating_class > option').each(function() {
      if ($(this).attr('graduating_year') == graduatingYear) {
        selectedOption = $(this).val();
        $('#id_graduating_class').val(selectedOption).change();
        foundMatch = true;
      }
    });
    if (foundMatch) {
      return;
    }
  }
  $('#id_graduating_class').val('').change();
}

$('#id_graduating_year').change();

$(document).ready(function () {

  //Phone number form functionality
  let phoneNumberInput = $('#id_phone_number');

  // API
  $("#contact-form").submit(function (event) {
    event.preventDefault();
    let data = {
      'phone_number': '+7' + phoneNumberInput.inputmask('unmaskedvalue'),
    };

    $.ajax({
      url: '/api/order_create/',
      type: 'POST',
      data: JSON.stringify(data),
      contentType: 'application/json',
      success: function (response) {
        $("#submitSuccessMessage").removeClass('d-none');
      },
      error: function (error) {
        $("#submitErrorMessage").removeClass('d-none');
      }
    });
  });

  // Phone number validation
  phoneNumberInput.inputmask("+7 (999) 999 99-99");
  phoneNumberInput.on('input', function (event) {
    if (phoneNumberInput.inputmask("isComplete")){
      $("#submitButton").removeClass('disabled')
    } else {
      $("#submitButton").addClass('disabled')
    }
  })

  //

});
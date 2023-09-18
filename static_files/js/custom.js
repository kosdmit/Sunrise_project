// Gets csrf token from cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');


$(document).ready(function () {

  //Phone number form functionality
  let phoneNumberInput = $('#id_phone_number');

  // API
  $("#contact-form").submit(function (event) {
    event.preventDefault();
    let phoneNumber = '+7' + phoneNumberInput.inputmask('unmaskedvalue')
    console.log('sending phone number: ' + phoneNumber)


    $.ajax({
      headers: {'X-CSRFToken': csrftoken},
      url: '/api/order_create/',
      type: 'POST',
      data: {
        'phone_number': phoneNumber,
      },
      success: function (response) {
        $("#submitSuccessMessage").removeClass('d-none');
        $("#submitErrorMessage").addClass('d-none');
      },
      error: function (error) {
        $("#submitErrorMessage").removeClass('d-none');
        $("#submitSuccessMessage").addClass('d-none');
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


  // Masonry Grid activation
  let $masonryGrid = $('.masonry-grid').masonry({
      itemSelector: '.grid-item',
      columnWidth: '.grid-sizer',
      percentPosition: true,
      // nicer reveal transition
      visibleStyle: { transform: 'translateY(0)', opacity: 1 },
      hiddenStyle: { transform: 'translateY(100px)', opacity: 0 },
  });
  // get Masonry instance
  let msnry = $masonryGrid.data('masonry');

  // init Infinite Scroll
  $masonryGrid.infiniteScroll({
    path: '.next-page-link',
    append: '.grid-item',
    outlayer: msnry,
    scrollThreshold: false,
    history: false,
    hideNav: '.pagination',
    status: '.page-load-status',
    button: '.view-more-button',
    debug: true,

  });

});
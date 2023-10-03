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


  // API
  $("form[name='contact-form']").each(function () {
    $(this).submit(function (event) {
      event.preventDefault();
      let phoneNumberInput = $(this).find('input[name="phone_number"]');
      let phoneNumber = '+7' + phoneNumberInput.inputmask('unmaskedvalue')
      let customerName = $(this).find('input[name="customer_name"]').val()
      let tariffSlug = $(this).attr('data-tariff-slug')
      console.log('sending phone number: ' + phoneNumber)
      console.log('sending customer name: ' + customerName)
      console.log('sending tariff slug: ' + tariffSlug)


      $.ajax({
        headers: {'X-CSRFToken': csrftoken},
        url: '/api/order_create/',
        type: 'POST',
        data: {
          'phone_number': phoneNumber,
          'customer_name': customerName,
          'tariff_slug': tariffSlug,
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
  })

  // Phone number validation
  $('input[name="phone_number"]').each(function () {
    $(this).inputmask("+7 (999) 999 99-99");
    $(this).on('input', function (event) {
      if ($(this).inputmask("isComplete")){
        $(this).closest('form').find('button[name="submitButton"]').removeClass('disabled')
      } else {
        $(this).closest('form').find('button[name="submitButton"]').addClass('disabled')
      }
    })
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

  // Fix for doubling request and process buttons
  let $viewMoreButton = $('.view-more-button')
  let lastPageFlag = false

  $masonryGrid.on( 'request.infiniteScroll', function( event, path, fetchPromise ) {
    console.log(`Loading page: ${path}`);
    $viewMoreButton.hide()
  });
  $masonryGrid.on( 'last.infiniteScroll', function( event, body, path ) {
    console.log(`Last page hit on ${path}`);
    $viewMoreButton.hide()
    lastPageFlag = true
  });
  $masonryGrid.on( 'append.infiniteScroll', function( event, body, path, items, response ) {
    console.log(`Appended ${items.length} items on ${path}`);
    if (!lastPageFlag) {
      $viewMoreButton.show()
    }
  });



  // goTariffsButton functionality
  function addTariffsButton () {
    $('button[name="goTariffsButton"]').each(function () {
      let button = $(this);
      let modalElement = button.closest('.modal')[0];
      let modal = new bootstrap.Modal(modalElement);

      button.click(function () {
        modal.hide();
        modalElement.addEventListener('hidden.bs.modal', function (event) {
          // Scroll to the desired section
          $("html, body").animate({
            scrollTop: $("#tariffs").offset().top
          }, 0); // The "0" is the duration in milliseconds it will take to scroll to the section.
        }, {once: true}); // This ensures the listener is removed after being executed once

      });
    });
  }
  addTariffsButton()
  $masonryGrid.on( 'append.infiniteScroll', function( event, body, path, items, response ) {
    addTariffsButton()
  });


  // Set fixed background image size for prising section
  function setFixedBackground () {
    console.log($(window).width())
    let $pricingContainer = $('#tariffs div.pricing-bg');
    let containerHeight = $pricingContainer.innerHeight();
    console.log(containerHeight)
    if ($(window).width() < 992) {
      $pricingContainer.css(
          'background',
          `linear-gradient(to bottom, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.5) calc(${containerHeight}px - 25%), rgb(0,0,0) ${containerHeight}px, rgb(0,0,0) 100%)`);
      let styleContent = `
          #tariffs div.pricing-bg::before {
              background-position: top;
              background-size: auto ${containerHeight}px;
          }
      `;
      $('<style>').text(styleContent).appendTo('head');
    } else {
      $pricingContainer.css(
          'background',
          `linear-gradient(to bottom, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.5) 75%, rgb(0,0,0) 100%)`);
      let styleContent = `
          #tariffs div.pricing-bg::before {
              background-position: center;
              background-size: cover;
          }
      `;
      $('<style>').text(styleContent).appendTo('head');
    }

  }
  setFixedBackground();
  var lastWindowWidth = $(window).width();
  $(window).resize(function() {
    var currentWindowWidth = $(window).width();
    if (lastWindowWidth !== currentWindowWidth) {
        setFixedBackground();
        lastWindowWidth = currentWindowWidth;
    }
  });


  // Animation for detailButton of pricing cards
  $('button[name="detailsButton"], button[data-bs-target="#tariffsComparing"]').each(function () {
    $(this).click(function () {
      let $icon = $(this).children('svg')
      // Get current rotation state. If undefined, set to 0.
      let currentRotation = $(this).data('rotation') || 0;
      // Toggle between 0 and 180 degrees.
      let newRotation = (currentRotation == 0) ? 180 : 0;
      $icon.css({
          "transform": "rotate(" + newRotation + "deg)",
          "transition": "0.35s ease"
      });
      // Store the new rotation state.
      $(this).data('rotation', newRotation);
    })
  })


  // Category buttons functionality
  let url_string = window.location.href
  let url = new URL(url_string);
  let category_slug = url.searchParams.get("category");
  if (category_slug !== null) {
    $('#category-button-all').removeClass('active');
    $('#category-button-' + category_slug).addClass('active');
    $('#category-dropdown-item-all').removeClass('active');
    $('#category-dropdown-item-' + category_slug).addClass('active');
  }


  // Different content for order-modal
  const orderModal = document.getElementById('order-modal')
  if (orderModal) {
    orderModal.addEventListener('show.bs.modal', event => {
      // Button that triggered the modal
      const button = event.relatedTarget
      // Extract info from data-bs-* attributes
      const tariffSlug = button.getAttribute('data-bs-whatever')
      // If necessary, you could initiate an Ajax request here
      // and then do the updating in a callback.

      // Update the modal's content.
      const modalContactForm = orderModal.querySelector('#modal-contact-form')

      modalContactForm.setAttribute('data-tariff-slug', tariffSlug)
    })
  }

});
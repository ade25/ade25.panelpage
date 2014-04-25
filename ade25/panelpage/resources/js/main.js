/*global jQuery:false, document:false */
'use strict';

(function ($) {

  $(document).ready(function () {

    $('a[data-appui="contextmenu"]').on({
      click: function (e) {
        e.preventDefault();
        var $contextMenu = $(this).data('target');
        $contextMenu.toggleClass('cbp-spmenu-open');
      }
    });
    $('a[data-appui="contextmenu-close"]').on({
      click: function (e) {
        e.preventDefault();
        $(this).closest('.panelpage-slide').removeClass('cbp-spmenu-open');
      }
    });
    $('div[data-appui="editable"]').on({
      mouseenter: function () {
        $(this).find('.contentpanel-editbar')
          .removeClass('fadeOutUp')
          .addClass('fadeInLeft')
          .show();
      },
      mouseleave: function () {
        $(this).find('.contentpanel-editbar')
          .removeClass('fadeInLeft')
          .addClass('fadeOutUp');
      }
    });
    var $sortableSection = $('.ppe-section-sortable').sortable({
      items: '.ppe-block-sortable',
      handle: '.ppe-dragindicator'
    });
    if ($sortableSection.length) {
      $sortableSection.on('sortupdate', function () {
        var $ajaxTarget = $sortableSection.data('appui-ajax-uri'),
            $data = $('#ppe-form-rearrange').serializeArray();
        $.ajax({
          url: $ajaxTarget,
          data: $data,
          context: document.body,
          success: function (data) {
            if (data.success === true) {
              var $message = data.message,
                  $htmlString = '<p class="text-warning">' + $message + '</p>';
              $('#ppe-statusinfo-content').append($htmlString).removeClass('hidden').slideDown('slow');
            } else {
              // This could be nicer in the future...
              console.log('Form could not be submitted. Bummer.');
            }
          }
        });
      });
    }
  }
        );
}(jQuery));

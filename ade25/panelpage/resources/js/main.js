/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false */
'use strict';

(function ($) {
    $(document).ready(function () {

        var $sortableSection = $('.ppe-section-sortable').sortable({
            items: '.ppe-block-sortable',
            handle: '.ppe-dragindicator'
        });
        if ($sortableSection.length) {
            $sortableSection.on('sortupdate', function () {
                var $ajaxTarget = $sortableSection.data('appui-ajax-uri');
                var $data = $('#ppe-form-rearrange').serializeArray();
                $.ajax({
                    url: $ajaxTarget,
                    data: $data,
                    context: document.body,
                    success: function (data) {
                        if (data.success === true) {
                            var $message = data.message;
                            var $htmlString = '<p class="text-warning">' + $message + '</p>';
                            $('#ppe-statusinfo').append($htmlString).removeClass('hide').slideDown('slow');
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

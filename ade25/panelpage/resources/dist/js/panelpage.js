/*!
* panelpage by Ade25
* Copyright Ade25
* Licensed under MIT.
*
* Designed and built by ade25
*/
if (typeof jQuery === "undefined") { throw new Error("We require jQuery") }

/*
 * HTML5 Sortable jQuery Plugin
 * http://farhadi.ir/projects/html5sortable
 * 
 * Copyright 2012, Ali Farhadi
 * Released under the MIT license.
 */
(function($) {
var dragging, placeholders = $();
$.fn.sortable = function(options) {
	var method = String(options);
	options = $.extend({
		connectWith: false
	}, options);
	return this.each(function() {
		if (/^enable|disable|destroy$/.test(method)) {
			var items = $(this).children($(this).data('items')).attr('draggable', method == 'enable');
			if (method == 'destroy') {
				items.add(this).removeData('connectWith items')
					.off('dragstart.h5s dragend.h5s selectstart.h5s dragover.h5s dragenter.h5s drop.h5s');
			}
			return;
		}
		var isHandle, index, items = $(this).children(options.items);
		var placeholder = $('<' + (/^ul|ol$/i.test(this.tagName) ? 'li' : 'div') + ' class="sortable-placeholder">');
		items.find(options.handle).mousedown(function() {
			isHandle = true;
		}).mouseup(function() {
			isHandle = false;
		});
		$(this).data('items', options.items)
		placeholders = placeholders.add(placeholder);
		if (options.connectWith) {
			$(options.connectWith).add(this).data('connectWith', options.connectWith);
		}
		items.attr('draggable', 'true').on('dragstart.h5s', function(e) {
			if (options.handle && !isHandle) {
				return false;
			}
			isHandle = false;
			var dt = e.originalEvent.dataTransfer;
			dt.effectAllowed = 'move';
			dt.setData('Text', 'dummy');
			index = (dragging = $(this)).addClass('sortable-dragging').index();
		}).on('dragend.h5s', function() {
			if (!dragging) {
				return;
			}
			dragging.removeClass('sortable-dragging').show();
			placeholders.detach();
			if (index != dragging.index()) {
				dragging.parent().trigger('sortupdate', {item: dragging});
			}
			dragging = null;
		}).not('a[href], img').on('selectstart.h5s', function() {
			this.dragDrop && this.dragDrop();
			return false;
		}).end().add([this, placeholder]).on('dragover.h5s dragenter.h5s drop.h5s', function(e) {
			if (!items.is(dragging) && options.connectWith !== $(dragging).parent().data('connectWith')) {
				return true;
			}
			if (e.type == 'drop') {
				e.stopPropagation();
				placeholders.filter(':visible').after(dragging);
				dragging.trigger('dragend.h5s');
				return false;
			}
			e.preventDefault();
			e.originalEvent.dataTransfer.dropEffect = 'move';
			if (items.is(this)) {
				if (options.forcePlaceholderSize) {
					placeholder.height(dragging.outerHeight());
				}
				dragging.hide();
				$(this)[placeholder.index() < $(this).index() ? 'after' : 'before'](placeholder);
				placeholders.not(placeholder).detach();
			} else if (!placeholders.is(this) && !$(this).children(options.items).length) {
				placeholders.detach();
				$(this).append(placeholder);
			}
			return false;
		});
	});
};
})(jQuery);

/*global jQuery:false, document:false */
'use strict';

(function ($) {

  $(document).ready(function () {
    //var DemoGrid = {
    //    currentSize: 3,
    //};
    //$('#grid').gridList({
    //    rows: DemoGrid.currentSize,
    //    widthHeightRatio: 264 / 294,
    //    heightToFontSizeRatio: 0.25,
    //    onChange: function (changedItems) {
    //        DemoGrid.flashItems(changedItems);
    //    }
    //});
    //$('#grid li .resize').click(function (e) {
    //    e.preventDefault();
    //    var itemElement = $(e.currentTarget).closest('li'),
    //        itemSize = $(e.currentTarget).data('size');
    //    $('#grid').gridList('resizeItem', itemElement, itemSize);
    //});
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

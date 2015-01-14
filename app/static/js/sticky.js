(function() {
  var reset_scroll;

  $(function() {
    return $("[data-sticky_column]").stick_in_parent({
      parent: "[data-sticky_parent]"
    });
  });

  reset_scroll = function() {
    var scroller;
    scroller = $("body,html");
    scroller.stop(true);
    if ($(window).scrollTop() !== 0) {
      scroller.animate({
        scrollTop: 0
      }, "fast");
    }
    return scroller;
  };

  window.scroll_it = function() {
    var max;
    max = $(document).height() - $(window).height();
    return reset_scroll().animate({
      scrollTop: max
    }, max * 3).delay(100).animate({
      scrollTop: 0
    }, max * 3);
  };

  window.scroll_it_wobble = function() {
    var max, third;
    max = $(document).height() - $(window).height();
    third = Math.floor(max / 3);
    return reset_scroll().animate({
      scrollTop: third * 2
    }, max * 3).delay(100).animate({
      scrollTop: third
    }, max * 3).delay(100).animate({
      scrollTop: max
    }, max * 3).delay(100).animate({
      scrollTop: 0
    }, max * 3);
  };

  $(window).on("resize", (function(_this) {
    return function(e) {
      return $(document.body).trigger("sticky_kit:recalc");
    };
  })(this));

}).call(this);

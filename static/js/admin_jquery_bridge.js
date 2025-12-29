// Ensure select2 (loaded afterwards) finds a global jQuery by bridging django.jQuery to window.jQuery
(function(){
  try {
    if (typeof window !== 'undefined' && window.django && window.django.jQuery && !window.jQuery) {
      window.jQuery = window.django.jQuery;
    }
  } catch(e) { console.warn('admin_jquery_bridge failed', e); }
})();

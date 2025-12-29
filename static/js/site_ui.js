// site_ui.js - small dynamic enhancements: fade-in on scroll, smooth anchor scroll, lazy load images
(function(){
  function fadeInOnScroll(){
    var els = document.querySelectorAll('.fade-in');
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){ if(e.isIntersecting) e.target.classList.add('visible'); });
    }, { threshold: 0.1 });
    els.forEach(function(el){ io.observe(el); });
  }

  function smoothAnchors(){
    document.addEventListener('click', function(e){
      var a = e.target.closest('a[href^="#"]');
      if(!a) return;
      var id = a.getAttribute('href').slice(1);
      var target = document.getElementById(id);
      if(target){ e.preventDefault(); target.scrollIntoView({behavior:'smooth'}); }
    });
  }

  function lazyLoadImages(){
    var imgs = document.querySelectorAll('img[data-src]');
    if('IntersectionObserver' in window){
      var io = new IntersectionObserver(function(entries){
        entries.forEach(function(entry){
          if(entry.isIntersecting){
            var img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            img.classList.remove('lazy-img');
            io.unobserve(img);
          }
        });
      });
      imgs.forEach(function(img){ io.observe(img); });
    } else {
      imgs.forEach(function(img){ img.src = img.dataset.src; img.classList.remove('lazy-img'); });
    }
  }

  document.addEventListener('DOMContentLoaded', function(){
    fadeInOnScroll(); smoothAnchors(); lazyLoadImages();
  });
})();

// animations.js - Enhanced dynamic visual effects for the site
(function(){
  // 1. 页面元素渐入与上升动画
  function initFadeInElements(){
    var elements = document.querySelectorAll('.fade-in, .article-card, h1, h2');
    if(!window.IntersectionObserver) return;
    
    var observer = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    
    elements.forEach(function(el){ observer.observe(el); });
  }

  // 2. 按钮与链接悬停特效
  function initHoverEffects(){
    document.addEventListener('mouseover', function(e){
      var btn = e.target.closest('a, button, .btn, .card');
      if(!btn) return;
      btn.style.transition = 'all 0.3s cubic-bezier(0.4,0,0.2,1)';
    });
  }

  // 3. 滚动条视觉反馈
  function initScrollProgress(){
    var progressBar = document.createElement('div');
    progressBar.style.cssText = 'position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,#ff4081,#7873f5);z-index:999;transition:width 0.2s ease;';
    document.body.appendChild(progressBar);
    
    window.addEventListener('scroll', function(){
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var scrollPercent = (scrollTop / docHeight) * 100;
      progressBar.style.width = scrollPercent + '%';
    });
  }

  // 4. 平滑滚动锚点
  function initSmoothScroll(){
    document.addEventListener('click', function(e){
      var a = e.target.closest('a[href^="#"]');
      if(!a) return;
      e.preventDefault();
      var id = a.getAttribute('href').slice(1);
      var target = document.getElementById(id);
      if(target){
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }

  // 5. 表单输入焦点效果
  function initFormEffects(){
    var inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(function(inp){
      inp.addEventListener('focus', function(){
        this.style.boxShadow = '0 0 0 3px rgba(255,64,129,0.15)';
        this.style.transform = 'scale(1.01)';
      });
      inp.addEventListener('blur', function(){
        this.style.boxShadow = '';
        this.style.transform = '';
      });
    });
  }

  // 6. 文章卡片交互动画
  function initCardAnimations(){
    var cards = document.querySelectorAll('.article-card, .card');
    cards.forEach(function(card){
      card.addEventListener('mouseenter', function(){
        this.style.transform = 'translateY(-8px) scale(1.01)';
        this.style.boxShadow = '0 12px 24px rgba(0,0,0,0.15)';
      });
      card.addEventListener('mouseleave', function(){
        this.style.transform = '';
        this.style.boxShadow = '';
      });
    });
  }

  // 7. 加载动画（页面加载完成后隐藏）
  function initPageLoadAnimation(){
    var loader = document.getElementById('page-loader');
    if(loader){
      window.addEventListener('load', function(){
        loader.style.opacity = '0';
        loader.style.transition = 'opacity 0.5s ease';
        setTimeout(function(){ loader.style.display = 'none'; }, 500);
      });
    }
  }

  // 8. 按钮点击波纹效果
  function initRippleEffect(){
    document.addEventListener('click', function(e){
      var btn = e.target.closest('.btn, a');
      if(!btn) return;
      
      var rect = btn.getBoundingClientRect();
      var ripple = document.createElement('span');
      ripple.style.cssText = 'position:absolute;border-radius:50%;background:rgba(255,255,255,0.6);transform:scale(0);animation:ripple 0.6s ease-out;';
      
      var size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size/2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size/2) + 'px';
      
      btn.style.position = 'relative';
      btn.style.overflow = 'hidden';
      btn.appendChild(ripple);
      
      setTimeout(function(){ ripple.remove(); }, 600);
    });
  }

  // CSS 动画定义
  var style = document.createElement('style');
  style.textContent = `
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes ripple {
      to { transform: scale(4); opacity: 0; }
    }
    @keyframes slideIn {
      from { opacity: 0; transform: translateX(-20px); }
      to { opacity: 1; transform: translateX(0); }
    }
    * { transition-property: background-color, border-color, color, fill, stroke; }
  `;
  document.head.appendChild(style);

  // 初始化所有动画
  document.addEventListener('DOMContentLoaded', function(){
    initFadeInElements();
    initHoverEffects();
    initScrollProgress();
    initSmoothScroll();
    initFormEffects();
    initCardAnimations();
    initPageLoadAnimation();
    initRippleEffect();
  });
})();

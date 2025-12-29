// enhanced_animations.js - 高级动画与交互效果库
(function(){
  // 防抖函数
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // 1. 页面加载进度条
  function initProgressBar(){
    const bar = document.createElement('div');
    bar.id = 'progress-bar';
    bar.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, #ff4081, #7873f5, #42e695);
      z-index: 10000;
      transition: width 0.3s ease;
      width: 0%;
      box-shadow: 0 0 10px rgba(255, 64, 129, 0.5);
    `;
    document.body.appendChild(bar);

    let current = 0;
    const increment = () => {
      current += Math.random() * 30;
      if(current > 90) current = 90;
      bar.style.width = current + '%';
    };

    const complete = () => {
      current = 100;
      bar.style.width = '100%';
      setTimeout(() => { bar.style.opacity = '0'; }, 300);
    };

    window.addEventListener('load', complete);
    const timer = setInterval(increment, 500);
    setTimeout(complete, 3000);
  }

  // 2. 鼠标跟随光标效果
  function initFollowCursor(){
    const cursor = document.createElement('div');
    cursor.style.cssText = `
      position: fixed;
      width: 20px;
      height: 20px;
      border: 2px solid rgba(255, 64, 129, 0.5);
      border-radius: 50%;
      pointer-events: none;
      z-index: 9999;
      transition: all 0.1s ease-out;
      display: none;
    `;
    document.body.appendChild(cursor);

    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      cursor.style.display = 'block';
      cursor.style.left = (mouseX - 10) + 'px';
      cursor.style.top = (mouseY - 10) + 'px';
    });

    document.addEventListener('mouseleave', () => {
      cursor.style.display = 'none';
    });
  }

  // 3. 侧边栏粘性导航指示器
  function initNavIndicator(){
    const headings = document.querySelectorAll('h2, h3');
    if(headings.length < 2) return;

    const nav = document.createElement('nav');
    nav.id = 'toc-nav';
    nav.style.cssText = `
      position: fixed;
      right: 20px;
      top: 100px;
      max-width: 200px;
      background: rgba(255, 255, 255, 0.9);
      padding: 1rem;
      border-radius: 0.5rem;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      font-size: 0.9rem;
      max-height: 60vh;
      overflow-y: auto;
      display: none;
    `;

    const list = document.createElement('ul');
    list.style.cssText = 'list-style: none; padding: 0; margin: 0;';

    headings.forEach((h, i) => {
      h.id = h.id || 'heading-' + i;
      const li = document.createElement('li');
      li.style.cssText = `padding: 0.25rem 0; margin-left: ${(h.tagName === 'H3' ? 1 : 0)}rem;`;
      const a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      a.style.cssText = `
        text-decoration: none;
        color: var(--text-light);
        transition: all 0.2s ease;
        display: block;
        padding: 0.25rem 0.5rem;
        border-left: 2px solid transparent;
      `;
      a.addEventListener('mouseenter', function(){
        this.style.color = 'var(--primary)';
        this.style.borderLeftColor = 'var(--primary)';
      });
      a.addEventListener('mouseleave', function(){
        this.style.color = 'var(--text-light)';
        this.style.borderLeftColor = 'transparent';
      });
      li.appendChild(a);
      list.appendChild(li);
    });

    nav.appendChild(list);
    document.body.appendChild(nav);

    // 在文章内容较长时显示
    window.addEventListener('scroll', debounce(() => {
      if(document.body.scrollHeight > 1000){
        nav.style.display = 'block';
      }
    }, 100));
  }

  // 4. 段落延迟显示动画
  function initParagraphAnimation(){
    const paragraphs = document.querySelectorAll('p, li, .card');
    if(!window.IntersectionObserver) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if(entry.isIntersecting){
          entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -100px 0px' });

    paragraphs.forEach((p, i) => {
      if(!p.style.animation) {
        p.style.opacity = '0';
        p.style.animationDelay = (i * 0.05) + 's';
        observer.observe(p);
      }
    });
  }

  // 5. 按钮按下反馈（震动）
  function initButtonFeedback(){
    document.addEventListener('click', function(e){
      const btn = e.target.closest('button, a.btn, .btn');
      if(!btn) return;

      // 创建涟漪效果
      const ripple = document.createElement('span');
      const rect = btn.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      
      ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.8), rgba(255,255,255,0));
        width: ${size}px;
        height: ${size}px;
        left: ${e.clientX - rect.left - size/2}px;
        top: ${e.clientY - rect.top - size/2}px;
        animation: ripple-wave 0.6s ease-out;
        pointer-events: none;
      `;

      btn.style.position = 'relative';
      btn.style.overflow = 'hidden';
      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  }

  // 6. 页面滚动高度指示
  function initScrollGauge(){
    const gauge = document.createElement('div');
    gauge.style.cssText = `
      position: fixed;
      bottom: 30px;
      right: 30px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: conic-gradient(var(--primary) 0deg, var(--primary) var(--progress), #eee var(--progress));
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.8rem;
      font-weight: bold;
      color: var(--primary);
      z-index: 1000;
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
      --progress: 0deg;
    `;
    gauge.id = 'scroll-gauge';
    document.body.appendChild(gauge);

    window.addEventListener('scroll', debounce(() => {
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrolled = window.scrollY;
      const percent = (scrolled / scrollHeight) * 360;
      gauge.style.setProperty('--progress', percent + 'deg');
      gauge.style.opacity = scrolled > 500 ? '1' : '0';
      gauge.textContent = Math.round((scrolled / scrollHeight) * 100) + '%';
    }, 50));
  }

  // 7. 动画CSS定义
  function injectAnimations(){
    const style = document.createElement('style');
    style.textContent = `
      @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
      }
      @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
      }
      @keyframes ripple-wave {
        to { transform: scale(4); opacity: 0; }
      }
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
      }
      @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
      }
      @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(255,64,129,0.5); }
        50% { box-shadow: 0 0 20px rgba(255,64,129,0.8); }
      }
    `;
    document.head.appendChild(style);
  }

  // 初始化
  document.addEventListener('DOMContentLoaded', () => {
    injectAnimations();
    initProgressBar();
    // initFollowCursor(); // 可选：开启鼠标跟随
    initNavIndicator();
    initParagraphAnimation();
    initButtonFeedback();
    initScrollGauge();
  });
})();

// micro_interactions.js - 微交互与细节动画
(function(){
  // 1. 输入框焦点特效
  function initFormMicroInteractions(){
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], textarea, select');
    
    inputs.forEach(input => {
      const wrapper = input.parentElement;
      
      input.addEventListener('focus', function(){
        this.style.transform = 'scale(1.01)';
        this.style.boxShadow = '0 0 0 3px rgba(255,64,129,0.15)';
        if(this.previousElementSibling?.tagName === 'LABEL'){
          this.previousElementSibling.style.color = 'var(--primary)';
          this.previousElementSibling.style.transform = 'translateY(-2px)';
        }
      });
      
      input.addEventListener('blur', function(){
        this.style.transform = '';
        this.style.boxShadow = '';
        if(this.previousElementSibling?.tagName === 'LABEL'){
          this.previousElementSibling.style.color = '';
          this.previousElementSibling.style.transform = '';
        }
      });
    });
  }

  // 2. 链接悬停效果
  function initLinkEffects(){
    const links = document.querySelectorAll('a:not([role="tab"])');
    
    links.forEach(link => {
      // 检查是否已是导航链接（跳过导航栏链接）
      if(link.closest('nav')) return;
      
      const originalColor = window.getComputedStyle(link).color;
      
      link.addEventListener('mouseenter', function(){
        this.style.transition = 'all 0.2s ease';
        this.style.textDecoration = 'underline';
        this.style.textDecorationColor = 'rgba(255,64,129,0.5)';
      });
      
      link.addEventListener('mouseleave', function(){
        this.style.textDecoration = '';
        this.style.textDecorationColor = '';
      });
    });
  }

  // 3. 卡片层级深度效果
  function initCardDepthEffect(){
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
      card.addEventListener('mouseenter', function(){
        this.style.transform = 'translateY(-8px) scale(1.01)';
        this.style.boxShadow = '0 16px 32px rgba(0,0,0,0.15)';
      });
      
      card.addEventListener('mouseleave', function(){
        this.style.transform = '';
        this.style.boxShadow = '';
      });
    });
  }

  // 4. 侧边栏导航指示器
  function initNavHighlight(){
    const navLinks = document.querySelectorAll('a.nav-link');
    const updateActiveLink = () => {
      navLinks.forEach(link => {
        link.style.position = 'relative';
        
        // 判断当前页面
        const href = link.getAttribute('href');
        const pathname = window.location.pathname;
        
        if(href && pathname.includes(href.replace(/^\//, ''))){
          link.style.color = 'var(--primary)';
          link.style.fontWeight = '600';
          
          // 添加下划线动画
          const underline = document.createElement('span');
          underline.style.cssText = `
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 100%;
            height: 2px;
            background: var(--primary);
            border-radius: 1px;
            animation: slideInLeft 0.3s ease-out;
          `;
          
          if(!link.querySelector('span[style*="position"]')){
            link.appendChild(underline);
          }
        }
      });
    };
    
    updateActiveLink();
  }

  // 5. 段落首字大写装饰
  function initFirstLetterStyle(){
    const articles = document.querySelectorAll('article');
    
    articles.forEach(article => {
      const firstP = article.querySelector('p:first-of-type');
      if(!firstP) return;
      
      const text = firstP.textContent;
      if(text.length > 0){
        const firstLetter = text[0];
        const rest = text.slice(1);
        
        firstP.innerHTML = `<span style="
          font-size: 2rem;
          font-weight: 700;
          color: var(--primary);
          float: left;
          line-height: 1;
          margin-right: 0.2rem;
          margin-top: 0.1rem;
        ">${firstLetter}</span>${rest}`;
      }
    });
  }

  // 6. 滚动时的数字统计动画
  function initStatisticAnimation(){
    const stats = document.querySelectorAll('[data-stat]');
    if(!window.IntersectionObserver || stats.length === 0) return;
    
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if(entry.isIntersecting){
          const el = entry.target;
          const max = parseInt(el.dataset.stat);
          let current = 0;
          const speed = max / 30; // 30帧动画
          
          const animate = () => {
            current += speed;
            if(current > max) current = max;
            el.textContent = Math.round(current);
            if(current < max) requestAnimationFrame(animate);
          };
          
          animate();
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    
    stats.forEach(el => observer.observe(el));
  }

  // 7. 图片加载优化与动画
  function initImageOptimization(){
    const images = document.querySelectorAll('img[data-src]');
    
    if(!window.IntersectionObserver) {
      images.forEach(img => img.src = img.dataset.src);
      return;
    }
    
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if(entry.isIntersecting){
          const img = entry.target;
          img.src = img.dataset.src;
          img.style.animation = 'fadeIn 0.5s ease-out';
          observer.unobserve(img);
        }
      });
    }, { rootMargin: '50px' });
    
    images.forEach(img => observer.observe(img));
  }

  // 8. 页面转移动画
  function initPageTransition(){
    window.addEventListener('beforeunload', () => {
      document.documentElement.style.opacity = '0.8';
      document.documentElement.style.transition = 'opacity 0.3s ease';
    });
  }

  // 初始化所有微交互
  document.addEventListener('DOMContentLoaded', () => {
    initFormMicroInteractions();
    initLinkEffects();
    initCardDepthEffect();
    initNavHighlight();
    // initFirstLetterStyle(); // 可选：开启首字装饰
    initStatisticAnimation();
    initImageOptimization();
    initPageTransition();
  });
})();

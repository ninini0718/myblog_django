// theme_manager.js - 主题管理与动画
(function(){
  // 主题配置
  const themes = {
    light: {
      primary: '#ff4081',
      primaryLight: '#ff79b0',
      bg: '#ffffff',
      text: '#333333',
      textLight: '#666666',
      border: '#e0e0e0',
      shadow: 'rgba(0,0,0,0.1)',
    },
    dark: {
      primary: '#ff4081',
      primaryLight: '#ff79b0',
      bg: '#1a1a1a',
      text: '#ffffff',
      textLight: '#b0b0b0',
      border: '#333333',
      shadow: 'rgba(0,0,0,0.3)',
    },
  };

  // 平滑过渡主题变更
  function transitionTheme() {
    document.documentElement.style.transition = 'background-color 0.3s ease, color 0.3s ease';
  }

  // 恢复过渡
  function resetTransition() {
    setTimeout(() => {
      document.documentElement.style.transition = '';
    }, 300);
  }

  // 获取系统偏好的主题
  function getSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  // 应用主题
  function applyTheme(themeName) {
    const theme = themes[themeName] || themes.light;
    const root = document.documentElement;

    transitionTheme();

    Object.entries(theme).forEach(([key, value]) => {
      const cssVar = '--' + key.replace(/([A-Z])/g, '-$1').toLowerCase();
      root.style.setProperty(cssVar, value);
    });

    localStorage.setItem('preferred-theme', themeName);
    resetTransition();
  }

  // 监听系统主题变更
  function watchSystemTheme() {
    if (!window.matchMedia) return;

    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    darkModeQuery.addEventListener('change', (e) => {
      const newTheme = e.matches ? 'dark' : 'light';
      if (!localStorage.getItem('preferred-theme')) {
        applyTheme(newTheme);
      }
    });
  }

  // 初始化主题
  function initTheme() {
    let theme = localStorage.getItem('preferred-theme');
    
    if (!theme) {
      theme = getSystemTheme();
    }

    applyTheme(theme);
    watchSystemTheme();
  }

  // 暴露接口
  window.themeManager = {
    apply: applyTheme,
    init: initTheme,
    getSystemTheme: getSystemTheme,
    themes: themes,
  };

  // 页面加载时初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    initTheme();
  }
})();

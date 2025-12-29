// 在 admin 中初始化 Select2 用于 tags，支持创建新 tag（通过后端 API）
(function(){
  function getCookie(name){ const v = document.cookie.match('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)'); return v? v.pop():''; }

  document.addEventListener('DOMContentLoaded', function(){
    // 仅在 admin 的 article edit 页面初始化（通过检查 select[name="tags"]）
    var select = document.querySelector('select[name="tags"]');
    if(!select) return;

    // Convert to a Select2 widget (use django.jQuery if available)
    var $j = (window.django && window.django.jQuery) ? window.django.jQuery : (window.jQuery || window.$);
    if(!$j) return;
    $j(select).select2({
      width: '60%',
      tags: false, // 我们不启用内建 tags creation，以便使用后端创建
      placeholder: '输入并选择标签',
      allowClear: true,
    });

    // 当用户输入没有匹配项时，按 Enter 创建新标签（仅限 staff）
    // select2 搜索框在动态创建后存在，使用事件委托轮询查找
    function bindSearchField(){
      var searchField = document.querySelector('.select2-search__field');
      if(!searchField) return false;
      searchField.addEventListener('keydown', function(e){
        if(e.key === 'Enter'){
          e.preventDefault();
          var name = this.value.trim();
          if(!name) return;
          fetch('/articles/api/create_tag/', {
            method: 'POST', credentials: 'same-origin',
            headers: { 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' },
            body: new URLSearchParams({ name: name })
          }).then(function(r){ if(!r.ok) return r.json().then(function(d){ throw d; }); return r.json(); })
          .then(function(data){
            if(data && data.success){
              // add option and select it
              var opt = new Option(data.name, data.id, true, true);
              $j(select).append(opt).trigger('change');
              // clear search
              $j('.select2-search__field').val('');
            } else {
              alert((data && data.message) || '创建失败');
            }
          }).catch(function(err){ alert((err && err.message) || '网络或权限错误'); });
        }
      });
      return true;
    }

    // 尝试绑定，最多尝试 10 次，每 200ms
    var attempts = 0;
    var t = setInterval(function(){
      attempts++;
      if(bindSearchField() || attempts > 10) clearInterval(t);
    }, 200);

  });
})();

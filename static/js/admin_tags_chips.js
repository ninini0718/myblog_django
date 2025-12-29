// 将选中的 tags 显示为 chips，并可在输入框中保留 autocomplete 行为
(function() {
  function makeChip(name, id) {
    var span = document.createElement('span');
    span.className = 'tag-chip';
    span.setAttribute('data-id', id);
    span.textContent = name;
    var remove = document.createElement('button');
    remove.className = 'tag-chip-remove';
    remove.type = 'button';
    remove.textContent = '×';
    remove.addEventListener('click', function(){
      span.remove();
      // 同步到隐藏的 select/m2m widget：移除 option 的 selected
      var select = document.querySelector('select[name="tags"]');
      if (select) {
        for (var i=0;i<select.options.length;i++){
          var opt = select.options[i];
          if (opt.text === name) {
            opt.selected = false;
          }
        }
      }
    });
    span.appendChild(remove);
    return span;
  }

  function init() {
    // 找到 tags 的 autocomplete 容器
    var container = document.querySelector('.field-tags');
    var input = container ? container.querySelector('input, .vManyToManyRawIdAdminField, select') : null;
    if (!container) return;
    var chipArea = document.createElement('div');
    chipArea.className = 'tag-chip-area';
    container.insertBefore(chipArea, container.firstChild);

    // 初始化已选择的 options
    var select = container.querySelector('select');
    if (select) {
      for (var i=0;i<select.options.length;i++){
        var opt = select.options[i];
        if (opt.selected) {
          chipArea.appendChild(makeChip(opt.text, opt.value));
        }
      }

      // 监听 select 的变更（通过 admin 自动完成触发）
      select.addEventListener('change', function(){
        chipArea.innerHTML = '';
        for (var i=0;i<select.options.length;i++){
          var opt = select.options[i];
          if (opt.selected) chipArea.appendChild(makeChip(opt.text, opt.value));
        }
      });
    }

    // 新增：当输入框存在时，提供创建 tag 的能力（仅当没有匹配时）
    if (input && input.tagName === 'INPUT'){
      var createBtn = document.createElement('button');
      createBtn.type = 'button';
      createBtn.className = 'btn btn-sm btn-outline-primary ms-2';
      createBtn.textContent = '创建标签';
      createBtn.style.display = 'none';
      container.appendChild(createBtn);

      function getCookie(name){ const v = document.cookie.match('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)'); return v? v.pop():''; }

      createBtn.addEventListener('click', function(){
        var name = input.value.trim();
        if(!name) return alert('请输入标签名称');
        createBtn.disabled = true;
        fetch('/articles/api/create_tag/', {
          method: 'POST',
          credentials: 'same-origin',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: new URLSearchParams({ name: name })
        }).then(function(r){
          createBtn.disabled = false;
          if(!r.ok) return r.json().then(function(d){ throw d; });
          return r.json();
        }).then(function(data){
          if(data && data.success){
            // 将新 option 添加到 select 并选中
            if(select){
              var opt = document.createElement('option');
              opt.value = data.id;
              opt.text = data.name;
              opt.selected = true;
              select.appendChild(opt);
              // 触发 change
              var ev = new Event('change', { bubbles: true });
              select.dispatchEvent(ev);
            }
            input.value = '';
            createBtn.style.display = 'none';
          } else {
            alert((data && data.message) || '创建失败');
          }
        }).catch(function(err){
          createBtn.disabled = false;
          alert((err && err.message) || '网络或权限错误');
        });
      });

      // 显示/隐藏创建按钮：当输入有内容且没有匹配时显示
      input.addEventListener('input', function(){
        var v = input.value.trim();
        if(!v) { createBtn.style.display = 'none'; return; }
        // 简单策略：如果 select 中没有文本匹配则显示创建按钮
        var found = false;
        if(select){
          for(var i=0;i<select.options.length;i++){ if(select.options[i].text.toLowerCase().indexOf(v.toLowerCase()) !== -1){ found = true; break; } }
        }
        createBtn.style.display = found ? 'none' : 'inline-block';
      });
    }
  }

  // 延迟初始化，等待 admin JS 创建控件
  document.addEventListener('DOMContentLoaded', function(){
    setTimeout(init, 500);
  });
})();

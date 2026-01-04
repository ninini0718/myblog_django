// article_field_search.js
// 在文章创建页为 category 和 tags 添加搜索功能
(function(){
  function createModal(){
    var modal = document.createElement('div');
    modal.className = 'afs-modal';
    modal.style.position = 'fixed'; 
    modal.style.left = '0'; 
    modal.style.top = '0'; 
    modal.style.width = '100%'; 
    modal.style.height = '100%';
    modal.style.background = 'rgba(0,0,0,0.5)'; 
    modal.style.display = 'flex'; 
    modal.style.alignItems = 'center'; 
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '2000';
    modal.innerHTML = `
      <div class="afs-dialog" style="background:#fff;padding:20px;border-radius:8px;min-width:320px;max-width:500px;max-height:600px;display:flex;flex-direction:column;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <strong class="afs-title">选择</strong>
          <button type="button" class="btn btn-sm btn-close afs-close" aria-label="Close"></button>
        </div>
        <div style="margin-bottom:12px;">
          <input class="form-control afs-search" placeholder="搜索..." style="width:100%;" />
        </div>
        <div class="afs-results" style="flex:1;overflow-y:auto;border:1px solid #e9ecef;border-radius:4px;padding:8px;"></div>
      </div>`;
    document.body.appendChild(modal);
    
    // 点击外部关闭
    modal.addEventListener('click', function(e){
      if(e.target === modal) modal.remove();
    });
    
    modal.querySelector('.afs-close').addEventListener('click', function(e){
      e.preventDefault();
      modal.remove();
    });
    
    return modal;
  }

  function openSearch(kind, fieldContainer, onSelect){
    var modal = createModal();
    var input = modal.querySelector('.afs-search');
    var results = modal.querySelector('.afs-results');
    modal.querySelector('.afs-title').textContent = (kind=='category'?'选择分类':'选择标签');

    function renderList(items){
      results.innerHTML = '';
      if(!items || !items.length) {
        results.innerHTML = '<div class="text-muted p-3 text-center">无匹配结果</div>';
        return;
      }
      items.forEach(function(it){
        var div = document.createElement('div');
        div.className = 'afs-item p-2';
        div.style.cursor = 'pointer';
        div.style.borderBottom = '1px solid #f0f0f0';
        div.style.transition = 'background 0.2s';
        div.textContent = it.name;
        div.dataset.id = it.id;
        div.addEventListener('mouseover', function(){ this.style.background = '#f8f9fa'; });
        div.addEventListener('mouseout', function(){ this.style.background = ''; });
        div.addEventListener('click', function(e){ 
          e.preventDefault();
          onSelect(it); 
          modal.remove(); 
        });
        results.appendChild(div);
      });
    }

    var timer = null;
    function doSearch(q){
      var endpoint = (kind=='category'?'search_categories':'search_tags');
      var url = '/articles/api/' + endpoint + '/?q=' + encodeURIComponent(q||'');
      fetch(url)
        .then(function(r){ 
          if(!r.ok) throw new Error('Network error');
          return r.json(); 
        })
        .then(function(d){ 
          renderList(d.results || []); 
        })
        .catch(function(err){
          console.error('搜索错误:', err);
          renderList([]); 
        });
    }
    
    // 监听搜索输入
    input.addEventListener('input', function(){ 
      clearTimeout(timer); 
      timer = setTimeout(function(){ doSearch(input.value.trim()); }, 300); 
    });
    
    // 立即加载所有选项
    doSearch('');
    
    // 自动focus
    setTimeout(function(){ input.focus(); }, 100);
  }

  document.addEventListener('DOMContentLoaded', function(){
    // 处理分类字段
    var catField = document.querySelector('.field-category');
    if(catField){
      var btn = document.createElement('button'); 
      btn.type='button'; 
      btn.className='btn btn-sm btn-outline-primary ms-2'; 
      btn.textContent='🔍 搜索分类';
      btn.style.marginLeft = '8px';
      btn.style.marginTop = '8px';
      catField.appendChild(btn);
      btn.addEventListener('click', function(e){
        e.preventDefault();
        e.stopPropagation();
        openSearch('category', catField, function(item){
          // 设置 select 的值
          var sel = catField.querySelector('select');
          if(sel){ 
            sel.value = item.id; 
            try{ sel.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){} 
          }
        });
      });
    }
    
    // 处理标签字段
    var tagsField = document.querySelector('.field-tags');
    if(tagsField){
      var btn2 = document.createElement('button'); 
      btn2.type='button'; 
      btn2.className='btn btn-sm btn-outline-primary ms-2'; 
      btn2.textContent='🔍 搜索标签';
      btn2.style.marginLeft = '8px';
      btn2.style.marginTop = '8px';
      tagsField.appendChild(btn2);
      btn2.addEventListener('click', function(e){
        e.preventDefault();
        e.stopPropagation();
        openSearch('tags', tagsField, function(item){
          // tags 是 CheckboxSelectMultiple，找到对应的 checkbox
          var check = Array.from(tagsField.querySelectorAll('input[type="checkbox"]')).find(function(i){ 
            return i.value == item.id; 
          });
          if(check){ 
            check.checked = true; 
            try{ check.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){} 
          }
        });
      });
    }
  });
})();

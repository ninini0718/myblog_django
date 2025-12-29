// article_field_search.js
// 在文章创建页为 category 和 tags 添加搜索按钮与弹出搜索选择
(function(){
  function createModal(){
    var modal = document.createElement('div');
    modal.className = 'afs-modal';
    modal.style.position = 'fixed'; modal.style.left = 0; modal.style.top = 0; modal.style.width = '100%'; modal.style.height = '100%';
    modal.style.background = 'rgba(0,0,0,0.4)'; modal.style.display = 'flex'; modal.style.alignItems = 'center'; modal.style.justifyContent = 'center';
    modal.style.zIndex = 2000;
    modal.innerHTML = `
      <div class="afs-dialog" style="background:#fff;padding:16px;border-radius:8px;min-width:320px;max-width:720px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <strong class="afs-title">选择</strong>
          <button type="button" class="btn-close afs-close" aria-label="Close"></button>
        </div>
        <div style="margin-bottom:8px;">
          <input class="form-control afs-search" placeholder="搜索..." />
        </div>
        <div class="afs-results" style="max-height:360px;overflow:auto;"></div>
      </div>`;
    document.body.appendChild(modal);
    modal.querySelector('.afs-close').addEventListener('click', function(){ modal.remove(); });
    return modal;
  }

  function openSearch(kind, onSelect){
    var modal = createModal();
    var input = modal.querySelector('.afs-search');
    var results = modal.querySelector('.afs-results');
    modal.querySelector('.afs-title').textContent = (kind=='category'?'搜索分类':'搜索标签');

    function renderList(items){
      results.innerHTML = '';
      if(!items.length) results.innerHTML = '<div class="text-muted">无匹配结果</div>';
      items.forEach(function(it){
        var div = document.createElement('div');
        div.className = 'afs-item p-2';
        div.style.cursor = 'pointer';
        div.textContent = it.name;
        div.dataset.id = it.id;
        div.addEventListener('click', function(){ onSelect(it); modal.remove(); });
        results.appendChild(div);
      });
    }

    var timer = null;
    function doSearch(q){
      var url = '/articles/api/' + (kind=='category'?'search_categories/':'search_tags/') + '?q=' + encodeURIComponent(q||'');
      fetch(url).then(function(r){ return r.json(); }).then(function(d){ renderList(d.results || []); }).catch(function(){ renderList([]); });
    }
    input.addEventListener('input', function(){ clearTimeout(timer); timer = setTimeout(function(){ doSearch(input.value.trim()); }, 250); });
    // 立即加载默认列表
    doSearch('');
  }

  document.addEventListener('DOMContentLoaded', function(){
    // 插入两个按钮到 category 和 tags 字段旁
    var catField = document.querySelector('.field-category');
    var tagsField = document.querySelector('.field-tags');
    if(catField){
      var btn = document.createElement('button'); btn.type='button'; btn.className='btn btn-sm btn-outline-primary ms-2 afs-open-cat'; btn.textContent='搜索分类';
      catField.appendChild(btn);
      btn.addEventListener('click', function(){
        openSearch('category', function(item){
          // 设置 select 的值
          var sel = catField.querySelector('select');
          if(sel){ sel.value = item.id; try{ sel.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){} }
        });
      });
    }
    if(tagsField){
      var btn2 = document.createElement('button'); btn2.type='button'; btn2.className='btn btn-sm btn-outline-primary ms-2 afs-open-tags'; btn2.textContent='搜索标签';
      tagsField.appendChild(btn2);
      btn2.addEventListener('click', function(){
        openSearch('tag', function(item){
          // tags 当前是 CheckboxSelectMultiple，尝试选中对应的 checkbox 或为 select 添加 option
          var check = Array.from(tagsField.querySelectorAll('input[type="checkbox"]')).find(function(i){ return i.value == item.id; });
          if(check){ check.checked = true; check.dispatchEvent(new Event('change',{bubbles:true})); }
          else {
            // 如果不存在 checkbox，尝试找到 select 并添加选项
            var sel = tagsField.querySelector('select');
            if(sel){ var opt = new Option(item.name, item.id, true, true); sel.appendChild(opt); try{ sel.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){} }
          }
        });
      });
    }
  });
})();

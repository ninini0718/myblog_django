(function(){
    function qs(selector, ctx){ return (ctx||document).querySelector(selector); }
    function qsa(selector, ctx){ return Array.from((ctx||document).querySelectorAll(selector)); }

    let lastUnread = 0;
    function animateBell() {
        const bell = document.querySelector('#notificationDropdown i.fas.fa-bell');
        if(bell){
            bell.classList.add('bell-ring');
            setTimeout(()=>bell.classList.remove('bell-ring'), 1400);
        }
    }

    function playKawaiiBeep(){
        try{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.type = 'sine';
            o.frequency.setValueAtTime(880, ctx.currentTime);
            g.gain.setValueAtTime(0, ctx.currentTime);
            g.gain.linearRampToValueAtTime(0.08, ctx.currentTime + 0.01);
            g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
            o.connect(g); g.connect(ctx.destination);
            o.start();
            setTimeout(()=>{ o.stop(); ctx.close(); }, 500);
        }catch(e){/* ignore audio failures */ }
    }

    function renderNotificationItem(n){
        if(!n) return null;
        const a = document.createElement('a');
        a.className = 'list-group-item kawaii-item d-flex justify-content-between align-items-start';
        if(n.unread) a.classList.add('unread');
        a.dataset.id = n.id || '';
        // 若通知包含文章 slug 和评论 id，则构建跳转链接到文章的对应评论锚点
        const articleSlug = (n.data && n.data.article_slug) ? n.data.article_slug : (n.data && n.data.article_id ? n.data.article_id : null);
        const commentId = (n.data && n.data.comment_id) ? n.data.comment_id : null;
        const profileUsername = (n.data && n.data.profile_username) ? n.data.profile_username : null;
        if (articleSlug && commentId) {
            a.href = `/articles/${articleSlug}/#comment-${commentId}`;
        } else if (profileUsername) {
            a.href = `/users/${profileUsername}/`;
        } else {
            a.href = '#';
        }
        const actor = n.actor || '系统';
        const actorAvatar = n.actor_avatar || null;
        const timestamp = n.timestamp || '';
        const verb = n.verb || '';
        const excerpt = (n.data && n.data.comment_excerpt) ? escapeHtml(n.data.comment_excerpt) : '';
        a.innerHTML = `
            <div class="d-flex align-items-center">
                ${actorAvatar? `<img src="${actorAvatar}" class="rounded-circle me-2" width="40" height="40" onerror="this.onerror=null;this.src='/static/images/default_avatar.jpg'">` : `<div class="avatar-circle">${actor.charAt(0).toUpperCase()}</div>`}
                <div class="ms-2">
                    <div class="small text-muted">${timestamp}</div>
                    <div class="k-verb">${actor} ${verb}</div>
                    ${excerpt ? `<div class="small text-muted k-excerpt">${excerpt}</div>` : ''}
                </div>
            </div>
            <div class="k-badge">${n.unread?'<span class="badge k-new">新</span>':''}</div>
        `;
        a.addEventListener('click', e=>{ 
            e.preventDefault(); 
            if(n.id) {
                // 标记已读后跳转到文章评论位置（如果有目标）
                markAsRead(n.id);
            }
            if(a.href && a.href !== '#') {
                // 延迟短时间，确保服务端收到已读请求
                setTimeout(()=>{ window.location.href = a.href; }, 150);
            }
        });
        return a;
    }

    function escapeHtml(s){ if(!s) return ''; return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

    function fetchNotifications(){
        fetch('/comments/notifications/json/', {credentials: 'same-origin'})
        .then(r=>r.json())
        .then(data=>{
            if(!data) return;
            const badge = document.querySelector('.badge-notification');
            const unreadCount = data.unread_count || 0;
            if(badge){
                if(unreadCount>0){
                    if(unreadCount > lastUnread){
                        animateBell(); playKawaiiBeep();
                    }
                    badge.textContent = unreadCount;
                } else {
                    badge.remove();
                }
            }
            lastUnread = unreadCount;

            const panel = document.querySelector('.notifications-panel .list-group');
            if(panel && Array.isArray(data.notifications)){
                panel.innerHTML = '';
                data.notifications.forEach(n=>{
                    const item = renderNotificationItem(n);
                    if(item) panel.appendChild(item);
                });
            }
        }).catch(()=>{});
    }

    window.markAsRead = function(id){
        if(!id) return;
        const data = new FormData();
        data.append('notification_id', id);
        data.append('action','mark_read');
        fetch('/comments/notifications/mark/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: data
        }).then(()=>fetchNotifications()).catch(()=>{});
    }

    function markAllRead(){
        const ids = Array.from(document.querySelectorAll('.kawaii-item, .notification-item')).map(el=>el.dataset.id).filter(Boolean);
        ids.forEach(id=>{
            const data = new FormData(); 
            data.append('notification_id', id); 
            data.append('action','mark_read');
            fetch('/comments/notifications/mark/', {
                method:'POST',
                credentials:'same-origin',
                headers:{'X-CSRFToken':getCookie('csrftoken')},
                body: data
            }).catch(()=>{});
        });
        setTimeout(fetchNotifications,300);
    }

    function getCookie(name){
        const v = document.cookie.match('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)');
        return v ? v.pop() : '';
    }

    document.addEventListener('DOMContentLoaded', function(){
        fetchNotifications();
        setInterval(fetchNotifications, 30000);
        // 监听页面上 follow-toggle 按钮的点击（事件委托）
        document.body.addEventListener('click', function(e){
            const btn = e.target.closest('.follow-toggle');
            if(!btn) return;
            e.preventDefault();
            const username = btn.dataset.username;
            const following = btn.dataset.following === '1' || btn.dataset.following === 'true';
            const csrftoken = getCookie('csrftoken');
            const url = following ? `/users/api/unfollow/${username}/` : `/users/api/follow/${username}/`;
            fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }).then(r=>r.json()).then(data=>{
                if(data && data.success){
                    // 切换按钮显示
                    btn.dataset.following = following ? '0' : '1';
                    if(btn.classList.contains('btn-outline-primary')){
                        btn.classList.remove('btn-outline-primary');
                        btn.classList.add('btn-outline-secondary');
                    } else if(btn.classList.contains('btn-outline-secondary')){
                        btn.classList.remove('btn-outline-secondary');
                        btn.classList.add('btn-outline-primary');
                    }
                    btn.textContent = following ? '关注' : '已关注';
                    // 刷新通知面板以便即时看到新关注通知
                    setTimeout(fetchNotifications, 200);
                }
            }).catch(()=>{});
        });
        const markAll = document.getElementById('markAllRead');
        if(markAll) markAll.addEventListener('click', function(e){ e.preventDefault(); markAllRead(); });
        // 为服务端渲染的通知项绑定点击事件（标记已读）
        Array.from(document.querySelectorAll('.kawaii-item, .notification-item')).forEach(el=>{
            el.addEventListener('click', function(e){
                e.preventDefault();
                const id = el.dataset.id;
                if(id) markAsRead(id);
            });
        });
    });
})();

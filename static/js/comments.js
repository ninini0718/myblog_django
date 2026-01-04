    let submitInProgress = false;  // 全局标志防止重复提交

    /* ==========================
       1️⃣ AJAX 提交评论 / 回复
    ========================== */
    function submitCommentForm(form) {
        // 防止重复提交
        if (submitInProgress) {
            return;
        }
        submitInProgress = true;
        
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"], button:not([type])');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.dataset.origText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 提交中...';
        }

        fetch(form.action, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (!data) throw new Error('无返回数据');
            if (data.error) {
                alert(data.error);
                throw new Error(data.error);
            }

            // 兼容后端可能包裹在 `comment` 字段或直接返回对象的情况
            const c = data.comment || data;
            const cid = c.id || c.comment_id || data.id;

            if (!cid) {
                throw new Error('无法获取评论 ID');
            }

            if (document.getElementById(`comment-${cid}`)) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.dataset.origText || '发表评论';
                }
                showTopNotice('评论已发布', 'success');
                submitInProgress = false;
                return;
            }

            const html = buildCommentHTML({
                id: cid,
                article_id: c.article_id || c.article || c.articleId,
                avatar: c.author_avatar || c.author_avatar || '/static/images/default_avatar.jpg',
                author: c.author_nickname || c.author_username || (c.author || '用户'),
                created_at: c.created_at || c.timestamp || '',
                likes_count: c.likes ?? 0,
                is_author: c.is_author || false,
                is_staff: c.is_staff || false,
                content: c.content || '',
                image: c.image || '',
                parent_id: c.parent_id || null,
            });

            if (c.is_reply && c.parent_id) {
                let parentReplies = document.querySelector(`#comment-${c.parent_id} .replies`);
                if (!parentReplies) {
                    const parentEl = document.getElementById(`comment-${c.parent_id}`);
                    if (parentEl) {
                        parentReplies = document.createElement('div');
                        parentReplies.className = 'replies mt-3';
                        parentEl.appendChild(parentReplies);
                    }
                }
                if (parentReplies) parentReplies.insertAdjacentHTML('beforeend', html);
            } else {
                const list = document.querySelector('.comment-list');
                if (list) list.insertAdjacentHTML('afterbegin', html);
            }

            form.reset();
            const replyBox = form.closest('.reply-form');
            if (replyBox) replyBox.style.display = 'none';

            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.dataset.origText || '发表评论';
            }
            showTopNotice('评论发布成功！', 'success');
            submitInProgress = false;
        })
        .catch(err => {
            console.error(err);
            alert('提交失败，请重试');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.dataset.origText || '发表评论';
            }
            submitInProgress = false;
        });
    }

    /* ==========================
       2️⃣ 构建评论 HTML
    ========================== */
    function buildCommentHTML(c) {
        // 安全默认值，避免出现 undefined
        const avatar = c.avatar || c.author_avatar || '/static/images/default_avatar.jpg';
        const author = c.author || c.author_nickname || c.author_username || '匿名';
        const created = c.created_at || c.timestamp || '';
        const likes = (typeof c.likes_count !== 'undefined') ? c.likes_count : (typeof c.likes !== 'undefined' ? c.likes : 0);
        const content = c.content_html || c.content || '';
        const image = c.image || c.image_url || '';

        return `
        <div class="card mt-2" id="comment-${c.id}">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <img src="${avatar}" alt="Avatar" onerror="this.onerror=null;this.src='/static/images/default_avatar.jpg'" class="rounded-circle me-1" width="25">
                        <strong><a href="/users/${encodeURIComponent(c.author_username||c.author||'')}/" class="text-decoration-none text-dark">${escapeHtml(author)}</a></strong>
                        <small class="text-muted">${escapeHtml(created)}</small>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-danger like-btn" data-comment-id="${c.id}">
                            <i class="far fa-heart"></i> (<span class="like-count">${likes}</span>)
                        </button>
                        ${ (c.is_author || c.is_staff) ? `<button class="btn btn-sm btn-outline-danger delete-btn" data-comment-id="${c.id}">删除</button>` : ''}
                    </div>
                </div>

                <p class="mt-2">
                    ${escapeHtml(content)}
                    ${image ? `<br><img src="${image}" class="img-fluid mt-2" style="max-height:200px;" onerror="this.onerror=null;this.style.display='none'">` : ''}
                </p>

                <button class="btn btn-sm btn-link reply-btn" data-comment-id="${c.id}">回复</button>

                <div class="reply-form mt-2" id="reply-form-${c.id}" style="display:none;">
                            <form method="post" action="/comments/add/${(c.article_id||c.article||c.articleId)||document.querySelector('.main-comment-form')?.dataset.articleId||''}/" enctype="multipart/form-data">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <input type="hidden" name="parent_id" value="${c.id}">

                        <div class="position-relative mb-2">
                            <textarea name="content" class="form-control comment-textarea" rows="2" required></textarea>

                            <button type="button"
                                class="btn btn-sm btn-light emoji-btn"
                                style="position:absolute; right:5px; bottom:5px;">
                                😊
                            </button>

                            <div class="emoji-panel d-none">
                                <span>😄</span><span>😆</span><span>😂</span><span>🤣</span>
                                <span>😊</span><span>😍</span><span>😭</span><span>😡</span>
                                <span>👍</span><span>👎</span><span>🎉</span><span>❤️</span>
                                <span>🔥</span>
                            </div>
                        </div>

                        <input type="file" name="image" class="form-control mb-2">
                        <button type="submit" class="btn btn-sm btn-primary">回复</button>
                    </form>
                </div>

                <div class="replies mt-3"></div>
            </div>
        </div>`;
    }

    /* ==========================
       3️⃣ 主评论提交和回复表单提交
    ========================== */
    const mainForm = document.querySelector('.main-comment-form');
    if (mainForm) {
        // 如果主表单已被页面内联脚本标记为由其它脚本处理，则不要重复绑定
        if (mainForm.dataset.ajaxBound !== "1") {
            mainForm.addEventListener('submit', e => {
                e.preventDefault();
                submitCommentForm(mainForm);
            });
            // 标记已绑定，防止页面内其他脚本重复绑定导致双重提交
            try { mainForm.dataset.ajaxBound = "1"; } catch(e){}
        }
    }

    /* ==========================
       4️⃣ 评论区事件委托（点赞/删除/回复）
    ========================== */
    const commentList = document.querySelector('.comment-list');
    commentList?.addEventListener('click', function (e) {
        const btn = e.target.closest('button');
        if (!btn) return;

        // 优先处理表情按钮，避免被其他按钮逻辑干扰（回复框的表情）
        if (btn.classList.contains('emoji-btn')) {
            e.stopPropagation();
            // 找到最贴近的容器并定位 textarea 与 panel
            const container = btn.closest('.position-relative') || btn.closest('.reply-form') || btn.closest('form') || btn.parentElement;
            const panel = container ? container.querySelector('.emoji-panel') : null;
            const textarea = container ? container.querySelector('.comment-textarea, textarea') : null;
            // 隐藏页面中其他面板
            document.querySelectorAll('.emoji-panel').forEach(p => { if (p !== panel) p.classList.add('d-none'); });
            if (panel) panel.classList.toggle('d-none');
            activeTextarea = textarea || null;
            return;
        }

        const id = btn.dataset.commentId;

        if (btn.classList.contains('reply-btn')) {
            document.querySelectorAll('.reply-form').forEach(f => f.style.display = 'none');
            const box = document.getElementById(`reply-form-${id}`);
            if (box) box.style.display = 'block';
        }

        if (btn.classList.contains('like-btn')) likeComment(id, btn);
        if (btn.classList.contains('delete-btn')) deleteComment(id);
    });

    // 处理回复表单的提交（事件委托）
    commentList?.addEventListener('submit', function (e) {
        const form = e.target.closest('form');
        if (!form) return;
        
        // 如果是主评论表单，跳过（已单独处理）
        if (form === mainForm) return;
        
        e.preventDefault();
        submitCommentForm(form);
    });

    /* ==========================
       5️⃣ 点赞（无刷新）
    ========================== */
    function likeComment(id, btn) {
        if (!id) return;
        fetch(`/comments/like/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(res => res.json())
        .then(d => {
            if (d.success) {
                btn.querySelector('.like-count').textContent = d.likes;
            }
        });
    }

    /* ==========================
       6️⃣ 删除（无刷新）
    ========================== */
    function deleteComment(id) {
        if (!id) return;
        if (!confirm('确认删除？')) return;

        fetch(`/comments/delete/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(res => res.json())
        .then(d => {
            if (d.success) {
                const el = document.getElementById(`comment-${id}`);
                if (el) el.innerHTML = '<div class="alert alert-warning">评论已删除</div>';
            } else {
                alert(d.message || '删除失败');
            }
        });
    }

    /* ==========================
       7️⃣ 表情功能
    ========================== */
    document.addEventListener('click', function (e) {
        const emojiBtn = e.target.closest('.emoji-btn');
        if (emojiBtn) {
            e.stopPropagation();
            // 尝试在多种可能的父容器中寻找 textarea
            let box = emojiBtn.closest('.position-relative') || emojiBtn.closest('.reply-form') || emojiBtn.closest('form') || emojiBtn.parentElement;
            let textarea = box ? box.querySelector('.comment-textarea, textarea') : null;
            // 如果没找到，再从表单或最近的祖先里寻找 textarea
            if (!textarea) {
                const form = emojiBtn.closest('form');
                textarea = form ? form.querySelector('.comment-textarea, textarea') : null;
            }
            activeTextarea = textarea || null;
            // 隐藏其他面板，再切换当前面板
            document.querySelectorAll('.emoji-panel').forEach(p => p.classList.add('d-none'));
            const panel = (box && box.querySelector('.emoji-panel')) || emojiBtn.parentElement.querySelector('.emoji-panel') || emojiBtn.closest('form')?.querySelector('.emoji-panel');
            if (panel) panel.classList.toggle('d-none');
            return;
        }

        const emojiSpan = e.target.closest('.emoji-panel span');
        if (emojiSpan) {
            // 如果当前 activeTextarea 不可用，尝试从 emojiSpan 的祖先中找到 textarea
            let textarea = activeTextarea;
            if (!textarea) {
                const box = emojiSpan.closest('.position-relative') || emojiSpan.closest('.reply-form') || emojiSpan.closest('form');
                textarea = box ? box.querySelector('.comment-textarea, textarea') : null;
            }
            if (textarea) {
                const emoji = emojiSpan.textContent;
                const start = textarea.selectionStart || 0;
                const end = textarea.selectionEnd || 0;
                textarea.value = textarea.value.slice(0, start) + emoji + textarea.value.slice(end);
                textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
                textarea.focus();
            }
            // 隐藏所有面板
            document.querySelectorAll('.emoji-panel').forEach(p => p.classList.add('d-none'));
            return;
        }

        // 点击其他地方时关闭所有 emoji 面板，并清空 activeTextarea
        document.querySelectorAll('.emoji-panel').forEach(p => p.classList.add('d-none'));
        activeTextarea = null;
    });

    /* ==========================
       8️⃣ 获取 CSRF
    ========================== */
    function getCookie(name) {
        return document.cookie.split('; ').find(c => c.startsWith(name + '='))?.split('=')[1];
    }

    function showTopNotice(message, level='info') {
        const existing = document.getElementById('top-comment-notice');
        if (existing) existing.remove();
        const div = document.createElement('div');
        div.id = 'top-comment-notice';
        div.className = `alert alert-${level} position-fixed top-0 start-50 translate-middle-x mt-3`;
        div.style.zIndex = 1050;
        div.innerHTML = message + ' <button type="button" class="btn-close" aria-label="Close" onclick="this.parentElement.remove()"></button>';
        document.body.appendChild(div);
        setTimeout(() => { div.classList.add('fade'); setTimeout(()=>div.remove(), 500); }, 2800);
    }

    function escapeHtml(s){ if(!s && s !== 0) return ''; return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

});

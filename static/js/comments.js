document.addEventListener('DOMContentLoaded', function () {

    let activeTextarea = null;

    /* ==========================
       1️⃣ AJAX 提交评论 / 回复
    ========================== */
    function submitCommentForm(form) {
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) return alert(data.error);

            const html = buildCommentHTML(data);

            if (data.is_reply && data.parent_id) {
                document
                    .querySelector(`#comment-${data.parent_id} .replies`)
                    .insertAdjacentHTML('beforeend', html);
            } else {
                document
                    .querySelector('.comment-list')
                    .insertAdjacentHTML('afterbegin', html);
            }

            form.reset();
            const replyBox = form.closest('.reply-form');
            if (replyBox) replyBox.style.display = 'none';
        })
        .catch(err => {
            console.error(err);
            alert('提交失败，请重试');
        });
    }

    /* ==========================
       2️⃣ 构建评论 HTML（支持点赞/删除/回复/表情）
    ========================== */
    function buildCommentHTML(c) {
        return `
        <div class="card mt-2" id="comment-${c.id}">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <img src="${c.avatar}" alt="Avatar" class="rounded-circle me-1" width="25">
                        <strong>${c.author}</strong>
                        <small class="text-muted">${c.created_at}</small>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-danger like-btn" data-comment-id="${c.id}">
                            <i class="far fa-heart"></i> (<span class="like-count">${c.likes_count}</span>)
                        </button>
                        ${c.is_author || c.is_staff ? `<button class="btn btn-sm btn-outline-danger delete-btn" data-comment-id="${c.id}">删除</button>` : ''}
                    </div>
                </div>

                <p class="mt-2">
                    ${c.content}
                    ${c.image ? `<br><img src="${c.image}" class="img-fluid mt-2" style="max-height:200px;">` : ''}
                </p>

                <button class="btn btn-sm btn-link reply-btn" data-comment-id="${c.id}">回复</button>

                <div class="reply-form mt-2" id="reply-form-${c.id}" style="display:none;">
                    <form method="post" action="/comments/add/${c.article_id}/">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${c.csrf}">
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
                        <button class="btn btn-sm btn-primary">回复</button>
                    </form>
                </div>

                <div class="replies mt-3"></div>
            </div>
        </div>`;
    }

    /* ==========================
       3️⃣ 主评论提交
    ========================== */
    const mainForm = document.querySelector('.main-comment-form');
    if (mainForm) {
        mainForm.addEventListener('submit', e => {
            e.preventDefault();
            submitCommentForm(mainForm);
        });
    }

    /* ==========================
       4️⃣ 评论区事件委托（点赞/删除/回复）
    ========================== */
    const commentList = document.querySelector('.comment-list');
    commentList?.addEventListener('click', function (e) {
        const btn = e.target.closest('button');
        if (!btn) return;

        const id = btn.dataset.commentId;

        if (btn.classList.contains('reply-btn')) {
            document.querySelectorAll('.reply-form').forEach(f => f.style.display = 'none');
            const box = document.getElementById(`reply-form-${id}`);
            if (box) box.style.display = 'block';
        }

        if (btn.classList.contains('like-btn')) likeComment(id, btn);
        if (btn.classList.contains('delete-btn')) deleteComment(id);
    });

    // 回复表单提交
    commentList?.addEventListener('submit', function (e) {
        const form = e.target.closest('form');
        if (!form) return;
        e.preventDefault();
        submitCommentForm(form);
    });

    /* ==========================
       5️⃣ 点赞
    ========================== */
    function likeComment(id, btn) {
        fetch(`/comments/like/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(res => res.json())
        .then(d => {
            btn.querySelector('.like-count').textContent = d.likes_count;
        });
    }

    /* ==========================
       6️⃣ 删除
    ========================== */
    function deleteComment(id) {
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
                document.getElementById(`comment-${id}`)
                    .innerHTML = '<div class="alert alert-warning">评论已删除</div>';
            }
        });
    }

    /* ==========================
       7️⃣ 表情功能（完整保留）
    ========================== */
    document.addEventListener('click', function (e) {
        const emojiBtn = e.target.closest('.emoji-btn');
        if (emojiBtn) {
            e.stopPropagation();
            const box = emojiBtn.closest('.position-relative');
            activeTextarea = box.querySelector('.comment-textarea');
            document.querySelectorAll('.emoji-panel').forEach(p => p.classList.add('d-none'));
            box.querySelector('.emoji-panel').classList.toggle('d-none');
            return;
        }

        const emojiSpan = e.target.closest('.emoji-panel span');
        if (emojiSpan && activeTextarea) {
            const emoji = emojiSpan.textContent;
            const start = activeTextarea.selectionStart;
            const end = activeTextarea.selectionEnd;
            activeTextarea.value = activeTextarea.value.slice(0, start) + emoji + activeTextarea.value.slice(end);
            activeTextarea.selectionStart = activeTextarea.selectionEnd = start + emoji.length;
            activeTextarea.focus();
            emojiSpan.closest('.emoji-panel').classList.add('d-none');
            return;
        }

        // 点击空白关闭表情面板
        document.querySelectorAll('.emoji-panel').forEach(p => p.classList.add('d-none'));
    });

    /* ==========================
       8️⃣ 获取 CSRF
    ========================== */
    function getCookie(name) {
        return document.cookie.split('; ').find(c => c.startsWith(name + '='))?.split('=')[1];
    }

});

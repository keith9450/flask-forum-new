// Forum JavaScript

// Flash message handling
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// User check and update UI
async function checkUser() {
    try {
        const response = await fetch('/api/user/check');
        const data = await response.json();
        
        const userArea = document.getElementById('user-area');
        if (userArea) {
            if (data.authenticated) {
                userArea.innerHTML = `
                    <div class="user-menu">
                        <a href="/user/${data.user.id}">
                            <img src="${data.user.avatar}" class="user-avatar" alt="${data.user.username}">
                            <span>${data.user.username}</span>
                        </a>
                        ${data.user.role === 'admin' ? '<a href="/admin" class="btn btn-outline">管理后台</a>' : ''}
                        <a href="/logout" class="btn btn-outline">退出</a>
                    </div>
                `;
            } else {
                userArea.innerHTML = `
                    <div class="user-menu">
                        <a href="/login" class="btn btn-outline">登录</a>
                        <a href="/register" class="btn btn-primary">注册</a>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error checking user:', error);
    }
}

// Like post
async function likePost(postId) {
    try {
        const response = await fetch(`/post/${postId}/like`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        });
        const data = await response.json();
        
        if (data.success) {
            const likeBtn = document.querySelector(`[data-post-id="${postId}"] .like-btn`);
            const likeCount = document.querySelector(`[data-post-id="${postId}"] .like-count`);
            
            if (likeBtn) {
                likeBtn.classList.toggle('liked', data.action === 'liked');
                likeBtn.innerHTML = data.action === 'liked' ? 
                    '<svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6.5l3.5 2 .5-.8 2.5-3A1.5 1.5 0 0 1 14 5.5V5a1 1 0 0 0-1-1H6a1 1 0 0 0-1 1v.5z"/></svg> 已赞' :
                    '<svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6.5l3.5 2 .5-.8 2.5-3A1.5 1.5 0 0 1 14 5.5V5a1 1 0 0 0-1-1H6a1 1 0 0 0-1 1v.5z"/></svg> 点赞';
            }
            if (likeCount) {
                likeCount.textContent = data.like_count;
            }
        }
    } catch (error) {
        alert('请先登录');
        window.location.href = '/login';
    }
}

// Form validation
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('[required]');
    
    inputs.forEach(input => {
        const error = input.parentElement.querySelector('.form-error');
        if (error) error.remove();
        
        if (!input.value.trim()) {
            isValid = false;
            const errorEl = document.createElement('div');
            errorEl.className = 'form-error';
            errorEl.textContent = '此字段必填';
            input.parentElement.appendChild(errorEl);
        }
    });
    
    return isValid;
}

// Search form
document.querySelectorAll('.search-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const input = this.querySelector('input[name="search"]');
        if (!input.value.trim()) {
            e.preventDefault();
        }
    });
});

// Category filter
function filterByCategory(categoryId) {
    const url = new URL(window.location);
    if (categoryId) {
        url.searchParams.set('category', categoryId);
    } else {
        url.searchParams.delete('category');
    }
    window.location.href = url.toString();
}

// Sort posts
function sortPosts(sortType) {
    const url = new URL(window.location);
    url.searchParams.set('sort', sortType);
    window.location.href = url.toString();
}

// Delete confirmation
function confirmDelete(message) {
    return confirm(message || '确定要删除吗？此操作不可撤销。');
}

// Initialize
checkUser();

# users/forms.py
from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import UserProfile   # ✅ 只导入 UserProfile

print("🔥 users/forms.py LOADED")

# ===============================
# 用户资料 + 博客设置表单
# ===============================
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile   # ✅ 必须是 UserProfile
        fields = (
            'nickname',
            'avatar',
            'bio',
            'date_of_birth',
            'location',
            'website',

            'blog_title',
            'blog_description',
            'blog_theme',
            'blog_background',
        )

print("🔥 forms file =", __file__)


# ===============================
# 密码修改表单
# ===============================
class CustomPasswordChangeForm(PasswordChangeForm):
    pass

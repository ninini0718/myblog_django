"""
Django settings for myblog project.
"""
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-n&wq57u^ai_(a9n@z1zudqz&zsp2_7n0#_ec3h4$xa$n6!$o&d')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ],
}

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    # 第三方应用
    'allauth',
    'allauth.account', 
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',  # 添加Google登录
    'allauth.socialaccount.providers.weibo',   # 添加微博登录
    'tinymce',
    'django_summernote',
    'haystack',
    'markdownx',
    'debug_toolbar',
    'ckeditor',
    'widget_tweaks',

    # 自定义应用
    
    'users',
    'core',
    'articles',
    'comments',
    
]

# 合并认证后端（避免重复）
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'myblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.blog_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'myblog.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='myblog'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}

CKEDITOR_CONFIGS = {
      'default': {
          'toolbar': 'full',
          'extraPlugins': ['image', 'code'],
      }
}

MARKDOWNX_SETTINGS = {
      'mode': 'default',
      'auto_scroll': True,
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# myblog/settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    

# 默认主键
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自定义用户模型
AUTH_USER_MODEL = 'users.User'

# Django-allauth配置


SITE_DOMAIN = "localhost:8000"
SITE_NAME = "MyBlog"

ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# 第三方登录（扩展支持Google、Weibo）
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': ['user:email'],
        'AUTH_PARAMS': {'access_type': 'offline'},
        'APP': {
            'client_id': config('GITHUB_CLIENT_ID', default=''),
            'secret': config('GITHUB_SECRET', default=''),
        }
    },
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'offline'},
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_CLIENT_SECRET', default=''),
        }
    },
    'weibo': {
        'SCOPE': ['email', 'profile'],
        'APP': {
            'client_id': config('WEIBO_CLIENT_ID', default=''),
            'secret': config('WEIBO_CLIENT_SECRET', default=''),
        }
    },
}

# Redis缓存
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# 阿里云OSS文件存储
DEFAULT_FILE_STORAGE = 'core.storage.AliyunOSSStorage'

# Haystack搜索
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# ===========================================
# 邮件配置（支持密码找回、评论通知）
# ===========================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.qq.com')
EMAIL_PORT = config('EMAIL_PORT', default=465, cast=int)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# 邮件管理器配置
EMAIL_PRIMARY_PROVIDER = config('EMAIL_PRIMARY_PROVIDER', default='QQ')

# Gmail API配置
GMAIL_CREDENTIALS_PATH = BASE_DIR / 'credentials' / 'gmail_credentials.json'
GMAIL_TOKEN_PATH = BASE_DIR / 'credentials' / 'gmail_token.pickle'

# QQ邮箱SMTP配置
EMAIL_HOST_QQ = config('EMAIL_HOST_QQ', default='smtp.qq.com')
EMAIL_PORT_QQ = config('EMAIL_PORT_QQ', default=465, cast=int)
EMAIL_USE_TLS_QQ = config('EMAIL_USE_TLS_QQ', default=False, cast=bool)
EMAIL_USE_SSL_QQ = config('EMAIL_USE_SSL_QQ', default=True, cast=bool)
EMAIL_HOST_USER_QQ = config('EMAIL_HOST_USER_QQ', default='')
EMAIL_HOST_PASSWORD_QQ = config('EMAIL_HOST_PASSWORD_QQ', default='')

# SendGrid配置
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')

# 测试邮件地址
TEST_EMAIL_ADDRESS = config('TEST_EMAIL_ADDRESS', default='')

# 阿里云OSS配置
ACCESS_KEY_ID = config('ACCESS_KEY_ID', default='')
ACCESS_KEY_SECRET = config('ACCESS_KEY_SECRET', default='')
BUCKET_NAME = config('BUCKET_NAME', default='')
ENDPOINT = config('ENDPOINT', default='')

# 调试工具栏
INTERNAL_IPS = [
    '127.0.0.1',
]

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 登录重定向URL
SITE_ID = 1
LOGIN_REDIRECT_URL = 'users:profile'
LOGOUT_REDIRECT_URL = 'articles:article_list'
ACCOUNT_LOGOUT_REDIRECT_URL = LOGOUT_REDIRECT_URL
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'

ACCOUNT_ALLOW_REGISTRATION = True
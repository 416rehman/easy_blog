"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import re
import mimetypes

from dotenv import load_dotenv

load_dotenv()
import os.path
from pathlib import Path

DEFAULT_DOMAIN = 'https://blog.ahmadz.ai'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIRS = os.path.join(BASE_DIR, 'templates')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "blog\static"),
]
print(os.path.join(BASE_DIR, "blog/static"))
mimetypes.add_type("text/css", ".css", True)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tinymce',
    'background_task',
    'users',
    'blog',
    'hitcount',
    'django_cleanup.apps.CleanupConfig',
    'rest_framework',
    'django_elasticsearch_dsl',
    'django_elasticsearch_dsl_drf',
    'storages'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'blog.middleware.RestrictInactiveUsersMiddleware',
    'csp.middleware.CSPMiddleware',
]

# SameSite cookies
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = None
SESSION_COOKIE_SAMESITE = None

# django-csp
CSP_UPGRADE_INSECURE_REQUESTS = not DEBUG
CSP_BASE_URI = ["'self'"]
CSP_DEFAULT_SRC = ("'self'",)
CSP_IMG_SRC = ["'self'", "https: data:", "blob:"]
CSP_FRAME_SRC = ["'self'", "https:", "data:"]
CSP_SCRIPT_SRC = [
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    "gist.github.com",
    "https://cdnjs.cloudflare.com",
    "https://fonts.googleapis.com",
    "https://unpkg.com",
    "http://127.0.0.1:8000/"
]
CSP_STYLE_SRC = ["'self'",
                 "'unsafe-inline'",
                 "https://github.githubassets.com",
                 "cdnjs.cloudflare.com",
                 "https://fonts.googleapis.com"]
CSP_FONT_SRC = ['https://fonts.gstatic.com']
CSP_CONNECT_SRC = ["'self'", 'https://unpkg.com/']
CSP_INCLUDE_NONCE_IN = ['script-src']
CSP_OBJECT_SRC = ["'none'"]
# CSP_REPORT_URI = ["http://localhost:8000/fake-report-uri/"]
CSP_REPORT_ONLY = False  # enforcement mode

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIRS],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.default_domain',
                'blog.context_processors.aws_media_url'
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/auth/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# TINYMCE
TINYMCE_EXTRA_MEDIA = {
    'css': {
        'all': [
            "/static/css/themes.css",
            "/static/css/base.css"
        ],
    }
}
TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "icons": "thin",
    "menubar": False,
    "plugins": "autoresize quickbars image media table hr codesample textpattern lists code link fullscreen autolink "
               "paste autosave autoresize wordcount",
    "contextmenu": 'formatselect paste link image imagetools table spellchecker lists wordcount code',
    "quickbars_selection_toolbar": "bold italic link | checklist | align | h1 h2 h3 | blockquote ",
    "quickbars_insert_toolbar": "paste codesample | align | image media table hr | code",
    "textpattern_patterns": [
        {"start": '*', "end": '*', "format": 'italic'},
        {"start": '**', "end": '**', "format": 'bold'},
        {"start": '1. ', "cmd": 'InsertOrderedList'},
        {"start": '* ', "cmd": 'InsertUnorderedList'},
        {"start": '- ', "cmd": 'InsertUnorderedList'},
        {"start": 'a. ', "cmd": 'InsertOrderedList', "value": {'list-style-type': 'lower-alpha'}},
        {"start": '##', "format": 'h2'},
        {"start": '###', "format": 'h3'},
        {"start": '####', "format": 'h4'},
        {"start": '#####', "format": 'h5'},
        {"start": '######', "format": 'h6'},
        {"start": '`', "end": '`', "format": 'code'},
        {"start": '```', "format": 'pre'},
    ],
    "smart_paste": True,
    # 'paste_word_valid_elements': 'b,strong,i,em,h1,h2,h3',
    'paste_data_images': True,
    'image_caption': True,
    "toolbar": False,
    "height": 500,
    "placeholder": "Tell your story...",
    "content_style": "@import url('https://fonts.googleapis.com/css2?family=Merriweather&display=swap'); body { "
                     "font-family: 'Merriweather', serif; font-size: min(4vw, 15px); color: var(--text-color); background-color: --var(primary-color);}"
                     "code {"
                     "background-color: #828282 !important;"
                     "border-radius: 2px;"
                     "padding: 1px;"
                     "}"
                     "span.mce-preview-object.mce-object-iframe {"
                     "display: block;"
                     "}"
                     "p {"
                     "font-family: 'Merriweather', serif;"
                     "font-size:calc(13px + 0.4vw);"
                     "font-weight: 400;"
                     "letter-spacing: 0.003em;"
                     "word-spacing: 0.05em;"
                     "line-height: 32px;"
                     "}"
                     "body {"
                     "margin: 0;"
                     "background-color: var(--primary-color);"
                     "}"
                     "iframe {"
                     "width:100%;"
                     "}"
                     ".mce-content-body:not([dir=rtl])[data-mce-placeholder]:not(.mce-visualblocks)::before { color: #757575;}"
                     "iframe.pdf-iframe {"
                     "overflow: auto;"
                     "resize: vertical;"
                     "height: 800px;"
                     "width: 100%;"
                     "border-radius: 5px;"
                     "border-style: solid;"
                     "border-color: var(--button-border);"
                     "}",
    "branding": False,
    "statusbar": False,
    "body_class": 'dark',
    "autosave_interval": '20s',
    "autosave_restore_when_empty": True,
    "allow_script_urls": True,
    "paste_postprocess": "function(plugin, args) {"
                         "console.log(args.node.textContent);"
    # PDF smart embed
                         "if (args.node.textContent.match(/(https?:\/\/)?([A-Za-z0-9\-]+)?\.([A-Za-z0-9\-]+)\.([A-Za-z0-9\-]+)(\/?.*\/(.+\.pdf$)$)/ig)) { "
                         "let br = document.createElement('br');"
                         "const pdfiframe = document.createElement('iframe');"
                         "pdfiframe.setAttribute('src', args.node.textContent);"
                         "pdfiframe.classList.add('pdf-iframe');"
                         "args.node.appendChild(br);"
                         "args.node.appendChild(pdfiframe);"
                         "}"
    # GIST smart embed
                         "else {"

                         "const regex = /(\<script src=\")(https:\/\/gist.github.com\/\S*\.js)(\"><\/script>)/ig;"
                         "let found = regex.exec(args.node.textContent);"
                         "let link;"
                         "if (found && found[2]) link = found[2];"
                         "else { "
                         "link = /https:\/\/gist.github.com\/\S*\/\S*/.exec(args.node.textContent);"
                         "if (link && link[0]) {"
                         "link = link[0];"
                         "if (link && !link.endsWith('.js')) link = link + '.js';"
                         "}"
                         "}"
                         "if (link) {"
                         "let br = document.createElement('br');"
                         "const random_id='_' + Math.random().toString(36).substr(2,9);"
                         "const gistiframe = document.createElement('iframe');"
                         "gistiframe.setAttribute('id', random_id);"
                         "gistiframe.setAttribute('src', `data:text/html;charset=utf-8, "
                         "<head><base target=\"_blank\"></head> <body><script src='${link}'></script>"
                         "<script type=\"text/javascript\">window.addEventListener(\"load\",function(){const myID='${random_id}';let o={iframeID: myID, height:document.body.scrollHeight,width:document.body.scrollWidth};window.parent.postMessage(o,\"*\")});</script>"
                         "</body>`);"
                         "gistiframe.classList.add('gist-iframe');"
                         "args.node.appendChild(br);"
                         "args.node.appendChild(gistiframe);"
                         "}"
                         "}"
                         "}",
}

# Twilio SendGrid
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# AWS
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_PUBLIC_MEDIA_LOCATION = 'media'

DEFAULT_FILE_STORAGE = 'mysite.storage_backends.MediaStorage'

# ELASTICSEARCH
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'ORDERING_PARAM': 'ordering',
}

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}

ELASTICSEARCH_INDEX_NAMES = {
    'search.documents.post': 'post',
    'search.documents.user': 'user',
}

# USERS
AUTH_USER_MODEL = 'users.User'

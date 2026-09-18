import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key' # Replace with production key in prod

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jazzmin', # Place before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third Party
    'rest_framework',

    # Local Apps
    'inventory',
    'members',
    'bookings',
    'payments',
    'audit',
    'dashboard',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'housing.apm_system.AdvancedAPMMiddleware', # <-- ANTIGRAVITY APM CAMERA
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

if not DEBUG:
    # Only use WhiteNoise in production
    MIDDLEWARE.insert(3, 'whitenoise.middleware.WhiteNoiseMiddleware')

CACHE_MIDDLEWARE_SECONDS = 120
CACHE_MIDDLEWARE_KEY_PREFIX = 'housing'

ROOT_URLCONF = 'housing.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'housing.wsgi.application'

POSTGRES_DB = os.environ.get("POSTGRES_DB", "housing")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "housing")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "housing")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
        'CONN_MAX_AGE': 600,  # Keep DB connections open to speed up requests
    }
}

AUTH_PASSWORD_VALIDATORS = [] # Simplified for offline dev

LANGUAGE_CODE = 'ar' # Arabic
TIME_ZONE = 'Africa/Cairo' # Local time
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cache static files in browser for 1 year (after first load, browser never re-downloads)
WHITENOISE_MAX_AGE = 31536000

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# In-memory cache (avoids hitting the slow HDD for repeated data)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'housing-cache',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# Store sessions in cache+DB (reads from fast RAM instead of slow HDD)
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

X_FRAME_OPTIONS = 'SAMEORIGIN'

DATE_INPUT_FORMATS = [
    '%d/%m/%Y',    # 31/03/2026 or 2/5/2026
    '%d-%m-%Y',    # 31-03-2026 or 2-5-2026
    '%Y-%m-%d',    # 2026-03-31 (ISO)
    '%d/%m/%y',    # 31/03/26
    '%d-%m-%y',    # 31-03-26
]

JAZZMIN_SETTINGS = {
    "site_title": "نظام إدارة الإسكان",
    "site_header": "الإسكان",
    "site_brand": "المجمع الخدمى لنوادي وفنادق 6 اكتوبر",
    "site_logo": None,
    "welcome_sign": "مرحباً بك في نظام إدارة الإسكان",
    "copyright": "made by : AhmedEssam & mokhtar the IT departement 2026",
    "search_model": ["members.Member", "bookings.Booking"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "الرئيسية", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "لوحة المتابعة", "url": "/dashboard/", "new_window": False, "permissions": ["dashboard.view_wallboard"]},
        {"name": "تقرير الفاكسات", "url": "/dashboard/fax/", "new_window": False, "permissions": ["reports.view_faxreport"]},
        {"name": "تقرير الخلوات", "url": "/dashboard/vacancies/", "new_window": False, "permissions": ["reports.view_vacanciesreport"]},
        {"name": "لوحة التحليلات", "url": "/analytics/", "new_window": False},
        {"app": "bookings"},
        {"app": "inventory"},
        {"app": "members"},
    ],
    "show_sidebar": False,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "inventory.Club": "fas fa-hotel",
        "inventory.Building": "fas fa-building",
        "inventory.Unit": "fas fa-door-open",
        "members.Member": "fas fa-id-card",
        "bookings.Booking": "fas fa-calendar-check",
    },
    "default_icon_parents": "fas fa-chevron-circle-left",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": "css/jazzmin_custom_v5.css",
    "custom_js": "js/admin_back_btn.js",
    "show_ui_builder": False,
    "changeform_format": "single",
    "changeform_format_overrides": {},
    "ui_sections": True,
}

JAZZMIN_UI_CONFIG = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

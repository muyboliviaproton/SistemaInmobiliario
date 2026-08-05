from pathlib import Path
# ============================================================
# RUTAS DEL PROYECTO
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
# ============================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================
SECRET_KEY = 'django-insecure-i(t7wi@fl%2t%=c_&*ea33zgu$3wqd2zz@dv%10@*(a#g#jht4'
DEBUG = True
ALLOWED_HOSTS = []
# ============================================================
# APLICACIONES INSTALADAS
# ============================================================
INSTALLED_APPS = [
    # --------------------------------------------------------
    # Aplicaciones de Django
    # --------------------------------------------------------
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # --------------------------------------------------------
    # Aplicaciones propias del sistema
    # --------------------------------------------------------
    'accounts',
    'dashboard',
    'clientes',
    'gestion_seguimientos',
    'oportunidades',
    'visitas',
    'recordatorios',
    'lotes',
    'mapa',
]
# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]
# ============================================================
# CONFIGURACIÓN PRINCIPAL DE URLS
# ============================================================
ROOT_URLCONF = 'config.urls'
# ============================================================
# CONFIGURACIÓN DE TEMPLATES
# ============================================================
TEMPLATES = [
    {

        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # ----------------------------------------------------
        # Carpeta global de templates
        # ----------------------------------------------------
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        # ----------------------------------------------------
        # También buscar templates dentro de cada aplicación
        # ----------------------------------------------------

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.datos_generales',
            ],

        },

    },

]


# ============================================================
# CONFIGURACIÓN WSGI
# ============================================================

WSGI_APPLICATION = 'config.wsgi.application'
# ============================================================
# BASE DE DATOS POSTGRESQL
# ============================================================
DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sistema_inmobiliario',
        'USER': 'postgres',
        'PASSWORD': '12345678',
        'HOST': 'localhost',
        'PORT': '5432',
    }

}


# ============================================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================================

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


# ============================================================
# INTERNACIONALIZACIÓN
# ============================================================

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

# ============================================================
# ARCHIVOS ESTÁTICOS
# ============================================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ============================================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# ============================================================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = '/accounts/login/'
# ============================================================
# CLAVE PRIMARIA POR DEFECTO
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
from datetime import datetime
from .local import *

if ENABLE_LOG:
    log_date = datetime.now().strftime("%Y/%m")
    log_today_date = datetime.now().strftime("%d")
    LOG_DIR = os.path.join(BASE_DIR, 'logs', log_date)
    os.makedirs(LOG_DIR, exist_ok=True)

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[{asctime}] {levelname} {module}: {message}',
                'style': '{',
            },
            'simple': {
                'format': '[{asctime}] {levelname}: {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': os.path.join(LOG_DIR, f'{log_today_date}.log'),
                'formatter': 'verbose',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }


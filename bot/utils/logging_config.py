config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'detailed': {
            'format': '[%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(lineno)d | %(message)s ]',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        },

        'simple': {
            "format": '[%(asctime)s] | %(levelname)s | %(message)s ]',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        },

    },

    'handlers': {
        'console_logs': {
            'level': 'WARNING',
            'formatter': 'simple',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        },

        'detailed_logs': {
            'level': 'INFO',
            'formatter': 'detailed',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 мб
            'backupCount': 2,
        },
    },

    'loggers': {
        '': {
            'handlers': ['console_logs', 'detailed_logs'],
            'level': 'INFO'
        }
    },
}
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'app_env': os.getenv('APP_ENV', 'development'),
    'host': os.getenv('APP_HOST', 'http://localhost:5000'),
    'web_app_url': os.getenv('WEB_APP_URL', 'http://localhost:3000'),
    'database': {
        'name': os.getenv('DB_NAME', 'stormiqdb'),
        'host': os.getenv('DB_HOST_NAME', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', 3306)
    },
    'email': {
        'support_email': '',
        'support_name': 'StormIQ'
    },
    'sendgrid': {
        'api_key': os.getenv('SENDGRID_API_KEY')
    }
}


class Config:
    def __init__(self):
        self._config = config

    def get(self, key):
        keys = key.split('.')
        value = self._config
        for key in keys:
            value = value.get(key)
            if value is None:
                break

        return value

    def is_production(self):
        return self._config.get('app_env') == 'production'

    def is_staging(self):
        return self._config.get('app_env') == 'staging'

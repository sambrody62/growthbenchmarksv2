import os

class Config(object):
    PROJECT_ID = "fathom-8cdfe"

    SERVICE_ACCOUNT = os.path.join('fathom','firebase-private-key.json')

    # Platform connectors
    CONNECTORS = {
        "FACEBOOK": {
            "APP_ID": os.environ.get("FACEBOOK_APP_ID"),
            "APP_SECRET": os.environ.get("FACEBOOK_APP_SECRET"),
            "PREFIX": "fb"
        },
        "GOOGLE_ADS": {
            "APP_ID": os.environ.get("GOOGLE_ADS_APP_ID"),
            "APP_SECRET": os.environ.get("GOOGLE_ADS_APP_SECRET"),
            "APP_DEVELOPER_TOKEN": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "PREFIX": "google"
        }
    }

    CLOUD_RUN_REVISION = os.environ.get('K_REVISION', "NOT_SET")

    POSTMARK_SERVER_API_TOKEN = os.environ.get("POSTMARK_SERVER_API_TOKEN")

class DevConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

class ProdConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'INFO'  # CRITICAL / ERROR / WARNING / INFO / DEBUG
import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "785d87dd-8c7f-442b-954b-9abd3d363c60")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "lnm7Q~wsbE2v.c.-8aOuF4sD89.Uwy2Jpe1O3")
    CONNECTION_NAME = os.environ.get("ConnectionName", "connection string")

    # APP_ID = os.environ.get("MicrosoftAppId", "")
    # APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
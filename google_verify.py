from google.oauth2 import id_token
from google.auth.transport import requests
import os

client_id = os.getenv("client_id")


def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

        return idinfo
    except ValueError:
        print("Invalid Token")
        return None
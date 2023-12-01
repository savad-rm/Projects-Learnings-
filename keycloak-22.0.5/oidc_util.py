import json
import requests
import base64
import logging

# Load the client_secrets.json file into a Python dictionary.
with open("client_secrets.json", "r") as f:
    client_secrets = json.load(f)

CLIENT_ID = client_secrets["web"]["client_id"]
CLIENT_SECRET = client_secrets["web"]["client_secret"]

KC_URL = client_secrets["web"]["issuer_url"]
KC_REALM = client_secrets["web"]["realms"]

def refresh_token(refresh_token):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'code': refresh_token,
        'grant_type': 'refresh_token'
    }
    url = KC_URL + 'realms/' + KC_REALM + '/protocol/openid-connect/token'
    response = requests.post(url, data=data)
    if response.status_code != requests.codes.ok:
        return """
                {'access_token': '',
                'expires_in': -1,
                'refresh_expires_in': -1,
                'refresh_token': ''
                'token_type': 'Bearer',
                'id_token': ''
                'not-before-policy': 0,
                'session_state': '',
                'scope': 'openid email profile'} 
                """
    else:
        return  response.json()


def get_access_token(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    url = KC_URL + '/realms/' + KC_REALM + '/protocol/openid-connect/token'
    response = requests.post(url, data=data)
    if response.status_code != requests.codes.ok:
        return """
                {'access_token': '',
                'expires_in': -1,
                'refresh_expires_in': -1,
                'refresh_token': ''
                'token_type': 'Bearer',
                'id_token': ''
                'not-before-policy': 0,
                'session_state': '',
                'scope': 'openid email profile'} 
                """
    else:
        return  response.json()
    
def get_user_profile(access_token):

    if access_token and access_token.startswith('Bearer'):
        access_token = access_token[7:]

    url = KC_URL + '/realms/' + KC_REALM + '/protocol/openid-connect/userinfo'
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)
    if response.status_code != requests.codes.ok:
        return """
                {
                "sub": "",
                "email_verified": false,
                "name": "",
                "preferred_username": "",
                "given_name": "",
                "family_name": "",
                "email": ""
                }

                """
    else:
        return  response.json()
    
def validate_access_token_for_user(access_token):
    
    # Remove header prefix "Bearer"
    if access_token and access_token.startswith('Bearer'):
        access_token = access_token[7:]

    encoded_header = f"{CLIENT_ID}:{CLIENT_SECRET}"

    # Encode the string to Base64
    encoded_bytes = base64.b64encode(encoded_header.encode('utf-8'))

    # Convert the bytes to a string (optional)
    encoded_string = encoded_bytes.decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {encoded_string}'
    }

    body = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'token': access_token
    }
    
    valid_url = KC_URL + '/realms/' + \
        KC_REALM+ '/protocol/openid-connect/token/introspect'
    response = requests.post(valid_url, data=body, headers=headers)

    data = response.json()
    logging.debug(f"Validating access token: {str(data)}")
    if data['active']:
        return data['username']
    else:
        return None
    
    
def logout_user(access_token):
    
    # Remove header prefix "Bearer"
    if access_token and access_token.startswith('Bearer'):
        access_token = access_token[7:]

    encoded_header = f"{CLIENT_ID}:{CLIENT_SECRET}"

    # Encode the string to Base64
    encoded_bytes = base64.b64encode(encoded_header.encode('utf-8'))

    # Convert the bytes to a string (optional)
    encoded_string = encoded_bytes.decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {encoded_string}'
    }

    body = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'token': access_token
    }
    
    valid_url = KC_URL + '/realms/' + \
        KC_REALM+ '/protocol/openid-connect/logout'
    response = requests.post(valid_url, data=body, headers=headers)
    print(response)
    # data = response.json()
    # print(data)
    return response.json

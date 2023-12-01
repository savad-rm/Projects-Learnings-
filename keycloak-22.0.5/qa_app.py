from flask import Flask, request, jsonify, redirect, abort, render_template
from services import main as main
import json
#from user_agent import parse
# from flask_oidc import OpenIDConnect

# from flask_smorest import Api
from flask_jwt_extended import JWTManager
import secrets
import logging
import os
import json
import logging
from flask_cors import CORS
import requests
import jwt
import oidc_util
from flask_oidc_ext import OpenIDConnect
from oauth2client.client import OAuth2Credentials
from logging import Formatter, FileHandler
# from flask_session import Session

#logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# CORS(app)
# session = Session(app)

# Load the client_secrets.json file into a Python dictionary.
with open("client_secrets.json", "r") as f:
    client_secrets = json.load(f)

KC_URL = client_secrets["web"]["issuer_url"]
KC_REALM = client_secrets["web"]["realms"]

cors = CORS(app, resources={r"/*": {"origins": KC_URL}})

# os.environ["CLIENT_ID"] = "wbs-client" 
# os.environ["CLIENT_SECRET"] = "jXOjbvuTEdIVa53SAn8hdPM048PZfz3U" 
# os.environ["KEYCLOAK_URI"] = "http://localhost:8080" 
# os.environ["REALM"] = "chat-bot" 

app.logger.setLevel(logging.INFO)

# app.config["OIDC_CALLBACK_ROUTE"] = "/oidc_callback"
# Once you have set the OIDC_CALLBACK_ROUTE configuration variable, 
# you can redirect users to the OpenID Connect provider's login page using the oidc.login() function.
# app.config['SESSION_TYPE'] = 'filesystem'

app.config.update({
    'SECRET_KEY': 'Wu49INqQ1qmcLEEywzWeFZH94noIVFtQFgi5tWdn9qihF3KQFWrfzqQnFrN2k4VHjoK5Rr1xjgENxhpzxMSGTcDF2ct7sg4OBeOw',
    'SESSION_TYPE': 'filesystem',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'qa-document',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'bearer',
    'OIDC_REDIRECT_URI': 'http://localhost:5000/'
})
oidc = OpenIDConnect(app)

@oidc.accept_token
@app.route('/validate_token', methods=['GET'])
@oidc.accept_token(require_token=True)
def validate_token(access_token):
    return oidc_util.validate_access_token(access_token)


@app.route('/refresh_token', methods=['GET'])
def refresh_token(refresh_token):
    return oidc_util.refresh_token(refresh_token)

@app.route("/oidc_callback")
def oidc_callback():
    # Get the user's information and access token from Flask-OIDC
    user_info = oidc.user_getinfo()
    access_token = oidc.access_token

    # Store the user's information in the session
    # session["user_info"] = user_info
    # user_info = session["user_info"] 

    # Redirect the user to a protected page
    return redirect("/private")

@app.route('/private')
@oidc.require_login
def private_login():
    # info = oidc.user_getinfo(['email', 'openid_id'])
    info = oidc.user_getinfo(['preferred_username', 'email', 'sub'])
    username = info.get('preferred_username')
    email = info.get('email')
    user_id = info.get('sub')  
    logging.debug(f"username: {username}, email: {email}")
    access_token = ''
    if user_id in oidc.credentials_store:
        try:
            access_token = OAuth2Credentials.from_json(oidc.credentials_store[user_id]).access_token
            refresh_token = OAuth2Credentials.from_json(oidc.credentials_store[user_id]).refresh_token
            # session["access_token"] = access_token
            # session["refresh_token"] = refresh_token

            if not access_token:
                access_token = refresh_token(refresh_token) 

            logging.info(f"access_token: {access_token[:15]}")
            logging.info(f"refresh_token: {refresh_token[:15]}")
            
            # headers = {'Authorization': 'Bearer %s' % (access_token)}
            # action_url = f"{server_url}get_document_list"
            # greeting = requests.get(action_url, headers=headers).text
        except Exception as e:
            print(f"Could not access {str(e)}")
    return render_template('index.html',access_token=access_token )

LOGIN_MESSAGE = 'Invalid user. Please login'

# Create a REST endpoint to serve the HTML page
@app.route('/')
def index():
    return render_template('login.html')


# @app.route('/')
# def elastic_question_with_pdf():
#     return render_template('elastic_question_with_pdf.html')

@app.route('/generate_presentation')
@oidc.require_login
def generate_presentation():
    return render_template('generate_presentation_from_pdf.html')

@app.route('/process_file', methods=['POST'])
@oidc.require_login
def process_file():
    # Check if a file was uploaded
    if 'pdf-file' not in request.files:
        return 'No PDF file uploaded', 400

    pdf_file = request.files['pdf-file']
    try:            
        # Check if the file is a PDF
        if pdf_file.filename.endswith('.pdf') or pdf_file.filename.endswith('.PDF'):
            # Process the PDF file here
            # You can perform operations like text extraction, analysis, etc.
            # Replace the code below with your own processing logic
            file_content = pdf_file.read()
            file_name = pdf_file.filename
            response = jsonify({'message': main.process_file(file_name, file_content)})
            response.status_code = 200
            return response
        else:
            response = jsonify({'message': 'Invalid file format. Only PDF files are allowed'})
            response.status_code = 400
            return response
    
    except Exception as e:
        response = jsonify({'message': str(e)})
        response.status_code = 400
        return response


@app.post("/ask_question_against_pdf")
# @oidc.require_login
def ask_question_against_pdf():
    if request.method == 'OPTIONS':
        response_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        print('::OPTIONS::')
        return ('', 204, response_headers)
    else:
        access_token = request.headers.get('Authorization')
        logging.debug(f"Authorization from request: {access_token}")

        request_data = request.get_json()
        question = request_data['question']
        selected_topic = request_data['topic']
        
        user_name = oidc_util.validate_access_token_for_user(access_token)
        logging.info(f"user_name from access token {user_name}")
        # user_name = request_data['user_name']
        if user_name is None or user_name == "":
            return {"message":LOGIN_MESSAGE}
        else:
            # ip_address = request.remote_addr
            # user_agent = request.user_agent.string
            # user_name = f"IP Address: {ip_address}, User Agent: {user_agent}"
            if(question == "" or len(question) < 10 or len(question) > 2500):

                result = {"message":"ERROR: Bad request. Ensure that your question has is with in 10 - 2500 characters"}
                """
                abort(
                    400,
                    description="Bad request. Ensure that your question has is with in 10 - 2500 characters"
                )"""
            else:
                
                result = {"message":main.ask_question_against_pdf(selected_topic, question, user_name)}
            #response = {'message': result}  # create a response dictionary
            return json.dumps(result)  # return the response as JSON


@app.post("/generate_presentation_from_document")
@oidc.require_login
def generate_presentation_from_document():
    if request.method == 'OPTIONS':
        response_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        print('::OPTIONS::')
        return ('', 204, response_headers)
    else:
        request_data = request.get_json()
        template = 'pre-sales-template-02' #request_data['template']
        selected_topic = request_data['topic']
        ip_address = request.remote_addr
        user_agent = request.user_agent.string
        user_name = f"IP Address: {ip_address}, User Agent: {user_agent}"
        print(user_name)

    if(template == "" ):

        result = {"message":"ERROR: Bad request. Ensure that you have specified valid template"}
        """
        abort(
            400,
            description="Bad request. Ensure that your question has is with in 10 - 2500 characters"
        )"""
    else:
        result = {"message":main.generate_presentation_with_pdf(template, selected_topic, user_name)}
    #response = {'message': result}  # create a response dictionary
    return json.dumps(result)  # return the response as JSON


@app.get("/get_document_list")
@oidc.require_login
def get_document_list():
    result = {"message":main.get_document_list()}
    return json.dumps(result)  

@app.route('/ping')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    #Setup the logger
    # app.run(host='192.168.185.239', port=5010, debug=False)
    app.run(debug=False)
    

def create_app(db_url=None):
    
    #JWT configuration
    app.config["JWT_SECRET_KEY"] = "326196139961721987606935457191380359653"
    #secrets.SystemRandom().getrandbits(128)
    #"Q8pM8YxdL4XDYiT61aHY7KwQ1OKo"
    jwt = JWTManager(app)
    return app


@app.route('/token_login', methods=['POST'])
def get_token():
    print('app token_login....')
    body = request.get_json()
    for field in ['username', 'password']:
        if field not in body:
            return error(f"Field {field} is missing!"), 400
    data = {
        'grant_type': 'password',
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'username': body['username'],
        'password': body['password']
    }
    url = ''.join([
        os.getenv('KEYCLOAK_URI'),
        '/realms/',
        os.getenv('REALM'),
        '/protocol/openid-connect/token'
    ])
    response = requests.post(url, data=data)
    if response.status_code > 200:
        message = "Error invalid username/password"
        return error(message), 400
    tokens_data = response.json()
    # print(f'tokens_data: {tokens_data}')
    access_token = tokens_data['access_token']
    refresh_token = tokens_data['refresh_token']
    profile_dict = decode_jwt_token(access_token)
    user_name = profile_dict['name']
    email = profile_dict['email']
    access_roles = profile_dict['realm_access']['roles']
    print(f'login user: {user_name}; email: {email}; access_roles: {access_roles}')
    ret = {
        'tokens': {"access_token": access_token,
                   "refresh_token": refresh_token, }
    }

    return jsonify(ret), 200

def decode_jwt_token(jwt_token):
    try:
        if jwt_token.startswith("Bearer "):
            jwt_token = jwt_token[len("Bearer "):]
        elif jwt_token.startswith("Authorization: Bearer "):
            jwt_token = jwt_token[len("Authorization: Bearer "):]

        # token = jwt_token.split(" ")[1]  # Extract the token from the bearer token string
        header = {"alg": "RS256", "typ": "JWT"}
        # Decode the JWT using the header
        decoded_token = jwt.decode(jwt_token, algorithms=["RS256"], options={"verify_signature": False}, header=header)

        return decoded_token
    except jwt.exceptions.DecodeError:
        # Handle decoding errors
        return None


def decode_access_token(access_token):
    try:
        decoded_token = jwt.decode(access_token, algorithms=["RS256"], verify=False)
        return decoded_token
    except jwt.exceptions.DecodeError:
        # Handle decoding errors
        return None

@app.route('/token_refresh/', methods=['POST'])
def refresh_token():
    body = request.get_json()
    for field in ['refresh_token']:
        if field not in body:
            return error(f"Field {field} is missing!"), 400
    data = {
        'grant_type': 'refresh_token',
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'refresh_token': body['refresh_token'],
    }
    url = os.getenv('KEYCLOAK_URI') + '/realms/' + \
        os.getenv('REALM') + '/protocol/openid-connect/token'
    response = requests.post(url, data=data)
    if response.status_code != requests.codes.ok:
        return error("Error en refresh token"), 400
    data = response.json()
    ret = {
        "access_token": data['access_token'],
        "refresh_token": data['refresh_token']
    }
    return jsonify(ret), 200


@app.route('/users/', methods=['POST'])
def create_user():
    try:
        body = request.get_json()
        endpoint = '/users'
        data = {
            "email": body.get('email'),
            "username": body.get('email'),
            "firstName": body.get('name'),
            "lastName": body.get('sirname'),
            "credentials": [{"value": body.get('password'), "type": 'password', 'temporary': False}],
            "enabled": True,
            "emailVerified": False
        }
        response = keycloak_post(endpoint, data)
    except KeycloakAdminTokenError  as e:
        try:
            message = e.response.json().get('errorMessage')
        except Exception as err:
            message = e.message
        app.logger.error(e.traceback())
        return error(message), 400
    except Exception as e:
        print(e)
        return error('Error with keycloak'), 400
    return "", 204


@app.errorhandler(404)
def not_found(e):
    return error("The requested URL path does not exist in this API"), 404


@app.errorhandler(405)
def doesnt_exist(e):
    return error("The requested method not allowed"), 405


def error(message):
    return jsonify({
        'success': False,
        'message': message
    })


def keycloak_post(endpoint, data):
    """
        Perform a POST request to Keycloak
        :param {string} endpoint: Keycloak endpoint
        :param {object} data: Keycloak data object
        :return {Response}: request response object
    """
    url = os.getenv('KEYCLOAK_URI') + '/admin/realms/' + \
        os.getenv('REALM') + endpoint
    headers = get_keycloak_headers()
    response = requests.post(url, headers=headers, json=data)
    if response.status_code >= 300:
        app.logger.error(response.text)
        raise KeycloakAdminTokenError(response)
    return response


def get_keycloak_headers():
    """
    Devuelve los headers necesarios para comunicarlos con la API de Keycloak
    utilizando el usuario de administración del Realm.
    :return {object} Objeto con headers para API de Keycloak
    """
    return {
        'Authorization': 'Bearer ' + get_keycloak_access_token(),
        'Content-Type': 'application/json'
    }


def get_keycloak_access_token():
    """
    Devuelve los tokens del usuario `admin` de Keycloak
    :returns {string} Keycloak admin user access_token
    """
    data = {
        'grant_type': 'password',
        'client_id': 'admin-cli',
        'username': os.getenv('ADMIN_USER'),
        'password': os.getenv('ADMIN_PASS')
    }
    response = requests.post(os.getenv('KEYCLOAK_URI') + '/realms/' +
                             os.getenv('REALM') + '/protocol/openid-connect/token', data=data)
    if response.status_code != requests.codes.ok:
        raise KeycloakAdminTokenError(response)
    data = response.json()
    return data.get('access_token')


class KeycloakAdminTokenError(Exception):
    message = 'Keycloak error'

    def __init__(self, response, message=None):
        if message is not None:
            self.message = message
        # Call the base class constructor with the parameters it needs
        super().__init__(self.message)
        # Now for your custom code...
        self.response = response

    def __str__(self):
        return json.dumps({
            'message': self.message,
            'status_code': self.response.status_code,
            'text': self.response.text
        })
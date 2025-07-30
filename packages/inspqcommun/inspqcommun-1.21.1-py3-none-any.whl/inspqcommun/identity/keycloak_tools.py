import os
import socket
import jwt
import time
import uuid
from inspqcommun.identity.keycloak import KeycloakAPI, get_service_account_token, get_token
import ast

class KeycloakEnvironment():

    JWT_SECRET = 'secret'
    JWT_ALGO = 'HS256'
    
    def __init__(self,
                 defaultKeycloakPort:int=18081,
                 defaultAuthClientId:str="admin-cli",
                 defaultAuthClientSecret:str=None,
                 defaultProtocol:str="http",
                 defaultAuthRealm:str="master",
                 defaultAuthUser:str=None,
                 defaultAuthPassword:str=None,
                 defaultAdminAuthUser:str='admin',
                 defaultAdminAuthPassword:str='admin',
                 defaultAdminAuthRealm:str='master',
                 defaultValidateCert:bool=False,
                 defaultKeycloakEnabled:bool=True,
                 defaultBaseKeycloakUrl:str="http://keycloak.url/auth",
                 ) -> None:
        self.defaultKeycloakPort = defaultKeycloakPort
        self.defaultAuthClientId = defaultAuthClientId
        self.defaultAuthClientSecret = defaultAuthClientSecret
        self.defaultProtocol = defaultProtocol
        self.defaultAuthRealm = defaultAuthRealm
        self.defaultAuthUser = defaultAuthUser
        self.defaultAuthPassword = defaultAuthPassword
        self.defaultAdminAuthUser = defaultAdminAuthUser
        self.defaultAdminAuthPassword = defaultAdminAuthPassword
        self.defaultValidateCert = defaultValidateCert
        self.defaultAdminAuthRealm = defaultAdminAuthRealm
        
        if 'KEYCLOAK_ENABLED' in os.environ:
            self.keycloak_enabled = bool(self.__str_to_bool(os.environ['KEYCLOAK_ENABLED']))
        else:
            self.keycloak_enabled = defaultKeycloakEnabled
        if 'KEYCLOAK_BASE_URL' in os.environ:
            self.keycloak_url = "{0}/auth".format(os.environ['KEYCLOAK_BASE_URL'])
        elif defaultBaseKeycloakUrl:
            self.keycloak_url = defaultBaseKeycloakUrl if defaultBaseKeycloakUrl.endswith('/auth') else defaultBaseKeycloakUrl + "/auth"
        else:
            self.keycloak_url = "{protocol}://{host}:{port}/auth".format(
                protocol=self.defaultProtocol,
                host=socket.getfqdn(),
                port=self.defaultKeycloakPort)
            print("URL Keycloak non specifie: Utilisation de l'URL par defaut")
        self.keycloak_auth_realm = os.environ['KEYCLOAK_AUTH_REALM'] if 'KEYCLOAK_AUTH_REALM' in os.environ else self.defaultAuthRealm
        self.keycloak_auth_client_id = os.environ['KEYCLOAK_AUTH_CLIENT_ID'] if 'KEYCLOAK_AUTH_CLIENT_ID' in os.environ else self.defaultAuthClientId
        self.keycloak_auth_client_secret = os.environ.get('KEYCLOAK_AUTH_CLIENT_SECRET', self.defaultAuthClientSecret)
        self.keycloak_auth_user = os.environ['KEYCLOAK_AUTH_USER'] if 'KEYCLOAK_AUTH_USER' in os.environ else self.defaultAuthUser
        self.keycloak_auth_password = os.environ['KEYCLOAK_AUTH_PASSWORD'] if 'KEYCLOAK_AUTH_PASSWORD' in os.environ else self.defaultAuthPassword
        self.keycloak_admin_auth_user = os.environ['KEYCLOAK_ADMIN_AUTH_USER'] if 'KEYCLOAK_ADMIN_AUTH_USER' in os.environ else self.defaultAdminAuthUser
        self.keycloak_admin_auth_password = os.environ['KEYCLOAK_ADMIN_AUTH_PASSWORD'] if 'KEYCLOAK_ADMIN_AUTH_PASSWORD' in os.environ else self.defaultAdminAuthPassword
        self.keycloak_admin_auth_realm = os.environ['KEYCLOAK_ADMIN_AUTH_REALM'] if 'KEYCLOAK_ADMIN_AUTH_REALM' in os.environ else self.defaultAdminAuthRealm
        self.validate_certs = bool(self.__str_to_bool(os.environ['VALIDATE_CERTS'])) if 'VALIDATE_CERTS' in os.environ else self.defaultValidateCert
        self.kc = self.init_keycloak_api()

    def init_keycloak_api(self) -> KeycloakAPI:
        if self.keycloak_enabled and self.keycloak_admin_auth_user is not None and self.keycloak_admin_auth_password is not None:
            kcapi = KeycloakAPI(auth_keycloak_url=self.keycloak_url,
                         auth_client_id="admin-cli",
                         auth_username=self.keycloak_admin_auth_user,
                         auth_password=self.keycloak_admin_auth_password,
                         auth_realm=self.keycloak_admin_auth_realm,
                         auth_client_secret=None,
                         validate_certs=self.validate_certs)
        else:
            kcapi = None
        
        return kcapi
    
    def authenticate(self,
                     client_roles=[],
                     realm_roles:list=[],
                     given_name:str=None,
                     family_name:str=None,
                     username:str=None,
                     password:str=None,
                     client_id:str=None) -> dict:
        if self.keycloak_enabled:
            if not self.keycloak_auth_user or not self.keycloak_auth_password:
                return self.__authenticate_by_service_account(client_id=client_id)
            else:
                return self.__authenticate_by_username_password(client_id=client_id,
                                                                username=username,
                                                                password=password)
        else:
            if client_id is None:
                client_id = self.keycloak_auth_client_id
            preferred_username = username if username is not None else "service-account-{client_id}".format(
                client_id=client_id
            )
            return self.__get_test_access_token(
                client_id=client_id,
                client_roles=client_roles,
                realm_roles=realm_roles,
                given_name=given_name,
                family_name=family_name,
                preferred_username=preferred_username)

    def get_token_url(self) -> str:
        token_url = KeycloakAPI.format_token_url(baseurl=self.keycloak_url, realm=self.keycloak_auth_realm)
        return token_url

    def get_client_secret(self, client_id:str, realm:str=None) -> str:
        if realm is None:
            realm = self.keycloak_auth_realm
        if self.keycloak_enabled and (self.kc is not None or self.init_keycloak_api() is not None):
            keycloak_client = self.kc.get_client_by_clientid(client_id=client_id, realm=realm)
            keycloak_auth_client_secret = self.kc.get_client_secret_by_id(keycloak_client["id"], realm=realm)
            keycloak_auth_client_secret_value = keycloak_auth_client_secret['value'] if keycloak_auth_client_secret is not None and 'value' in keycloak_auth_client_secret else None
            return keycloak_auth_client_secret_value
        return None
    
    def __authenticate_by_service_account(self,
                                          client_id:str=None,
                                          client_realm:str=None) -> dict:
        headers = {}
        client = client_id if client_id is not None else self.keycloak_auth_client_id
        realm = client_realm if client_realm is not None else self.keycloak_auth_realm

        if self.keycloak_enabled:
            if (self.keycloak_auth_client_secret is None or len(self.keycloak_auth_client_secret) == 0) and (self.kc is not None or self.init_keycloak_api() is not None):
                self.keycloak_auth_client_secret = self.get_client_secret(client_id=client, realm=realm)
            
            headers = get_service_account_token(
                base_url=self.keycloak_url,
                auth_realm=self.keycloak_auth_realm,
                client_id=client,
                client_secret=self.keycloak_auth_client_secret,
                validate_certs=self.validate_certs) if self.keycloak_auth_client_secret is not None else {}
        self.headers = headers
        return headers

    def __authenticate_by_username_password(self,
                                            username:str=None,
                                            password:str=None,
                                            client_id:str=None) -> dict:
        headers = {}
        if self.keycloak_enabled:
            if client_id is None:
                client_id = self.keycloak_auth_client_id
            if (self.keycloak_auth_client_secret is None or len(self.keycloak_auth_client_secret) == 0) and (self.kc is not None or self.init_keycloak_api() is not None):
                self.keycloak_auth_client_secret = self.get_client_secret(client_id=self.client_id, realm=self.keycloak_auth_realm)
            if username is None:
                username = self.keycloak_auth_user
            if password is None:
                password = self.keycloak_auth_password
            headers = get_token(
                base_url=self.keycloak_url,
                validate_certs=self.validate_certs,
                auth_realm=self.keycloak_auth_realm,
                client_id=client_id,
                auth_username=username,
                auth_password=password, 
                client_secret=self.keycloak_auth_client_secret) if self.keycloak_auth_client_secret is not None else {}
        self.headers = headers
        return headers

    def __str_to_bool(self, value: str) -> bool:
        if value.upper() == "TRUE":
            value = "True"
        elif value.upper() == "FALSE":
            value = "False"
        bool_value = False
        try:
            bool_value = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return False
        return bool(bool_value)
    
    def __get_test_access_token(self,
                                client_id:str,
                                client_roles,
                                realm_roles:list,
                                given_name:str,
                                family_name:str,
                                preferred_username:str) -> str:
        if len(client_roles) == 0:
            client_roles = [
                "fa-saisie",
                "fa-utilisateur",
                "superuser"]
        if len(realm_roles) == 0:
            realm_roles = [
                "offline_access",
                "default-roles-msss",
                "uma_authorization"]
        if given_name is None:
            given_name = "Super"
        if family_name is None:
            family_name = "Permissions"
        if preferred_username is None:
            preferred_username = self.keycloak_auth_user
        ressource_access = {}
        if type(client_roles) is list:
            ressource_access[self.keycloak_auth_client_id] = {
                "roles": client_roles
            }
        elif type(client_roles) is dict:
            ressource_access = client_roles

        if client_id is None:
            client_id = self.keycloak_auth_client_id
        decoded_access_token = {
            "exp": round(time.time()) + 300,
            "iat": round(time.time()),
            "auth_time": round(time.time()),
            "jti": str(uuid.uuid1()),
            "iss": "{}/realms/{}".format(self.keycloak_url, self.keycloak_auth_realm),
            "aud": client_id,
            "sub": str(uuid.uuid1()),
            "typ": "ID",
            "azp": client_id,
            "nonce": str(uuid.uuid1()),
            "session_state": str(uuid.uuid1()),
            "acr": "0",
            "email_verified": False,
            "groups": [
                "create-realm",
                "offline_access",
                "admin",
                "uma_authorization",
                "cluster-admin"
            ],
            "preferred_username": preferred_username,
            "allowed-origins": [
                "*"
            ],
            "realm_access": {
                "roles": realm_roles
            },
            "resource_access": ressource_access,
            "scope": "openid profile email",
            "sid": str(uuid.uuid1()),
            "name": "{given_name} {family_name}".format(given_name=given_name, family_name=family_name),
            "given_name": given_name,
            "family_name": family_name,
            "email": "nobody@inspq.qc.ca"
        }
        access_token = jwt.encode(decoded_access_token, self.JWT_SECRET, algorithm=self.JWT_ALGO, headers={
                                    'kid': 'NWBeViRdZb3-n0pBGu5YMJnaV1UMRMLjcvMOPJA2Gko', 'alg': self.JWT_ALGO, 'typ': 'jwt'})
        str_access_token = access_token.decode() if isinstance(access_token, (bytes,bytearray)) else access_token
        headers = {
            "Authorization": "bearer " + str_access_token
        }
        return headers


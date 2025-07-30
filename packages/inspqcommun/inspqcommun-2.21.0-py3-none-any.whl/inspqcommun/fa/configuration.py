import os
import ast
from inspqcommun.identity.keycloak_tools import KeycloakEnvironment

DEFAULT_LOG_LEVEL: str = "INFO"
DEFAULT_FILES_PATH: str = None
DEFAULT_FA_BASE_URL: str = 'http://localhost:8089'
DEFAULT_FA_BASE_URI: str = '/fa-services'
DEFAULT_KEYCLOAK_URL: str = 'http://keycloak.url/auth'
DEFAULT_KEYCLOAK_AUTH_REALM: str = 'msss'
DEFAULT_KEYCLOAK_AUTH_USER: str = 'PERMISSIONS'
DEFAULT_KEYCLOAK_AUTH_PASSWORD: str = ''
DEFAULT_KEYCLOAK_AUTH_CLIENT_ID: str = "admin-cli"
DEFAULT_KEYCLOAK_ENABLED: str = "False"
DEFAULT_VALIDATE_CERTS: str = "true"
class Configuration:
    client_roles = ["fa-utilisateur", "fa-saisie","superuser"]
    username = None
    password = None
    def __init__(self, client_id:str=None, client_roles:list=None, username:str=None, password=None) -> None:
        if client_roles is not None and len(client_roles) > 0:
            self.client_roles = client_roles
        
        self.username = username
        self.password = password
        self.client_id = client_id

    def __str_to_bool(self, value: str) -> bool:
        bool_value = False
        try:
            bool_value = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return False
        return bool(bool_value)
    
    def get_log_level(self, default_value=DEFAULT_LOG_LEVEL) -> str:
        return os.environ.get("LOG_LEVEL", default_value)

    def get_files_path(self, default_value=DEFAULT_FILES_PATH) -> str:
        return os.environ.get("FILES_PATH", default_value)

    def get_fonctions_allegees_url(self, default_value=DEFAULT_FA_BASE_URL) -> str:
        return os.environ.get("FA_BASE_URL", default_value)

    def get_fonctions_allegees_uri(self, default_value=DEFAULT_FA_BASE_URI) -> str:
        return os.environ.get("FA_BASE_URI", default_value)
    
    def get_keycloak_base_url(self, default_value=DEFAULT_KEYCLOAK_URL) -> str:
        url = os.environ.get("KEYCLOAK_BASE_URL", default_value) 
        return url if url.endswith("/auth") else url + "/auth"
        
    def get_keycloak_auth_realm(self, default_value=DEFAULT_KEYCLOAK_AUTH_REALM) -> str:
        return os.environ.get("KEYCLOAK_AUTH_REALM", default_value)
    
    def get_keycloak_auth_user(self, default_value=DEFAULT_KEYCLOAK_AUTH_USER) -> str:
        if self.username is None:
            return os.environ.get("KEYCLOAK_AUTH_USER", default_value)
        return self.username

    def get_keycloak_auth_password(self, default_value=DEFAULT_KEYCLOAK_AUTH_PASSWORD) -> str:
        return os.environ.get("KEYCLOAK_AUTH_PASSWORD", default_value)

    def get_keycloak_auth_client_id(self, default_value=DEFAULT_KEYCLOAK_AUTH_CLIENT_ID) -> str:
        return os.environ.get("KEYCLOAK_AUTH_CLIENT_ID", default_value)

    def get_keycloak_enabled(self, default_value=DEFAULT_KEYCLOAK_ENABLED) -> bool:
        return self.__str_to_bool(os.environ.get("KEYCLOAK_ENABLED", default_value))

    def get_validate_certs(self, default_value=DEFAULT_VALIDATE_CERTS) -> bool:
        return self.__str_to_bool(os.environ.get("VALIDATE_CERTS", default_value))
    
    def get_authorization_header(self) -> str:
        kcenv = KeycloakEnvironment(
            defaultAuthRealm=self.get_keycloak_auth_realm(),
            defaultAuthUser=self.get_keycloak_auth_user(),
            defaultAuthPassword=self.get_keycloak_auth_password(),
            defaultBaseKeycloakUrl=self.get_keycloak_base_url(),
            defaultKeycloakEnabled=self.get_keycloak_enabled(),
            defaultAuthClientId=self.get_keycloak_auth_client_id(),
            defaultValidateCert=self.get_validate_certs())
        headers = kcenv.authenticate(client_id=self.client_id,
                                     client_roles=self.client_roles,
                                     username=self.username,
                                     password=self.password)
        return headers.get('Authorization')
    

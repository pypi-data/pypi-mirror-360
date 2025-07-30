""" Http clients to get tokens from 4P authserver using OIDC protocol """
__author__ = "4th Platform team"
__license__ = "see LICENSE file"

import logging
import random
from collections import namedtuple
from datetime import datetime, timedelta
from os import getenv
from pathlib import Path

import requests
import ujson as json
from clients.cache import lru_cache
from clients.exceptions import (AuthserverError, ConfigurationError,
                                InvalidSignature)
from jose import JWSError, jws, jwt
from jose.backends import ECKey, RSAKey
from jose.constants import ALGORITHMS
from requests.auth import HTTPBasicAuth

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
AuthserverConfig = namedtuple(
    "AuthserverConfig",
    [
        "issuer",
        "token_endpoint",
        "authorization_endpoint",
        "jwks",
        "introspection_endpoint",
        "introspection_auth",
    ],
)
ASSERTION_EXP_GAP = timedelta(minutes=60)
DEFAULT_REQUEST_TIMEOUT = (
    15  # timeout in seconds to wait for a response from authserver
)
TTL_CACHE = 15 * 60
NTTL_CACHE = 20 * 60
SIZE_CACHE = 10


@lru_cache(max_size=SIZE_CACHE, ttl=TTL_CACHE, nttl=NTTL_CACHE)
def get_authserver_config(authserver_endpoint, verify_certs=True):
    """
    It returns the configuration needed in our client of the authserver 4P:
        token endpoint and public keys in jwk format
    :param verify_certs:
    :param authserver_endpoint:
    :return: namedtupl
    """
    if authserver_endpoint.endswith("/"):
        authserver_endpoint = authserver_endpoint[:-1]

    well_known_uri = authserver_endpoint + "/.well-known/openid-configuration"
    try:
        response = requests.get(
            well_known_uri, verify=verify_certs, timeout=DEFAULT_REQUEST_TIMEOUT)
        config = response.json()
        token_endpoint = config["token_endpoint"]
        authorization_endpoint = config["authorization_endpoint"]
        issuer = config["issuer"]
        jwks_uri = config["jwks_uri"]
        introspection_endpoint = config["introspection_endpoint"]
        introspection_auth = config["introspection_endpoint_auth_methods_supported"]
        response = requests.get(
            jwks_uri, verify=verify_certs, timeout=DEFAULT_REQUEST_TIMEOUT)
        jwks = response.json()
        return AuthserverConfig(
            issuer=issuer,
            token_endpoint=token_endpoint,
            authorization_endpoint=authorization_endpoint,
            jwks=jwks,
            introspection_endpoint=introspection_endpoint,
            introspection_auth=introspection_auth,
        )
    except Exception as error:
        msg = f"Error getting authserver configuration: {str(error)}"
        logger.error(msg)
        raise AuthserverError(msg) from error


def guess_key(key_path, encoding='utf-8'):
    """
    Guess the key format of the key in path given and return the  key
    :param key_path:
    :return:
    """

    # Try RSA keys (most common with hassh SHA256 -> RS256 alg)
    try:
        key_content = Path(key_path).read_text(encoding=encoding)
        key = RSAKey(key_content, ALGORITHMS.RS256)
        if key.is_public():
            logger.debug("RSA public key %s ignored", key_path)
            return None
        key.to_dict()
        return key
    # pylint:disable=broad-exception-caught
    except Exception as error:
        logger.debug("RSA key %s invalid: %s", key_path, str(error))

    # Try EC keys (most common with hassh SHA256 -> ES256 alg)
    try:
        key_content = Path(key_path).read_text(encoding=encoding)
        key = ECKey(key_content, ALGORITHMS.ES256)
        if key.is_public():
            logger.debug("EC public key %s ignored", key_path)
            return None
        key.to_dict()
        return key
    # pylint:disable=broad-exception-caught
    except Exception as error:
        logger.debug("EC key %s invalid: %s", key_path, str(error))

    return None


def load_jwk_set(path,):
    """
    It builds  JWKS set, (private and public) with the private keys found
    that will be used for signing assertions in jwt-bearer and expose the set in public format
    :param path: path to all private keys files
    :return: a tuple with private and public keys in dict format following JWK format
    """
    keys_private = []
    keys_public = []
    if path:
        for filename in Path(path).iterdir():
            key = guess_key(filename)
            if not key:
                logger.warning("The key %s is not supported", filename)
            else:
                keys_private.append(key.to_dict())
                keys_public.append(key.public_key().to_dict())

    return {"keys": keys_private}, {"keys": keys_public}


def ensure_string(in_bytes):
    """
    Ensures that the input, is converted to a UTF-8 encoded string.

    Parameters:
    - in_bytes (bytes): The input bytes that need to be converted to a string.

    Returns:
    str: The UTF-8 encoded string representation of the input bytes.
    """
    try:
        return in_bytes.decode("UTF-8")

    # pylint:disable=broad-exception-caught
    except Exception:
        return in_bytes


def is_truthy(var):
    """ Checks if a variable represents a truthy value. """
    return var not in ("False", "false", False)


def verify_signature(id_token, jwks):
    """
    Verifies the signature of an ID token using the provided JSON Web Key Set (JWKS).

    Parameters:
    - id_token (str): ID token to verify.
    - jwks (dict): JSON Web Key Set.

    Returns:
    - dict: Payload of the verified ID token.

    Raises:
    - InvalidSignature: If the signature verification fails.
    - AuthserverError: If the ID token is not a valid JWT.
    """
    try:
        # pylint:disable=c-extension-no-member
        header = jws.get_unverified_header(id_token)
        payload = jws.verify(id_token, jwks, header["alg"])
        return json.loads(payload)
    except JWSError as error:
        raise InvalidSignature(
            f"Error verifying signature of id_token: {str(error)}") from error
    except ValueError as error:
        raise AuthserverError("The id_token is not a valid JWT") from error

# pylint:disable=too-many-arguments


def build_jwt_payload(
    sub,
    scopes,
    purposes,
    issuer,
    audience,
    key,
    authorization_id=None,
    identifier=None,
    acr=None,
    authentication_context=None,
):
    """
    Builds a JWT payload for user authentication.

    Parameters:
    - sub (str): Subject identifier.
    - scopes (list): List of requested scopes.
    - purposes (list): List of requested purposes.
    - issuer (str): Issuer of the token.
    - audience (str): Audience of the token.
    - key (dict): Key for encoding the token.
    - authorization_id (str, optional): Authorization identifier.
    - identifier (str, optional): Identifier.
    - acr (str, optional): Authentication context reference.
    - authentication_context (str, optional): Authentication context.

    Returns:
    - str: JWT assertion.
    """
    now = datetime.utcnow()  # jose library converts to epoch time
    payload = {
        "sub": sub,
        "active": True,
        "scope": " ".join(scopes),
        "purpose": " ".join(purposes),
        "exp": now + ASSERTION_EXP_GAP,
        "iat": now,
        "iss": issuer,
        "aud": audience,
    }
    if authorization_id:
        payload["authorization_id"] = authorization_id

    if identifier:
        payload["identifier"] = identifier

    if acr:
        payload["acr"] = acr
    if authentication_context:
        payload["authentication_context"] = authentication_context

    assertion = jwt.encode(payload, key, algorithm=key["alg"])
    return assertion


def build_jwk_set(public_keys, dump_json=True):
    """
    Builds a JSON Web Key Set (JWKS) from a list of public keys.

    Parameters:
    - public_keys (list): List of public keys.
    - dump_json (bool, optional): Whether to dump the JWKS to JSON. Defaults to True.

    Returns:
    - str or dict: JSON Web Key Set.
    """
    public_key_jwk_serialized = map(
        lambda key: {k: ensure_string(v) for k, v in key.items()}, public_keys
    )
    jwk_set = {"keys": list(public_key_jwk_serialized)}
    # pylint:disable=c-extension-no-member
    return json.dumps(jwk_set) if dump_json else jwk_set


class OpenIDClient:
    """ OpenID Client for handling authentication and token requests. """
   # pylint:disable=too-many-arguments,too-many-instance-attributes

    def __init__(
        self,
        authserver_endpoint=None,
        client_id=None,
        client_secret=None,
        issuer=None,
        private_certs_path=None,
    ):
        """
        Initializes an OpenIDClient instance.

        Parameters:
        - authserver_endpoint (str, optional): Authserver endpoint.
        - client_id (str, optional): Client ID.
        - client_secret (str, optional): Client secret.
        - issuer (str, optional): Issuer of the tokens.
        - private_certs_path (str, optional): Path to private certificates.
        """
        self.verify_certs = is_truthy(getenv("BAIKAL_VERIFY_CERTS"))
        if not self.verify_certs:
            # pylint:disable=import-outside-toplevel
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self._authserver_endpoint = (
            getenv("BAIKAL_AUTHSERVER_ENDPOINT") or authserver_endpoint
        )
        self._client_id = getenv("BAIKAL_CLIENT_ID") or client_id
        self._client_secret = getenv("BAIKAL_CLIENT_SECRET") or client_secret
        self._sanity_check()

        self._authserver_auth = HTTPBasicAuth(
            self._client_id, self._client_secret)
        self.issuer = getenv("BAIKAL_ISSUER") or issuer
        self.private_keys, self.public_keys = load_jwk_set(
            getenv("BAIKAL_PRIVATE_CERTS_PATH") or private_certs_path,
            # getenv("BAIKAL_CLIENT_KEYS") or client_keys,
        )

    def _sanity_check(self):
        """ Performs a sanity check to ensure required configuration values are set. """
        if not self._authserver_endpoint:
            raise ConfigurationError("authserver endpoint not configured")

        if not self._client_id:
            raise ConfigurationError("client_id not configured")

        if not self._client_secret:
            raise ConfigurationError("client_secret not configured")

    @property
    def authserver_config(self):
        """It returns the configuration needed in our client of the authserver 4P:
        token endpoint and public keys in jwk format"""

        return get_authserver_config(
            self._authserver_endpoint, verify_certs=self.verify_certs
        )

    def get_random_key(self):
        """It returns a random key"""
        return random.choice(self.private_keys["keys"])

   # pylint:disable=too-many-arguments
    def grant_user(
        self,
        sub,
        scopes,
        purposes,
        authorization_id=None,
        identifier=None,
        # pylint:disable=dangerous-default-value
        headers={},
        timeout=15,
        full_authserver_response=False,
    ):
        """
        Grants user access by exchanging a JWT assertion for an access token.

        Parameters:
        - sub (str): Subject identifier.
        - scopes (list): List of requested scopes.
        - purposes (list): List of requested purposes.
        - authorization_id (str, optional): Authorization identifier.
        - identifier (str, optional): Identifier.
        - acr (str, optional): Authentication context reference.
        - authentication_context (str, optional): Authentication context.
        - headers (dict, optional): Additional HTTP headers.
        - timeout (int, optional): Request timeout.
        - full_authserver_response (bool, optional): Return the full Authserver response.

        Returns:
        - dict: Authserver response.

        Raises:
        - ConfigurationError: If issuer or private keys are not configured.
        - AuthserverError: If an error occurs during the request.
        """
        if not self.issuer:
            raise ConfigurationError(
                "Issuer should be defined to generate tokens with jwt-bearer"
            )
        if not self.private_keys["keys"]:
            raise ConfigurationError(
                "No private keys found for generating assertion")

        assertion = build_jwt_payload(
            sub,
            scopes,
            purposes,
            self.issuer,
            self.authserver_config.issuer,
            self.get_random_key(),
            authorization_id=authorization_id,
            identifier=identifier,
        )
        body = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }

        return self._call_token_endpoint(
            body, headers, timeout, full_authserver_response=full_authserver_response
        )

   # pylint:disable=too-many-arguments
    def grant_client(
        self,
        scopes=None,
        purposes=None,
        # pylint:disable=dangerous-default-value
        headers={},
        timeout=DEFAULT_REQUEST_TIMEOUT,
        full_authserver_response=False,
    ):
        """
        Grants client access using client credentials.

        Parameters:
        - scopes (list, optional): List of requested scopes.
        - purposes (list, optional): List of requested purposes.
        - headers (dict, optional): Additional HTTP headers.
        - timeout (int, optional): Request timeout.
        - full_authserver_response (bool, optional): Return the full Authserver response.

        Returns:
        - dict: Authserver response.

        Raises:
        - AuthserverError: If an error occurs during the request.
        """
        body = {"grant_type": "client_credentials"}
        if scopes:
            body["scope"] = " ".join(scopes)
        if purposes:
            body["purpose"] = " ".join(purposes)
        return self._call_token_endpoint(
            body, headers, timeout, full_authserver_response=full_authserver_response
        )

    def authorize(
        self, scopes=None, purposes=None, redirect_uri=None, **extra_params
    ):
        """
        Generates an authorization URL for user consent.

        Parameters:
        - scopes (list, optional): List of requested scopes.
        - purposes (list, optional): List of requested purposes.
        - redirect_uri (str): Redirect URI for authorization response.
        - **extra_params: Additional parameters to include in the authorization URL.

        Returns:
        - str: Authorization URL.

        Raises:
        - AuthserverError: If redirect_uri is not provided.
        """
        authorization_url = f"""{
                self.authserver_config.authorization_endpoint
                }?response_type=code&client_id={
                self._client_id
                }"""

        if scopes:
            authorization_url = f"{authorization_url}&scope={' '.join(scopes)}"
        if purposes:
            authorization_url = f"{authorization_url}&purpose={' '.join(purposes)}"
        if not redirect_uri:
            raise AuthserverError("redirect_uri field is mandatory")
        authorization_url = f"{authorization_url}&redirect_uri={redirect_uri}"
        extra_params_builder = [
            f"{key}={value}" for key, value in extra_params.items()]
        if extra_params_builder:
            authorization_url = f"{authorization_url}&{'&'.join(extra_params_builder)}"
        return authorization_url

   # pylint:disable=too-many-arguments
    def grant_code(
        self,
        code=None,
        redirect_uri=None,
        # pylint:disable=dangerous-default-value
        headers={},
        timeout=DEFAULT_REQUEST_TIMEOUT,
        full_authserver_response=False,
    ):
        """
        Grants access using an authorization code.

        Parameters:
        - code (str): Authorization code.
        - redirect_uri (str): Redirect URI used in the authorization request.
        - headers (dict, optional): Additional HTTP headers.
        - timeout (int, optional): Request timeout.
        - full_authserver_response (bool, optional): Return the full Authserver response.

        Returns:
        - dict: Authserver response.

        Raises:
        - AuthserverError: If code or redirect_uri is not provided.
        """
        if not code:
            raise AuthserverError("code field is mandatory")
        if not redirect_uri:
            raise AuthserverError("redirect_uri field is mandatory")
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        return self._call_token_endpoint(
            body, headers, timeout, full_authserver_response=full_authserver_response
        )

    def introspect(self, access_token, timeout=DEFAULT_REQUEST_TIMEOUT):
        """
        Introspects an access token to validate its status.

        Parameters:
        - access_token (str): Access token to introspect.
        - timeout (int, optional): Request timeout.

        Returns:
        - dict: Token introspection response.

        Raises:
        - AuthserverError: If an error occurs during the introspection.
        """
        response = requests.post(
            self.authserver_config.introspection_endpoint,
            {"token": access_token},
            auth=self._authserver_auth,
            verify=self.verify_certs,
            timeout=timeout,
        )
        # pylint:disable=no-member
        if response.status_code != requests.codes.ok:
            raise AuthserverError(
                f"Error from introspection endpoint: {str(self._parse_error(response))}"
            )
        return response.json()

    @staticmethod
    def _parse_error(response):
        """ Parse response error """
        try:
            error = response.json()
            return str(error)
        except ValueError:
            return (
                f"Unexpected response from authserver: status_code "
                f"{str(response.status_code)}; resp: {str(response.text)}"
            )

    def _call_token_endpoint(
        self, body, headers, timeout, full_authserver_response=False
    ):
        """POST call to token endpoint"""
        response = requests.post(
            self.authserver_config.token_endpoint,
            body,
            auth=self._authserver_auth,
            verify=self.verify_certs,
            headers=headers,
            timeout=timeout,
        )
        # pylint:disable=no-member
        if response.status_code == requests.codes.unauthorized:
            raise AuthserverError(
                "The credentials client_id/client_secret are invalid."
            )
        # pylint:disable=no-member
        if response.status_code != requests.codes.ok:
            raise AuthserverError(
                "Error from token endpoint of Authserver: " +
                self._parse_error(response)
            )

        body = response.json()
        return body if full_authserver_response else body["access_token"]

    def _verify_signature(self, id_token):
        """
        The `verify_signature` method asynchronously verifies the signature of the provided
        ID token using the authentication server's configuration.
        Args:
            id_token (str): The ID token to be verified.
        Returns:
            bool: A boolean indicating whether the signature is verified."""
        return verify_signature(id_token, self.authserver_config.jwks)

    def get_jwk_set(self, dump_json=True):
        """
        The `get_jwk_set` method retrieves the JSON Web Key (JWK) set, which contains the
        public keys used for signature verification.
        Args:
            dump_json (bool, optional): A boolean indicating whether to dump the JWK
            set in JSON format. Defaults to True.
        Returns:
            dict or str: The JWK set in the specified format.
        """
        return build_jwk_set(self.public_keys["keys"], dump_json=dump_json)

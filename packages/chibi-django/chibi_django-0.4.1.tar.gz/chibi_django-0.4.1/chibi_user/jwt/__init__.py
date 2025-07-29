import json
import uuid
import warnings
from calendar import timegm
from datetime import datetime

import jwt
from chibi_auth0 import Chibi_auth0
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.settings import api_settings


def get_username_field():
    try:
        username_field = get_user_model().USERNAME_FIELD
    except Exception:
        username_field = 'username'

    return username_field


def get_username(user):
    try:
        username = user.get_username()
    except AttributeError:
        username = user.username

    return username


def get_secret_key( setting, payload=None ):
    """
    For enhanced security you may want to use a secret key based on user.

    This way you have an option to logout only this user if:
        - token is compromised
        - password is changed
        - etc.
    """
    if setting.JWT_GET_USER_SECRET_KEY:
        User = get_user_model()  # noqa: N806
        user = User.objects.get( pk=payload.get( 'user_id' ))
        key = str( setting.JWT_GET_USER_SECRET_KEY( user ))
        return key
    return setting.JWT_SECRET_KEY


def payload_handler( user ):
    username_field = get_username_field()
    username = get_username( user )

    warnings.warn(
        'The following fields will be removed in the future: '
        '`email` and `user_id`. ',
        DeprecationWarning
    )

    payload = {
        'user_id': user.pk,
        'username': username,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }
    if hasattr( user, 'email' ):
        payload['email'] = user.email
    if isinstance( user.pk, uuid.UUID ):
        payload['user_id'] = str( user.pk )

    payload[username_field] = username

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload


def get_user_id_from_payload_handler( payload ):
    """
    Override this function if user_id is formatted differently in payload
    """
    warnings.warn(
        'The following will be removed in the future. '
        'Use `JWT_PAYLOAD_GET_USERNAME_HANDLER` instead.',
        DeprecationWarning
    )

    return payload.get( 'user_id' )


def get_username_from_payload_handler( payload ):
    """
    Override this function if username is formatted differently in payload
    """
    return payload.get( 'username' )


def encode_handler( payload, setting ):
    key = setting.JWT_PRIVATE_KEY or get_secret_key( setting, payload )
    return jwt.encode(
        payload, key, setting.JWT_ALGORITHM ).decode( 'utf-8' )


def decode_handler( token, setting ):
    options = {
        'verify_exp': setting.JWT_VERIFY_EXPIRATION,
    }
    # get user from token, BEFORE verification, to get user secret key
    unverified_payload = jwt.decode( token, None, False )
    secret_key = get_secret_key( setting, unverified_payload )

    return jwt.decode(
        token,
        setting.JWT_PUBLIC_KEY or secret_key,
        setting.JWT_VERIFY,
        options=options,
        leeway=setting.JWT_LEEWAY,
        audience=setting.JWT_AUDIENCE,
        issuer=setting.JWT_ISSUER,
        algorithms=[setting.JWT_ALGORITHM]
    )


def response_payload_handler( token, user=None, request=None ):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.

    Example:

    def response_payload_handler( token, user=None, request=None ):
        return {
            'token': token,
            'user': UserSerializer( user, context={'request': request}).data
        }

    """
    return {
        'token': token
    }


def jwt_get_username_from_payload_handler( payload ):
    username = payload.get( 'sub' )
    authenticate( remote_user=username )
    return username


def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    auth0 = Chibi_auth0(
        domain=settings.JWT_AUTH.JWT_CLIENT_DOMAIN,
        client_id=settings.JWT_AUTH.JWT_CLIENT_ID,
        client_secret=settings.JWT_AUTH.JWT_CLIENT_SECRET,
        audience=settings.JWT_AUTH.JWT_AUDIENCE,
    )
    jwks = auth0.well_know
    public_key = None
    for jwk in jwks[ 'keys' ]:
        if jwk[ 'kid' ] == header[ 'kid' ]:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(
                json.dumps( jwk ) )

    if public_key is None:
        raise Exception( 'Public key not found.' )

    return jwt.decode(
        token, public_key,
        audience=settings.JWT_AUTH.JWT_AUDIENCE,
        issuer=settings.JWT_AUTH.JWT_ISSUER,
        algorithms=[ 'RS256' ] )

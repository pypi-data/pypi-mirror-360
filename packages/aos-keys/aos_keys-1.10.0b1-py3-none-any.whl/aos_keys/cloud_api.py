#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
"""aos-keys cloud API implementations."""
from urllib.parse import urljoin

from aos_keys.common import AosKeysError, ca_certificate
from aos_keys.crypto_container import AosCryptoContainer
from aos_keys.key_manager import extract_cloud_domain_from_cert
from requests import post
from requests.exceptions import SSLError

_ME_CERT_ENDPOINT = '/api/v11/users/me/'
_UPLOAD_USER_CERTIFICATE = '/api/v11/user-certificates/'
_POST_TIMEOUT = 30


INVALID_TOKEN_ERROR = AosKeysError(
    'FORBIDDEN status was received from the AosEdge Cloud!',
    help_text='Access token is wrong or already used',
)


def get_user_info_by_cert(pkcs12_path: str):
    """Get user info from the Cloud by user certificate.

    Args:
        pkcs12_path: Full path to user certificate in pkcs12 format.

    Returns:
        Json response from cloud
    """
    domain = extract_cloud_domain_from_cert(pkcs12_path)
    with ca_certificate() as server_certificate_path:
        with AosCryptoContainer(pkcs12_path).create_requests_session() as session:
            response = session.get(
                urljoin(f'https://{domain}:10000', _ME_CERT_ENDPOINT),
                verify=server_certificate_path,
            )
            response.raise_for_status()
            return response.json()


def receive_certificate_by_token(domain: str, token: str, csr: str) -> str:
    """Get user info from the Cloud by user certificate.

    Args:
        domain: Domain to request client certificate.
        token: Authentication  one-time user token.
        csr: User CSR in PEM format.

    Raises:
        INVALID_TOKEN_ERROR: FORBIDDEN status was received from the AosEdge Cloud!

    Returns:
        The user certificate issued by the AosEdge Cloud
    """
    try:
        with ca_certificate() as server_certificate_path:
            upload_response = post(
                urljoin(f'https://{domain}:10000', _UPLOAD_USER_CERTIFICATE),
                json={'csr': csr},
                headers={
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Referer': f'https://{domain}',
                    'Authorization': f'Token {token}',
                },
                verify=server_certificate_path,
                timeout=_POST_TIMEOUT,
            )
            if upload_response.status_code == 403:  # noqa: WPS432
                raise INVALID_TOKEN_ERROR
            upload_response.raise_for_status()

    except SSLError as exc:
        # Try using system root certificate storage as the trusted sources instead of the AosEdge root certificate
        upload_response = post(
            urljoin(f'https://{domain}:10000', _UPLOAD_USER_CERTIFICATE),
            json={'csr': csr},
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Referer': f'https://{domain}',
                'Authorization': f'Token {token}',
            },
            timeout=_POST_TIMEOUT,
        )
        if upload_response.status_code == 403:  # noqa: WPS432
            raise INVALID_TOKEN_ERROR from exc
        upload_response.raise_for_status()

    return upload_response.json()['certificate']

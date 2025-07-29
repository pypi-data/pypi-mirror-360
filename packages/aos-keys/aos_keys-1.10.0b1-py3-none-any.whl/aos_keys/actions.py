#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
"""aos-keys actions."""

import platform
from pathlib import Path

from aos_keys.certificate_manager import (
    install_root_certificate_linux,
    install_root_certificate_macos,
    install_root_certificate_windows,
    install_user_certificate_linux,
    install_user_certificate_macos,
    install_user_certificate_windows,
)
from aos_keys.cloud_api import get_user_info_by_cert, receive_certificate_by_token
from aos_keys.common import (
    DEFAULT_ADMIN_FILE_NAME,
    DEFAULT_FLEET_FILE_NAME,
    DEFAULT_OEM_FILE_NAME,
    DEFAULT_SP_FILE_NAME,
    AosKeysError,
    UserType,
    print_message,
    print_success,
)
from aos_keys.key_manager import (
    generate_pair,
    pem_to_pkcs12_bytes,
    pkcs12_to_pem_bytes,
    print_cert_info,
)
from requests import HTTPError, exceptions
from rich.table import Table


def install_user_certificate(path_to_certificate):
    """Install user certificate into browsers.

    Args:
        path_to_certificate: Path to user certificate to install.

    Raises:
        AosKeysError: If something fails.
    """
    if not Path(path_to_certificate).exists():
        raise AosKeysError(f'File {path_to_certificate} not found!')

    if platform.system() == 'Windows':
        install_user_certificate_windows(path_to_certificate)
    elif platform.system() == 'Linux':
        install_user_certificate_linux(path_to_certificate)
    elif platform.system() == 'Darwin':
        install_user_certificate_macos(path_to_certificate)
    else:
        raise AosKeysError('Unsupported platform')


def install_root_ca():
    """Install Cloud root certificate system-wide.

    Raises:
        AosKeysError: If something fails.
    """
    if platform.system() == 'Windows':
        install_root_certificate_windows()
    elif platform.system() == 'Linux':
        install_root_certificate_linux()
    elif platform.system() == 'Darwin':
        install_root_certificate_macos()
    else:
        raise AosKeysError('Unsupported platform')


def new_token_user(
    domain: str,
    output_directory: str,
    auth_token: str,
    user_type: UserType,
    create_ec_key: bool,
    skip_install_into_browsers: bool,
):
    """Create a new user key/certificate and register it on the cloud.

    Args:
        domain: Domain where to register user.
        output_directory: Directory to save user key/certificate.
        auth_token: Authenticity token for cloud.
        user_type: Type of user (SP or OEM).
        create_ec_key: Generate RSA or EC key.
        skip_install_into_browsers: flag to skip installing into browsers certificate and key.

    Raises:
        AosKeysError: If user hasn't the access to the cloud or his role is not OEM.
    """
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    names = {
        UserType.SP.value: {
            'path': Path(output_directory) / DEFAULT_SP_FILE_NAME,
            'friendly_name': 'Aos SP client certificate',
        },
        UserType.OEM.value: {
            'path': Path(output_directory) / DEFAULT_OEM_FILE_NAME,
            'friendly_name': 'Aos OEM client certificate',
        },
        UserType.FLEET.value: {
            'path': Path(output_directory) / DEFAULT_FLEET_FILE_NAME,
            'friendly_name': 'Aos Fleet Owner client certificate',
        },
        UserType.ADMIN.value: {
            'path': Path(output_directory) / DEFAULT_ADMIN_FILE_NAME,
            'friendly_name': 'Aos ADMIN client certificate',
        },
    }
    config = names[user_type.value]

    if config['path'].exists():
        raise AosKeysError(f'File {config["path"]} exists. Cannot proceed!')

    private_key_bytes, csr = generate_pair(create_ec_key)
    user_certificate = receive_certificate_by_token(domain, token=auth_token, csr=csr.decode())
    pkcs12_bytes = pem_to_pkcs12_bytes(
        private_key_bytes,
        user_certificate.encode(encoding='UTF-8'),
        config['friendly_name'],
    )

    with open(config['path'], 'wb') as save_file:
        save_file.write(pkcs12_bytes)

    print_success(f'File {config["path"]} created')
    print_success('Done!')

    if not skip_install_into_browsers:
        install_user_certificate(config['path'])


def convert_pkcs12_file_to_pem(pkcs12_path: str, output_dir: str):
    """Convert pkcs12 file to pem key and certificate.

    Args:
        pkcs12_path: Full path to user certificate in pkcs12 format.
        output_dir: Directory to store pem files.

    Raises:
        AosKeysError: In case when can't create new files.

    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    cert_file_name = Path(output_dir) / 'user-certificate.pem'
    key_file_name = Path(output_dir) / 'user-key.pem'

    if not Path(pkcs12_path).exists():
        raise AosKeysError(f'File {pkcs12_path} not found. Cannot proceed!')

    for file_name in (cert_file_name, key_file_name):
        if file_name.exists():
            raise AosKeysError(f'Destination file {file_name} exists. Cannot proceed!')

    with open(pkcs12_path, 'rb') as pkcs12_file:
        key_bytes, cert_bytes = pkcs12_to_pem_bytes(pkcs12_file.read())

    with open(cert_file_name, 'wb') as cert:
        cert.write(cert_bytes)
        print_success(f'File created: {cert_file_name}!')

    with open(key_file_name, 'wb') as key:
        key.write(key_bytes)
        print_success(f'File created: {key_file_name}!')

    print_success('Done!')


def print_user_info(pkcs12_path: str):
    """Print info about user certificate and available permissions on the cloud.

    Args:
        pkcs12_path: Full path to user certificate in pkcs12 format.

    Raises:
        AosKeysError: If received error during communication with Cloud.
    """
    print_cert_info(pkcs12_path)
    try:
        user_info = get_user_info_by_cert(pkcs12_path)
    except HTTPError as net_err:
        raise AosKeysError('Error receiving user info') from net_err
    except exceptions.InvalidJSONError as json_err:
        error_msg = str(json_err)
        raise AosKeysError(f'Error parsing user info JSON response: "{error_msg}"') from json_err

    user_role = user_info.get('role', '')
    print_info = {
        'User name: ': user_info.get('username'),
        'email: ': user_info.get('email'),
        'role: ': user_role,
    }

    if user_role in {'oem', 'fleet owner'}:
        print_info['OEM Title:'] = user_info.get('oem').get('title')
        print_info['Fleets:'] = '\n'.join(fleet['title'] for fleet in user_info.get('fleets', []))
    elif user_role == 'service provider':
        print_info['SP Title:'] = user_info.get('service_provider').get('title')

    print_info['Permission groups: '] = '\n'.join(user_info.get('permission_groups', []))
    print_info['Standalone permissions: '] = '\n'.join(user_info.get('permissions', []))

    table = Table(padding=0, title='Cloud user info', show_header=False)
    table.add_column('', no_wrap=True, justify='left', style='')
    table.add_column('')
    for key, print_info_value in print_info.items():
        table.add_row(key, str(print_info_value))

    print_message(table)

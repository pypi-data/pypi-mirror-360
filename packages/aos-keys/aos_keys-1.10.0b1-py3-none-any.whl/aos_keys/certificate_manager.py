#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
"""Install root and client certificates on different OSes."""
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import List

from aos_keys.common import (
    AosKeysError,
    aos_root_ca_certificate1,
    aos_root_ca_certificate2,
    print_error,
    print_message,
    print_success,
)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import PrivateFormat, pkcs12

_KDF_ROUNDS = 50000

# MaxOS keychain path:
#    root: /System/Library/Keychains/SystemRootCertificates.keychain
#    system: /Library/Keychains/System.keychain
#    user: /UserHome/Library/Keychains/login.keychain-db


def _execute_command(command):
    try:
        completed_process = subprocess.run(command, capture_output=False, env=os.environ.copy(), check=False)
    except KeyboardInterrupt as exc:
        raise AosKeysError('Operation interrupted by user') from exc
    if completed_process.returncode == 0:
        return

    error = completed_process.stderr
    if not error and completed_process.stdout:
        error = completed_process.stdout
        if error:
            error = error.decode('utf8')
    print_error(completed_process.stderr)
    raise AosKeysError(f'Failed to install certificate:\n {error}')


def _check_linux_has_pk12util():
    """Check if libnss3-tools present on the Linux host.

    Raises:
        AosKeysError: If libnss3-tools is not installed.
    """
    if subprocess.run(['/usr/bin/dpkg', '-s', 'libnss3-tools'], capture_output=True, check=False).returncode == 0:
        return

    raise AosKeysError(
        'Failed to install certificate. "libnss3-tools" package is missing',
        'Install libnss3-tools with command: sudo apt install libnss3-tools',
    )


def _check_linux_has_ca_certificates():
    """Check if ca-certificates present on the Linux host.

    Raises:
        AosKeysError: If ca-certificates is not installed.
    """
    if subprocess.run(['/usr/bin/dpkg', '-s', 'ca-certificates'], capture_output=True, check=False).returncode == 0:
        return

    raise AosKeysError(
        'Failed to install certificate. "update-ca-certificates" package is missing',
        'Install update-ca-certificates with command: sudo apt install ca-certificates',
    )


def check_root_certificate_linux() -> bool:
    home_str = str(Path.home())
    nssdb_dir = f'{home_str}/.pki/nssdb'
    if not os.path.exists(nssdb_dir):
        return False
    command = ['certutil', '-d', nssdb_dir, '-L']
    completed_process = subprocess.run(command, capture_output=True, check=False)
    return completed_process.returncode == 0


def install_root_certificate_macos():
    """Install root certificate on current user's Trusted Root CA."""
    print_message('We are going to add two Aos Root certificate as trusted certificates.')
    print_message('The OS will ask your password TWICE to proceed with operation.')

    user_home_path = str(Path.home())

    for ca_cert_path in (aos_root_ca_certificate1(), aos_root_ca_certificate2()):
        command = [
            'security',
            'add-trusted-cert',
            '-r',
            'trustRoot',
            '-k',
            f'{user_home_path}/Library/Keychains/login.keychain-db',
            str(ca_cert_path),
        ]
        _execute_command(command)


def install_root_certificate_windows():
    """Install root certificate on current user's Trusted Root CA."""
    for ca_cert_path in (aos_root_ca_certificate1(), aos_root_ca_certificate2()):
        command = ['certutil', '-addstore', '-f', '-user', 'Root', ca_cert_path]
        _execute_command(command)


def install_root_certificate_linux():
    """Install root certificate on linux host.

    Raises:
        AosKeysError: Failed to create empty user's certificate DB.
    """
    _check_linux_has_ca_certificates()
    _check_linux_has_pk12util()

    firefox_profiles = find_firefox_profile_locations()

    # Create empty user's certificate DB if absent
    home_str = str(Path.home())
    nssdb_dir = f'{home_str}/.pki/nssdb'
    if not os.path.exists(nssdb_dir):
        os.makedirs(nssdb_dir, exist_ok=True)
        command = ['certutil', '-d', nssdb_dir, '-N', '--empty-password']
        completed_process = subprocess.run(command, capture_output=True, check=False)
        if completed_process.returncode > 0:
            raise AosKeysError("Failed to create empty user's certificate DB")
        print_success('Empty users certificate DB has been successfully created')

    os.makedirs(f'{home_str}/.aos/scripts', exist_ok=True)
    script_filename = f'{home_str}/.aos/scripts/install_aos_root_ca.sh'
    with open(script_filename, 'wt', encoding='utf-8') as file_handle:
        file_handle.write('mkdir -p /usr/local/share/ca-certificates\n')
        file_handle.write(f'cp {aos_root_ca_certificate1()} /usr/local/share/ca-certificates/AosRootCA.crt\n')
        file_handle.write(f'cp {aos_root_ca_certificate2()} /usr/local/share/ca-certificates/AosECRootCA.crt\n')
        file_handle.write('update-ca-certificates\n')
    command = ['chmod', '+x', script_filename]
    _execute_command(command)

    print_success('To install system root certificate execute next command:')
    print_message('sudo ~/.aos/scripts/install_aos_root_ca.sh\n')

    with tempfile.NamedTemporaryFile() as password_file:
        cert_info = (
            (aos_root_ca_certificate1(), 'Aos root certificate'),
            (aos_root_ca_certificate2(), 'Aos EC root certificate'),
        )
        for ca_cert_path, ca_alias in cert_info:
            # empty password file prevents asking password from stdin
            command = [
                'certutil',
                '-d',
                f'sql:{home_str}/.pki/nssdb',
                '-A',
                '-t',
                'C',
                '-n',
                ca_alias,
                '-i',
                ca_cert_path,
                '-f',
                password_file.name,
            ]
            _execute_command(command)

            for firefox_profile in firefox_profiles:
                command = [
                    'certutil',
                    '-d',
                    f'sql:{firefox_profile}',
                    '-A',
                    '-t',
                    'C',
                    '-n',
                    ca_alias,
                    '-i',
                    ca_cert_path,
                    '-f',
                    password_file.name,
                ]
                _execute_command(command)


def add_password_to_pkcs12(filename_in: str, filename_out: str, password: bytes, friendly_name: bytes or None):
    with open(filename_in, 'rb') as file_in_handle:
        pkcs12_bytes = file_in_handle.read()
    key_certificates = pkcs12.load_pkcs12(pkcs12_bytes, None)

    # This code should be used after PR release https://github.com/pyca/cryptography/pull/7560/
    encryption = (
        PrivateFormat.PKCS12.encryption_builder().
        kdf_rounds(_KDF_ROUNDS).
        key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC).
        hmac_hash(hashes.SHA1()).build(password)  # noqa: S303
    )

    protected_pkcs12_bytes = pkcs12.serialize_key_and_certificates(
        friendly_name,
        key_certificates.key,
        key_certificates.cert.certificate,
        [cert.certificate for cert in key_certificates.additional_certs],
        encryption,  # See comment above
    )
    with open(filename_out, 'wb') as file_out_handle:
        file_out_handle.write(protected_pkcs12_bytes)


def find_firefox_profile_locations() -> List[str]:  # pylint: disable=R0912
    home_dir = Path.home()

    result_locations = []

    # Based on http://kb.mozillazine.org/Profile_folder_-_Firefox

    if platform.system() == 'Linux':
        # Linux:
        #  ~/.mozilla/firefox/profile
        #  ~/snap/firefox/profile
        for root, _, files in os.walk(os.path.join(home_dir, '.mozilla', 'firefox')):
            if 'cert9.db' in files:
                result_locations.append(root)

        for browser in ('firefox', 'opera', 'chromium', 'chrome'):
            for root, _, files in os.walk(os.path.join(home_dir, 'snap', browser)):  # noqa: WPS440
                if 'cert9.db' in files:
                    result_locations.append(root)

    if platform.system() == 'Darwin':
        # macOS:
        #  ~/Library/Application Support/Firefox/Profiles/<profile folder>
        #  ~/Library/Mozilla/Firefox/Profiles/<profile folder>
        profile_app_path = os.path.join(home_dir, 'Library', 'Application Support', 'Firefox', 'Profiles')
        for root, _, files in os.walk(profile_app_path):  # noqa: WPS440
            if 'cert9.db' in files:
                result_locations.append(root)

        profile_lib_path = os.path.join(home_dir, 'Library', 'Mozilla', 'Firefox', 'Profiles')
        for root, _, files in os.walk(profile_lib_path):  # noqa: WPS440
            if 'cert9.db' in files:
                result_locations.append(root)

    if platform.system() == 'Windows':
        # Windows: %APPDATA%\Mozilla\Firefox\Profiles
        home_dir = os.environ.get('APPDATA', '')
        if home_dir:
            for root, _, files in os.walk(os.path.join(home_dir, 'Mozilla', 'Firefox', 'Profiles')):  # noqa: WPS440
                if 'cert9.db' in files:
                    result_locations.append(root)

    return result_locations


def install_user_certificate_windows(certificate_path: Path):
    """Install client certificate to the Windows Personal store.

    Args:
        certificate_path: path to certificate which will be installed.
    """
    print_message('We are going to import your private key and certificate to your personal store.')
    password_protected_filename = str(certificate_path) + '.pswd'
    add_password_to_pkcs12(str(certificate_path), password_protected_filename, b'1234', None)
    command = [
        'certutil',
        '-importpfx',
        '-f',
        '-user',
        '-p',
        '1234',
        password_protected_filename,
    ]
    try:  # noqa: WPS501
        _execute_command(command)
    finally:
        os.unlink(password_protected_filename)


def install_user_certificate_linux(certificate_path: Path):
    """Install client certificate to the Windows Personal store.

    Args:
        certificate_path: path to certificate which will be installed.

    Raises:
        AosKeysError: Failed to install User's certificate.
    """
    print_message('We are going to import your private key and certificate to browsers databases.')
    if not check_root_certificate_linux():
        raise AosKeysError('Failed to install certificate:\n Aos root certificate is not installed.')

    password_protected_filename = str(certificate_path) + '.pswd'
    add_password_to_pkcs12(str(certificate_path), password_protected_filename, b'1234', None)

    firefox_profiles = find_firefox_profile_locations()
    home_str = str(Path.home())
    all_profiles = [f'sql:{home_str}/.pki/nssdb']
    all_profiles.extend(firefox_profiles)

    with tempfile.NamedTemporaryFile() as password_file:
        password_file.write(b'1234')
        password_file.flush()

        try:  # noqa: WPS501
            for profile_item in all_profiles:
                command = [
                    'pk12util',
                    '-d',
                    profile_item,
                    '-i',
                    password_protected_filename,
                    '-w',
                    password_file.name,
                ]
                _execute_command(command)
        finally:
            os.unlink(password_protected_filename)


def install_user_certificate_macos(certificate_path: Path):
    """Install client certificate to the Windows Personal store.

    Args:
        certificate_path: path to certificate which will be installed.
    """
    print_message('We are going to import your private key and certificate to browsers databases.')
    password_protected_filename = str(certificate_path) + '.pswd'
    add_password_to_pkcs12(str(certificate_path), password_protected_filename, b'1234', None)

    command = [
        'security',
        'import',
        password_protected_filename,
        '-f',
        'pkcs12',
        '-P',
        '1234',
    ]
    try:  # noqa: WPS501
        _execute_command(command)
    finally:
        os.unlink(password_protected_filename)

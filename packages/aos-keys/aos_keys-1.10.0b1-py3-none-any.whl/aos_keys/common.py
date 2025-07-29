#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
"""Common defaults and settings."""

import sys
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Iterable

from rich.console import Console

if sys.version_info > (3, 9):
    from importlib import resources as pkg_resources  # noqa: WPS433, WPS440
else:
    import importlib_resources as pkg_resources  # noqa: WPS433, WPS440

DEFAULT_CREDENTIALS_PATH = Path.home() / '.aos' / 'security'
DEFAULT_CREDENTIALS_FOLDER = str(DEFAULT_CREDENTIALS_PATH)

DEFAULT_OEM_FILE_NAME = 'aos-user-oem.p12'
DEFAULT_FLEET_FILE_NAME = 'aos-user-fleet.p12'
DEFAULT_SP_FILE_NAME = 'aos-user-sp.p12'
DEFAULT_ADMIN_FILE_NAME = 'aos-user-admin.p12'

DEFAULT_OEM_PATH = str(DEFAULT_CREDENTIALS_PATH / DEFAULT_OEM_FILE_NAME)
DEFAULT_SP_PATH = str(DEFAULT_CREDENTIALS_PATH / DEFAULT_SP_FILE_NAME)

FILES_DIR = 'aos_keys'
ROOT_CA_CERT_FILENAME = 'files/1rootCA.crt'
ROOT_CA_CERT1_FILENAME = 'files/aos_root_ca_1.crt'
ROOT_CA_CERT2_FILENAME = 'files/aos_root_ca_2.crt'


console = Console()
error_console = Console(stderr=True, style='red')
ALLOW_PRINT = True


def print_success(message):
    if ALLOW_PRINT:
        str_message = str(message)
        print_message(f'[green]{str_message}')


def print_error(message):
    if ALLOW_PRINT:
        error_console.print(message)


def print_message(formatted_text, end='\n', ljust: int = 0):
    if ALLOW_PRINT:
        if ljust > 0:
            formatted_text = formatted_text.ljust(ljust)
        console.print(formatted_text, end=end)


@contextmanager
def ca_certificate():
    """
    Aos root certificate to verify server certificate.

    Yields:
        server_certificate_path: Path to certificate file.
    """
    server_certificate = pkg_resources.files(FILES_DIR) / ROOT_CA_CERT_FILENAME
    with pkg_resources.as_file(server_certificate) as server_certificate_path:
        yield server_certificate_path


def aos_root_ca_certificate1() -> str:
    """
    Aos root RSA certificate.

    Returns:
        str: Path to certificate file.
    """
    ca_cert = pkg_resources.files(FILES_DIR) / ROOT_CA_CERT1_FILENAME
    with pkg_resources.as_file(ca_cert) as ca_certificate_path:
        return str(ca_certificate_path)


def aos_root_ca_certificate2() -> str:
    """
    Aos root EC certificate.

    Returns:
        str: Path to certificate file.
    """
    ca_cert = pkg_resources.files(FILES_DIR) / ROOT_CA_CERT2_FILENAME
    with pkg_resources.as_file(ca_cert) as ca_certificate_path:
        return str(ca_certificate_path)


def _print_help_with_spaces(text):
    if ALLOW_PRINT:
        print_error(f'  {text}')


class AosKeysError(Exception):
    """Exception with help text with recommended user actions."""

    def __init__(self, message, help_text=None):
        """Exception with help text with recommended user actions.

        Args:
            message: Exception message.
            help_text: Help text to print after error.
        """
        super().__init__(message)
        self.help_text = help_text

    def print_message(self):
        """Print exception with help text if existed."""
        print_error(f'ERROR: {self}')

        if not self.help_text:
            return

        if isinstance(self.help_text, str) or not isinstance(self.help_text, Iterable):
            _print_help_with_spaces(self.help_text)
            return

        for row in self.help_text:
            _print_help_with_spaces(row)


class UserType(Enum):
    """Supported user types."""

    SP = 'sp'  # noqa: WPS115
    OEM = 'oem'  # noqa: WPS115
    FLEET = 'fleet'  # noqa: WPS115
    ADMIN = 'admin'  # noqa: WPS115

    @property
    def default_user_certificate_path(self) -> Path:
        """Absolute path to default certificate file.

        Returns:
            (Path): Path to certificate filename.
        """
        return DEFAULT_CREDENTIALS_PATH / self.default_file_name

    @property
    def default_file_name(self) -> str:
        """Return default certificate file name for selector user type.

        Returns:
            (str): Certificate filename.
        """
        if self.value == 'sp':
            return DEFAULT_SP_FILE_NAME

        if self.value == 'oem':
            return DEFAULT_OEM_FILE_NAME

        if self.value == 'fleet':
            return DEFAULT_FLEET_FILE_NAME

        if self.value == 'admin':
            return DEFAULT_ADMIN_FILE_NAME

        return ''

    @classmethod
    def from_input(cls, received_val: str):
        """Create user type from command input.

        Args:
            received_val (str): received parameter.

        Returns:
            (UserType): Instantiated UserType.

        Raises:
            AosKeysError: If received unknown parameter.
        """
        prepared = received_val.strip(' -').upper()
        try:
            return cls[prepared]
        except KeyError as exc:
            raise AosKeysError(f'Received unsupported user type: [bold]{prepared}[/bold]') from exc

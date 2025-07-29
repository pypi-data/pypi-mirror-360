#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
"""aos-keys certificates manager module."""
from aos_keys.common import AosKeysError, console
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_pem_private_key,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_pkcs12,
    serialize_key_and_certificates,
)
from cryptography.x509 import (
    CertificateSigningRequestBuilder,
    Name,
    load_pem_x509_certificate,
)
from cryptography.x509.oid import NameOID
from rich.table import Table

_CERTIFICATE_START = b'-----BEGIN CERTIFICATE-----'


def _print_cert_field(table, caption: str, certificate, oid):
    """
    Print certificate filed in console table.

    Args:
        table: Table object.
        caption (str): row caption.
        certificate: Certificate object.
        oid: Oid to print.
    """
    if certificate.subject.get_attributes_for_oid(oid):
        table.add_row(caption, certificate.subject.get_attributes_for_oid(oid)[0].value)


def _split_certificate_chain(pem_bytes: bytes):
    """
    Split certificate chain to user certificate and other certificates.

    Args:
        pem_bytes (bytes): certificate chain in PEM container.

    Returns:
        user certificate, other certificates chain: Tuple of user certificate and chain
    """
    pem_certs_split = pem_bytes.split(_CERTIFICATE_START)
    pem_certs_split = list(filter(None, pem_certs_split))
    user_certificate = load_pem_x509_certificate(_CERTIFICATE_START + pem_certs_split[0])
    other_certificates = []
    for single_pem_cert in pem_certs_split[1:]:
        cert = load_pem_x509_certificate((_CERTIFICATE_START + single_pem_cert))
        other_certificates.append(cert)

    return user_certificate, other_certificates


def generate_pair(use_elliptic_curves=True):
    """
    Generate private key and CSR.

    Args:
        use_elliptic_curves: use elliptic curves if true.

    Returns:
        (private_key, csr): private_key and csr bytes
    """
    if use_elliptic_curves:
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    else:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)  # noqa: WPS432

    private_key_pem_bytes = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    empty_subject_name = Name([])
    csr = CertificateSigningRequestBuilder().subject_name(empty_subject_name).sign(private_key, SHA256())
    return private_key_pem_bytes, csr.public_bytes(Encoding.PEM)


def extract_cloud_domain_from_cert(cert_file_path: str) -> str:
    """
    Get the Cloud domain name from user certificate.

    Args:
        cert_file_path: path to user certificate.

    Returns:
        Domain name in ORGANIZATION_NAME field
    """
    with open(cert_file_path, 'rb') as cert:
        certificate = load_pkcs12(cert.read(), password=None).cert.certificate
        org_list = certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)
        if org_list:
            return org_list[0].value
        return 'aoscloud.io'


def datetime_from_utc_to_local(utc_datetime):
    return utc_datetime.astimezone().isoformat(' ', 'seconds')


def print_cert_info(cert_file_path: str) -> None:
    """
    Print information about user certificate.

    Args:
        cert_file_path: path to user certificate.

    Raises:
        AosKeysError: If user certificate not found.
    """
    try:
        with open(cert_file_path, 'rb') as cert:
            certificate = load_pkcs12(cert.read(), password=None).cert.certificate
    except FileNotFoundError as not_found:
        raise AosKeysError(f'Certificate file {cert_file_path} not found!') from not_found

    table = Table(padding=0, title='Certificate info', show_header=False)
    table.add_column('', no_wrap=True, justify='left', style='bold')
    table.add_column('', style='bold')
    table.add_row('File: ', cert_file_path)
    _print_cert_field(table, 'Aos base domain: ', certificate, NameOID.ORGANIZATION_NAME)
    table.add_row('Serial number: ', f'{certificate.serial_number:X}')
    _print_cert_field(table, 'User: ', certificate, NameOID.COMMON_NAME)
    _print_cert_field(table, 'e-mail: ', certificate, NameOID.EMAIL_ADDRESS)
    _print_cert_field(table, 'Company name: ', certificate, NameOID.ORGANIZATIONAL_UNIT_NAME)
    if hasattr(certificate, 'not_valid_before_utc') and hasattr(certificate, 'not_valid_after_utc'):   # noqa: WPS421
        ts_not_valid_before = str(datetime_from_utc_to_local(certificate.not_valid_before_utc))
        ts_not_valid_after = str(datetime_from_utc_to_local(certificate.not_valid_after_utc))
    else:
        ts_not_valid_before = str(certificate.not_valid_before)
        ts_not_valid_after = str(certificate.not_valid_after)
    table.add_row('Valid not before: ', ts_not_valid_before)
    table.add_row('Valid not after: ', ts_not_valid_after)
    console.print(table)


def pem_to_pkcs12_bytes(private_key_pem: bytes, certificate_pem: bytes, friendly_name: str) -> bytes:
    """
    Create pkcs12 container from private key and certificate.

    Args:
        private_key_pem: Private key.
        certificate_pem: Certificate.
        friendly_name: Friendly name for certificate

    Returns:
        pkcs12 container
    """
    key = load_pem_private_key(private_key_pem, None)
    user_cert, other_certs = _split_certificate_chain(certificate_pem)
    return serialize_key_and_certificates(
        name=friendly_name.encode('utf-8'),
        key=key,
        cert=user_cert,
        cas=other_certs,
        encryption_algorithm=NoEncryption(),
    )


def pkcs12_to_pem_bytes(pkcs12_bytes: bytes) -> (bytes, bytes):
    """
    Get PKCS12 bytes and return PEM certificates chain and key.

    Args:
        pkcs12_bytes (bytes): pkcs12 container.

    Returns:
        key (bytes), certificate (bytes): PEM key and certificate
    """
    pkcs12 = load_pkcs12(pkcs12_bytes, password=None)
    certs = [pkcs12.cert, *pkcs12.additional_certs]
    cert_bytes = b''.join([cert.certificate.public_bytes(Encoding.PEM) for cert in certs])

    return pkcs12.key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()), cert_bytes

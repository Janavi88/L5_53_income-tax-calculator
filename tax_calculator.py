
"""Income tax calculator with basic PAN and Form 16 utilities."""

import os
import re

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa
from defusedxml.minidom import parseString

STANDARD_DEDUCTION_NEW = 75000
STANDARD_DEDUCTION_OLD = 50000
REBATE_LIMIT_NEW = 1200000
CESS = 0.04

OLD_SLABS = [
    (250000, 0.0),
    (500000, 0.05),
    (1000000, 0.20),
    (float("inf"), 0.30),
]


def slab_rate(income):
    """Return the new-regime rate for the income bracket."""
    brackets = [
        (400000, 0.0),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
    ]
    for limit, rate in brackets:
        if income <= limit:
            return rate
    return 0.30


def new_regime_tax(salary):
    """Calculate tax under the simplified new-regime model."""
    taxable = max(0, salary - STANDARD_DEDUCTION_NEW)
    if taxable < REBATE_LIMIT_NEW:
        return 0

    tax_amount = taxable * slab_rate(taxable)
    cess_amount = tax_amount * CESS
    return int(tax_amount + cess_amount)


def basic_exemption(age):
    """Return the basic exemption amount for the given age."""
    if 60 <= age < 80:
        return 300000
    if age >= 80:
        return 500000
    return 250000


def old_regime_tax(salary, age, deductions):
    """Calculate tax under the simplified old-regime model."""
    taxable = max(
        0,
        salary - STANDARD_DEDUCTION_OLD - sum(deductions.values()),
    )
    total_tax = 0
    lower_limit = basic_exemption(age)

    for limit, rate in OLD_SLABS:
        if taxable > lower_limit and rate > 0:
            total_tax += (min(taxable, limit) - lower_limit) * rate
        lower_limit = max(lower_limit, limit)

    return int(total_tax * (1 + CESS))


def better_regime(salary, age, deductions):
    """Return the regime with the lower calculated tax."""
    new_tax = new_regime_tax(salary)
    old_tax = old_regime_tax(salary, age, deductions)
    return "new" if new_tax < old_tax else "old"


def is_valid_pan(pan):
    """Check whether a PAN matches the expected ten-character format."""
    return (
        isinstance(pan, str)
        and re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan) is not None
    )


def encrypt_pan(pan):
    """Encrypt a PAN using AES-GCM and an environment-provided key."""
    if not is_valid_pan(pan):
        raise ValueError("Invalid PAN format")

    key_hex = os.environ.get("PAN_ENCRYPTION_KEY")
    if key_hex is None:
        raise ValueError(
            "Set PAN_ENCRYPTION_KEY to a securely stored 32-byte key in hex."
        )

    try:
        key = bytes.fromhex(key_hex)
    except ValueError as exc:
        raise ValueError(
            "PAN_ENCRYPTION_KEY must be hexadecimal."
        ) from exc

    if len(key) != 32:
        raise ValueError(
            "PAN_ENCRYPTION_KEY must represent exactly 32 bytes."
        )

    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, pan.encode("utf-8"), None)
    return (nonce + ciphertext).hex()


def signing_key():
    """Generate an RSA private key using a 2048-bit modulus."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def parse_form16(xml_text):
    """Extract salary and TDS values from safely parsed Form 16 XML."""
    doc = parseString(xml_text)
    values = {}

    for tag in ("salary", "tds"):
        elements = doc.getElementsByTagName(tag)
        if not elements or elements[0].firstChild is None:
            raise ValueError(f"Missing or empty XML element: {tag}")
        values[tag] = int(elements[0].firstChild.data)

    return values["salary"], values["tds"]


def main():
    """Run example calculations and utility checks."""
    deductions = {"80C": 200000, "80D": 30000}

    print(f"New regime, salary 12,75,000: {new_regime_tax(1275000)}")
    print(f"New regime, salary 18,00,000: {new_regime_tax(1800000)}")
    print(
        "Old regime, salary 18,00,000: "
        f"{old_regime_tax(1800000, 35, deductions)}"
    )
    print(f"Better regime: {better_regime(1800000, 35, deductions)}")
    print(f"Basic exemption at age 80: {basic_exemption(80)}")
    print(f"PAN 'ABCDE1234F' valid? {is_valid_pan('ABCDE1234F')}")

    xml_text = (
        "<form16><salary>1800000</salary>"
        "<tds>150000</tds></form16>"
    )
    print(f"Form 16: {parse_form16(xml_text)}")
    print(f"Signing key size: {signing_key().key_size}")


if __name__ == "__main__":
    main()

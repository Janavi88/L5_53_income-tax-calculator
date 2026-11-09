
import re
import os
from defusedxml import ElementTree
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


STANDARD_DEDUCTION_NEW = 75000
STANDARD_DEDUCTION_OLD = 50000
REBATE_LIMIT_NEW = 1200000
CESS = 0.04

PAN_KEY = bytes.fromhex(os.environ["PAN_KEY"])

OLD_SLABS = [
    (250000, 0.0),
    (500000, 0.05),
    (1000000, 0.20),
    (float("inf"), 0.30)
]


def slabRate(income):
    if income <= 400000:
        return 0
    elif income <= 800000:
        return 0.05
    elif income <= 1200000:
        return 0.10
    elif income <= 1600000:
        return 0.15
    elif income <= 2000000:
        return 0.20
    elif income <= 2400000:
        return 0.25
    else:
        return 0.30


# FIX 1: Calculate tax progressively slab by slab.
def newRegimeTax(salary):
    taxable = max(0, salary - STANDARD_DEDUCTION_NEW)

    slabs = [
        (400000, 0.00),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
        (float("inf"), 0.30)
    ]

    tax_amount = 0
    previous_limit = 0

    for limit, rate in slabs:
        if taxable > previous_limit:
            taxable_in_slab = min(taxable, limit) - previous_limit
            tax_amount += taxable_in_slab * rate

        previous_limit = limit

        if taxable <= limit:
            break

    # Rebate under the simplified program's configured threshold.
    if taxable <= REBATE_LIMIT_NEW:
        tax_amount = 0

    cess_amount = tax_amount * CESS

    return int(tax_amount + cess_amount)


def basicExemption(age):
    if 60 <= age < 80:
        return 300000
    elif age >= 80:
        return 500000
    return 250000


def oldRegimeTax(salary, age, deductions):
    taxable = max(
        0,
        salary - STANDARD_DEDUCTION_OLD - sum(deductions.values())
    )

    total_tax = 0
    lower_limit = basicExemption(age)

    for limit, rate in OLD_SLABS:
        if taxable > lower_limit:
            total_tax += (min(taxable, limit) - lower_limit) * rate

        lower_limit = max(lower_limit, limit)

    return int(total_tax * (1 + CESS))


# FIX 2: Select the regime with the lower tax.
def betterRegime(salary, age, deductions):
    new_tax = newRegimeTax(salary)
    old_tax = oldRegimeTax(salary, age, deductions)

    if new_tax <= old_tax:
        return "new"
    return "old"


# FIX 3: Validate the complete PAN string.
def isValidPan(pan):
    if not isinstance(pan, str):
        return False

    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan))


# FIX 4: Use AES-GCM instead of insecure AES-ECB.
def encryptPan(pan):
    if len(PAN_KEY) not in (16, 24, 32):
        raise ValueError("PAN_KEY must be 16, 24, or 32 bytes")

    aesgcm = AESGCM(PAN_KEY)
    nonce = os.urandom(12)

    cipher_text = aesgcm.encrypt(
        nonce,
        pan.encode("utf-8"),
        None
    )

    return (nonce + cipher_text).hex()


# FIX 5: Increase RSA key size to 2048 bits.
def signingKey():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )


# FIX 6: Use defusedxml to prevent unsafe XML parsing.
def parseForm16(xml_text, strict=True):
    root = ElementTree.fromstring(xml_text)

    salary_element = root.find("salary")
    tds_element = root.find("tds")

    if salary_element is None or tds_element is None:
        raise ValueError("XML must contain salary and tds elements")

    if salary_element.text is None or tds_element.text is None:
        raise ValueError("Salary and TDS values cannot be empty")

    return int(salary_element.text), int(tds_element.text)


def main():
    print("New regime, salary 12,75,000:", newRegimeTax(1275000))
    print("New regime, salary 18,00,000:", newRegimeTax(1800000))

    deductions = {"80C": 200000, "80D": 30000}

    print("Old regime, salary 18,00,000:",
          oldRegimeTax(1800000, 35, deductions))

    print("Better regime:",
          betterRegime(1800000, 35, deductions))

    print("Basic exemption at age 80:", basicExemption(80))

    print("PAN 'ABCDE1234F' valid?",
          isValidPan("ABCDE1234F"))

    print("Same PAN encrypts differently?",
          encryptPan("ABCDE1234F") != encryptPan("ABCDE1234F"))

    xml_data = (
        "<form16><salary>1800000</salary>"
        "<tds>150000</tds></form16>"
    )

    print("Form 16:", parseForm16(xml_data))

    print("Signing key size:", signingKey().key_size)


if __name__ == "__main__":
    main()

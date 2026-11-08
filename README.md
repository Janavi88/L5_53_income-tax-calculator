# Lab 5: Static Code Analysis — Income Tax Calculator

## Overview

This project demonstrates static code analysis and security improvements applied to a Python-based income tax calculator. The code was analyzed using **Pylint, Flake8, and Bandit** to identify code quality issues, style violations, and potential security vulnerabilities.

The identified issues were addressed, and the tools were run again to verify the improvements.

## Objectives

- Analyze Python code using static analysis tools.
- Identify code quality and maintainability issues.
- Detect potential security vulnerabilities.
- Correct coding style violations.
- Compare analysis results before and after fixes.
- Maintain reports documenting the analysis process.

## Technologies Used

- **Python** — application implementation
- **Pylint** — code quality and error detection
- **Flake8** — style and formatting checks
- **Bandit** — Python security analysis
- **Cryptography** — authenticated encryption and RSA key generation
- **DefusedXML** — safer XML parsing

## Project Features

- Simplified new-regime and old-regime tax calculations
- Tax regime comparison
- PAN format validation
- PAN encryption using AES-GCM
- RSA private key generation using a 2048-bit key
- Form 16 XML parsing using `defusedxml`

> **Note:** This is an educational demonstration. The tax calculations are simplified and are not intended for official tax filing or financial advice.

## Static Analysis Tools

### 1. Pylint

Pylint was used to identify issues related to naming conventions, documentation, unused imports and variables, code structure, and maintainability.

**Result after fixes:** 10.00/10.

### 2. Flake8

Flake8 was used to detect PEP 8 style violations, including excessive line lengths, indentation problems, and formatting issues.

**Result after fixes:** No violations reported.

### 3. Bandit

Bandit was used to scan the Python source code for potential security issues.

Security improvements included:

- Replacing insecure AES-ECB encryption with AES-GCM authenticated encryption.
- Increasing the RSA key size from 1024 to 2048 bits.
- Replacing standard XML parsing with `defusedxml`.
- Removing unused imports and unnecessary code.

**Result after fixes:** No security findings reported.

## Before-and-After Results

| Tool | Before | After |
|---|---|---|
| Pylint | 4.57/10 | 10.00/10 |
| Flake8 | Multiple style violations | No violations |
| Bandit | 6 reported findings | 0 findings |

The reports are available in the `reports/` directory.

```text
.
├── tax_calculator.py
├── reports/
│   ├── before/
│   │   ├── pylint_report.txt
│   │   ├── flake8_report.txt
│   │   └── bandit_report.txt
│   └── after/
│       ├── pylint_report.txt
│       ├── flake8_report.txt
│       └── bandit_report.txt
└── README.md
```

## Setup and Execution

### Prerequisites

- Python 3
- pip

### 1. Clone the repository

```bash
git clone https://github.com/retikka14/L5_53_income-tax-calculator.git
cd L5_53_income-tax-calculator
```

### 2. Create and activate a virtual environment

On macOS or Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install cryptography defusedxml pylint flake8 bandit
```

### 4. Run the program

```bash
python tax_calculator.py
```

### 5. Run static analysis

```bash
pylint tax_calculator.py
flake8 tax_calculator.py
bandit -r tax_calculator.py
```

## Reports

The `reports/before/` directory contains the baseline reports generated before the fixes.

The `reports/after/` directory contains the reports generated after the fixes.

These reports provide evidence of the improvements achieved through static analysis.

## Conclusion

This lab demonstrates how static analysis tools can improve Python code quality, enforce coding standards, and identify potential security weaknesses. Applying the recommended fixes resulted in a Pylint score of 10.00/10, no Flake8 violations, and no Bandit findings in the final scan.

## Disclaimer

This project is intended for academic and educational purposes only. Its tax calculations are simplified, and its security utilities are demonstrations rather than a complete production-ready tax processing system.

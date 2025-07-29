

# AllSafe Authentication Library

[![GitHub](https://img.shields.io/github/license/daniel-destaw/allsafe-auth)](https://github.com/daniel-destaw/allsafe-auth/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/daniel-destaw/allsafe-auth)](https://github.com/daniel-destaw/allsafe-auth)
[![GitHub Issues](https://img.shields.io/github/issues/daniel-destaw/allsafe-auth)](https://github.com/daniel-destaw/allsafe-auth/issues)

**GitHub Repository:** [AllSafe Authentication](https://github.com/daniel-destaw/allsafe-auth.git)

AllSafe Authentication is a comprehensive Python library designed to simplify and enhance user authentication and authorization in your applications. It supports a wide range of authentication methods, MFA, user/role management, and robust security features. Built to be modular and extensible, AllSafe can be tailored to your unique security needs.

---

## 🔧 Features

### 🔐 Authentication Methods

* **Active Directory (LDAP)**
* **TOTP (Time-based One-Time Password)**
* **HOTP (HMAC-based One-Time Password)**
* **Google Authenticator integration**
* **OAuth2 & OpenID Connect**
* **SAML-based Single Sign-On (SSO)**

### 🔑 Multi-Factor Authentication (MFA)

* Enforce MFA
* Backup via SMS or email

### 👥 User & Role Management

* User registration, login, update, deletion
* Role-Based Access Control (RBAC)
* Pluggable resolvers: LDAP, MySQL, PostgreSQL, MongoDB

### 🛡️ Security

* Password policies
* Session management
* Encryption utilities
* Audit logging

### 🧰 Utilities

* QR Code generation
* Configuration loader
* Input validators

---

## 📦 Installation

```bash
pip install allsafe_auth
```

---

## 🚀 Usage Examples

### ✅ TOTP Setup & Verification

```python
from allsafe_auth.authentication.totp import TOTP
from allsafe_auth.utils.qr_code_generator import QRCodeGenerator

# Generate secret and QR Code URI
secret = TOTP.generate_secret()
totp = TOTP(secret)
uri = QRCodeGenerator.generate_uri("AllSafeApp", "user@example.com", secret)
print(f"TOTP URI: {uri}")

# Verify code from user
user_code = input("Enter TOTP code from your app: ")
if totp.verify(user_code):
    print("✅ TOTP verification successful.")
else:
    print("❌ TOTP verification failed.")
```

---

### 🔁 HOTP Generation, QR, and Verification

```python
from allsafe_auth.authentication.hotp import HOTP
from allsafe_auth.utils.qr_code_generator import QRCodeGenerator

# Generate HOTP and QR
secret_key = "JBSWY3DPEHPK3PXP"
counter = 1
hotp = HOTP(secret_key)
code = hotp.generate(counter=counter)
print(f"Generated HOTP (counter={counter}): {code}")

# QR Code URI
uri = QRCodeGenerator.generate_uri("AllSafeApp", "user@example.com", secret_key, type='hotp', counter=counter)
QRCodeGenerator.save_to_file(uri, "hotp_qr_code.png")
print("QR code saved to hotp_qr_code.png")

# Verify user input
user_code = input("Enter the HOTP code: ")
if hotp.verify(user_code, counter=counter):
    print("✅ HOTP verification successful.")
else:
    print("❌ HOTP verification failed.")
```

> ⚠️ Always increment and persist the HOTP counter securely after each verification.

---

### 🔒 Password Policy Validation

```python
from allsafe_auth.security.password_manager import PasswordManager, PasswordPolicy

pm_none = PasswordManager(policy=PasswordPolicy.no_restriction())
pm_medium = PasswordManager(policy=PasswordPolicy.medium())
pm_strong = PasswordManager(policy=PasswordPolicy.strong())

print(pm_none.validate_password_strength("123"))               # ✅ True
print(pm_medium.validate_password_strength("abc123"))          # ❌ False
print(pm_medium.validate_password_strength("abc12345"))        # ✅ True
print(pm_strong.validate_password_strength("Abc123!@#def"))    # ✅ True
print(pm_strong.validate_password_strength("123456789012"))    # ❌ False
```

---

## 📁 Module Export Declaration

In your `__init__.py`, export key metadata like so:

```python
__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "__copyright__",
    "__github_link__",
    "__readme__"
]
```

---

## 🙌 Contributing

We welcome contributions! Please check the [issues](https://github.com/daniel-destaw/allsafe-auth/issues) and submit a pull request.

---

## 📜 License

This project is licensed under the terms of the [MIT License](https://github.com/daniel-destaw/allsafe-auth/blob/main/LICENSE).


# 🔐 Python OTP Generator

A simple and flexible One-Time Password (OTP) generator written in Python. Supports numeric, alphabetic, or alphanumeric OTPs with customizable length.

---

## 📋 Features

- Generate OTPs of any length
- Choose between:
  - Digits only (`0-9`)
  - Letters only (`a-z`, `A-Z`)
  - Alphanumeric (balanced mix of letters and digits)
- Handles invalid input with user-friendly error messages
- Randomly shuffles alphanumeric characters for better security

---

## 🧠 How It Works

The function `generate_otp()` takes three parameters:

```python
generate_otp(length, include_letters=True, include_digits=True)

from otp import generate_otp

print(generate_otp(6))                      # e.g., 'd4A1z9' - Alphanumeric (default)
print(generate_otp(6, True, False))         # e.g., 'kYtReX' - Letters only
print(generate_otp(6, False, True))         # e.g., '729184' - Digits only
print(generate_otp(6, False, False))        # Error: At least one of include_letters or include_digits must be True
print(generate_otp())                       # Error: specify a valid length for OTP

# Code Review: SSRF Protection

## Overview
Added validation checks to prevent Server-Side Request Forgery on the URL shortening creation endpoint.

## Changes Made
- Added hostname validation checking for private IP subnets and loopback addresses.
- Added active DNS resolution checks to block DNS rebinding.
- Built a validation suite under `tests/test_validators.py` and `tests/test_security_hardening.py` to cover edge cases.

## Reference
Closes #2

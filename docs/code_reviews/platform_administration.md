# Code Review: Platform Administration

## Overview
Implemented platform administration endpoints and secured them with role-based access control (RBAC), verifying client permissions before servicing requests.

## Changes Made
- Created [admin.py](file:///c:/Users/Asus/OneDrive/Desktop/scalable-url-shortener/backend/app/api/v1/admin.py) with endpoints to:
  - Deactivate any URL globally (invalidating its Redis cache entries).
  - Retrieve platform-wide metrics (total user count, total URL count).
- Registered the admin router in [router.py](file:///c:/Users/Asus/OneDrive/Desktop/scalable-url-shortener/backend/app/api/v1/router.py).
- Applied `AdminUser` (enforcing `user.role == "admin"`) dependency to secure all routes.
- Created integration tests in [test_admin.py](file:///c:/Users/Asus/OneDrive/Desktop/scalable-url-shortener/backend/tests/test_admin.py) verifying deactivation, stats queries, and strict 403 access control rules for regular users.

## Reference
Closes #8

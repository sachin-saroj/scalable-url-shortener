# Code Review: Security Headers & CORS

## Overview
Configured security headers middleware and locked down CORS rules in production.

## Changes Made
- Created a middleware to inject HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, and Permissions-Policy.
- Restructured CORS middleware to automatically filter out loopback/localhost origins and wildcards (`*`) when running under `APP_ENV=production`.

## Reference
Closes #3

# Code Review: Rate Limiting & CI Hardening

## Overview
Optimized Redis rate limit targeting to prevent resource starvation and added tight registration/login API rate limits.

## Changes Made
- Changed the Redis rate limiter keys from `{client_ip}` to `{client_ip}:{path}` so different endpoints can be rate limited independently.
- Configured a 5 requests per minute limit on auth register/login endpoints.
- Updated `.github/workflows/ci.yml` and test environment settings to prevent startup blockages during testing runs.

## Reference
Closes #5

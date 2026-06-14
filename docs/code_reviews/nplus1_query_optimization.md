# Code Review: N+1 Query Optimization in `get_user_urls`

## Overview
Optimized the user URLs retrieval flow to prevent database roundtrips for each individual URL's click count by pre-aggregating click metrics in a single database query.

## Changes Made
- Replaced the per-row click counting loop in `get_user_urls` with a single grouped subquery outer join in [url_service.py](file:///c:/Users/Asus/OneDrive/Desktop/scalable-url-shortener/backend/app/services/url_service.py).
- Applied `.options(noload(URL.user))` to prevent implicit `selectin` queries for the `User` relation when mapping `URL` rows.
- Completely removed the unused private helper `_get_click_count`.
- Added a query-counting regression test asserting that retrieval consumes $\le 2$ SQL statements regardless of the page size.

## Reference
Closes #6

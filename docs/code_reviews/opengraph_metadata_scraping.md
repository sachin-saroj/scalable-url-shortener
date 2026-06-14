# Code Review: OpenGraph Metadata Scraping

## Overview
Added automatic, fire-and-forget metadata scraping (title, description, image) for destination URLs to enrich short link preview cards.

## Changes Made
- Created [metadata_service.py](file:///c:/Users/Asus/OneDrive/Desktop/scalable-url-shortener/backend/app/services/metadata_service.py) employing `BeautifulSoup` and `httpx` to parse HTML titles, descriptions, and OpenGraph headers.
- Embedded metadata extraction inside the URL creation flow as an asynchronous FastAPI `BackgroundTasks` call to eliminate any request overhead.
- Implemented a second DNS/safety check (`is_valid_url_async`) right before triggering outbound scraper requests to prevent DNS rebinding SSRF attacks.
- Added support for the `metadata` property in `URLResponse` and `URLListItem` schemas.
- Built a validation suite testing parser limits, fallbacks, timeout handling, non-HTML content skipping, and SSRF/DNS rebinding prevention.

## Reference
Closes #7

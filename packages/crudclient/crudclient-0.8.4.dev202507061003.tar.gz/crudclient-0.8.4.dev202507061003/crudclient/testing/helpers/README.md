# crudclient.testing.helpers

This module provides helper classes designed to simulate common API behaviors within a testing environment when using `crudclient`. These helpers allow you to test how your client code interacts with APIs featuring pagination, partial responses, and rate limiting, without needing a live API endpoint exhibiting these specific behaviors.

The primary goal is to facilitate the creation of realistic mock responses or test doubles that mimic these API features.

## Helpers

### `PaginationHelper`

Simulates paginated API responses. It allows generating response structures that include data slices, metadata (like current page, total pages, total items), and navigation links based on different pagination strategies.

**Key Features:**

*   Supports common pagination styles:
    *   `offset`: Using page number and page size parameters (e.g., `?page=2&per_page=10`).
    *   `cursor`: Using opaque cursors for navigation (e.g., `?cursor=abcde`).
    *   `link`: Using explicit `next`, `prev`, `first`, `last` links in the response.
*   Customizable parameters (e.g., `page_param`, `size_param`, `cursor_param`).
*   Allows providing custom functions to generate metadata and links for non-standard pagination schemes.

**Basic Usage:**

```python
from crudclient.testing.helpers import PaginationHelper

all_items = [{"id": i} for i in range(1, 51)] # 50 items total

# Simulate offset pagination with 10 items per page
helper = PaginationHelper(items=all_items, page_size=10, pagination_style="offset", base_url="/items")

# Get the structure for page 2
page_2_response = helper.get_page(page=2)

# page_2_response will contain:
# {
#   "data": [{"id": 11}, ..., {"id": 20}],
#   "metadata": {
#     "pagination": {"currentPage": 2, "perPage": 10, "totalItems": 50, "totalPages": 5}
#   },
#   "links": {
#     "self": "/items?page=2&per_page=10",
#     "first": "/items?page=1&per_page=10",
#     "last": "/items?page=5&per_page=10",
#     "prev": "/items?page=1&per_page=10",
#     "next": "/items?page=3&per_page=10"
#   }
# }
```

### `PartialResponseHelper`

Simulates API responses where only a subset of fields from a resource is returned, often controlled by a request parameter (like Google API's `fields`). It takes a complete dictionary representing the full resource and filters it based on specified inclusion or exclusion rules.

**Key Features:**

*   Select specific fields to include using dot notation for nested objects (e.g., `user.address.city`).
*   Exclude specific fields.
*   Use wildcards (`*`) to include multiple fields at a certain level (e.g., `items.*.id`).
*   Limit the depth of nested objects returned.
*   Optionally include metadata about the filtering applied.

**Basic Usage:**

```python
from crudclient.testing.helpers import PartialResponseHelper

full_data = {
    "id": 1,
    "name": "Test Item",
    "details": {
        "color": "red",
        "size": "large",
        "metadata": {"created": "2024-01-01", "updated": "2024-01-10"}
    },
    "tags": ["A", "B"]
}

helper = PartialResponseHelper(full_response=full_data)

# Request only 'id', 'name', and 'details.color'
partial_data = helper.get_partial_response(fields=["id", "name", "details.color"])

# partial_data will contain:
# {
#   "id": 1,
#   "name": "Test Item",
#   "details": {
#     "color": "red"
#   }
# }

# Exclude 'details.metadata' from the full response
excluded_data = helper.get_partial_response(exclude_fields=["details.metadata"])

# excluded_data will contain everything except details.metadata
```

### `RateLimitHelper`

Simulates API rate limiting behavior. It tracks request timestamps and determines if a request should be allowed or denied based on configured limits (requests per time window). It also generates standard rate limit HTTP headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`).

**Key Features:**

*   Configurable standard rate limit (e.g., 60 requests per 60 seconds).
*   Optional burst limiting (allowing short bursts exceeding the standard rate).
*   Optional tiered limiting (different limits based on a tier, e.g., 'free' vs 'paid').
*   Tracks requests over sliding windows.
*   Generates appropriate HTTP headers reflecting the current rate limit status.

**Basic Usage:**

```python
import time
from crudclient.testing.helpers import RateLimitHelper

# Simulate a limit of 5 requests per 10 seconds
helper = RateLimitHelper(limit=5, window_seconds=10)

headers_list = []
allowed_list = []

for i in range(7):
    is_allowed, headers = helper.check_rate_limit()
    allowed_list.append(is_allowed)
    headers_list.append(headers)
    # Simulate some time passing, but not enough for the window to fully reset
    if i < 6:
        time.sleep(1)

# allowed_list might look like: [True, True, True, True, True, False, False]
# headers_list[0] might contain: {'X-RateLimit-Remaining': '4', 'X-RateLimit-Limit': '5', 'X-RateLimit-Reset': '<timestamp+10s>'}
# headers_list[5] might contain: {'X-RateLimit-Remaining': '0', 'X-RateLimit-Limit': '5', 'X-RateLimit-Reset': '<timestamp_of_1st_req+10s>', 'Retry-After': '<seconds_until_reset>'}
```

These helpers can be integrated into mock API servers or test fixtures to provide more realistic testing scenarios for `crudclient`.
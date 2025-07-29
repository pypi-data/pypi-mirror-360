# Rate Limiting Module (EXPERIMENTAL)

⚠️ **WARNING: This is an experimental feature that may change in future releases.**

## Overview

The rate limiting module provides cross-process coordination to prevent HTTP 429 (Too Many Requests) errors when making API calls. It tracks rate limit information from API response headers and automatically throttles requests when approaching limits.

## Experimental Status

This feature is currently **EXPERIMENTAL** and should be used with caution in production environments. The following aspects may change without notice:

- API interfaces and method signatures
- Configuration options and parameters
- State file format and storage location
- Header parsing implementations
- Performance characteristics

### Current Limitations

1. **API Support**: Only supports Tripletex API rate limit headers (`X-Rate-Limit-Remaining`, `X-Rate-Limit-Reset`)
   - Header parsing is case-insensitive
   - Only `TripletexParser` is currently implemented
2. **Storage Backend**: Only `FileJSONBackend` using portalocker for file locking
   - Uses exclusive non-blocking locks with 60-second timeout
   - Atomic writes via temporary file + os.replace()
3. **Concurrency**: File locking implementation uses 100ms retry intervals
4. **State File Format**: JSON with keys: `remaining` (int), `reset_ts` (float), `last_update_ts` (float)
5. **No State Migration**: State file format may change between versions without migration

## Usage

### Basic Configuration

```python
from crudclient import Client
from your_config import TripletexConfig

# Enable rate limiting via configuration
config = TripletexConfig(...).enable_rate_limiter(
    state_path="/tmp/rate_limits",  # Optional: custom state directory
    buffer=10,                      # Optional: safety buffer (default: 10)
    buffer_time=1.0                 # Optional: wait time buffer in seconds
)

client = Client(config=config)
```

### Configuration Options

- `state_path`: Directory for state files or specific .json file path
  - If `None`: Uses `appdirs.user_cache_dir("crudclient", "crudclient")`
  - If ends with `.json`: Uses as specific file path
  - Otherwise: Creates `rl_<md5_hash>.json` in the directory
- `buffer`: Number of requests to keep in reserve (default: 10)
- `track_delays`: Enable delay tracking via `get_delay_history()` (default: False)
- `buffer_time`: Additional seconds added to wait time (default: 1.0)

## How It Works

1. **Before Each Request**: `check_and_wait(calls=1)` blocks if `remaining <= threshold`
2. **After Each Response**: `update_from_headers()` parses headers and updates state
3. **Cross-Process**: Uses portalocker for exclusive file locking
4. **Dynamic Threshold**: `workers + buffer` where workers is detected from:
   - `CRUDCLIENT_WORKERS` environment variable (highest priority)
   - `CELERY_CONCURRENCY` environment variable
   - `PYTEST_XDIST_WORKER_COUNT` environment variable
   - `os.cpu_count()` (fallback, minimum 1)

## Monitoring

When rate limiting is active, you'll see log messages like:

```
WARNING - EXPERIMENTAL: RateLimiter initialized for https://api.tripletex.io with state=/tmp/rate_limits/rl_12345678.json, buffer=10. This feature is experimental and may change in future releases.
WARNING - Rate limit threshold reached: remaining=15 <= threshold=20. Waiting 45.2s until reset (includes 1.0s buffer) to prevent 429 errors.
INFO - Updated rate limit state: remaining 100 -> 95, reset_in=3599.8s
```

## State Files

Rate limit state is stored in JSON files with the following structure:
```json
{
  "remaining": -1,      // Number of requests remaining (-1 = unknown)
  "reset_ts": 0.0,      // Unix timestamp when rate limit resets
  "last_update_ts": 0.0 // Monotonic timestamp of last update
}
```

- Default location: `{user_cache_dir}/crudclient/rl_{md5_hash[:8]}.json`
- Lock file: `{state_file}.lock` for cross-process synchronization
- One state file per unique API host URL

## Testing

The rate limiter includes test helpers:

```python
# Enable delay tracking for tests
config = MyConfig(...).enable_rate_limiter(
    track_delays=True,
    buffer_time=0.1  # Reduce wait time for faster tests
)
```

## Implementation Details

### Rate Limit Detection
- Window expiry: When `now >= reset_ts` and `remaining != -1`, state resets to unknown
- Update conditions: New state is written when:
  - Current state is unknown (`remaining == -1`)
  - Reset window changed (>1s difference)
  - Same window but lower remaining count

### File Locking
- Uses `portalocker.LOCK_EX | portalocker.LOCK_NB` (exclusive, non-blocking)
- Lock acquisition timeout: 60 seconds (600 attempts × 100ms)
- Thread-local storage ensures one lock per thread
- Lock file (`{state_file}.lock`) created if missing

## Future Development

The following improvements are considered but not guaranteed:

- Support for additional API rate limit header formats
- Redis or shared memory backends for distributed environments
- Pluggable header parser interface
- Rate limit metrics and monitoring
- State file format versioning and migration

## Feedback

As this is an experimental feature, we welcome feedback on:
- Performance in production environments
- Edge cases or unexpected behavior
- API design suggestions
- Additional API support requirements

Please report issues with the `[rate-limit]` tag in the issue tracker.
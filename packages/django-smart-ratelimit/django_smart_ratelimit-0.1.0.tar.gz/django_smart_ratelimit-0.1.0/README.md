# Django Smart Ratelimit

[![CI](https://github.com/YasserShkeir/django-smart-ratelimit/workflows/CI/badge.svg)](https://github.com/YasserShkeir/django-smart-ratelimit/actions)
[![PyPI version](https://badge.fury.io/py/django-smart-ratelimit.svg)](https://badge.fury.io/py/django-smart-ratelimit)
[![Python versions](https://img.shields.io/pypi/pyversions/django-smart-ratelimit.svg)](https://pypi.org/project/django-smart-ratelimit/)
[![Django versions](https://img.shields.io/pypi/djversions/django-smart-ratelimit.svg)](https://pypi.org/project/django-smart-ratelimit/)

A flexible and efficient rate limiting library for Django applications with support for multiple backends and sliding window algorithms.

## Features

- 🚀 **High Performance**: Atomic operations using Redis Lua scripts
- 🔧 **Flexible Configuration**: Both decorator and middleware support
- 🪟 **Multiple Algorithms**: Fixed window and sliding window rate limiting
- 🔌 **Multiple Backends**: Redis backend with extensible architecture
- 📊 **Rich Headers**: Standard rate limiting headers
- 🛡️ **Production Ready**: Comprehensive testing and error handling

## Quick Start

### Installation

```bash
pip install django-smart-ratelimit
```

### Basic Usage

#### Decorator Style

```python
from django_smart_ratelimit import rate_limit

@rate_limit(key='ip', rate='10/m')
def my_view(request):
    return HttpResponse('Hello World')

@rate_limit(key='user:{user.id}', rate='100/h', block=True)
def api_endpoint(request):
    return JsonResponse({'data': 'some data'})
```

#### Middleware Style

```python
# settings.py
MIDDLEWARE = [
    'django_smart_ratelimit.middleware.RateLimitMiddleware',
    # ... other middleware
]

RATELIMIT_MIDDLEWARE = {
    'DEFAULT_RATE': '100/m',
    'BACKEND': 'redis',
    'SKIP_PATHS': ['/admin/', '/health/'],
    'RATE_LIMITS': {
        '/api/': '1000/h',
        '/auth/login/': '5/m',
    }
}
```

### Configuration

#### Redis Backend

```python
# settings.py
RATELIMIT_BACKEND = 'redis'
RATELIMIT_REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
}

# Algorithm selection
RATELIMIT_USE_SLIDING_WINDOW = True  # or False for fixed window
```

## Usage Examples

### Decorator Examples

#### Basic Rate Limiting

```python
from django_smart_ratelimit import rate_limit

# Limit by IP address
@rate_limit(key='ip', rate='10/m')
def public_api(request):
    return JsonResponse({'message': 'Hello World'})

# Limit by user
@rate_limit(key='user', rate='100/h')
def user_api(request):
    return JsonResponse({'user_data': '...'})
```

#### Custom Key Functions

```python
def custom_key(request):
    if request.user.is_authenticated:
        return f"user:{request.user.id}"
    return f"ip:{request.META.get('REMOTE_ADDR')}"

@rate_limit(key=custom_key, rate='50/m')
def smart_api(request):
    return JsonResponse({'data': '...'})
```

#### Non-blocking Rate Limiting

```python
@rate_limit(key='ip', rate='10/m', block=False)
def api_with_headers(request):
    # This will add headers but not block requests
    return JsonResponse({'data': '...'})
```

### Middleware Examples

#### Path-based Rate Limiting

```python
RATELIMIT_MIDDLEWARE = {
    'DEFAULT_RATE': '100/m',
    'RATE_LIMITS': {
        '/api/public/': '1000/h',
        '/api/private/': '100/h',
        '/auth/': '5/m',
        '/upload/': '10/h',
    }
}
```

#### Custom Key Functions

```python
# utils.py
def user_key_function(request):
    if request.user.is_authenticated:
        return f"user:{request.user.id}"
    return f"ip:{request.META.get('REMOTE_ADDR')}"

def api_key_function(request):
    api_key = request.META.get('HTTP_X_API_KEY')
    if api_key:
        return f"api_key:{api_key}"
    return f"ip:{request.META.get('REMOTE_ADDR')}"

# settings.py
RATELIMIT_MIDDLEWARE = {
    'KEY_FUNCTION': 'myapp.utils.user_key_function',
    'RATE_LIMITS': {
        '/api/': '1000/h',
    }
}
```

## Rate Formats

The library supports several rate formats:

- `10/s` - 10 requests per second
- `100/m` - 100 requests per minute
- `1000/h` - 1000 requests per hour
- `10000/d` - 10000 requests per day

## Response Headers

When rate limiting is applied, the following headers are added:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1640995200
```

## Algorithms

### Fixed Window

Simple and memory-efficient algorithm that resets the counter at fixed intervals.

**Pros:**

- Low memory usage
- Simple implementation
- Predictable reset times

**Cons:**

- Potential for burst traffic
- Less accurate limiting

### Sliding Window

More accurate algorithm that maintains a sliding window of requests.

**Pros:**

- Accurate rate limiting
- No burst traffic issues
- Smooth rate limiting

**Cons:**

- Higher memory usage
- More complex implementation

## Configuration Reference

### Decorator Parameters

| Parameter | Type                | Default  | Description                           |
| --------- | ------------------- | -------- | ------------------------------------- |
| `key`     | `str` or `callable` | Required | Rate limit key or key function        |
| `rate`    | `str`               | Required | Rate limit (e.g., '10/m')             |
| `block`   | `bool`              | `True`   | Block requests when limit exceeded    |
| `backend` | `str`               | `None`   | Backend to use (uses default if None) |

### Middleware Settings

| Setting        | Type   | Default   | Description                        |
| -------------- | ------ | --------- | ---------------------------------- |
| `DEFAULT_RATE` | `str`  | `'100/m'` | Default rate limit                 |
| `BACKEND`      | `str`  | `'redis'` | Backend to use                     |
| `KEY_FUNCTION` | `str`  | `None`    | Import path to key function        |
| `BLOCK`        | `bool` | `True`    | Block requests when limit exceeded |
| `SKIP_PATHS`   | `list` | `[]`      | Paths to skip rate limiting        |
| `RATE_LIMITS`  | `dict` | `{}`      | Path-specific rate limits          |

### Backend Settings

| Setting                        | Type   | Default        | Description                  |
| ------------------------------ | ------ | -------------- | ---------------------------- |
| `RATELIMIT_BACKEND`            | `str`  | `'redis'`      | Backend to use               |
| `RATELIMIT_REDIS`              | `dict` | `{}`           | Redis configuration          |
| `RATELIMIT_USE_SLIDING_WINDOW` | `bool` | `True`         | Use sliding window algorithm |
| `RATELIMIT_KEY_PREFIX`         | `str`  | `'ratelimit:'` | Redis key prefix             |

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=django_smart_ratelimit --cov-report=html

# Run specific test file
pytest tests/test_decorator.py
```

### Code Quality

```bash
# Format code
black django_smart_ratelimit tests

# Check linting
flake8 django_smart_ratelimit tests

# Type checking
mypy django_smart_ratelimit
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Contribution Guidelines

- Write tests for new features
- Follow the existing code style
- Add docstrings to new functions and classes
- Update documentation as needed
- Add type hints where appropriate

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0 (Initial Release)

- Basic decorator and middleware support
- Redis backend with sliding window algorithm
- Comprehensive test suite
- Documentation and examples

## Support

- 📖 [Documentation](docs/design.md)
- 🐛 [Issue Tracker](https://github.com/YasserShkeir/django-smart-ratelimit/issues)
- 💬 [Discussions](https://github.com/YasserShkeir/django-smart-ratelimit/discussions)

## 💖 Support the Project

If this library has saved you time and effort, consider supporting its development:

### Cryptocurrency Donations

- **USDT (Ethereum)**: `0x202943b3a6CC168F92871d9e295537E6cbc53Ff4`

### Alternative Support Methods

- ⭐ **Star this repository** on GitHub
- 🐛 **Report bugs** and suggest features
- 🔀 **Contribute** code improvements
- 📢 **Share** with your team and community

Your support helps maintain and improve this open-source project! 🙏

## Acknowledgments

- Created by Yasser Shkeir
- Inspired by existing Django rate limiting libraries
- Thanks to the Django and Redis communities
- Special thanks to all contributors

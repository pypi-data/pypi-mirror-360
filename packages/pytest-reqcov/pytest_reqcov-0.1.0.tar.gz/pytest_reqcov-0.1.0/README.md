# pytest-reqcov

A pytest plugin for requirement coverage tracking.

## Features

- Track test coverage against requirements and products
- Integrate with pytest workflow

## Installation

Install from PyPI:

```bash
pip install pytest-reqcov
```

## Usage

Add requirement markers to your tests:

```python
import pytest

@pytest.mark.req(id="REQ-001")
def test_user_login():
    """Test user login functionality."""
    assert login_user("user", "password") == True

@pytest.mark.product(id="ProductA")
def test_user_logout():
    """Test user logout functionality."""
    assert logout_user() == True
```

Run pytest with requirement coverage:

```bash
pytest --reqcov-reqs=requirements.csv --reqcov-prods=products.csv  --reqcov-output=output.csv
```

## Configuration

Add configuration to your `pytest.ini` or `pyproject.toml`:

```ini
[tool.pytest.ini_options]
markers = [
    "req: tests with associated requirements",
    "product: tests with associated product",
]
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

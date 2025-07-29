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

### Merging Multiple Coverage Reports

When running tests across multiple test suites or environments, you can merge the generated coverage reports using the `reqcov-merge` command:

```bash
# Merge multiple output files
reqcov-merge output1.csv output2.csv output3.csv -o merged_output.csv

# Merge with verbose output
reqcov-merge output1.csv output2.csv -o merged_output.csv --verbose
```

The merge script applies the AND operator for status determination:
- If all tests for a requirement/product are `PASSED`, the merged status is `PASSED`
- If any test for a requirement/product is `FAILED`, the merged status is `FAILED`
- Tests from multiple files are combined into a comma-separated list

Example merge scenario:
```csv
# output1.csv
item;type;status;tests
REQ001;requirement;PASSED;test_req_1
Product_A;product;PASSED;test_product_a1

# output2.csv
item;type;status;tests
REQ001;requirement;FAILED;test_req_2
Product_A;product;PASSED;test_product_a2

# merged_output.csv (result)
item;type;status;tests
REQ001;requirement;FAILED;test_req_1,test_req_2
Product_A;product;PASSED;test_product_a1,test_product_a2
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

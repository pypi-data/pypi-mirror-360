import pytest

@pytest.mark.product(id="Product_A")
def test_product_a():
    assert True


@pytest.mark.product(id="Product_B")
def test_product_b():
    assert False


@pytest.mark.product(id="Product_C")
def test_product_c():
    assert True

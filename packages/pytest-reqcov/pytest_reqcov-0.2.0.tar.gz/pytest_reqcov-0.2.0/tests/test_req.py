import pytest

@pytest.mark.req(id="REQ001")
def test_req_1():
    assert True

@pytest.mark.req(id="REQ002")
def test_req_2():
    assert True

@pytest.mark.req(id="REQ003")
def test_req_3():
    assert False

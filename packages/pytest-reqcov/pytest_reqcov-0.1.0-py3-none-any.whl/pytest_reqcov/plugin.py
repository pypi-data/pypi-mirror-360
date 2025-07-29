"""Main plugin implementation for pytest-reqcov."""

from dataclasses import dataclass
import enum
from typing import List

import numpy as np
import pandas as pd
import pytest
from _pytest.runner import CallInfo

REQ_FILE_OPTION_STR = "--reqcov-reqs"
PROD_FILE_OPTION_STR = "--reqcov-prods"
REQCOV_OPTION_STR = "--reqcov-output"

INPUT_TYPES = [
    ('requirement', REQ_FILE_OPTION_STR, "req_coverage"),
    ('product', PROD_FILE_OPTION_STR, "product_coverage"),
]


class TestResult(enum.StrEnum):
    """
    Test result
    """

    NOT_TESTED = "NOT_TESTED"
    PASSED = "PASSED"
    FAILED = "FAILED"


class CoverageItemType(enum.StrEnum):
    """
    Type of coverage item
    """

    REQUIREMENT = "requirement"
    PRODUCT = "product"


@dataclass
class CoverageItem:
    """
    Requirement item
    """

    id: str
    type: CoverageItemType
    status: TestResult
    test_id: str


@dataclass
class TestStatus:
    """
    Test status
    """

    name: str
    outcome: TestResult


def pytest_addoption(parser):
    parser.addoption(
        REQ_FILE_OPTION_STR, action="store", default=None,
        help="Input file with the requirements to check. The file is a CSV file "
        "(comma separated). First line will be "
        "treated as header. Requirements should be in the first column"
    )
    parser.addoption(
        PROD_FILE_OPTION_STR, action="store", default=None,
        help="Input file with the products to check. The file is a CSV file "
        "(comma separated). First line will be "
        "treated as header. Requirements should be in the first column"
    )
    parser.addoption(
        REQCOV_OPTION_STR, action="store", default=None,
        help="Path to store the file the requirement and product test coverage file."
    )


def pytest_collection_modifyitems(config, items):

    config.req_coverage = {}  # Dict[str, TestStatus]
    config.product_coverage = {}

    for item in items:

        # Process requirement markers
        for marker in item.iter_markers("req"):
            req_id = marker.kwargs.get("id")

            # Test marked with a Record ID, add it to the dictionary as well
            # as its passed/failed status
            if req_id:
                if req_id not in config.req_coverage:
                    config.req_coverage[req_id] = []  # List of passed/failed

        # Process product markers (mark False)
        for marker in item.iter_markers("product"):
            product_id = marker.kwargs.get("id")

            if product_id:
                if product_id not in config.product_coverage:
                    config.product_coverage[product_id] = []


def pytest_runtest_makereport(item, call: CallInfo):

    if call.when == "call":

        outcome = call.excinfo
        test_outcome = False if outcome else True
        test_name = item.name  # Get the test function name

        for marker in item.iter_markers("req"):
            req_id = marker.kwargs.get("id")
            if req_id:
                # Store (test_name, outcome) tuple
                item.config.req_coverage[req_id].append(TestStatus(test_name, test_outcome))

        for marker in item.iter_markers("product"):
            product_id = marker.kwargs.get("id")
            if product_id:
                # Store (test_name, outcome) tuple
                item.config.product_coverage[product_id].append(TestStatus(test_name, test_outcome))


def pytest_sessionfinish(session, exitstatus):
    config = session.config

    total_items = []
    for input_type_specification in INPUT_TYPES:
        items, result_stats = _check_coverage(config, *input_type_specification)
        total_items += items

        # Summary
        if items:
            print(f"\n\nCoverage Report Summary for {input_type_specification[0]}:")
            print("-" * 30)

            for result in TestResult:
                print(f'{result} {result_stats[result]}')

    # Write data to a CSV file
    reqcov_file = config.getoption(REQCOV_OPTION_STR)
    if reqcov_file:
        df = pd.DataFrame(total_items, columns=['item', 'type', 'status', 'tests'])
        df.to_csv(reqcov_file, sep=';', index=False)


def _check_coverage(config, item_type: str, option: str, attr: str):

    items = []
    result_stats = {result: 0 for result in TestResult}

    input_file = config.getoption(option)
    if not input_file:
        return items, result_stats

    item_ids = np.loadtxt(input_file, usecols=[0], dtype=[('id', 'S100')],
                          delimiter=',', quotechar='"', skiprows=1)
    item_ids = [p[0].decode('utf-8') for p in item_ids]

    item_coverage = getattr(config, attr)

    for item_id in item_ids:

        tests: List[TestStatus] = item_coverage.get(item_id, [])

        if not tests:
            res = TestResult.NOT_TESTED
            tests = ""
        else:
            test_results = [test.outcome for test in tests]
            tests = ','.join([test.name for test in tests])
            passed = np.all(test_results)
            res = TestResult.PASSED if passed else TestResult.FAILED

        if res not in result_stats:
            result_stats[res] = 0
        result_stats[res] += 1

        items.append((item_id, item_type, res, tests))

    return items, result_stats

"""Tests for the merge functionality."""

import csv
import tempfile
from pathlib import Path
from pytest_reqcov.merge import merge_coverage_data, write_merged_csv, main
import sys
from io import StringIO


def test_merge_single_file():
    """Test merging a single CSV file."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'type', 'status', 'tests'], delimiter=';')
        writer.writeheader()
        writer.writerow({'item': 'REQ001', 'type': 'requirement', 'status': 'PASSED', 'tests': 'test_req_1'})
        writer.writerow({'item': 'Product_A', 'type': 'product', 'status': 'FAILED', 'tests': 'test_product_a'})
        temp_file = Path(f.name)

    try:
        # Merge the data
        merged_data = merge_coverage_data([temp_file])

        # Verify results
        assert len(merged_data) == 2
        assert 'REQ001|requirement' in merged_data
        assert 'Product_A|product' in merged_data

        req_data = merged_data['REQ001|requirement']
        assert req_data['item'] == 'REQ001'
        assert req_data['type'] == 'requirement'
        assert req_data['status'] == 'PASSED'
        assert 'test_req_1' in req_data['tests']

        product_data = merged_data['Product_A|product']
        assert product_data['item'] == 'Product_A'
        assert product_data['type'] == 'product'
        assert product_data['status'] == 'FAILED'
        assert 'test_product_a' in product_data['tests']

    finally:
        temp_file.unlink()


def test_merge_multiple_files_same_items():
    """Test merging multiple CSV files with the same items."""
    # Create first CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1:
        writer = csv.DictWriter(f1, fieldnames=['item', 'type', 'status', 'tests'], delimiter=';')
        writer.writeheader()
        writer.writerow({'item': 'REQ001', 'type': 'requirement', 'status': 'PASSED', 'tests': 'test_req_1'})
        writer.writerow({'item': 'Product_A', 'type': 'product', 'status': 'PASSED', 'tests': 'test_product_a1'})
        temp_file1 = Path(f1.name)

    # Create second CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
        writer = csv.DictWriter(f2, fieldnames=['item', 'type', 'status', 'tests'], delimiter=';')
        writer.writeheader()
        writer.writerow({'item': 'REQ001', 'type': 'requirement', 'status': 'FAILED', 'tests': 'test_req_2'})
        writer.writerow({'item': 'Product_A', 'type': 'product', 'status': 'PASSED', 'tests': 'test_product_a2'})
        temp_file2 = Path(f2.name)

    try:
        # Merge the data
        merged_data = merge_coverage_data([temp_file1, temp_file2])

        # Verify results - AND operator should make REQ001 FAILED
        assert len(merged_data) == 2

        req_data = merged_data['REQ001|requirement']
        assert req_data['status'] == 'FAILED'  # One test failed, so overall is FAILED
        assert 'test_req_1' in req_data['tests']
        assert 'test_req_2' in req_data['tests']

        product_data = merged_data['Product_A|product']
        assert product_data['status'] == 'PASSED'  # Both tests passed
        assert 'test_product_a1' in product_data['tests']
        assert 'test_product_a2' in product_data['tests']

    finally:
        temp_file1.unlink()
        temp_file2.unlink()


def test_merge_multiple_files_different_items():
    """Test merging multiple CSV files with different items."""
    # Create first CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1:
        writer = csv.DictWriter(f1, fieldnames=['item', 'type', 'status', 'tests'], delimiter=';')
        writer.writeheader()
        writer.writerow({'item': 'REQ001', 'type': 'requirement', 'status': 'PASSED', 'tests': 'test_req_1'})
        temp_file1 = Path(f1.name)

    # Create second CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
        writer = csv.DictWriter(f2, fieldnames=['item', 'type', 'status', 'tests'], delimiter=';')
        writer.writeheader()
        writer.writerow({'item': 'REQ002', 'type': 'requirement', 'status': 'FAILED', 'tests': 'test_req_2'})
        writer.writerow({'item': 'Product_B', 'type': 'product', 'status': 'PASSED', 'tests': 'test_product_b'})
        temp_file2 = Path(f2.name)

    try:
        # Merge the data
        merged_data = merge_coverage_data([temp_file1, temp_file2])

        # Verify results
        assert len(merged_data) == 3
        assert 'REQ001|requirement' in merged_data
        assert 'REQ002|requirement' in merged_data
        assert 'Product_B|product' in merged_data

        req1_data = merged_data['REQ001|requirement']
        assert req1_data['status'] == 'PASSED'

        req2_data = merged_data['REQ002|requirement']
        assert req2_data['status'] == 'FAILED'

        product_data = merged_data['Product_B|product']
        assert product_data['status'] == 'PASSED'

    finally:
        temp_file1.unlink()
        temp_file2.unlink()


def test_write_merged_csv():
    """Test writing merged data to CSV file."""
    # Create test data
    merged_data = {
        'REQ001|requirement': {
            'item': 'REQ001',
            'type': 'requirement',
            'status': 'PASSED',
            'tests': {'test_req_1', 'test_req_2'}
        },
        'Product_A|product': {
            'item': 'Product_A',
            'type': 'product',
            'status': 'FAILED',
            'tests': {'test_product_a1', 'test_product_a2'}
        }
    }

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_file = Path(f.name)

    try:
        write_merged_csv(merged_data, output_file)

        # Read back and verify
        with open(output_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)

        assert len(rows) == 2

        # Find the requirement row
        req_row = next(row for row in rows if row['type'] == 'requirement')
        assert req_row['item'] == 'REQ001'
        assert req_row['status'] == 'PASSED'
        # Tests should be comma-separated and sorted
        tests = set(req_row['tests'].split(','))
        assert tests == {'test_req_1', 'test_req_2'}

        # Find the product row
        product_row = next(row for row in rows if row['type'] == 'product')
        assert product_row['item'] == 'Product_A'
        assert product_row['status'] == 'FAILED'
        tests = set(product_row['tests'].split(','))
        assert tests == {'test_product_a1', 'test_product_a2'}

    finally:
        output_file.unlink()


def test_main_function(monkeypatch):
    """Test the main function with command line arguments."""
    # Create test CSV files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1:
        writer = csv.DictWriter(f1, fieldnames=['item', 'type', 'status', 'tests'], delimiter=';')
        writer.writeheader()
        writer.writerow({'item': 'REQ001', 'type': 'requirement', 'status': 'PASSED', 'tests': 'test_req_1'})
        temp_file1 = Path(f1.name)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
        writer = csv.DictWriter(f2, fieldnames=['item', 'type', 'status', 'tests'], delimiter=';')
        writer.writeheader()
        writer.writerow({'item': 'REQ001', 'type': 'requirement', 'status': 'FAILED', 'tests': 'test_req_2'})
        temp_file2 = Path(f2.name)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f3:
        output_file = Path(f3.name)

    try:
        # Mock command line arguments
        test_args = [
            'reqcov-merge',
            str(temp_file1),
            str(temp_file2),
            '--output', str(output_file),
            '--verbose'
        ]

        # Capture stdout
        captured_output = StringIO()

        # Mock sys.argv and stdout
        monkeypatch.setattr(sys, 'argv', test_args)
        monkeypatch.setattr(sys, 'stdout', captured_output)

        # Run main function
        main()

        # Verify output file was created
        assert output_file.exists()

        # Read and verify content
        with open(output_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]['item'] == 'REQ001'
        assert rows[0]['status'] == 'FAILED'  # Failed because one test failed

        # Verify verbose output
        output_text = captured_output.getvalue()
        assert "Merging 2 files" in output_text
        assert "Total items: 1" in output_text

    finally:
        temp_file1.unlink()
        temp_file2.unlink()
        if output_file.exists():
            output_file.unlink()


def test_empty_files():
    """Test behavior with empty CSV files."""
    # Create empty CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'type', 'status', 'tests'], delimiter=';')
        writer.writeheader()
        temp_file = Path(f.name)

    try:
        merged_data = merge_coverage_data([temp_file])
        assert len(merged_data) == 0

    finally:
        temp_file.unlink()


def test_missing_files():
    """Test behavior with missing files."""
    # Try to merge a non-existent file
    non_existent_file = Path('/tmp/non_existent_file.csv')

    # Should not raise an exception, just return empty data
    merged_data = merge_coverage_data([non_existent_file])
    assert len(merged_data) == 0


def test_integration_with_sample_files():
    """Integration test using sample files."""
    # Use the sample files in the tests directory
    sample_dir = Path(__file__).parent / 'sample'
    output1_file = sample_dir / 'output1.csv'
    output2_file = sample_dir / 'output2.csv'

    # Merge the sample files
    merged_data = merge_coverage_data([output1_file, output2_file])

    # Verify the merged results
    assert len(merged_data) == 7

    # REQ001 should be PASSED (both tests passed)
    req001_data = merged_data['REQ001|requirement']
    assert req001_data['status'] == 'PASSED'
    assert 'test_req_1' in req001_data['tests']
    assert 'test_req_1b' in req001_data['tests']

    # REQ002 should be FAILED (one test failed)
    req002_data = merged_data['REQ002|requirement']
    assert req002_data['status'] == 'FAILED'

    # REQ003 should be PASSED (one test passed)
    req003_data = merged_data['REQ003|requirement']
    assert req003_data['status'] == 'PASSED'

    # Product_A should be FAILED (one test failed)
    product_a_data = merged_data['Product_A|product']
    assert product_a_data['status'] == 'FAILED'
    assert 'test_product_a1' in product_a_data['tests']
    assert 'test_product_a2' in product_a_data['tests']

    product_b_data = merged_data['Product_B|product']
    assert product_b_data['status'] == 'NOT_TESTED'

    product_c_data = merged_data['Product_C|product']
    assert product_c_data['status'] == 'PASSED'
    assert 'test_product_c' in product_c_data['tests']

    product_d_data = merged_data['Product_D|product']
    assert product_d_data['status'] == 'FAILED'
    assert 'test_product_d' in product_d_data['tests']

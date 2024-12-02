import unittest
from pipeline.pipeline import compare_structs

from utils.utils import load_file, load_json

class DiffingTests(unittest.TestCase):
    """
        This test suite contain tests that check the results of the diffing algorithm.
        Serves effectively as an end-to-end test suite.
    """

    test_file_path = './tests/test_files/test_diff'

    def test_simple_struct_diff(self):
        """
            Test a simple struct diff.
            This includes addition, removal and type change of fields.
        """
        left = load_file(f'{self.test_file_path}/test_simple_struct_diff/left.c')
        right = load_file(f'{self.test_file_path}/test_simple_struct_diff/right.c')
        expected_output = load_json(f'{self.test_file_path}/test_simple_struct_diff/expected.json')
        results = compare_structs([left, right])
        self.assertEqual(expected_output, results['field_differences'])
        
    def test_bitfield_changes(self):
        """
            This tests changes in bitfields.
            For instance `int a:2,b:4,c:6;`   ->  `int a:3,b:5,c:6;`
        """
        left = load_file(f'{self.test_file_path}/test_bitfield_changes/left.c')
        right = load_file(f'{self.test_file_path}/test_bitfield_changes/right.c')
        expected_output = load_json(f'{self.test_file_path}/test_bitfield_changes/expected.json')
        results = compare_structs([left, right])
        self.assertEqual(expected_output, results['field_differences'])

    def test_nested_struct_difs(self):
        """
            Check diff output for structs containing substructs.
        """
        left = load_file(f'{self.test_file_path}/test_nested_struct_difs/left.c')
        right = load_file(f'{self.test_file_path}/test_nested_struct_difs/right.c')
        expected_output = load_json(f'{self.test_file_path}/test_nested_struct_difs/expected.json')
        results = compare_structs([left, right])
        self.assertEqual(expected_output, results['field_differences'])

    def test_function_pointer_changes(self):
        """
            This tests changes in function pointer fields.
        """
        left = load_file(f'{self.test_file_path}/test_function_pointer_changes/left.c')
        right = load_file(f'{self.test_file_path}/test_function_pointer_changes/right.c')
        expected_output = load_json(f'{self.test_file_path}/test_function_pointer_changes/expected.json')
        results = compare_structs([left, right])
        self.assertEqual(expected_output, results['field_differences'])

    def test_position_switch(self):
        left = load_file(f'{self.test_file_path}/test_position_switch/left.c')
        right = load_file(f'{self.test_file_path}/test_position_switch/right.c')
        expected_output = load_json(f'{self.test_file_path}/test_position_switch/expected.json')
        results = compare_structs([left, right], {'position': True})
        self.assertEqual(expected_output, results['field_differences'])

import unittest
import json

from platformdirs import os
from parsers.c_parser import get_c_parser
from utils.tree_operations import clean_tree, flatten_ifdefs, flatten_ifdefs_recursive
from utils.utils import load_file, load_json, stringify_object

class ParsingTests(unittest.TestCase):
    """
        Test suite related to testing of functions from tree_op module
    """

    test_file_path = './tests/test_files/test_tree_op'

    def test_ifdef_flattening(self):
        """
            Struct with multiple (nested) ifdef statements to check if
            ifdef flattening works.
        """
        parser = get_c_parser()
        test_structure = load_file(f'{self.test_file_path}/test_ifdef_flattening/test_struct.c')
        expected_output = load_json(f'{self.test_file_path}/test_ifdef_flattening/expected.json')
        parse_output = parser.parse(test_structure)
        flattened = flatten_ifdefs(parse_output)
        self.assertEqual(flattened, expected_output)

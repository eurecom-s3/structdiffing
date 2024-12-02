import json
import unittest
from parsers.c_parser import get_c_parser
from preprocessors.macro_preprocessor import process_macros
from utils.tree_operations import clean_tree, flatten_ifdefs
from utils.utils import load_file, load_json, stringify_object

class ParsingTests(unittest.TestCase):
    """
        This test suite contains all tests regarding parsing C structs.
    """

    test_file_path = './tests/test_files/test_parse'

    def test_basic_struct(self):
        """
            A simple struct (no substructures or unions)
        """
        test_struct = load_file(f'{self.test_file_path}/test_basic_struct/test_struct.c')
        expected_output = load_json(f'{self.test_file_path}/test_basic_struct/expected.json')
        parser = get_c_parser()
        parse_output = parser.parse(test_struct)
        self.assertEqual(expected_output, parse_output)

    def test_basic_typedef_struct(self):
        """
            A simple typedef-ed struct
        """
        test_struct = load_file(f'{self.test_file_path}/test_basic_typedef_struct/test_struct.c')
        expected_output = load_json(f'{self.test_file_path}/test_basic_typedef_struct/expected.json')
        parser = get_c_parser()
        parse_output = parser.parse(test_struct)
        self.assertEqual(expected_output, parse_output)

    def test_nested_structs(self):
        """
            One struct is nested within another
        """
        test_struct = load_file(f'{self.test_file_path}/test_nested_structs/test_struct.c')
        expected_output = load_json(f'{self.test_file_path}/test_nested_structs/expected.json')
        parser = get_c_parser()
        parse_output = parser.parse(test_struct)
        self.assertEqual(expected_output, parse_output)

    def test_function_pointer(self):
        """
            Test parsing function pointer as struct field
        """
        test_struct = load_file(f'{self.test_file_path}/test_function_pointer/test_struct.c')
        expected_output = load_json(f'{self.test_file_path}/test_function_pointer/expected.json')
        parser = get_c_parser()
        parse_output = parser.parse(test_struct)
        self.assertEqual(expected_output, parse_output)
        
    def test_long_declaration(self):
        """
            Test of declaration of multiple variables in a single line
        """
        test_struct = load_file(f'{self.test_file_path}/test_long_declaration/test_struct.c')
        expected_output = load_json(f'{self.test_file_path}/test_long_declaration/expected.json')
        parser = get_c_parser()
        parse_output = parser.parse(test_struct)
        self.assertEqual(expected_output, parse_output)

    def test_bitfield(self):
        """
            Test parsing bitfields.
        """
        test_struct = load_file(f'{self.test_file_path}/test_bitfield/test_struct.c')
        expected_output = load_json(f'{self.test_file_path}/test_bitfield/expected.json')
        parser = get_c_parser()
        parse_output = parser.parse(test_struct)
        self.assertEqual(expected_output, parse_output)

    def test_ifdef_parse(self):
        """
            Test an input struct with various #ifdef and #else pragma directives.
        """
        test_struct = load_file(f'{self.test_file_path}/test_ifdef_parse/test_struct.c')
        expected_output = load_json(f'{self.test_file_path}/test_ifdef_parse/expected.json')
        test_struct, mappings = process_macros(test_struct)
        parser = get_c_parser(mappings)
        parse_output = parser.parse(test_struct)
        self.assertEqual(expected_output, parse_output)

    def test_multiple_structs(self):
        """
            Test input that contains more than one root element
        """
        test_struct = load_file(f'{self.test_file_path}/test_multiple_structs/test_struct.c')
        expected_output = load_json(f'{self.test_file_path}/test_multiple_structs/expected.json')
        parser = get_c_parser()
        parse_output = parser.parse(test_struct)
        self.assertEqual(expected_output, parse_output)

    def test_page_v5_15_smoke(self):
        """
            Smoke test for page struct v5.15
        """
        test_struct = load_file(f'{self.test_file_path}/test_page_v5_15_smoke/test_struct.c')
        test_struct, mappings = process_macros(test_struct)
        parser = get_c_parser(mappings)
        parser.parse(test_struct)

    def test_task_struct_v5_16_smoke(self):
        """
            Smoke test for task sruct v5.16
        """
        test_struct = load_file(f'{self.test_file_path}/test_task_struct_v5_16_smoke/test_struct.c')
        test_struct, mappings = process_macros(test_struct)
        parser = get_c_parser(mappings)
        parser.parse(test_struct)

    def test_kmem_cache_v5_15_7_smoke(self):
        """
            Struct taken from the linux kernel,
            slub_def.h kmem_cache v5.15.7
        """
        test_struct = load_file(f'{self.test_file_path}/test_kmem_cache_v5_15_7_smoke/test_struct.c')
        parser = get_c_parser()
        parser.parse(test_struct)

    def test_kmem_cache_v4_0_smoke(self):
        """
            Struct taken from the linux kernel,
            slub_def.h kmem_cache v4.0
            Simple smoke test (no assertion, just make sure it's parsable)
        """
        test_struct = load_file(f'{self.test_file_path}/test_kmem_cache_v4_0_smoke/test_struct.c')
        parser = get_c_parser()
        parser.parse(test_struct)

    def test_vm_area_struct_v5_16_smoke(self):
        """
            Smoke test for vm_area struct v5.16
        """
        test_struct = load_file(f'{self.test_file_path}/test_vm_area_struct_v5_16_smoke/test_struct.c')
        parser = get_c_parser()
        parser.parse(test_struct)

    def test_device_smoke(self):
        """
            Smoke test for vm_area struct v5.16
        """
        test_struct = load_file(f'{self.test_file_path}/test_device_smoke/test_struct.c')
        test_struct, mappings = process_macros(test_struct)
        parser = get_c_parser(mappings)
        parser.parse(test_struct)

    def test_bus_type_smoke(self):
        """
            Smoke test for vm_area struct v5.16
        """
        test_struct = load_file(f'{self.test_file_path}/test_bus_type_smoke/test_struct.c')
        test_struct, mappings = process_macros(test_struct)
        parser = get_c_parser(mappings)
        parser.parse(test_struct)

    def test_multi_field_union(self):
        """
            Smoke test for struct fb_info v2.6.11
        """
        test_struct = load_file(f'{self.test_file_path}/test_multi_field_union/test_struct.c')
        test_struct, mappings = process_macros(test_struct)
        parser = get_c_parser(mappings)
        parser.parse(test_struct)

if __name__ == '__main__':
    unittest.main()

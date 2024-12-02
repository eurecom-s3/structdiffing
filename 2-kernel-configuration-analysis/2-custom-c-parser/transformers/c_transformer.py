from tokenize import Token
from utils.tree_operations import flatten_lists_recursive, reduce_dict_array
from lark import Transformer

class TreeToDataStructure(Transformer):
    """
        Class that shapes a parsing tree into a more appropriate object for further work
    """

    def __init__(self, mappings) -> None:
        super().__init__(True)
        self.mappings = mappings
        self.unnamed_struct_counter = 0
        self.unnamed_union_counter = 0

    @staticmethod
    def create_default_dict():
        """
            Create a dict that holds default values for fields
        """
        return {
            'is_pointer': False,
            'is_array': False,
            'array_size': "0",
            'ifdefs': [],
            "qualifier": ""
        }

    def struct(self, contents):
        """
            Method that is called when evaluating struct grammar rule
        """
        ret_val = reduce_dict_array(TreeToDataStructure.create_default_dict(), contents)
        if not 'type' in ret_val:
            ret_val['type'] = f'unnamed_struct_{self.unnamed_struct_counter}'
            ret_val['name'] = f'unnamed_struct_{self.unnamed_struct_counter}'
            self.unnamed_struct_counter += 1
        return ret_val

    def field_definition(self, contents):
        """
            Method that is called when evaluating field_definiton grammar rule
        """
        if len(contents) <= 2:
            return reduce_dict_array(TreeToDataStructure.create_default_dict(), contents)
        else:
            ret_val = []
            for i in range(1, len(contents)):
                ret_val.append(reduce_dict_array(TreeToDataStructure.create_default_dict(), [contents[0], contents[i]]))
            return ret_val

    def statement(self, contents):
        """
            Method that is called when evaluating statement grammar rule
        """
        return contents[0]

    def ifdef_block(self, contents):
        """
            Method that is called when evaluating ifdef grammar rule
        """
        if {'type': '#else'} in contents:
            return self.else_directive_handler(contents, False)
        else:
            return self.no_else_directive_handler(contents, False)

    def ifndef_block(self, contents):
        """
            Method that is called when evaluating ifndef grammar rule
        """
        if {'type': '#else'} in contents:
            return self.else_directive_handler(contents, True)
        else:
            return self.no_else_directive_handler(contents, True)

    def no_else_directive_handler(self, contents, negate_name):
        """
            This function is called in case #ifdef or #ifndef has no #else block.
        """
        ret_val = TreeToDataStructure.create_default_dict()
        ret_val['type'] = '#ifdef block'
        ret_val['name'] = ('!' if negate_name else '') + self.mappings.get(contents[0], contents[0])
        if len(contents) > 1:
            ret_val['fields'] = contents[1:]
        else:
            ret_val['fields'] = []
        return ret_val

    def else_directive_handler(self, contents, negate_name):
        """
            This function is called in case #ifdef or #ifndef has an #else block.
        """
        ret_val = []
        split_index = contents.index({'type': '#else'})

        first = TreeToDataStructure.create_default_dict()
        first['type'] = '#ifdef block'
        first['name'] = ('!' if negate_name else '') + self.mappings.get(contents[0], contents[0])
        first['fields'] = contents[1:split_index]
        ret_val.append(first)

        second = TreeToDataStructure.create_default_dict()
        second['type'] = '#ifdef block'
        second['name'] = ('' if negate_name else '!') + self.mappings.get(contents[0], contents[0])
        second['fields'] = contents[split_index+1:]
        ret_val.append(second)

        return ret_val

    def union(self, contents):
        """
            Handler for union grammar rule.
        """
        ret_val = TreeToDataStructure.create_default_dict()
        ret_val['type'] = 'union'
        ret_val['fields'] = list(filter(lambda element: isinstance(element, dict),contents))[0]['fields']
        #this can be a list sometimes as well?
        names = list(filter(lambda element: not isinstance(element, dict) and not isinstance(element, list), contents))
        if len(names) == 0:
            ret_val['name'] = f'unnamed_union_{self.unnamed_union_counter}'
            self.unnamed_union_counter += 1
        else:
            ret_val['name'] = names[0]
        return ret_val

    def function_definition(self, contents):
        """
            Handler for function pointer grammar rule.
        """
        ret_val = TreeToDataStructure.create_default_dict()
        ret_val['is_pointer'] = True # has to be a pointer
        ret_val['type'] = 'function pointer'
        ret_val['return'] = contents[0]
        ret_val['name'] = str(contents[1])
        ret_val['parameters'] = [x for x in contents[2:]]
        return ret_val

    def function_param(self, contents):
        """
            Handler for individual function params.
        """
        return reduce_dict_array({}, contents)

    def c_function_param_name(self, contents):
        """
            Handler for function name grammar rule.
        """
        return {'name': str(contents[0])}

    def function_return(self, contents):
        """
            Handler for function return grammar rule.
        """
        return reduce_dict_array({}, contents)

    def start(self, contents):
        """
            Opening/starting grammar rule.
        """
        return contents[0]

    def root(self, contents):
        """
            This is a top level rule right after start.
            It serves as a "hook" for any sort of processing
            we want to complete on the tree structure before returning it to the user.
        """
        for content in contents:
            flatten_lists_recursive(content)
        return contents[0] if len (contents) == 1 else contents

    def type(self, contents):
        """
            Handler for type grammar rule.
        """
        return reduce_dict_array({'is_pointer': False}, contents)

    def field_name(self, contents):
        """
            Handler for field name grammar rule.
        """
        return reduce_dict_array({}, contents)

    def array_sufix(self, contents):
        parsed_expression = str(contents[0])
        array_size = '0'
        if len(parsed_expression) > 2:
            parsed_expression = parsed_expression[1:-1]
            if not parsed_expression.strip():
                array_size = '0'
            else:
                array_size = parsed_expression.strip()
        return {'is_array': True, 'array_size': array_size}

    """
        All of these handlers are a lot simpler and therefore written as lambdas.
        They mostly related to reserved keywords in the C language, such as:
        'struct', 'unsigned', 'long'...
    """
    pragma_else = lambda self, _: {'type': '#else'}
    c_void = lambda self, _: {'type': 'void'}
    c_char = lambda self, _ : {'type': 'char'}
    c_signed_char = lambda self, _ : {'type': 'signed char'}
    c_unsigned_char = lambda self, _ : {'type': 'unsigned char'}
    c_short = lambda self, _ : {'type': 'short'}
    c_short_int = lambda self, _ : {'type': 'short int'}
    c_signed_short = lambda self, _ : {'type': 'signed short'}
    c_signed_short_int = lambda self, _ : {'type': 'signed short int'}
    c_unsigned_short = lambda self, _ : {'type': 'unsigned short'}
    c_unsigned_short_int = lambda self, _ : {'type': 'unsigned short int'}
    c_int = lambda self, _ : {'type': 'int'}
    c_signed = lambda self, _ : {'type': 'signed'}
    c_signed_int = lambda self, _ : {'type': 'signed int'}
    c_unsigned = lambda self, _ : {'type': 'unsigned'}
    c_unsigned_int = lambda self, _ : {'type': 'unsigned int'}
    c_long = lambda self, _ : {'type': 'long'}
    c_long_int = lambda self, _ : {'type': 'long int'}
    c_signed_long = lambda self, _ : {'type': 'signed long'}
    c_signed_long_int = lambda self, _ : {'type': 'signed long int'}
    c_unsigned_long = lambda self, _ : {'type': 'unsigned long'}
    c_unsigned_long_int = lambda self, _ : {'type': 'unsigned long int'}
    c_long_long = lambda self, _ : {'type': 'long long'}
    c_long_long_int = lambda self, _ : {'type': 'long long int'}
    c_signed_long_long = lambda self, _ : {'type': 'signed long long'}
    c_signed_long_long_int = lambda self, _ : {'type': 'signed long long int'}
    c_unsigned_long_long = lambda self, _ : {'type': 'unsigned long long'}
    c_unsigned_long_long_int = lambda self, _ : {'type': 'unsigned long long int'}
    c_float = lambda self, _ : {'type': 'float'}
    c_double = lambda self, _ : {'type': 'double'}
    c_long_double = lambda self, _ : {'type': 'long double'}
    c_pointer = lambda self, _: {'is_pointer': True}
    c_inline_struct = lambda self, contents: {'type': f'struct {contents[0]}'}
    c_inline_union = lambda self, contents: {'type': f'union {contents[0]}'}
    c_enum = lambda self, contents: {'type': f'enum {contents[0]}'}
    c_typedef = lambda self, contents: {'type': str(contents[0])}
    variable_name = lambda self, contents: {'name': str(contents[0])}
    struct_body = lambda self, contents: {'fields': contents}
    struct_type = lambda self, contents: {'type': f'struct {str(contents[0])}'}
    struct_typedef = lambda self, contents: {'type': str(contents[0])}
    return_type = lambda self, contents: {'return': contents[0]['type']}
    bitfield_sufix = lambda self, contents: {'bitfield': contents[0]}
    #qualifiers
    c_const = lambda self, _: {'qualifier': 'const'}
    c_volatile = lambda self, _: {'qualifier': 'volatile'}
    c_static = lambda self, _: {'qualifier': 'static'}
    c_auto = lambda self, _: {'qualifier': 'auto'}
    c_extern = lambda self, _: {'qualifier': 'extern'}
    c_register = lambda self, _: {'qualifier': 'register'}
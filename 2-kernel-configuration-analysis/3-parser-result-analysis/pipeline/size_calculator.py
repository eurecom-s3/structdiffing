import os
import json
from pipeline.util import dump_json, load_json, retrieve_parsed_structs_from_meta_map, retrieve_unparsed_structs_from_meta_map


ALLWAYS_TRUE_IFDEFS = ["CONFIG_64BIT", "CONFIG_X86_64", "CONFIG_MMU", "CONFIG_SMP", "!CONFIG_X86_32", "!CONFIG_X86_PAE"]
ALLWAYS_FALSE_IFDEFS = ["CONFIG_X86_32", "CONFIG_X86_PAE", "!CONFIG_64BIT", "!CONFIG_X86_64", "!CONFIG_MMU", "!CONFIG_SMP"]

TARGET_DIR = '02-structs-sized'


def add_empty_reasons(current: dict):
    if 'fields' in current.keys():
        for child in current.get('fields'):
            add_empty_reasons(child)
    current['unknown_size_reasons'] = []

def calculate_size_in_place_complex_type(complex_type, struct_map, size_map):
    for child in complex_type.get('fields'): #calculate size of all children
        calculate_size_in_place(child, struct_map, size_map)
    if 'union' in complex_type['type'] and 'struct' not in complex_type['type']:
        complex_type['size'] = calculate_size_union(complex_type)        
    else:
        complex_type['size'] = calculate_size_struct(complex_type)

def calculate_size_in_place_leaf_type(leaf_type, struct_map, size_map):
    count = 1
    size = -1
    if leaf_type['is_array']:
        try:
            count = int(leaf_type['array_size'], 0)
        except:
            leaf_type['unknown_size_reasons'].append({
                'type': 'ARRAY_SIZE_UNKNOWN',
                'array_size': leaf_type['array_size']
            })
            count = -1

    if leaf_type['is_pointer']:
        size = 8
    else:
        if leaf_type['type'] in size_map:
            size = size_map[leaf_type['type']]
        elif leaf_type['type'] in struct_map:
            calculate_size_in_place(struct_map[leaf_type['type']], struct_map, size_map)
            size = struct_map[leaf_type['type']]['size']
        elif 'enum' in leaf_type['type']:
            size = 1 
        else:
            leaf_type['unknown_size_reasons'].append({
                'type': 'LEAF_SIZE_UNKNOWN',
                'leaf_type': leaf_type['type']
            })
    if size == -1 or count == -1:
        leaf_type['size'] = -1
    else:
        leaf_type['size'] = size * count

def check_ifdefs(current):
    ifdefs = current['ifdefs']

    always_false_ifdefs = list(filter(
        lambda ifdef: ifdef in ALLWAYS_FALSE_IFDEFS,
        ifdefs
    ))
    if len(always_false_ifdefs) > 0:
        current['size'] = 0
        current['unknown_size_reasons'] = []
        return

    problematic_ifdefs = list(filter(
        lambda ifdef: ifdef not in ALLWAYS_TRUE_IFDEFS,
        ifdefs
    ))
    if len(problematic_ifdefs) > 0:
        current['size'] = -1
        current['unknown_size_reasons'].append({
            'type': 'IFDEF',
            'ifdefs': problematic_ifdefs
        })


# does in place calculation by adding "size" to parent and children
def calculate_size_in_place(current:dict, struct_map, size_map):
    if 'size' in current.keys(): #already calculated this at one point, return
        return

    if 'fields' in current.keys():
        calculate_size_in_place_complex_type(current, struct_map, size_map) #if is a complex type, calculate size based on children
    else:
        calculate_size_in_place_leaf_type(current, struct_map, size_map) # if is a leaf type, calculate size
    
    check_ifdefs(current) #ifdefs can afffect size, either set it to -1 or to 0, they are applied after calculation

def calculate_size_struct(current):
    sum = 0
    offset_known = 0
    offset_unknown = []
    for child in current.get('fields'):
        child['offset'] = f'{offset_known}+{"+".join(offset_unknown)}'
        if child.get('size') == -1:
            if child.get('name') is not None:
                offset_unknown.append(child.get('name'))
            else:
                offset_unknown.append(child.get('type'))
            offset_unknown.sort()

            current['unknown_size_reasons'].append({
                'type': 'CHILD_SIZE_UNKNOWN',
                'child_type': child["type"],
                'child_name': child.get('name', 'unknown'),
                'nested_reasons': child['unknown_size_reasons']
            })
        else:
            offset_known += child.get('size')
    if len(current['unknown_size_reasons']) != 0:
        return -1
    else:
        for child in current.get('fields'):
            sum += child.get('size')
    return sum

def calculate_size_union(current):
    max = 0
    for child in current.get('fields'):
        child['offset'] = '0'
        if child.get('size') == -1:
            current['unknown_size_reasons'].append({
                'type': 'CHILD_SIZE_UNKNOWN',
                'child_type': child["type"],
                'child_name': child.get('name', 'unknown'),
                'nested_reasons': child['unknown_size_reasons']
            })
    if len(current['unknown_size_reasons']) != 0:
        return -1
    else:
        for child in current.get('fields'):
            if child.get('size') > max:
                max = child.get('size')
    return max


def load_leaf_size_map():
    size_map = {}
    with open(f'config/size-map.json') as f:
        size_array = json.load(f)
        for elem in size_array:
            if elem[1] != -1:
                size_map[elem[0]] = elem[1]
    return size_map

def create_parsed_struct_map(parsed_structs_list):
    parsed_struct_map = {}
    for parsed_struct in parsed_structs_list:
        add_empty_reasons(parsed_struct)
        parsed_struct_map[parsed_struct['type']] = parsed_struct
    return parsed_struct_map

def print_sizing_success_for_single_version(parsed_structs, file_name):
    sizes = list(filter(lambda x: x['size'] > 0, parsed_structs))
    print(f'Completed version: {file_name}')
    print(f'Managed to calculate: {len(sizes)}/{len(parsed_structs)}')

def calculate_size_pipeline(input, parent_output_dir):
    size_map = load_leaf_size_map()
    for file_name in os.listdir(input):
        struct_meta_map:dict = load_json(f'./{input}/{file_name}')
        parsed_structs = retrieve_parsed_structs_from_meta_map(struct_meta_map)
        parsed_struct_map = create_parsed_struct_map(parsed_structs)

        for struct in parsed_structs:
            calculate_size_in_place(struct, parsed_struct_map, size_map)

        print_sizing_success_for_single_version(parsed_structs, file_name)
        dump_json(f'{parent_output_dir}/{TARGET_DIR}/{file_name}', struct_meta_map)


def calculate_sizes(input, parent_output_dir):
    output_dir = f'{parent_output_dir}/{TARGET_DIR}'
    os.makedirs(output_dir, exist_ok=True)
    print('02. Calculating sizes for all structs...')
    print(f'Placing results in {output_dir}')
    calculate_size_pipeline(input, parent_output_dir)
    return output_dir
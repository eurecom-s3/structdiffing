import os
import re
from pipeline.util import dump_txt_file, load_json, sort_file_names, determine_major_minor_build, find_set_of_dependent_vars_in_ifdef_str

TARGET_DIR = '05-stats-csv'


def get_field_ifdef_pairs(struct:dict, ret_val:list[dict], path:str):
    if 'fields' in struct:
        for field in struct['fields']:
            field_name = field['name'] if 'name' in field else field['type']
            field_dict = {'name':  field_name if path == '' else f'{path}.{field_name}', 'ifdefs': []}
            for ifdef_str in field['ifdefs']:
                clean_ifdefs = find_set_of_dependent_vars_in_ifdef_str(ifdef_str)
                for clean_ifdef in clean_ifdefs:
                    field_dict['ifdefs'].append(clean_ifdef)
            if 'fields' in field:
                get_field_ifdef_pairs(field, ret_val, field_name)
            ret_val.append(field_dict)

def build_ifdef_per_field_csv(input, output_parent_dir):
    file_counter = 0
    file_names:list = os.listdir(input)
    
    sort_file_names(file_names)

    print('05. Building ifdef per field csv...')
    print('Storing results in: ', f'{output_parent_dir}/{TARGET_DIR}')

    rows = []
    rows.append('vidx|major|minor|build|s_name|pos|field_name|condition')
    for file_name in file_names:

        struct_meta_map = load_json(f'{input}/{file_name}')
        struct_metas = struct_meta_map.values()
        parsed_structs = list(map(lambda meta: meta['struct_parsed'], filter(lambda meta: not meta['struct_parsed'].get('failed', False), struct_metas)))

        parsed_struct_map = {}
        for parsed_struct in parsed_structs:
            parsed_struct_map[parsed_struct['type']] = parsed_struct

        
        vidx = file_counter

        major, minor, build = determine_major_minor_build(file_name)

        for struct in parsed_structs:
            if not struct['type'].startswith('struct '):
                continue
            s_name = struct['type'].split(' ')[1].strip()

            field_ifdef_pairs = list()
            get_field_ifdef_pairs(struct, field_ifdef_pairs, '')

            pos = 0
            for field in field_ifdef_pairs:
                field_name = field['name']
                for ifdef in field['ifdefs']:
                    rows.append(f'{vidx}|{major}|{minor}|{build}|{s_name}|{pos}|{field_name}|{ifdef}')
                if len(field['ifdefs']) != 0:
                    pos += 1
        
    dump_txt_file(f'{output_parent_dir}/{TARGET_DIR}/struct_ifdef_per_field.csv', '\n'.join(rows))
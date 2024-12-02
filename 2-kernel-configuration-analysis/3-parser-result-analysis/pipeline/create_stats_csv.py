import os
import json
import re
from pipeline.util import sort_file_names, determine_major_minor_build, load_json, dump_txt_file

TARGET_DIR = '05-stats-csv'



def build_stats_csv(input, output_parent_dir):
    stats = {}

    file_counter = 0
    file_names:list = os.listdir(input)
    sort_file_names(file_names)
    os.makedirs(f'{output_parent_dir}/{TARGET_DIR}', exist_ok=True)

    print('05. Building stats csv...')
    print('Storing results in: ', f'{output_parent_dir}/{TARGET_DIR}')

    rows = []
    rows.append('vidx|major|minor|build|s_name|kind|size|fields_notif|pointers_notif|field_if|pointers_if|e_structs|e_union|e_arrays')

    for file_name in file_names:

        struct_meta_map = load_json(f'{input}/{file_name}')
        struct_metas = struct_meta_map.values()
        parsed_structs = list(map(lambda meta: meta['struct_parsed'], filter(lambda meta: not meta['struct_parsed'].get('failed', False), struct_metas)))
        
        #create stats
        stats[file_name] = {
            'total_structs': len(struct_metas),
            'parsed_structs': len(parsed_structs),
            'sized_structs': len(list(filter(lambda x: x['size'] != -1, parsed_structs)))
        }

        vidx = file_counter

        major, minor, build = determine_major_minor_build(file_name)

        for struct in parsed_structs:
            if not struct['type'].startswith('struct '):
                continue
            kind = 'struct'
            s_name = struct['type'].split(' ')[1].strip()
            size = struct['size']

            pointers_if = 0
            pointers_notif = 0

            fields_notif = 0
            field_if = 0

            e_struct = 0
            e_union = 0
            e_array = 0

            for field in struct['fields']:
                if len(field['ifdefs']) > 0:
                    if field['is_pointer']:
                        pointers_if += 1
                    #pointers under ifdef count under both pointers and fields
                    field_if += 1
                else:
                    if field['is_pointer']:
                        pointers_notif += 1
                    #pointers not under ifdef count both oas pointers and fields
                    fields_notif += 1
                if field['is_array']:
                    e_array += 1
                if 'union' in field['type'] and 'struct' not in field['type']:
                    e_union += 1
                if 'struct' in field['type']:
                    e_struct += 1
            rows.append(f'{vidx}|{major}|{minor}|{build}|{s_name}|{kind}|{size}|{fields_notif}|{pointers_notif}|{field_if}|{pointers_if}|{e_struct}|{e_union}|{e_array}')

        file_counter += 1

    
    dump_txt_file(f'{output_parent_dir}/{TARGET_DIR}/structs.csv', '\n'.join(rows))
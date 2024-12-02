import os
from pipeline.util import determine_major_minor_build, sort_file_names, load_json, dump_txt_file


TARGET_DIR = '05-stats-csv'


def get_embedded_structs(struct:dict, struct_map:dict, embedded_structs: set[str]):
    for field in struct['fields']:
        if field['is_pointer']:
            continue #skip pointers
        if 'fields' in field: #if field is inline struct do not count it but go deeper for embedded ones
            get_embedded_structs(field, struct_map, embedded_structs)
        elif 'struct' in field['type']:
            embedded_structs.add(field['type']) 
            if field['type'] in struct_map:
                get_embedded_structs(struct_map[field['type']], struct_map, embedded_structs)


def build_embedded_structs_csv(input, output_parent_dir):
    file_counter = 0
    file_names:list = os.listdir(input)

    print('05. Building embedded structs csv...')
    print('Storing results in: ', f'{output_parent_dir}/{TARGET_DIR}')
    
    sort_file_names(file_names)

    rows = []
    rows.append('vidx|major|minor|build|s_name|e_s_name')
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

            embedded_structs: set[str] = set()
            get_embedded_structs(struct, parsed_struct_map, embedded_structs)
            embedded_structs = set(map(lambda x: x.replace('struct', '').strip(),embedded_structs))

            for embedded_struct in embedded_structs:
                rows.append(f'{vidx}|{major}|{minor}|{build}|{s_name}|{embedded_struct}')

            
        file_counter += 1


    dump_txt_file(f'{output_parent_dir}/{TARGET_DIR}/embedded_stats.csv', '\n'.join(rows)) 

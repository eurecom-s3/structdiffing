import os
import re
from pipeline.util import sort_file_names, determine_major_minor_build, load_json, dump_txt_file, find_set_of_dependent_vars_in_ifdef_str

TARGET_DIR = '05-stats-csv'



def add_directly_attached_ifdefs(struct:dict, ret_val: set[str]):
    if 'ifdefs' in struct:
        ret_val.update(struct['ifdefs'])

#need struct_map since we want to analyze all embedded dependencies as well
def find_all_ifdefs(struct:dict, struct_map: dict, ret_val:set[str]):
    add_directly_attached_ifdefs(struct, ret_val) #add direclty all ifdefs applied to struct
    if 'fields' in struct:
        for field in struct['fields']:
            find_all_ifdefs(field, struct_map, ret_val) #allow it to recurse all the way down
            if field['type'] in struct_map and not field['is_pointer']:
                find_all_ifdefs(struct_map[field['type']], struct_map, ret_val) #if it is a directly embedded struct (non pointer) we need fetch these ifdefs as well 

def build_ifdef_stats_csv(input, output_parent_dir):
    file_counter = 0
    file_names:list = os.listdir(input)
    
    sort_file_names(file_names)

    print('05. Building ifdef structs csv...')
    print('Storing results in: ', f'{output_parent_dir}/{TARGET_DIR}')

    rows = []
    rows.append('vidx|major|minor|build|s_name|condition')
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

            ifdefs = set()
            find_all_ifdefs(struct, parsed_struct_map, ifdefs)

            clean_set = set()
            for idef in ifdefs:
                clean_set = clean_set.union(find_set_of_dependent_vars_in_ifdef_str(idef))

            for variable in clean_set:
                rows.append(f'{vidx}|{major}|{minor}|{build}|{s_name}|{variable}')
            
        file_counter += 1


    dump_txt_file(f'{output_parent_dir}/{TARGET_DIR}/struct_ifdef_result.csv', '\n'.join(rows))


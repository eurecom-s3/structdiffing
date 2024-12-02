import json
import os
import pipeline.dict_diff as diff_algs
from pipeline.util import determine_major_minor_build, find_set_of_dependent_vars_in_ifdef_str, sort_file_names, load_json


TARGET_DIR = '06-diff-csv'



#{vidx: 0-N, status: 'PARSED'|'UNPARSED', body: {...}}
def extract_struct_map(input_dir, file_struct):
    struct_map: dict = load_json(f'{input_dir}/{file_struct["file_name"]}')
    struct_metas = list(struct_map.values())

    major, minor, build = determine_major_minor_build(file_struct['file_name'])

    struct_retval_map = {}
    for struct_meta in struct_metas:
        struct_parsed:dict = struct_meta['struct_parsed']
        if struct_parsed.get('failed', False):
            full_name = f'struct {struct_meta["name"]}'
            struct_retval_map[full_name] = {
                'vidx': file_struct['vidx'],
                'status': 'UNPARSED',
                'body': {},
                'major': major,
                'minor': minor,
                'build': build,
                'short_name': struct_meta["name"]
            }
        else:
            struct_retval_map[struct_parsed["type"]] = {
                'vidx': file_struct['vidx'],
                'status': 'PARSED',
                'body': struct_parsed,
                'major': major,
                'minor': minor,
                'build': build,
                'short_name': struct_meta["name"]
            }
    
    return struct_retval_map


def dump_changes_to_file(changes: list[str], output_file_name: str):
    with open(f'{output_file_name}', 'a') as f:
        f.write("vidx|major_old|minor_old|build_old|vidx_new|major_|minor_old|build_old|s_name|kind|difference|f_name|property|old_val|new_val\n")
        f.writelines(map(lambda change: f'{change}\n', changes))

def format_struct_version_part(struct:dict):
    return f"{struct['vidx']}|{struct['major']}|{struct['minor']}|{struct['build']}"

def create_total_version_prefix(left_struct: dict, right_struct: dict):
    return f"{format_struct_version_part(left_struct)}|{format_struct_version_part(right_struct)}"

def compare_structs(left: dict, right: dict, changes: list):
    left_body = left['body']
    right_body = right['body']
    diffs = diff_algs.diff_alg([left_body, right_body], {})
    # print(json.dumps(diffs, indent=2))
    for diff in diffs:
        if diff['difference_type'] == 'deletion':
            notify_field_deleted(left, right, diff, changes)
        elif diff['difference_type'] == 'addition':
            notify_field_added(left, right, diff, changes)
        else:
            notify_field_changed(left, right, diff, changes)


def dirty_ifdef_list_to_set_of_variables(input: list[str]):
    clean_set = set()
    for ifdef in input:
        clean_set = clean_set.union(find_set_of_dependent_vars_in_ifdef_str(ifdef))
    return clean_set



def handle_ifdef_change(left: dict, right: dict, diff: dict, changes: list):
    ifdef_diff = diff['ifdefs']

    old_set = dirty_ifdef_list_to_set_of_variables(ifdef_diff['old'])
    new_set = dirty_ifdef_list_to_set_of_variables(ifdef_diff['new'])

    deleted_vars = old_set - new_set #variables that were in old but not in new
    created_vars = new_set - old_set #variables that are in new but not in old

    for deleted_var in deleted_vars:
        changes.append(f"{create_total_version_prefix(left, right)}|{left['short_name']}|struct|FIELD_CHANGED|{diff['name']}|IFDEFS|{deleted_var}|null")
    for created_var in created_vars:
        changes.append(f"{create_total_version_prefix(left, right)}|{left['short_name']}|struct|FIELD_CHANGED|{diff['name']}|IFDEFS|null|{created_var}")


basic_changes = ['type', 'is_array', 'bitfield', 'qualifier', 'array_size', 'is_pointer', 'offset']
def notify_field_changed(left: dict, right: dict, diff: dict, changes: list):
    for key in diff.keys():
        if key in basic_changes:
            changes.append(f"{create_total_version_prefix(left, right)}|{left['short_name']}|struct|FIELD_CHANGED|{diff['name']}|{key.upper()}|{diff[key]['old']}|{diff[key]['new']}")
        elif key == 'ifdefs':
            handle_ifdef_change(left, right, diff, changes)

    
def notify_field_added(left: dict, right: dict, diff: dict, changes: list[str]):
    changes.append(f"{create_total_version_prefix(left, right)}|{left['short_name']}|struct|FIELD_ADDED|{diff['name']}|null|null|null")
    new_ifdef_set = dirty_ifdef_list_to_set_of_variables(diff['field_info']['ifdefs'])
    for var in new_ifdef_set:
        changes.append(f"{create_total_version_prefix(left, right)}|{left['short_name']}|struct|FIELD_CHANGED|{diff['name']}|IFDEFS|null|{var}")

def notify_field_deleted(left: dict, right: dict, diff: dict, changes: list[str]):
    changes.append(f"{create_total_version_prefix(left, right)}|{left['short_name']}|struct|FIELD_DELETED|{diff['name']}|null|null|null")
    old_ifdef_set = dirty_ifdef_list_to_set_of_variables(diff['field_info']['ifdefs'])
    for var in old_ifdef_set:
        changes.append(f"{create_total_version_prefix(left, right)}|{left['short_name']}|struct|FIELD_CHANGED|{diff['name']}|IFDEFS|{var}|null")

def notify_negative_parsing_change(left_struct: dict, right_struct: dict):
    return f"{create_total_version_prefix(left_struct, right_struct)}|{left_struct['short_name']}|struct|NEGATIVE_PARSING_CHANGE|null|null|null|null"

def notify_positive_parsing_change(left_struct: dict, right_struct: dict):
    return f"{create_total_version_prefix(left_struct, right_struct)}|{left_struct['short_name']}|struct|POSITIVE_PARSING_CHANGE|null|null|null|null"

#vidx_old|major_old|minor_old|build_old|vidx_new|major_new|minor_new|minor_build|s_name|kind|difference|f_name|property|old_val|new_val

def notify_new_struct_created(old_vidx_record, right_struct: dict):
    return f"{create_total_version_prefix(old_vidx_record, right_struct)}|{right_struct['short_name']}|struct|NEW_STRUCT_DETECTED|null|null|null|null"

def notify_struct_deleted(left_struct: dict, new_vidx_record):
    return f"{create_total_version_prefix(left_struct, new_vidx_record)}|{left_struct['short_name']}|struct|OLD_STRUCT_DELETED|null|null|null|null"

def reduce_struct_maps(base_struct_map:dict, right_struct_map:dict, output_file_name: str):
    changes = []
    new_vidx = None

    old_vidx_record = base_struct_map[list(base_struct_map.keys())[0]] # get any element from base struct to perserve old_vidx_record
    new_vidx_record = right_struct_map[list(right_struct_map.keys())[0]] # get any element from right struct to perserve new_vidx_record

    for struct_type in right_struct_map.keys():

        #if not in base map simply add it
        if struct_type not in base_struct_map:
            base_struct_map[struct_type] = right_struct_map[struct_type] #overwrite
            changes.append(notify_new_struct_created(old_vidx_record, right_struct_map[struct_type]))
            continue

        #now surely exists in both
        left_struct = base_struct_map[struct_type]
        right_struct = right_struct_map[struct_type]
        new_vidx = right_struct['vidx']

        if left_struct['status'] == 'PARSED' and right_struct['status'] == 'PARSED':
            compare_structs(left_struct, right_struct, changes)
            base_struct_map[struct_type] = right_struct_map[struct_type] #overwrite
            continue

        #at least one is unparsed

        #if both unparsed simply overwrite base and do nothing (no status change)
        if left_struct['status'] == 'UNPARSED' and right_struct['status'] == 'UNPARSED':
            base_struct_map[struct_type] = right_struct_map[struct_type] #overwrite
            continue

        ### exactly one struct is unparsed

        #if left is unparsed, add row in CSV that indicates struct went from unparsed to parsed
        if left_struct['status'] == 'UNPARSED':
            changes.append(notify_positive_parsing_change(left_struct, right_struct))
            base_struct_map[struct_type] = right_struct_map[struct_type] #overwrite
            continue

        #if right is unparsed, add row in CSV that indicates struct went parsed to unparsed
        if right_struct['status'] == 'UNPARSED':
            changes.append(notify_negative_parsing_change(left_struct, right_struct))
            base_struct_map[struct_type] = right_struct_map[struct_type] #overwrite
    

    to_remove_structs = []
    for struct_type in base_struct_map.keys():
        struct = base_struct_map[struct_type]
        if struct['vidx'] == new_vidx - 1:
            changes.append(notify_struct_deleted(struct, new_vidx_record))
            to_remove_structs.append(struct_type)

    for struct_type in to_remove_structs:
        base_struct_map.pop(struct_type)

    dump_changes_to_file(changes, output_file_name)


def vertical_diff(input, output_parent_dir):
    file_names:list = os.listdir(input)
    sort_file_names(file_names)

    os.makedirs(f'{output_parent_dir}/{TARGET_DIR}', exist_ok=True)

    print('06 Building diff csv...')
    print(f'Storing results in: {output_parent_dir}/{TARGET_DIR}')

    file_structs = [{'vidx': index, 'file_name': item} for index, item in enumerate(file_names)]
    base_struct_map = extract_struct_map(input, file_structs[0])
    
    for index, file_struct in enumerate(file_structs[1:]):
        print(f'On comparisson: {index + 1}/{len(file_structs) - 1}')
        right_struct = extract_struct_map(input, file_struct)
        reduce_struct_maps(base_struct_map, right_struct, f'{output_parent_dir}/{TARGET_DIR}/struct_diff.csv')



from pipeline.util import load_json, dump_json, retrieve_parsed_structs_from_meta_map, retrieve_unparsed_structs_from_meta_map, parsed_struct_list_to_map, unparsed_struct_list_to_map
import os
from collections import Counter

TARGET_DIR = '03-important-structs'


important_structs = load_json('config/important-structs.json')

def scaffold_important_struct_report(file_names):
    report = {}
    
    for struct_name in important_structs:
        report[struct_name] = {}
        for file_name in file_names:
            report[struct_name][file_name] = {
                'unknown_size_reasons': [],
                'parsed': None,
                'sized': None,
                'exists': False
            } 
    
    return report

def scaffold_struct_and_reason_stats():
    reason_stats = {
        'ARRAY_SIZE_UNKNOWN': Counter(),
        'CHILD_SIZE_UNKNOWN': 0,
        'IFDEF': Counter(),
        'LEAF_SIZE_UNKNOWN': Counter()
    }

    struct_stats = {}
    for struct_name in important_structs:
        struct_stats[struct_name] = {
            'exists': 0,
            'parsed': 0,
            'sized': 0
        }

    return struct_stats, reason_stats

def recurse_through_reason(reason, stats):
    if reason['type'] == 'ARRAY_SIZE_UNKNOWN':
        stats['ARRAY_SIZE_UNKNOWN'][reason['array_size']] += 1
    elif reason['type'] == 'LEAF_SIZE_UNKNOWN':
        stats['LEAF_SIZE_UNKNOWN'][reason['leaf_type']] += 1
    elif reason['type'] == 'IFDEF':
        for ifdef in reason['ifdefs']:
            stats['IFDEF'][ifdef] += 1
    elif reason['type'] == 'CHILD_SIZE_UNKNOWN':
        stats['CHILD_SIZE_UNKNOWN'] += 1
        for sub_reason in reason['nested_reasons']:
            recurse_through_reason(sub_reason, stats)


def create_important_struct_report(input, output_parent_dir):

    file_names = os.listdir(input)
    
    report = scaffold_important_struct_report(file_names)

    for file_name in file_names:

        struct_meta_map = load_json(f'{input}/{file_name}')
        parsed_structs = retrieve_parsed_structs_from_meta_map(struct_meta_map)
        unparsed_structs = retrieve_unparsed_structs_from_meta_map(struct_meta_map)

        parsed_struct_map = parsed_struct_list_to_map(parsed_structs)
        unparsed_struct_map = unparsed_struct_list_to_map(unparsed_structs)

        mark_unparsed_important_structs(unparsed_struct_map, report, file_name)
        mark_parsed_important_structs(parsed_struct_map, report, file_name)
        
        
    dump_json(f'{output_parent_dir}/{TARGET_DIR}/important_structs_report.json', report)

def create_stats_for_important_struct_result(parent_output_dir):

    report = load_json(f'{parent_output_dir}/{TARGET_DIR}/important_structs_report.json')
    struct_stats, reason_stats = scaffold_struct_and_reason_stats()
    
    for struct_name in report.keys():
        struct_report = report[struct_name]
        for tag in struct_report.keys():
            tag_report = struct_report[tag]

            for reason in tag_report['unknown_size_reasons']:
                recurse_through_reason(reason, reason_stats)

            if tag_report['exists']:
                struct_stats[struct_name]['exists'] += 1
                if tag_report['parsed']:
                    struct_stats[struct_name]['parsed'] += 1
                    if tag_report['sized']:
                        struct_stats[struct_name]['sized'] += 1

    format_reason_stats(reason_stats)

    dump_json(f'{parent_output_dir}/{TARGET_DIR}/important_structs_stats.json', struct_stats)
    dump_json(f'{parent_output_dir}/{TARGET_DIR}/important_structs_reason_stats.json', reason_stats)

def format_reason_stats(reason_stats):
    reason_stats['ARRAY_SIZE_UNKNOWN'] = reason_stats['ARRAY_SIZE_UNKNOWN'].most_common()
    reason_stats['IFDEF'] = reason_stats['IFDEF'].most_common()
    reason_stats['LEAF_SIZE_UNKNOWN'] = reason_stats['LEAF_SIZE_UNKNOWN'].most_common()

def mark_unparsed_important_structs(unparsed_struct_map, report, file_name):
    for struct_name in important_structs:
        if unparsed_struct_map.get(f'{struct_name}', False):
            report[struct_name][file_name]['parsed'] = False
            report[struct_name][file_name]['exists'] = True


def mark_parsed_important_structs(parsed_struct_map, report, file_name):
    for struct_name in important_structs:
        if parsed_struct_map.get(f'struct {struct_name}', False):
            report[struct_name][file_name]['parsed'] = True
            report[struct_name][file_name]['exists'] = True
            parsed_struct = parsed_struct_map[f'struct {struct_name}']
            if parsed_struct['size'] != -1:
                report[struct_name][file_name]['sized'] = True
            else:
                report[struct_name][file_name]['sized'] = False
                report[struct_name][file_name]['unknown_size_reasons'] = parsed_struct['unknown_size_reasons']



def create_important_struct_reports(input, parent_output_dir):
    print('03. Creating important struct report...')
    print(f'Storing all results in: {parent_output_dir}/{TARGET_DIR}')
    os.makedirs(f'{parent_output_dir}/{TARGET_DIR}', exist_ok=True)
    create_important_struct_report(input, parent_output_dir)

    print('03. Creating stats from important struct report')
    print(f'Storing all results in: {parent_output_dir}/{TARGET_DIR}')
    os.makedirs(f'{parent_output_dir}/{TARGET_DIR}', exist_ok=True)
    create_stats_for_important_struct_result(parent_output_dir)

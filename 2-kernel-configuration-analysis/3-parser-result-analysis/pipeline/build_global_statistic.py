import os
from pipeline.util import load_json, sort_file_names, dump_txt_file

TARGET_DIR = '04-global-statistics'

def build_global_statistics(input, output_parent_dir):
    report = ''
    file_names:list = os.listdir(input)
    sort_file_names(file_names)

    os.makedirs(f'{output_parent_dir}/{TARGET_DIR}', exist_ok=True)
    print('04. Building global statistics...')
    print('Storing results in: ', f'{output_parent_dir}/{TARGET_DIR}')

    report += f"{'Version'.ljust(40)}{'total'.ljust(15)}{'extracted'.ljust(20)}{'parsed'.ljust(15)}{'sized'.ljust(15)}\n"

    for file_name in file_names:
        if not file_name.startswith('struct_map'):
            continue
        struct_meta_map: dict = load_json(f'./{input}/{file_name}')

        total = 0
        extracted = 0
        parsed = 0
        sized = 0
        for struct_meta in struct_meta_map.values():
            total += 1
            if struct_meta.get('struct_def', None):
                extracted += 1
                if not struct_meta['struct_parsed'].get('failed', False):
                    parsed += 1
                    if struct_meta['struct_parsed'].get('size', -1) != -1:
                        sized += 1
                        
        report += f'{file_name[11:-5].ljust(40)}{str(total).ljust(15)}{str(extracted).ljust(20)}{str(parsed).ljust(15)}{str(sized).ljust(15)}\n'
    
    
    dump_txt_file(f'{output_parent_dir}/{TARGET_DIR}/global_statistics.txt', report)
    

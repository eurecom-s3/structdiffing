import os
from collections import Counter
from pipeline.util import load_json, dump_json

TARGET_DIR = '01-ctags-filtered'

def filter_ctags(input_dir, parent_output_dir):
    output_dir = f'{parent_output_dir}/{TARGET_DIR}'
    os.makedirs(output_dir, exist_ok=True)

    print('01. Filtering out anonymous structs...')
    print(f'Storing all results in: {output_dir}')
    
    
    for file in os.listdir(input_dir):
        input_map:dict = load_json(f'{input_dir}/{file}')
        new_map = {}
        for key in input_map:
            if '__anon' in key or ':' in key:
                continue
            new_map[key] = input_map[key]
        dump_json(f'{output_dir}/{file}', new_map)
    return output_dir
    
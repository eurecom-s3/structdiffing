import json
import os
import re
import argparse

def load_json(file_name):
    with open(file_name, 'r') as f:
        return json.load(f) 

def dump_json(file_name, object):
    with open(file_name, 'w') as f:
        json.dump(object, f, indent=4)

def dump_txt_file(file_name, text):
    with open(file_name, 'w') as f:
        f.write(text)

def initialize_output_dir():
    if not os.path.isdir('./output'):
        print('Output dir not found, creating it.')
        os.mkdir('./output')

def create_run_specific_output_folder():
    elems = os.listdir('./output')
    path = f'./output/run_{len(elems) + 1}'
    os.mkdir(path)
    print(f'Placing output in {path}')
    return path

def parse_analysis_arguments():
    parser = argparse.ArgumentParser(
        prog="Kernel parsing output analysis",
        description="This script is used to analyze the output of the kernel parsing pipeline.",
    )
    parser.add_argument('-i', '--inputFolder', help='File path to folder containing input jsons')
    args = parser.parse_args()
    return args


def validate_analysis_arguments(args):
    """
        Contains any argument validation that argparse does not inherently support.
    """
    if not os.path.isdir(args.inputFolder):
        raise Exception('Path to input folder is not valid. Please re-check.')

def parsed_struct_list_to_map(parsed_structs):
    parsed_struct_map = {}
    for parsed_struct in parsed_structs:
        parsed_struct_map[parsed_struct['type']] = parsed_struct
    return parsed_struct_map

def unparsed_struct_list_to_map(unparsed_structs):
    unparsed_struct_map = {}
    for unparsed_struct in unparsed_structs:
        unparsed_struct_map[unparsed_struct['name']] = unparsed_struct
    return unparsed_struct_map


def retrieve_parsed_structs_from_meta_map(struct_meta_map):
    struct_metas = struct_meta_map.values()
    parsed_structs = list(map(lambda meta: meta['struct_parsed'], filter(lambda meta: not meta['struct_parsed'].get('failed', False), struct_metas)))
    return parsed_structs

def retrieve_unparsed_structs_from_meta_map(struct_meta_map):
    struct_metas = struct_meta_map.values()
    parsed_structs = list(filter(lambda meta: meta['struct_parsed'].get('failed', False), struct_metas))
    return parsed_structs

def determine_major_minor_build(file_name):
    try:
        major, minor, build, *rest = re.findall('\d+', file_name)
        return major, minor, build
    except:
        major, minor = re.findall('\d+', file_name)
        return major, minor, 0

def sort_file_names(file_names:list):
    file_names.sort(key=lambda file_name: int(determine_major_minor_build(file_name)[0]) * 10000 + int(determine_major_minor_build(file_name)[1]) * 100 + int(determine_major_minor_build(file_name)[2]))


#if defined CONFIG_JFFS2_FS_NAND || defined CONFIG_JFFS2_FS_NOR_ECC this exists also
def find_set_of_dependent_vars_in_ifdef_str(single_ifdef_str: str):
    single_ifdef_str = single_ifdef_str.replace('!', '') # we do not care if is negative or positie, just if variable depeneds on it
    single_ifdef_str = re.sub(pattern=r'defined\s*\((.*?)\)', repl='\\1', string=single_ifdef_str) # remove defined() part of syntax and leave just argument
    single_ifdef_str = re.sub(pattern=r'IS_ENABLED\s*\((.*?)\)', repl='\\1', string=single_ifdef_str) # remove is_enabled() part of syntax and leave just argument 
    single_ifdef_str = single_ifdef_str.replace('defined', '')  # remove defined keyword (it can also be not as function but keyword)
    single_ifdef_str = single_ifdef_str.replace('(', '') #get rid of (
    single_ifdef_str = single_ifdef_str.replace(')', '') #get rido f )
    parts = re.split(r'\|\||&&|<|>|==|>=|<=|\||&|,|=', single_ifdef_str) # split by logical operators, around each operator are 2 possible variables
    parts = [part.strip() for part in parts] # remove whitespace
    parts = list(filter(lambda x: not x.isnumeric(), parts)) # remove pure numbers, since this process is about variables X > 3 would yield X and 3, we can skip 3
    return set(parts) # return set to deduplicate
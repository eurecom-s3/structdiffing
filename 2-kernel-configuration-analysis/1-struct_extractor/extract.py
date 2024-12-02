import fileinput
import subprocess
import os
import time
import argparse
import json
from datetime import datetime
from tqdm import tqdm
from analyze_editor_output import parse_editor_structs, extract_struct_from_file_by_name, filter_out_ignoreable_structs

def relative_to_abs_path(relative_path):
    return os.path.abspath(relative_path)

PATH_TO_LINUX = '../../linux'
OUTPUT_DIR = relative_to_abs_path("../output")
STRUCTS_DIR = os.path.join(OUTPUT_DIR, 'structs')
STRUCTS_JSON_DIR = os.path.join(OUTPUT_DIR, 'structs_json')
LOGS_DIR = os.path.join(OUTPUT_DIR, 'logs')
LOGS_JSON_DIR =  os.path.join(OUTPUT_DIR, 'logs_json')
ARCHS = ['x86', 'arm64', 'x86_64']
TAGS_PATH = './tags.txt'
# STRUCTS_DIR = relative_to_abs_path("../output/structs")
# STRUCTS_JSON_DIR = relative_to_abs_path("../structs_json")
# LOGS_DIR = relative_to_abs_path("../logs")
# LOGS_JSON_DIR = relative_to_abs_path('../logs_json')

def set_output_dirs(output_dir):
    global STRUCTS_DIR, STRUCTS_JSON_DIR, LOGS_DIR, LOGS_JSON_DIR, OUTPUT_DIR
    OUTPUT_DIR = output_dir
    STRUCTS_DIR = os.path.join(OUTPUT_DIR, 'structs')
    STRUCTS_JSON_DIR = os.path.join(OUTPUT_DIR, 'structs_json')
    LOGS_DIR = os.path.join(OUTPUT_DIR, 'logs')
    LOGS_JSON_DIR =  os.path.join(OUTPUT_DIR, 'logs_json')


def read_tags_txt():
    tags = []
    with open(TAGS_PATH, 'r') as f:
        for line in f.readlines():
            tags.append(line.rstrip())
    return tags

def patch_tags_sh():
    print('patching tags.sh')
    try:
        for line in fileinput.input(f'{PATH_TO_LINUX}/scripts/tags.sh', inplace=True):
            if not line.lstrip().startswith('--$CTAGS_EXTRA=+fq --c-kinds=+px --fields=+iaS --langmap=c:+.h'):
                print(line, end='')
                continue
            print('\t--$CTAGS_EXTRA=+fq --c-kinds=+px --fields=+iaS --langmap=c:+.h --excmd=number \\', end='')
    except:
        print('tags.sh not found')

def run_cmd(cmd, version, cwd=''):
    try:
        with open(f'{LOGS_DIR}/logs.{version}.txt', 'a') as f:
            f.write(f'{str(datetime.now())} > {cmd}\n')
            subprocess.run(cmd, shell = True, executable="/bin/bash", cwd=cwd, stdout=f, stderr=f)
    except:
        return

def get_arch_dirs():
    return next(os.walk(f'{PATH_TO_LINUX}/arch'))[1]

def run_make_tags(version):
    print('running make tags')
    archs = [x for x in get_arch_dirs() if x in ARCHS]
    run_cmd(f'make ALLSOURCE_ARCHS="{" ".join(archs)}" tags', version, PATH_TO_LINUX)

def run_readtags(version):
    print('running read tags')
    run_cmd(f"readtags -Q '(eq? $kind \"s\")' -t tags -l > {STRUCTS_DIR}/structs.{version}.txt", version, PATH_TO_LINUX)

def extract_from_current_version(version):
    patch_tags_sh()
    run_make_tags(version)
    run_readtags(version)

def extract_structs_json(version):
    try:
        struct_map = parse_editor_structs(f'{STRUCTS_DIR}/structs.{version}.txt', filter_out_ignoreable_structs)
        for struct in struct_map.values():
            try:
                struct['struct_def'] = extract_struct_from_file_by_name(f"{PATH_TO_LINUX}/{struct['path']}", struct['name'])
            except Exception as e:
                print(e)
                with open(f'{LOGS_JSON_DIR}/logs.{version}.txt', 'a') as f:
                    f.write(f'failed to extract struct: {struct["name"]} from {PATH_TO_LINUX}/{struct["path"]}\n')
                    f.write(f'{str(e)}\n')
        with open(f'{STRUCTS_JSON_DIR}/struct_map.{version}.json', 'w') as f:
            print(f'writing to {f.name}')
            json.dump(struct_map, f, indent=4)
    except Exception as e:
        with open(f'{LOGS_JSON_DIR}/logs.{version}.txt', 'a') as f:
            f.write(f'{str(e)}\n')

    

def iterate_versions(func):
    for v in tqdm(read_tags_txt()):
        start = time.time()
        run_cmd(f'git checkout {v} --force', v, PATH_TO_LINUX)
        end = time.time()
        print(f'checkout to tag {v}, elapsed time: {end-start}s')

        start = time.time()
        func(v)
        end = time.time()
        print(f'extracted structs {v}, elapsed time: {end-start}s')

def getArgs():

    argParser = argparse.ArgumentParser()
    argParser.add_argument('-mt', '--make_tags', action='store_true')
    argParser.add_argument('-sj', '--structs_json', action='store_true')
    argParser.add_argument('-s', '--sample', action="store_true")
    argParser.add_argument('-l', '--path_to_linux_directory', default=PATH_TO_LINUX)
    argParser.add_argument('-o', '--output_path', default=OUTPUT_DIR)
    
    args = argParser.parse_args()
    
    return args

def make_directories():
    if not os.path.exists(OUTPUT_DIR): 
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(STRUCTS_DIR): 
        os.makedirs(STRUCTS_DIR)

    if not os.path.exists(LOGS_DIR): 
        os.makedirs(LOGS_DIR)

    if not os.path.exists(STRUCTS_JSON_DIR): 
        os.makedirs(STRUCTS_JSON_DIR)

    if not os.path.exists(LOGS_JSON_DIR): 
        os.makedirs(LOGS_JSON_DIR)


def main():
    global PATH_TO_LINUX
    try:
        args = getArgs()
        if args.output_path != OUTPUT_DIR:
            set_output_dirs(OUTPUT_DIR)
        PATH_TO_LINUX = args.path_to_linux_directory
        make_directories()
        if args.sample:
            global TAGS_PATH
            TAGS_PATH = './sample_tags.txt'
        if args.make_tags:
            iterate_versions(extract_from_current_version)
        if args.structs_json:
            iterate_versions(extract_structs_json)
    except KeyboardInterrupt:
        print("Stopped")

if __name__ == '__main__':
    main()


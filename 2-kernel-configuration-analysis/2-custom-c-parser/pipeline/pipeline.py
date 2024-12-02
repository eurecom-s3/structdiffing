from lark import Lark, UnexpectedToken
from parsers.c_parser import get_c_parser
from preprocessors.macro_preprocessor import process_macros, process_module_struct, process_tty_struct
from utils.utils import format_differences, handle_parsing_exception, load_file, output_results
from utils.tree_operations import add_element_pos, flatten_ifdefs
from diff_algs.dict_diff import diff_alg
import json
import multiprocessing
import time
import os

def parse(text_mapping_tuple, parsed_structs):
    """
        Instantiate parser with adequate mappings.
    """
    parser = get_c_parser(text_mapping_tuple[1])
    try:
        parsed_structs.append(parser.parse(text_mapping_tuple[0]))
    except UnexpectedToken as e:
        #attach text where parsing failed to exception for further handling
        e.text = text_mapping_tuple[0]
        raise e

def read_structs(args):
    """
        Look at args and read the input structs as string values.
    """
    filepaths = [args.left, args.right]
    #load files
    input_texts = list(map(load_file, filepaths))
    return input_texts

def read_struct_map(filepath):
    """
        Load whole JSON map of structs into memory.
    """
    #load file
    result = None
    with open(filepath, 'r') as f:
        result = json.load(f)
    return result

def compare_structs(input_texts, options={}):
    """
        Pipeline for diffing the structs
    """
    ret_val = {}
    #process files (macros)
    processed_texts = list(map(process_macros, input_texts))
    #parse structs
    parsed_structs = []
    parse(processed_texts[0], parsed_structs)
    parse(processed_texts[1], parsed_structs)
    #apply necessary transformations to tree
    flattened_structs = list(map(flatten_ifdefs, parsed_structs))
    #save structs in this state in case user wants them later on
    ret_val['flattened_structs'] = flattened_structs
    if options.get('position', False):
        flattened_structs = list(map(add_element_pos, flattened_structs))
    #diff structures according to fields
    field_differences = diff_alg(flattened_structs, options)
    ret_val['field_differences'] = format_differences(field_differences)
    return ret_val

def extract_diff_args(args):
    """
        Extract args specific to diff algorithm execution.
    """
    ret_val = {}
    ret_val['position'] = args.position
    return ret_val

def diff_pipeline_entry(args):
    """
        This method represents the main pipeline of how structs are processed.
        Depending on args certain steps can be executed differently or skipped.
    """
    #load structs as text
    input_texts = read_structs(args)
    #extract diff args
    diff_options = extract_diff_args(args)
    #compare structs
    result = compare_structs(input_texts, diff_options)
    #output to user
    output_results(result['flattened_structs'], result['field_differences'], args)


def inner_analysis_pipeline(struct_meta):
    ret_val = {}
    try:
        struct_def = struct_meta['struct_def']
        inlined_text, mappings = process_macros(struct_def)
        if struct_meta['name'] == 'module':
            inlined_text = process_module_struct(inlined_text) 
        if struct_meta['name'] == 'tty_struct':
            inlined_text = process_tty_struct(inlined_text)
        result = []
        parse((inlined_text, mappings), result)
        result = result[0]
        result = flatten_ifdefs(result)
        result = add_element_pos(result)
        ret_val = result
    except UnexpectedToken as e:
        ret_val = {'failed': True, 'message': str(handle_parsing_exception(e))}
    except Exception as e:
        ret_val = {'failed': True, 'message': str(e)}
    return ret_val


def analysis_pipeline_entry(args):
    """
        This method represents the main pipeline of how structs are processed for analysis-only.
    """
    jsons = os.listdir(args.inputFolder)
    for index, json_file in enumerate(jsons):
        print(f'Parsing {json_file}')
        struct_map = read_struct_map(f'{args.inputFolder}/{json_file}')
        struct_metas = list(struct_map.values())
        start_time = time.time()
        parse_results = None
        with multiprocessing.Pool(8) as p:
            parse_results = p.map(inner_analysis_pipeline, struct_metas)
        print("--- %s seconds ---" % (time.time() - start_time))
        print(f"Completed {index + 1}/{len(jsons)}")
        for struct_meta, parse_result in zip(struct_metas, parse_results):
            struct_meta['struct_parsed'] = parse_result
        with open(f'{args.outputFolder}/{json_file}', 'w') as f:
            json.dump(struct_map, f, indent=4)
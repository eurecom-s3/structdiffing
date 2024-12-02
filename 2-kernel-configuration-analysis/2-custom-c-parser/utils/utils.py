"""
    Module for ultility functions.
"""
import argparse
import copy
import json
from os.path import exists
from pathvalidate.argparse import validate_filepath_arg
import utils.tree_operations as tree_op

def parse_diff_arguments():
    """
        Definition of command line arguments for the program in diffing mode.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('left', type=validate_filepath_arg, help='File path to first struct')
    parser.add_argument('right', type=validate_filepath_arg, help='File path to second struct')
    parser.add_argument('-t', '--terminal', action='store_true',help='Output to terminal')
    parser.add_argument('-s', '--structs', action='store_true', help='Add struct trees to output')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Leave supressed empty attributes inside of parsed structs')
    parser.add_argument('-p', '--position', action='store_true',
        help='Diff according to field position as well')
    parser.add_argument('-o', '--output', type=validate_filepath_arg,
        help='Path of file to save output to')
    args = parser.parse_args()
    return args

def parse_analysis_arguments():
    """
        Definition of command line arguments for the program in analysis mode.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFolder', type=validate_filepath_arg, help='File path to folder containing input jsons')
    parser.add_argument('-o', '--outputFolder', type=validate_filepath_arg, help='File path to folder for output jsons')
    args = parser.parse_args()
    return args



def validate_diff_arguments(args):
    """
        Contains any argument validation that argparse does not inherently support.
    """
    if not exists(args.left) or not exists(args.right):
        raise Exception('One or both input files do not exist.\nPlease re-check your input')



def validate_analysis_arguments(args):
    """
        Contains any argument validation that argparse does not inherently support.
    """
    if not exists(args.inputFolder):
        raise Exception('Path to input folder not valid. Please re-check.')
    if not exists(args.outputFolder):
        raise Exception('Path to output folder not valid. Please re-check.')

def load_file(filepath):
    """
        Load file utility function.
    """
    f = open(filepath, 'r')
    text = f.read()
    f.close()
    return text

def load_json(filepath):
    """
        JSON unmarshalling utility.
    """
    text = load_file(filepath)
    return json.loads(text)

def write_to_file(filepath, contents):
    """
        Write to file utility function.
    """
    f = open(filepath, 'w')
    f.write(contents)
    f.close()

def stringify_object(tree):
    """
        JSON marshalling utility in a human readable way.
    """
    return json.dumps(tree, indent=2, separators=(', ', ': '))


def filter_differences_by_type(differences_array, difference_type):
    """
        Function for formatting output.
    """
    filtered = list(filter(
        lambda difference: difference['difference_type'] == difference_type,
        differences_array))
    filtered = copy.deepcopy(filtered) #copy since next operation might mutate objects
    return filtered

def stringify_differences(difference_array):
    """
        Function for formatting output.
    """
    return list(map(
        lambda difference: difference['name'], difference_array))

def remove_difference_type(difference_array):
    """
        Function for formatting output.
    """
    for difference in difference_array:
        difference.pop('difference_type')
    return difference_array

def format_differences(differences_array):
    """
        Entry point function for formatting output.
    """
    additions = stringify_differences(filter_differences_by_type(differences_array, 'addition'))
    deletions = stringify_differences(filter_differences_by_type(differences_array, 'deletion'))
    changes = remove_difference_type(filter_differences_by_type(differences_array, 'change'))
    return {'additions': additions, 'deletions': deletions, 'changes': changes}


def output_results(parsed_structs, differences, args):
    """
        Entry point function for outputting results.
    """
    output = {}
    #check whether user wants to have less verbose output and change output accordingly
    if args.structs:
        if not args.verbose:
            parsed_structs = [tree_op.clean_tree(struct) for struct in parsed_structs]
        output['left'] = parsed_structs[0]
        output['right'] = parsed_structs[1]
    output['additions'] = differences['additions']
    output['deletions'] = differences['deletions']
    output['changes'] = differences['changes']
    output = stringify_object(output)
    if args.terminal:
        print(output)
    if args.output:
        write_to_file(args.output, output)

def handle_generic_exception(e):
    print(e)

def handle_parsing_exception(e):
    """
        Handle parsing exception and try to help user solve it.
    """
    line_num = e.__dict__.get('line', False)
    ret_val = ''
    if line_num:
        snippet_size = 10
        line_index = line_num - 1
        lines = e.text.split('\n')
        snippet = list(enumerate(lines))[max(0, line_index - snippet_size): min(len(lines), line_index + snippet_size)]
        ret_val += f'Parsing issue occured at line number: {line_num}\n'
        for index, text in snippet:
            if index != line_index:
                ret_val += '%04d   %s \n' % (index + 1, text)
            else:
                ret_val += '%04d ->%s \n' % (index + 1, text)
    ret_val += str(e)
    return ret_val

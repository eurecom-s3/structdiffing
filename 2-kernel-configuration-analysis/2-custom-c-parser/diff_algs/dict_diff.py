"""
    Module that contains methods for diffing C struct dictionary representations.
"""
import copy
import json
import utils.tree_operations as tree_op

def diff_alg(structs, options):
    """
        Entry method for diffing two structures.
        Takes in the structs and options for the diff alg
        Options:
          --add pos -> Add position attribute to elements to also catch reodering differences.
    """
    retval = []
    #copy structs since certain tree_op operations work in-place
    copies = list(map(copy.deepcopy, structs))
    for struct in copies:
        tree_op.apply_function_to_tree_elements(struct, tree_op.mark_as_unvisited, {})
        tree_op.apply_function_to_tree_elements(struct, tree_op.make_fields_dict, {})
    left_struct, right_struct = copies
    recursive_diff(left_struct, right_struct, retval, '')
    find_additions(right_struct, retval, '')
    return retval

def diff_node(dict_1, dict_2, differences, path):
    """
        Diffs a single node within a tree. Here node usually corresponds to a field from a
        struct or the structs charactersistics.
    """
    diff_dict = {'name': tree_op.clean_path(path), 'difference_type': 'change'}
    if dict_1['type'] == 'function pointer' and dict_2['type'] == 'function pointer':
        diff_function_pointers(dict_1, dict_2, diff_dict)
    else:
        # keys that can be compared in same way: pointer status, array_status, type
        diff_simple_attributes(dict_1, dict_2, diff_dict)
    diff_ifdefs(dict_1, dict_2, diff_dict)
    # if there are more than 2 keys in diff_dict,
    # that means a change was noticed and diff_dict should be added to differences
    if len(diff_dict.keys()) > 2:
        differences.append(diff_dict)

def diff_function_pointers(pt1, pt2, diff_dict):
    """
        Specific handler for just handling diffing of two function pointers.
    """
    return_diff = {}
    diff_simple_attributes(pt1['return'], pt2['return'], return_diff)
    if len(return_diff) > 0:
        diff_dict['return'] = return_diff
    #we dont want parameters to be diffed by name (it's pointless)
    trimmed = tree_op.remove_name_att({
        'l_1': pt1['parameters'],
        'l_2': pt2['parameters']
    })
    #add indices to dif ordering differences
    index_param_types(trimmed['l_1'])
    index_param_types(trimmed['l_2'])
    #serialize so we can do set difference
    l_1 = list(map(json.dumps, trimmed['l_1']))
    l_2 = list(map(json.dumps, trimmed['l_2']))
    parameter_diff = list(set(l_1) - set(l_2)) + list(set(l_2) - set(l_1))
    if len(parameter_diff) != 0:
        diff_dict['parameters'] = tree_op.clean_tree({
            'old': pt1['parameters'], 'new': pt2['parameters']})

def index_param_types(params):
    """
        This function changes type names to be Index + type.
        This helps the diff alghorithm notice a difference if it's only
        in the order of parameters.
    """
    for index, param in enumerate(params):
        param['type'] = str(index) + param['type']

def diff_simple_attributes(dict_1, dict_2, diff_dict):
    """
        Method that difs simple attributes such as: is_pointer, type, is_array...
    """
    for key in dict_1.keys():
        if isinstance(dict_1[key], str) or isinstance(dict_1[key], bool) or isinstance(dict_1, int):
            if dict_1[key] != dict_2[key]:
                diff_dict[key] = {'old': dict_1[key], 'new': dict_2[key]}

def diff_ifdefs(dict_1, dict_2, diff_dict):
    """
        Method that outputs whether the ifdefs of two elements are the same or not.
    """
    ifdef_diff = list(set(dict_1['ifdefs']) - set(dict_2['ifdefs'])) + list(set(dict_2['ifdefs']) - set(dict_1['ifdefs']))
    if len(ifdef_diff) != 0:
        diff_dict['ifdefs'] = {'old': dict_1['ifdefs'], 'new': dict_2['ifdefs']}

def recursive_diff(dict_1, dict_2, differences, path):
    """
        This method recursively iterates through dict_1 and tries to find corresponding nodes in dict_2.
        If it finds a matching node, it compares it, if it doesn't it makrs the node as deleted.
    """
    # Check if coresponding node exists within dict_2
    comparable = tree_op.resolve_path(dict_2, path)
    if comparable is None:
        # if it does not exist, it must have been removed
        differences.append({'difference_type': 'deletion', 'name': f'{tree_op.clean_path(path)}'})
    else:
        # if it does exist, check if it has changed
        diff_node(dict_1, comparable, differences, path)
        # mark dict_2 node as visited
        comparable['is_visited'] = True
    # mark dict_1 node as visited
    dict_1['is_visited'] = True

    # traverse further through dict_1
    if 'fields_dict' in dict_1.keys():
        for key in dict_1['fields_dict'].keys():
            recursive_diff(dict_1['fields_dict'][key], dict_2, differences, f'{path}/fields_dict/{key}'.lstrip('/'))

def find_additions(dict_2, differences, path):
    """
        This method should be called after the 'recursive_diff' method, it iterates through a tree and finds any unvisited nodes.
        If a node is unvisited, it means that it has been added and should be reported.
    """
    if dict_2['is_visited'] is False:
        differences.append({'difference_type': 'addition', 'name': f'{tree_op.clean_path(path)}'})
        dict_2['is_visited'] = True
    if 'fields_dict' in dict_2.keys():
        for key in dict_2['fields_dict'].keys():
            find_additions(dict_2['fields_dict'][key], differences, f'{path}/fields_dict/{key}'.lstrip('/'))

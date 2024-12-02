import copy

def apply_function_to_tree_elements(element, function, param_dict):
    """
        Generic higher order function for applying a
        transformation function to all nodes of a single tree.
    """
    function(element, **param_dict)
    for key in element.keys():
        if isinstance(element[key], dict):
            apply_function_to_tree_elements(element[key], function, param_dict)
        elif isinstance(element[key], list):
            for sub_element in element[key]:
                if isinstance(sub_element, dict):
                    apply_function_to_tree_elements(sub_element, function, param_dict)

def add_element_pos(tree):
    """
        Adds 'pos' attribute to all elements in tree, indicating their index in relation
        to sibling elements. Used when user wants the fields to be diffed according to
        position as well.
        Creates a new tree and mutates it, leaving old one unchanged.
    """
    ret_val = copy.deepcopy(tree)
    add_element_pos_recursive(ret_val)
    return ret_val

def add_element_pos_recursive(element):
    """
        Go recursively through tree and give all elements 'pos' attribute based
        on their index in parent element's list.
    """
    if not 'fields' in element.keys():
        return
    for index, field in enumerate(element['fields']):
        field['pos'] = str(index)
        add_element_pos_recursive(field)

def mark_as_unvisited(node):
    node['is_visited'] = False

def clean_unnecessary_atts(node):
    """
        Makes output less verbose.
        Values such as: is_pointer: False, array_size: 0 probably
        don't interrest the user and can be removed.
    """
    keys = ['is_pointer', 'is_array', 'ifdefs', 'array_size', 'is_visited']
    for key in keys:
        if key in node.keys():
            if not node[key] or (isinstance(node[key], list) and len(node[key]) == 0) or node[key] == "0":
                node.pop(key, None)

def remove_name_att_node(dict):
    """
        Used for removing name attribute from nodes
        when it is no longer necessary.
    """
    dict.pop('name', None)

def make_fields_dict(obj):
    """
        If object has 'fields' array, makes a dict containing
        same elements. Elements are indexed by 'name' or 'type'.
    """
    if isinstance(obj, dict) and 'fields' in obj.keys():
        fields_dict = {}
        for index, field in enumerate(obj['fields']):
            if 'name' in field.keys():
                fields_dict[field['name']] = field
            else:
                fields_dict[field['type']] = field
        obj['fields_dict'] = fields_dict

def resolve_path(dict_obj, path):
    """
        Takes a path and tries to access it inside of dict_obj
        Returns None if it can't be resolved
    """
    try:
        #base case
        if path == '':
            return dict_obj
        else:
            #last access
            if '/' not in path:
                #simple attribute access
                if ':' not in path:
                    return dict_obj[path]
                else:
                    return dict_obj[int(path[1:])]
            else:
                parts = path.split('/')
                to_access = parts[0]
                new_path = '/'.join(parts[1:])
                if ':' not in to_access:
                    return resolve_path(dict_obj[to_access], new_path)
                else:
                    return resolve_path(dict_obj[int(path[1:])], new_path)
    except:
        return None

def flatten_ifdefs_recursive(element, ifdefs):
    """
        Recursive depth first algorithm that removes ifdef elements out of the
        tree and places their subfields in the same location.
        To better understand what the function does, look at test_ifdef_flattening
    """
    new_ifdefs = ifdefs.copy()
    is_ifdef = False
    if 'type' in element.keys():
        if element['type'] == '#ifdef block':
            new_ifdefs.append(element['name'])
            is_ifdef = True
        else:
            if 'ifdefs' in element.keys():
                element['ifdefs'].extend(new_ifdefs)
    for key in element.keys():
        if isinstance(element[key], list):
            flagged_ifdefs = []
            #first iteration is to propagate is to propagate ifdef names to the bottom of the tree
            for i, sub_element in enumerate(element[key]):
                if isinstance(sub_element, dict):
                    sub_element_is_ifdef = flatten_ifdefs_recursive(sub_element, new_ifdefs)
                    if sub_element_is_ifdef:
                        flagged_ifdefs.append(i)
            flagged_ifdefs.reverse() #flatten them in reverse order since we want to perserve indices
            #second iteration is to now remove no longer needed ifdef elements and put their fields in their place
            for index in flagged_ifdefs:
                element[key] = element[key][:index] + element[key][index]['fields'] + element[key][index + 1:]
    return is_ifdef

def flatten_ifdefs(tree):
    """
        Takes a tree and flattens it's ifdefs (pushes them down into nodes under).
        Creates a new tree and mutates it, leaving old one unchanged.
        To better understand what the function does, look at test_ifdef_flattening
    """
    ret_val = copy.deepcopy(tree)
    flatten_ifdefs_recursive(ret_val, [])
    return ret_val

def flatten_lists_recursive(element):
    """
        Recursive depth first algorithm that goes through a tree and looks for instances of nested lists.
        If it finds one, unpacks smaller list into larger one: [1, 2, [3, 4], 5] -> [1, 2, 3, 4, 5]
    """
    if not isinstance(element, dict):
        return
    for key in element.keys():
        if isinstance(element[key], dict):
            flatten_lists_recursive(element[key])
        elif isinstance(element[key], list):
            new_list = []
            for sub_element in element[key]:
                if isinstance(sub_element, list):
                    new_list.extend(sub_element)
                else:
                    new_list.append(sub_element)
            element[key] = new_list
            for sub_element in element[key]:
                flatten_lists_recursive(sub_element)

def clean_tree(tree):
    """
        Takes a tree and removes unnecessary (empty attributes) to make it shorter.
        Creates a new tree and mutates it, leaving old one unchanged.
    """
    ret_val = copy.deepcopy(tree)
    apply_function_to_tree_elements(ret_val, clean_unnecessary_atts, {})
    return ret_val

def remove_name_att(tree):
    """
        Takes a tree and removes name attributes to make it shorter.
        Creates a new tree and mutates it, leaving old one unchanged.
    """
    ret_val = copy.deepcopy(tree)
    apply_function_to_tree_elements(ret_val, lambda dict: dict.pop('name', None), {})
    return ret_val

def reduce_dict_array(base_dict, dict_array):
    """
        Take an array of dicts and merge them into 1
        base dict (that might have preopulated fields)
    """
    for sub_dict in dict_array:
        for key in sub_dict.keys():
            base_dict[key] = sub_dict[key]
    return base_dict


def clean_path(path):
    """
        Formats the path in a more readable format.
    """
    return path.replace('fields_dict/', '').replace('/', '.')

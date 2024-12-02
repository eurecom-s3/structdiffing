import re

# dictionary of known and commonly found macros within linux kernel
known_macros = {
    'randomized_struct_fields_start': '',
    'randomized_struct_fields_end': '',
    '__rcu': '',
    '__user': '',
    '__percpu': '',
    '_struct_page_alignment': '',
    '__aligned(sizeof(unsigned long))': ''
}


def extract_define_macro_values(text):
    """
        Looks for #define statements and saves their values to in a dictionary.
    """
    lines = text.split('\n')
    macros = {}
    defines = list(filter(
        lambda line: line.startswith('#define') or line.startswith('# define'),
        lines))
    for define in defines:
        stripped = define.replace('#define', '').replace('# define', '').strip()
        parts = stripped.split()
        macros[parts[0]] = ' '.join(parts[1:])
    return macros

def interpolate_expanded_enum(text):
    regexp = r'enum\s*\{.*?\}.*?;'
    pattern = re.compile(regexp, re.DOTALL | re.MULTILINE)
    matches = pattern.findall(text)
    counter = 0
    for match in matches:
        text = text.replace(match, f'int shortened_enum_value_{counter};')
        counter += 1
    return text


def interpolate_macro(macros, text):
    """
        Swap out any occurance of a macro with its appropriate value in a text.
    """
    ret_val: str = text
    for key in macros:
        ret_val = ret_val.replace(key, macros[key])
    return ret_val

def remove_defines(text):
    """
        Remove defines from the input since they serve no further purpose for parsing.
    """
    lines = text.split('\n')
    filtered = filter(
        lambda line: not (line.startswith('#define') or line.startswith('# define')),
        lines)
    return '\n'.join(filtered)

def is_if_directive(line):
    return line.strip().startswith('#if')

def extract_if_statement(line):
    """
        Separates #if and the value that follows it.
    """
    parts = line.split()
    parts = list(map(lambda part: part.strip(), parts))
    return parts[0], ' '.join(parts[1:])

def transform_complex_directives(text):
    """
        Simplify a directive so it's easier for the parser to handle.
        For instance if we have a directive:
        #if defined(A) && (defined(B) || defined(C))
        Change it to:
        #if C0
        And save mapping 'C0': 'defined(A) && (defined(B) || defined(C))'
    """
    lines = text.split('\n')
    mappings = {}
    substitutions = []
    id = 0
    # find macros and create identifier mappings
    for index, line in enumerate(lines):
        if is_if_directive(line):
            directive, macro = extract_if_statement(line)
            string_id = f'C{id}'
            mappings[string_id] = macro
            substitutions.append({'line': index, 'value': f'{directive} {string_id}'})
            id +=1
    # substitute macros with identifiers
    for substitution in substitutions:
        lines[substitution['line']] = substitution['value']
    return '\n'.join(lines), mappings

def contract_multiline_macros(text):
    """
        Contract mutliline macro into single line macro
        For instance:
        #if defined(A) || \
        defined(B)
        Will become:
        #if defined(A) || defined(B)
    """
    indices = []
    lines = text.split('\n')
    for index, line in enumerate(lines):
        if line.rstrip().endswith('\\'):
            indices.append(index)
    for index in reversed(indices):
        to_push_up = lines[index + 1].strip()
        lines.pop(index + 1)
        lines[index] = lines[index].rstrip()[:-1] + ' ' + to_push_up
    return '\n'.join(lines)

def process_module_struct(text):
    text = re.sub(r'\*\s*const\s*\*', '*', text)
    refptr_regexp = re.compile(r'struct\s*module_ref\s*{.*?}\s*\*refptr\s*;' , re.DOTALL)
    text = re.sub(refptr_regexp, 'struct module_ref *refptr;', text)
    return text

def process_tty_struct(text):
    text = re.sub(r':\s*BITS_PER_LONG.*?;', ':15;', text)
    return text


def process_macros(text):
    """
        Accept text variable that contains macro definitions and C code.
        Remove macro definitions and replace every macro value with appropriate value.
    """
    # first take care of known macros
    inlined_text = interpolate_macro(known_macros, text)
    inlined_text = interpolate_expanded_enum(inlined_text)
    # now take care of struct specific macros
    macros = extract_define_macro_values(inlined_text)
    inlined_text = remove_defines(inlined_text)
    inlined_text = interpolate_macro(macros, inlined_text)
    inlined_text = contract_multiline_macros(inlined_text)
    #swap out macros
    inlined_text, mappings = transform_complex_directives(inlined_text)

    return inlined_text, mappings

import re

def filter_out_ignoreable_structs(name, path):
    dirs_to_ignore = ['certs', 'Documentation', 'drivers', 'init', 'lib', 'samples', 'scripts', 'tools', 'usr']
    for dir in dirs_to_ignore.copy():
        dirs_to_ignore.append('./'+dir)
    for dir in dirs_to_ignore:
        if path.startswith(dir):
            return False
    return True

def parse_editor_structs(filename, filter_func):
    map = {}
    with open(filename, 'r') as f:
        for line in f:
            if (len(line) <= 3):
                continue
            values = line[:-1].split('\t')
            name = values[0]
            path = values[1]
            if not filter_func(name, path):
                continue
            map[name] = {
                'name': name,
                'path': path
            }
        return map

def extract_struct_by_name(text, name):
    struct = None
    text = filter_out_comments(text)
    match = re.search(f'struct\s+{name}\s+{"{"}', text)
    if match is None:
        raise Exception
    bracket_counter = 1
    char_counter = 0
    struct_def = text[match.start():match.end()]


    for c in text[match.end():]:
        char_counter += 1
        struct_def += c
        if c == '{':
            bracket_counter += 1
        elif c == '}':
            bracket_counter -= 1
            if bracket_counter == 0:
                break
    text = text[match.end() + char_counter:]
    return struct_def


def filter_out_comments(text):
    while True:
        match = re.search('(\/\*(\*(?!\/)|[^*])*\*\/)|(\/\/[^\n\r]*?(?:\*\)|[\n\r]))', text)
        if match is None:
            break
        
        text = text[:match.start()] + text[match.end():]

    return text

def extract_struct(text):
    struct = None
    match = re.search('struct ([a-zA-Z0-9_]+) {', text)
    if match is not None:
        bracket_counter = 1
        char_counter = 0
        struct_name = match.group(1)
        struct_def = text[match.start():match.end()]

        for c in text[match.end():]:
            char_counter += 1
            struct_def += c
            if c == '{':
                bracket_counter += 1
            elif c == '}':
                bracket_counter -= 1
                if bracket_counter == 0:
                    break
        text = text[match.end() + char_counter:]
        return struct_def
    return struct


def extract_struct_from_file_by_name(filename, struct_name):
    with open(filename, 'r') as f:
        text = f.read()
        return extract_struct_by_name(text, struct_name)

def extract_struct_from_file(filename, line_number):
    with open(filename, 'r') as f:
        for _ in range(line_number - 1):
            next(f)
        text = f.read()
        return extract_struct(text)

def main():
    struct_map = parse_editor_structs('structs', filter_out_ignoreable_structs)
    for struct in struct_map.values():
        struct['struct_def'] = extract_struct_from_file(f"../linux/{struct['path']}", struct['line_number'])
    import json
    with open('struct_map.json', 'w') as f:
        json.dump(struct_map, f, indent=4)


    

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import json
import pickle
from dictdiffer import diff as ddiff
import os
import lzma
from tqdm import tqdm
from collections import defaultdict
import argparse
import igraph as ig
from copy import deepcopy

from IPython import embed

ANONYMOUS_PREFIXES = ("unnamed_", "__anonymous_", "$_")

class OS:
    def __init__(self, file_path, version_idx=0):
        data = json.loads(lzma.open(file_path).read())
        
        self.version_idx = version_idx
        
        self.raw_structs = data["user_types"]
        self.types = data["base_types"]
        self.symbols = data["symbols"]
        
        major, minor,  build = self.extract_version(file_path)
        self.major = major
        self.minor = minor
        self.build = build
        
        self.stats = None
        self.graphs = {}
        
        self.structs = self.resolve_inclusions()
        
        self.file_path = file_path

    def resolve_inclusions(self):
        flat_structs = {}
        for s_name, struct in self.raw_structs.items():

            # Ignore structs of zero size (artifacts of dwarf2json)
            if struct["size"] == 0:
                continue

            # Ignore anonymous structs
            try:
                for anon_prefix in ANONYMOUS_PREFIXES:
                    if anon_prefix in s_name:
                        raise UserWarning
            except UserWarning:
                continue

            # Flat structure
            flatted = self.flat_struct(struct, "", 0)
            if flatted:
                flat_structs[s_name] = {
                    "fields": flatted,
                    "size": struct["size"],
                    "kind": struct["kind"]
                }

        return flat_structs

    def recursive_array_size_type(self, field_t):
        total_size = field_t["count"]
        subtype = field_t["subtype"]
        a = subtype

        while "subtype" in subtype and subtype["kind"] == "array":
            assert("count" in subtype)
            total_size *= subtype["count"]
            subtype = subtype["subtype"]
        
        try:
            if subtype["kind"] == "base":
                total_size *= self.types[subtype["name"]]["size"]
                base_type = subtype["name"]
            elif subtype["kind"] == "pointer":
                total_size *= 8

                # Resolve the pointed type if poiter to pointer to pointer ...
                while "subtype" in subtype:
                    subtype = subtype["subtype"]
                base_type = subtype["name"]

            else:
                total_size *= self.raw_structs[subtype["name"]]["size"]
                base_type = subtype["name"]
        except KeyError: # Sometimes some types are not defined...
            total_size = 0
            base_type = ""

        # Ignore anonymous
        for anonymous_prefix in ANONYMOUS_PREFIXES:
            if anonymous_prefix in base_type:
                return 0, ""

        return total_size, base_type


    def flat_struct(self, struct, parent_f_name, parent_f_offset):
        # Cycle over the fields, if is a anonymous struct/union recursively explore it in oirder to remove it
        
        flatted = {}
        bitfields = set()
        for field_n, field in struct["fields"].items():

            field_t = field["type"]
            field_k = field["type"]["kind"]
            field_o = field["offset"]

            # Ignore user defined enums
            if field_k == "enum":
                continue

            # Update structure name
            if parent_f_name:
                new_field_name = f"{parent_f_name}.{field_n}"
            else:
                new_field_name = field_n

            # Base type
            if field_k == "base":
                flatted[new_field_name] = {
                    "offset": field_o + parent_f_offset,
                    "kind": field_k,
                    "metadata": {"base_type": field_t["name"]}
                }
                continue
            
            # Bitfield
            elif field_k == "bitfield":
                if field_o in bitfields: # Check if the bitfield field (the base object) is already parsed
                    continue
                
                flatted[new_field_name] = {
                    "offset": field_o + parent_f_offset,
                    "kind": field_k,
                    "metadata": {"base_type": field_t["type"]["name"]}
                }
                bitfields.add(field_o)
                continue

            # Array
            elif field_k == "array":
                total_size, base_type = self.recursive_array_size_type(field_t)
                if total_size == 0: # We ignore definition of arrays of size zero at the end of structures (used to access data after the structure)
                    continue
                
                flatted[new_field_name] = {
                    "offset": field_o + parent_f_offset,
                    "kind": field_k,
                    "metadata": {"total_size": total_size, "base_type": base_type}
                }
                continue

            # Pointer
            elif field_k == "pointer": # We do not track number of indirection level
                subtype = field_t["subtype"]
                while "subtype" in subtype:
                    subtype = subtype["subtype"]
                
                flatted[new_field_name] = {
                    "offset": field_o + parent_f_offset,
                    "kind": field_k,
                    "metadata": {
                        "base_kind": subtype["kind"],
                        "base_type": subtype.get("name", "")
                        }
                }
                continue

            # Resolve anonymous struct/union
            field_name = field_t.get("name", "")
            anonymous_struct = False
            for anon_prefix in ANONYMOUS_PREFIXES:
                if anon_prefix in field_name:
                    anonymous_struct = True
            
            if anonymous_struct:
    
                if parent_f_name:
                    if "unnamed_field_" not in field_n:
                        new_field_name = f"{parent_f_name}.{field_n}"
                    else:
                        new_field_name = parent_f_name
                else:
                    if "unnamed_field_" not in field_n:
                        new_field_name = field_n
                    else:
                        new_field_name = ""
                try:
                    flatted.update(self.flat_struct(self.raw_structs[field_t["name"]], new_field_name, field["offset"] + parent_f_offset))
                except KeyError:
                    pass # Sometimes certain anonymous structures are missing...
                continue
                        
            # Create field metadata (if needed)
            
            flatted[new_field_name] = {
                "offset": field["offset"] + parent_f_offset,
                "kind": "struct" if field_t["kind"] == "class" else field_t["kind"], # We convert class in structs (they have the same implementation)
                "metadata": {"base_type": field_t["name"]}
            }
            try:
                total_size = self.raw_structs[field_t["name"]]["size"]
                flatted[new_field_name]["metadata"]["total_size"] = total_size
            except KeyError as e:
                pass

        return flatted

    def extract_version(self, file_path):
        raise NotImplementedError

    def get_version(self):
        return  self.version_idx, self.major, self.minor, self.build

    @staticmethod
    def file_order(filename):
        raise NotImplementedError

    @staticmethod
    def beta_filter(filename):
        return True

    def type_has_same_size(self, l_type, r_type, right):
        try:
            return self.types[l_type]["size"] == right.types[r_type]["size"]
        except KeyError: # It is a composite type (struct or union)
            return l_type == r_type

    def __diff_structs_changed(self, commons, right):
        records = []
        # Changed structs/fields
        for struct_name in commons:
            left_s = self.structs[struct_name]
            right_s = right.structs[struct_name]

            common_fields = sorted(set(left_s["fields"].keys()).intersection(right_s["fields"].keys()))
            new_fields = sorted(set(right_s["fields"].keys()).difference(left_s["fields"].keys()))
            removed_fields = sorted(set(left_s["fields"].keys()).difference(right_s["fields"].keys()))

            # Change in structure metadata
            if left_s["size"] != right_s["size"]:
                records.append((
                    right.version_idx,
                    right.major,
                    right.minor,
                    right.build,
                    struct_name,
                    left_s["kind"], # struct, union, field
                    "change",  # change, addded, removed
                    "",    # name of the field changed, or empty if regards the entire struct
                    "s_size",  # what is changed
                    left_s["size"],
                    right_s["size"]
                ))

            # Change in structure kind
            if left_s["kind"] != right_s["kind"]:
                records.append((
                    right.version_idx,
                    right.major,
                    right.minor,
                    right.build,
                    struct_name,
                    left_s["kind"],
                    "change",
                    "",
                    "s_kind",
                    left_s["kind"],
                    right_s["kind"]
                ))

            # Add new fields
            for new_field in new_fields:
                records.append((
                    right.version_idx,
                    right.major,
                    right.minor,
                    right.build,
                    struct_name,
                    "field",
                    "added",
                    new_field,
                    "",
                    "",
                    right_s["fields"][new_field]["offset"]
                ))

            # Removed fields
            for removed_field in removed_fields:
                records.append((
                    right.version_idx,
                    right.major,
                    right.minor,
                    right.build,
                    struct_name,
                    "field",
                    "removed",
                    removed_field,
                    "",
                    left_s["fields"][removed_field]["offset"],
                    ""
                ))

            # Analyze differences in fields
            for common_field in common_fields:
                left_f = left_s["fields"][common_field]
                right_f = right_s["fields"][common_field]
                
                # Different offset
                if left_f["offset"] != right_f["offset"]:
                    records.append((
                        right.version_idx,
                        right.major,
                        right.minor,
                        right.build,
                        struct_name,
                        "field",
                        "change",
                        common_field,
                        "f_offset",
                        left_f["offset"],
                        right_f["offset"],
                    ))

                # Different kind
                if left_f["kind"] != right_f["kind"]:
                    records.append((
                        right.version_idx,
                        right.major,
                        right.minor,
                        right.build,
                        struct_name,
                        "field",
                        "change",
                        common_field,
                        "f_kind",
                        left_f["kind"],
                        right_f["kind"],
                    ))

                # Differences in metadata
                if "base_type" in left_f["metadata"] and "base_type" in right_f["metadata"]:
                    if left_f["metadata"]["base_type"] != right_f["metadata"]["base_type"]:

                        # Equivalent type (not pointer)
                        if left_f["kind"] != "pointer" and self.type_has_same_size(left_f["metadata"]["base_type"], right_f["metadata"]["base_type"], right):
                            continue

                        records.append((
                            right.version_idx,
                            right.major,
                            right.minor,
                            right.build,
                            struct_name,
                            "field",
                            "change",
                            common_field,
                            "f_type",
                            left_f["metadata"]["base_type"],
                            right_f["metadata"]["base_type"],
                        ))

                if "base_kind" in left_f["metadata"] and "base_kind" in right_f["metadata"]:
                    if left_f["metadata"]["base_kind"] != right_f["metadata"]["base_kind"]:
                        records.append((
                            right.version_idx,
                            right.major,
                            right.minor,
                            right.build,
                            struct_name,
                            "field",
                            "change",
                            common_field,
                            "f_kind",
                            left_f["metadata"]["base_kind"],
                            right_f["metadata"]["base_kind"],
                        ))

                if "total_size" in left_f["metadata"] and "total_size" in right_f["metadata"]:
                    if left_f["metadata"]["total_size"] != right_f["metadata"]["total_size"]:
                        records.append((
                            right.version_idx,
                            right.major,
                            right.minor,
                            right.build,
                            struct_name,
                            "field",
                            "change",
                            common_field,
                            "f_size",
                            left_f["metadata"]["total_size"],
                            right_f["metadata"]["total_size"],
                        ))

        return records

    def __diff_structs_add_rem(self, struct_names, op, right):
        records = []
        # New or deleted structures
        for struct_name in struct_names:

            if op == "added":
                records.append((
                    right.version_idx,
                    right.major,
                    right.minor,
                    right.build,
                    struct_name,
                    right.structs[struct_name]["kind"], # struct, union
                    "added",
                    "","","","" ))
            else:
                records.append((
                    self.version_idx,
                    self.major,
                    self.minor,
                    self.build,
                    struct_name,
                    self.structs[struct_name]["kind"], # struct, union
                    "removed",
                    "","","","" ))

        return records



    def __diff_structs(self, right):
        added = set(right.structs.keys()).difference(self.structs.keys())
        removed = set(self.structs.keys()).difference(right.structs.keys())
        commons = set(self.structs.keys()).intersection(right.structs.keys())

        results = []
        results = self.__diff_structs_changed(sorted(commons), right)
        results.extend(self.__diff_structs_add_rem(sorted(added), "added", right))
        results.extend(self.__diff_structs_add_rem(sorted(removed), "removed", right))

        return results


    def diff_structs(self, right):
        # Create diff results
        records = self.__diff_structs(right)
        records = list(set(records))
        records.sort(key=lambda x: x[2])
        return records

    def get_type_recursive(self, field):
        # Resolve the entire field path in case of pointer to pointer to pointer.. to obtain the real pointed type

        if field["kind"] in ("pointer", "array"):
            return self.get_type_recursive(field["subtype"])

        if field["kind"] in ("struct", "union"):
            if field["name"] not in self.structs: # Ignore structure that must not be parsed (size zero, anonymous etc.)
                return None
            return field["name"]
        else:
            return None

    def generate_stats(self, fields):
        # Generate statistics about single profile
        if self.stats and self.graphs:
            return self.stats
        
        stats = []
        graphs = {
            "nodes": [],
            "pointers": defaultdict(int),
            "embedded": defaultdict(int)
            }
        
        # Collect statistics on fields, and collect edges for graph
        for s_name, struct in self.structs.items():
            s_size = struct["size"]
            
            assert(s_size != 0)

            s_kind = struct["kind"]
            f_count = len(struct["fields"])

            f_struct_count = 0 # Number of embedded structs, unions or pointers and arrays
            f_union_count = 0
            f_pointer_count = 0
            f_array_count = 0
            
            for field_name, field in struct["fields"].items():
                field_k = field["kind"]

                if field_name not in fields[s_name]:
                    fields[s_name][field_name] = field_k

                # Ignore empty base type fields (they are pointer to functions for example)
                if field["metadata"]["base_type"] == "":
                    continue

                if field_k == "struct":
                    graphs["embedded"][(s_name, field["metadata"]["base_type"])] += 1
                    graphs["nodes"].append(s_name)
                    f_struct_count += 1

                elif field_k == "union":
                    if field["metadata"]["base_type"] not in self.types:
                        graphs["embedded"][(s_name, field["metadata"]["base_type"])] += 1
                        graphs["nodes"].append(s_name)
                    f_union_count += 1

                elif field_k == "pointer":
                    if field["metadata"]["base_type"] not in self.types:
                        graphs["pointers"][(s_name, field["metadata"]["base_type"])] += 1
                        graphs["nodes"].append(s_name)
                    f_pointer_count += 1

                elif field_k == "array":
                    if field["metadata"]["base_type"] not in self.types:
                        graphs["pointers"][(s_name, field["metadata"]["base_type"])] += 1
                        graphs["nodes"].append(s_name)
                    f_array_count += 1

                else:
                    # Ignore other types like base, enum, bitfield functions etc
                    continue

            stats.append((
                self.version_idx,
                self.major,
                self.minor,
                self.build,
                s_name,
                s_kind,
                s_size,
                f_count,
                f_struct_count,
                f_union_count,
                f_pointer_count,
                f_array_count
            ))

        graphs["nodes"] = set(graphs["nodes"])
        stats.sort(key=lambda x: x[2])
        self.stats = stats

        # Create graphs (embedded types)
        emb = ig.Graph.TupleList(((x,y,v) for (x,y),v in graphs["embedded"].items()),
                                 directed=True, weights=True)
        emb.add_vertices(list(graphs["nodes"].difference(emb.vs["name"])))
        emb["version_idx"] = self.version_idx
        emb["major"] = self.major
        emb["minor"] = self.minor
        emb["build"] = self.build

        # Create graph (pointers)
        ptrs = ig.Graph.TupleList(((x,y,v) for (x,y),v in graphs["pointers"].items()),
                                  directed=True, weights=True)
        ptrs.add_vertices(list(graphs["nodes"].difference(ptrs.vs["name"])))
        ptrs["version_idx"] = self.version_idx
        ptrs["major"] = self.major
        ptrs["minor"] = self.minor
        ptrs["build"] = self.build

        self.graphs = {
            "pointers": ptrs,
            "embedded": emb
        }
        return stats

    def records_to_csv(self, iterable):
        return ["|".join((str(i) for i in it_obj)) + "\n" for it_obj in iterable]

    def stats_to_csv(self, fields):
        stats = self.generate_stats(fields)
        return self.records_to_csv(stats)

    def diffs_to_csv(self, right):
        stats = self.diff_structs(right)
        return self.records_to_csv(stats)

    def symbols_to_csv(self):
        symbols_l = []
        for s_name, s_val in self.symbols.items():
            try:
                address = s_val["address"]
                if address == 0:
                    continue
                kind = s_val.get("type", {}).get("kind", "")
                symbols_l.append((self.version_idx, self.major, self.minor, self.build, s_name, kind, address))
            except:
                # Should not happens....
                continue
        return self.records_to_csv(symbols_l)

class XNU(OS):
    name = "xnu"

    def extract_version(self, file_path):
        filename_s = file_path.split("/")[-1].split("_")
        version_l = filename_s[2].split(".")
        if version_l[0] == '10':
            major = f"10.{version_l[1]}"
            minor = version_l[2]
        else:
            major = version_l[0]
            minor = version_l[1]

        build = filename_s[3].split("-")[-1].split(".")[0]

        return major, minor, build

    @staticmethod
    def file_order(filename):
        build = filename.split("/")[-1].split("-")[-1].split(".")[0]
        major = int(build[:2])
        minor = build[2]
        patch = build[3:]

        if patch[-1].isalpha():
            if patch[0] == "5" and len(patch[:-1]) > 3:
                patch1 = int(patch[1:-1])
            else:
                patch1 = int(patch[:-1])
            patch2 = patch[-1]
        else:
            patch1 = int(patch)
            patch2 = "z"

        return major, minor, patch1, patch2

    @staticmethod
    def beta_filter(filename):
        patch = filename.split("/")[-1].split("-")[-1].split(".")[0][3:]
        return not(patch[-1].isalpha())

class Windows(OS):
    name = "win"

    @staticmethod
    def file_order(filename):
        return [int(x) for x in filename.split("/")[-1].split(".")[:-2]]

    def extract_version(self, file_path):
        filename_s = file_path.split("/")[-1]
        M, m, minor, build = filename_s.split(".")[:4]
        if M == '5':
            major = 'XP' # XP
        elif M == '6':
            if m == '0': # Vista
                major = 'Vista'
            elif m == '1': # Win 7
                major = "7"
            elif m == '2': # Win 8
                major = '8'
            elif m == '3': # Win 8.1
                major = "8.1"
        elif M == '10':
            if int(minor) < 22000:
                major = "10"
            else:
                major = "11"

        return major, minor, build

class LNX(OS):
    name = "lnx"

    @staticmethod
    def file_order(filename):
        version = filename.split("/")[-1].split("_")[2].split("_")[0]
        major, minor, build = version.split(".")
        build, patch = build.split("-")
        patch_s = patch.split("+")

        return int(major), int(minor), int(build), *patch_s

    def extract_version(self, file_path):
        filename_s = file_path.split("/")[-1].split("_")[2]

        version_split = filename_s.split(".")
        if version_split[0] == '2':
            major = ".".join(version_split[:2])
            minor, build = version_split[2].split("-")
        else:
            major = version_split[0]
            minor = version_split[1]
            build = ".".join(version_split[2:])

        return major, minor, build

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-no-beta', action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-win', action='store_true')
    group.add_argument('-xnu', action='store_true')
    group.add_argument('-lnx', action='store_true')
    parser.add_argument('dataset', type=str, help='Dataset directory')
    args = parser.parse_args()

    dataset_dir = args.dataset
    output_dir = os.getcwd()
    fields = defaultdict(dict)

    # List all the files in the dataset directory and return ordered according to version
    file_paths = []
    for root, _, files in os.walk(dataset_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    if args.win:
        OS_CLASS = Windows
    elif args.xnu:
        OS_CLASS = XNU
    else:
        OS_CLASS = LNX

    if args.no_beta:
        file_paths = list(filter(OS_CLASS.beta_filter, file_paths))
    file_paths.sort(key=OS_CLASS.file_order)

    # Prepare output files
    with open(output_dir + f"/changes_{OS_CLASS.name}", "w") as changes_f, open(output_dir + f"/stats_{OS_CLASS.name}", "w") as stats_f, open(output_dir + f"/symbols_{OS_CLASS.name}", "w") as symbols_f:
        changes_f.write("vidx|major|minor|build|s_name|kind|difference|f_name|property|old_val|new_val\n")
        stats_f.write("vidx|major|minor|build|s_name|kind|size|fields|e_structs|e_union|pointers|arrays\n")
        symbols_f.write("vidx|major|minor|build|s_name|kind|address\n")

        ptrs = []
        emb = []

        # Parse the first profile
        left = OS_CLASS(file_paths[0], 0)
        stats_f.writelines(left.stats_to_csv(fields))
        symbols_f.writelines(left.symbols_to_csv())
        ptrs.append(left.graphs["pointers"])
        emb.append(left.graphs["embedded"])

        # Compare previous profile with current one and parse current one
        for version_idx, file_path in enumerate(tqdm(file_paths[1:]), start=1):
            right = OS_CLASS(file_path, version_idx)
            stats_f.writelines(right.stats_to_csv(fields))
            changes_f.writelines(left.diffs_to_csv(right))
            symbols_f.writelines(right.symbols_to_csv())

            ptrs.append(right.graphs["pointers"])
            emb.append(right.graphs["embedded"])

            left = right

    # Save graphs
    with open(output_dir + f"/ptrs_graph_{OS_CLASS.name}", "wb") as f:
        pickle.dump(ptrs, f)

    with open(output_dir + f"/emb_graph_{OS_CLASS.name}", "wb") as f:
        pickle.dump(emb, f)

    with open(output_dir + f"/fields_{OS_CLASS.name}.json", "w") as f:
        json.dump(fields, f)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import igraph
import pickle
import pandas as pd
import json
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.ticker as ticker

########################################### DEFINE LISTS OF VERSION NUMBERS, FORENSICS STRUCTURES ETC
lnx_tags = [["2.6.x", 0, 47], ["3.x", 47, 179], ["4.x", 179, 365], ["5.x", 365, 472], ["6.x", 472, None]]
xnu_tags = [['10.6', 0, 7], ['10.7', 7, 13], ['10.8', 13, 21], ['10.9', 21, 28], ['10.10', 28, 42], ['10.11', 42, 61], ['10.12', 61, 91], ['10.13', 91, 119], ['10.14', 119, 129], ['10.15', 129, 135], ['11', 135, 152], ['12', 152, 166], ['13', 166, 184], ['14', 184, None]]
win_tags = [['Vista', 0, 124], ['7', 124, 276], ['8', 276, 346], ['8.1', 346, 448], ['10', 448, 1460], ['11', 1460, None]]
tags = [lnx_tags, xnu_tags, win_tags]

os_names = ["Linux", "macOS", "Windows"]
proc_structs = [["task_struct"], ["proc"], ["_EPROCESS"]]

lnx_minors = [[0, 36], [36, 38], [38, 43], [43, 53], [53, 59], [59, 144], [144, 184], [184, 187], [187, 195], [195, 204], [204, 210], [210, 216], [216, 221], [221, 284], [284, 287], [287, 290], [290, 294], [294, 300], [300, 303], [303, 307], [307, 314], [314, 321], [321, 371], [371, 376], [375, 380], [380, 382], [382, 385], [385, 388], [388, 391], [391, 396], [396, 444], [444, 449], [449, 454], [454, 461], [461, 465], [465, 469], [469, 482], [482, 499], [499, 501], [501, 0]]
xnu_minors = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 12], [12, 13], [13, 14], [14, 16], [16, 17], [17, 18], [18, 21], [21, 22], [22, 24], [24, 25], [25, 26], [26, 28], [28, 29], [29, 30], [30, 31], [31, 33], [33, 42], [42, 43], [43, 44], [44, 45], [45, 46], [46, 47], [47, 48], [48, 61], [61, 62], [62, 63], [63, 64], [64, 65], [65, 66], [66, 67], [67, 91], [91, 92], [92, 93], [93, 94], [94, 96], [96, 97], [97, 119], [119, 121], [121, 122], [122, 123], [123, 124], [124, 125], [125, 129], [129, 130], [130, 131], [131, 135], [135, 138], [138, 139], [139, 143], [143, 144], [144, 145], [145, 147], [147, 151], [151, 152], [152, 153], [153, 154], [154, 156], [156, 158], [158, 159], [159, 162], [162, 164], [164, 166], [166, 168], [168, 169], [169, 170], [170, 172], [172, 174], [174, 177], [177, 184], [184, 185], [185, 191], [191, 193], [193, 0]]
win_minors = [[0, 124], [124, 276], [276, 346], [346, 448], [448, 570], [570, 605], [605, 757], [757, 845], [845, 938], [938, 1042], [1042, 1196], [1196, 1254], [1254, 1289], [1289, 1460], [1460, 1543], [1543, 0]]
minors = [lnx_minors, xnu_minors, win_minors]

forensics_sf = [
    { # LINUX
    'task_struct' : ['state', 'stack', 'usage', 'flags', 'ptrace', 'tasks', 'pushable_tasks', 'mm', 'active_mm', 'pid', 'tgid', 'stack_canary', 'parent', 'children', 'sibling', 'group_leader', 'cpu_timers', 'real_cred', 'replacement_session_keyring', 'comm'],
    'mm_struct' : ['mmap', 'mm_rb', 'mmap_cache', 'pgd', 'mm_users', 'mm_count', 'map_count', 'start_code', 'end_code', 'start_data', 'end_data', 'start_brk', 'brk', 'start_stack', 'arg_start', 'arg_end', 'env_start', 'env_end', 'ioctx_lock', 'ioctx_list', 'owner', 'exe_file', 'num_exe_file_vmas'],
    'vm_area_struct': ['vm_mm', 'vm_start', 'vm_end', 'vm_next', 'vm_prev', 'vm_page_prot', 'vm_flags', 'vm_rb', 'shared.linear.rb', 'shared.linear.rb_subtree_last', 'shared.nonlinear', 'shared.rb', 'shared.vm_set.head', 'shared.vm_set.list', 'shared.vm_set.parent', 'anon_vma_chain', 'anon_vma', 'vm_ops', 'vm_pgoff', 'vm_file', 'vm_private_data', 'vm_policy'],
    'file': ['f_path', 'f_op', 'f_lock', 'f_sb_list_cpu', 'f_count', 'f_flags', 'f_mode', 'f_pos', 'f_owner', 'f_cred', 'f_ra', 'f_version', 'f_security', 'private_data', 'f_ep_links', 'f_tfile_llink', 'f_mapping', 'f_u.fu_list', 'f_u.fu_llist', 'f_u.fu_rcuhead'],
    'address_space' : ['page_tree', 'a_ops', 'backing_dev_info'],
    'inet_sock': ['sk','pinet6', 'inet_dport','inet_num', 'inet_saddr', 'uc_ttl', 'cmsg_flags', 'inet_sport'],
    'sock_common': ['skc_daddr', 'skc_rcv_saddr', 'skc_family', 'skc_state', 'skc_prot'],
    'sk_buff' : ['next', 'len', 'head', 'data'],
    'rtable' : ['dst', 'rt_gateway', 'rt_dst'],
    'neighbour' : ['next', 'tbl', 'ha', 'dev' ],
    'resource' : ['start', 'end', 'name', 'sibling', 'child'],
    'sock': ["sk_socket", "sk_destruct"],
    'module' : ['name', 'list', 'kp', 'num_kp', 'module_init', 'init_size', 'module_core', 'core_size', 'sect_attrs', 'args', 'mkobj'],
    'vfsmount' : ['mnt_hash', 'mnt_parent', 'mnt_mountpoint', 'mnt_root', 'mnt_sb', 'mnt_devname'],
    'dentry' : ['d_parent', 'd_name', 'd_inode', 'd_sb', 'd_subdirs', 'd_u.d_alias', 'd_u.d_child', 'd_u.d_in_lookup_hash', 'd_u.d_rcu'],
    'file_system_type': ["name", "next"],
    'proto': ["name"],
    'inode' : ['i_mode', 'i_uid', 'i_gid', 'i_mapping', 'i_ino', 'i_mtime', 'i_atime', 'i_ctime', 'i_size'],
    'cred': ['uid', 'gid', 'euid', 'egid'],
    'tty_struct': ['dev', 'ldisc', 'name', 'session'],
    'seq_operations': ['start', 'stop', 'next', 'show'],
    'nf_hook_ops': ['list', 'hook', 'pf', 'hooknum'],
    'timespec': ["tv_sec"],
    'module_kobject': ["kobj"],
    'kmem_cache': ["list", "kmem_cache_node"],
    'path': ["mnt", "dentry"],
    'anon_vma': ["root"],
    'neigh_table': ["next"],
    'super_block': ["s_dev", ],
    },

    { # MACOS
    "proc": ["p_list.le_next", "p_list.le_prev", "p_pid", "task", "p_pptr", "p_uid", "p_gid", "p_sibling.le_next", "p_sibling.le_prev", "p_children.lh_first", "p_fd", "p_argslen", "p_argc", "p_comm", "p_name"],
    "task": ["map", "tasks", "threads", "bsd_info", "all_image_info_addr", "all_image_info_size"],
    "_vm_map": ["hdr", "pmap"],
    "vm_map_header": ["links", "nentries"],
    "vm_map_links": ["prev", "next", "start", "end"],
    "vm_map_entry": ["object", "offset"],
    "vm_map_object": ["sub_map", "vm_object"],
    "pmap": ["pm_task_map", "pm_cr3"],
    "dyld_all_image_infos": ["infoArray", "infoArrayCount"],
    "socket": ["so_state", "so_pcb", "so_proto"],
	"protosw": ["pr_protocol", "pr_domain"],
    "inpcb": ['inp_dependfaddr.inp46_foreign', 'inp_dependfaddr.inp6_foreign', 'inp_dependladdr.inp46_local', 'inp_dependladdr.inp6_local'],
    "zone": ["count", "elem_size", "sum_count", "zone_name"],
    "vnode": ["v_mntvnodes.tqe_next", "v_mntvnodes.tqe_prev", 'v_un.vu_fifoinfo', 'v_un.vu_mountedhere', 'v_un.vu_socket', 'v_un.vu_specinfo', 'v_un.vu_ubcinfo', "v_name", "v_parent"],
    "ubc_info": ["ui_pager", "ui_control"],
    "memory_object_control": ["moc_ikot", "moc_object"],
    "vm_object": ["memq"],
    "vm_page": ["next", "phys_page"],
    "mount": ["mnt_list"],
    "kmod_info": ["next", "name", "address", "size", "start", "stop"],
    "cpu_data_t" : ["rtclock_timer",  "cpu_active_thread"],
    "fileglob" : ["fg_ops", "fg_data"],
    "fileproc" : ["f_fglob"],
    "fs_event_watcher" : ["proc_name", "event_list", "pid"],
    "ifnet": ["if_name", "if_unit", "if_flags", "if_addrhead", 'if_link.tqe_next', 'if_link.tqe_prev', "if_lladdr"],
    "kauth_scope" : ["ks_link.tqe_next", "ks_identifier", "ks_idata"],
    "kmod_info_t" : ["address", "reference_count", "name", "next", "version"],
    "mac_policy_list_element": ["mpc"],
    "mac_policy_list" : ["entries"],
    "queue_entry" : ["next", "prev"],
    "session": ["s_leader", "s_login"],
    "sockaddr": ["sa_family"],
    "socket_filter": ["sf_filter", "sf_entry_head", "sf_global_next.tqe_next"],
    "sysctl_oid" : ["oid_name", "oid_arg1", "oid_handler", "oid_link.sle_next", "oid_number"],
    "thread" : ["next", "prev", "continuation", "state", "thread_group", "threads", "t_task", "thread_id", "sched_pri"],
    "ifnet": ["if_unit", "if_name", "if_flags"],
    "vnodeopv_desc": ["opv_desc_ops"]
    },
    
    { # WINDOWS
    "_FILE_OBJECT": [ "SectionObjectPointer", "FileName"],  
    "_SECTION_OBJECT_POINTERS": ["DataSectionObject", "ImageSectionObject", "SharedCacheMap",],
    "_CONTROL_AREA": ["Segment", "FilePointer"],
    "_SUBSECTION": ["ControlArea", "SubsectionBase", "PtesInSubsection", "NextSubsection"],
    "_SHARED_CACHE_MAP": ["SectionSize", "InitialVacbs", "Vacbs", "FileObjectFastRef"],
    "_VACB": ["BaseAddress", "SharedCacheMap", 'Overlay.ActiveCount', 'Overlay.FileOffset', 'Overlay.Links',],
    "_EPROCESS": ["ImageFileName", "UniqueProcessId", "InheritedFromUniqueProcessId", "Pcb", "CreateTime", "ExitTime", "ActiveProcessLinks", "SessionProcessLinks", "ObjectTable", "Token", "InheritedFromUniqueProcessId", "Session", "ThreadListHead", "ActiveThreads", "Peb", "VadRoot"],
    "_MMVAD" : ["StartingVpn", "Parent", "LeftChild", "RightChild"],
    "_MMPFN": ["PteAddress"],
    "_MM_SESSION_SPACE": ["SessionId", "ProcessList", "ImageList"],
    "_MM_AVL_TABLE": ["BalancedRoot"],
    "_MMADDRESS_NODE": ["StartingVpn", "EndingVpn", "LeftChild", "RightChild"],
    "_MMVAD_FLAGS": ['CommitCharge', 'DeleteInProgress'],
    "_SUBSECTION": ["ControlArea", "PtesInSubsection", "SubsectionBase", "NextSubsection", "StartingSector"],
    "_PEB": ["BeingDebugged", "ImageBaseAddress", "Ldr", "ProcessParameters", "ProcessHeap", "NumberOfHeaps", "ProcessHeaps"],
    "_RTL_USER_PROCESS_PARAMETERS": ["StandardInput", "StandardOutput", "StandardError", "CurrentDirectory", "ImagePathName", "CommandLine", "Environment"],
    "_PEB_LDR_DATA": ["InLoadOrderModuleList", "InMemoryOrderModuleList", "InInitializationOrderModuleList"],
    "_LDR_DATA_TABLE_ENTRY": ["DllBase", "EntryPoint", "SizeOfImage", "FullDllName", "BaseDllName", "LoadCount"],
    "_CMHIVE": ["Hive", "HiveList", "FileFullPath", "FileUserName", "HiveRootPath"],
    "_HHIVE": ["Signature", "BaseBlock", "Storage"],
    "_CM_KEY_NODE": ["SubKeyLists", "ValueList"],
    "_HANDLE_TABLE": ["TableCode", "QuotaProcess", "HandleTableList", "HandleCount"],
    "_HANDLE_TABLE_ENTRY": ["Object", "GrantedAccess"],
    "_KPROCESS": ["DirectoryTableBase"],
    "_OBJECT_SYMBOLIC_LINK": ["LinkTarget"],
    "_TOKEN": ["TokenId", "TokenSource", "AuthenticationId", "UserAndGroups", "RestrictedSids", "AuditPolicy", "SessionId", "UserAndGroupCount", "Privileges"],
    "_SID_AND_ATTRIBUTES": ['Attributes', 'Sid'],
    "_SID": ["Revision", "IdentifierAuthority", "SubAuthority"],
    "_SID_IDENTIFIER_AUTHORITY": ["Value"],
    "_LUID_AND_ATTRIBUTES": ["Luid", "Attributes"],
    "_SEP_TOKEN_PRIVILEGES": ["Present", "Enabled", "EnabledByDefault"],
    "_ETHREAD": ["Tcb", "ThreadName", "CrossThreadFlags", "StartAddress"],
    "_KMUTANT": ["Header"],
    "_DRIVER_OBJECT": ["DeviceObject", "DriverStart", "DriverSize", "DriverExtension", "DriverName", "DriverInit", "DriverUnload"],
    "_OBJECT_TYPE": ["Name", "TotalNumberOfObjects", "TotalNumberOfHandles", "TypeInfo", "Key"],
    "_OBJECT_HEADER": ["InfoMask", "PointerCount", "HandleCount", "TypeIndex", "SecurityDescriptor", "Body"],
    "_POOL_HEADER": ["BlockSize", "PoolIndex", "PoolTag"],
    "_POOL_TRACKER_TABLE": ["Key"],
    "_POOL_TRACKER_BIG_PAGES": ["Key", "PoolType", "NumberOfBytes"],
    "_DISPATCHER_HEADER": ["Inserted", "Type", "Size"],
    "_HEAP_ENTRY": ["Flags"],
    "_DRIVER_OBJECT": ["DeviceObject", "DriverStart", "DriverSize", "DriverExtension", "DriverName", "DriverInit", "DriverUnload"],
    "_DEVICE_OBJECT": ["DriverObject", "NextDevice", "AttachedDevice", "CurrentIrp", "DeviceExtension", "DeviceType"],
    "_KPCR": ["KdVersionBlock"],
    "_MM_SESSION_SPACE": ["SessionId", "ProcessList", "ImageList"],
    "_TEB" : ["NtTib"],
    "_KPRCB": ["CurrentPrcb"]
}]
forensics_structs = [set(forensics_sf[0].keys()), set(forensics_sf[1].keys()), set(forensics_sf[2].keys())]

####################################################################################

# Load datasets
print("Loading datasets...")
dataset = []
for kidx, k in enumerate(["lnx", "xnu", "win"]):
    dataset.append({})
    with open(f"./ptrs_graph_{k}", "rb") as f:
        dataset[-1]["gp"] = pickle.load(f)

    dataset[-1]["stats"] = pd.read_csv(f"./stats_{k}", sep="|",dtype={'major': str, 'minor': str, 'build': str})
    dataset[-1]["changes"] = pd.read_csv(f"./changes_{k}", sep="|",dtype={'major': str, 'minor': str, 'build': str})

    with open(f"./fields_{k}.json", "rb") as f:
        dataset[-1]["fields"] = json.load(f)

############################################ Print some simple statistics (Table 1)
print("\n")

total_fields = 0
total_versions = 0
for i in range(3):
    print(f"########## {os_names[i]} (Table 1) ############")

    l = int(dataset[i]["stats"]["vidx"].iloc[-1]) + 1
    total_versions += l
    print(f"Number of versions: {l}")
    
    
    m = ".".join(dataset[i]["stats"].iloc(0)[0][["major", "minor", "build"]].to_string(header=False, index=False).split('\n'))
    M = ".".join(dataset[i]["stats"].tail(1)[["major", "minor", "build"]].to_string(header=False, index=False).split('\n'))
    print(f"Minimum kernel version {m}")
    print(f"Maximum kernel version {M}")
    print(f"Number of forensics structs {len(forensics_structs[i])}")
    for k in forensics_sf[i].values():
        total_fields += len(k)

    # Percentage of versions without changes
    d = dataset[i]["changes"]
    changed_versions = len(set(d["vidx"]))

    filt = [(x, y) for x,v in forensics_sf[i].items() for y in v ]
    d = d[d[["s_name","f_name"]].apply(tuple, 1).isin(filt)]
    d = d[d["property"] == "f_offset"]

    changed_versions_forensics = len(set(d["vidx"]))
    print(f"Changed versions (percentage): {changed_versions/l * 100}")
    print(f"Changed versions due to offset shift (percentage): {changed_versions_forensics/l * 100}")    

print("\n")
print(f"Total forensics fields: {total_fields}")
print(f"Total versions: {total_versions}")


############################################## Figure 1
print("Plotting Figure 1... (output as PDF file)")
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

num_dtype = [] # Number of data types
for idx, profiles in enumerate(dataset):
    num_dtype.append([])
    for graph in profiles["gp"]:
        num_dtype[-1].append(len(graph.vs))

    axs[idx].plot(num_dtype[-1], ".", markersize=3)

    axs[idx].set_xlim(0, len(num_dtype[-1]))
    axs[idx].set_title(os_names[idx])

    axs[idx].set_title(os_names[idx])
    for i in tags[idx]:
        if i[2] is None:
            continue
        axs[idx].axvline(x=i[2], color='red', linestyle='--', alpha=0.5)
        axs[idx].set_xticks(list(zip(*tags[idx]))[1])
        axs[idx].set_xticklabels(list(zip(*tags[idx]))[0], rotation=90)

    d = dataset[idx]["changes"]
    
    all_mods = d.groupby(["vidx", "s_name"]).first().reset_index().groupby("vidx").count().reset_index()  # All versions with at least a structure modified per vidx
    total_structs = dataset[idx]["stats"].groupby(["vidx", "s_name"]).first().reset_index().groupby("vidx").count().reset_index() # All structures per vidx
    merged_df = pd.merge(all_mods[["vidx", "major"]], total_structs[["vidx", "minor"]], on='vidx')
    all_mods['percentage_changed'] = merged_df['major'] / merged_df['minor'] * 100

    ax2 = axs[idx].twinx()
    ax2.scatter(all_mods["vidx"], all_mods["percentage_changed"], marker="x", s=40, color="green")
    
    ax2.set_ylim(0, 50)
    ax2.set_yticks(range(0,51,5))
   
    tags_vidx = [x[2] for x in tags[idx] if x[2] is not None]

    for i in tags[idx]:
        if i[2] is None:
            continue
        ax2.axvline(x=i[2], color='black', linestyle='--', alpha=0.5)

    axs[0].set_ylabel('Number of data types')
    
    # Plot ticks
    if idx < 2:
        ax2.set_xticks(list(zip(*tags[idx]))[1])
        ax2.set_xticklabels(list(zip(*tags[idx]))[0], rotation=90)
    else:  
        tags_vidx.extend([x[1] for x in win_minors if x[1] is not None])
        for i in win_minors:
            if i[1] is None:
                continue
            ax2.axvline(x=i[1], color='grey', linestyle='--', alpha=0.3)
        
        ax2.set_xticklabels(list(list(zip(*tags[idx]))[0]), rotation=90)
        ticks = list(zip(*tags[idx]))[1] + list(zip(*win_minors))[1]
        ax2.set_xticks(ticks)
        ax2.set_ylabel('Percentage of data types changed')

plt.tight_layout()
plt.savefig("figure1.pdf")

############################################################## Table 2
print("\n")
matrix = []
tchange = ["added", "removed", "kind", "type", "size", "offset"]
kinds = ["base", "pointer", "array", "bitfield", "struct", "union"]
for idx in  range(0,3):
    print(f"########## {os_names[idx]} (Table 2) ############")
    columns = {
        "added" : defaultdict(int),
        "removed" : defaultdict(int),
        "offset" : defaultdict(int),
        "type" : defaultdict(int),
        "size" : defaultdict(int),
        "kind" : defaultdict(int)
    }
    
    c = dataset[idx]["changes"]
    c = c[(c["kind"] == "field")]
    
    print(f"Total number of changes {len(c)}")
    
    c = c[(c["s_name"].isin(forensics_structs[idx]))]
    filt = [(x, y) for x,v in forensics_sf[idx].items() for y in v ]
    c = c[c[["s_name","f_name"]].apply(tuple, 1).isin(filt)]
    
    cc = c[(c["difference"] == "change")]
    print(f"Total number of changes in forensic fields {len(c)}")

    # Collect different types of changes for each kind
    df = dataset[idx]["fields"]
    for _, row  in c[(c["difference"] == "added")][["s_name","f_name"]].groupby(["s_name","f_name"]).size().reset_index().iterrows():
        try:
            columns["added"][df[row["s_name"]][row["f_name"]]] += row[0]
        except KeyError:
            continue

    for _, row  in c[(c["difference"] == "removed")][["s_name","f_name"]].groupby(["s_name","f_name"]).size().reset_index().iterrows():
        try:
            columns["removed"][df[row["s_name"]][row["f_name"]]] += row[0]
        except KeyError:
            continue

    for _, row  in cc[(cc["property"] == "f_offset")][["s_name","f_name"]].groupby(["s_name","f_name"]).size().reset_index().iterrows():
        try:
            columns["offset"][df[row["s_name"]][row["f_name"]]] += row[0]
        except KeyError:
            continue

    for _, row  in cc[(cc["property"] == "f_type")][["s_name","f_name"]].groupby(["s_name","f_name"]).size().reset_index().iterrows():
        try:
            columns["type"][df[row["s_name"]][row["f_name"]]] += row[0]
        except KeyError:
            continue

    for _, row  in cc[(cc["property"] == "f_size")][["s_name","f_name"]].groupby(["s_name","f_name"]).size().reset_index().iterrows():
        try:
            columns["size"][df[row["s_name"]][row["f_name"]]] += row[0]
        except KeyError:
            continue

    for _, row  in cc[(cc["property"] == "f_kind")][["s_name","f_name"]].groupby(["s_name","f_name"]).size().reset_index().iterrows():
        try:
            columns["kind"][df[row["s_name"]][row["f_name"]]] += row[0]
        except KeyError:
            continue
    
    # Reorganize data to be put in a Dataframe
    res = {}
    for c in tchange:
        res[c] = []
        for r in kinds:
            try:
                res[c].append(columns[c][r])
            except:
                res[c].append(0)
    matrix.append(pd.DataFrame(res))

    # Get percentages and round up
    matrix[-1] = matrix[-1] / (matrix[-1].sum().sum()) * 100
    matrix[-1]["field_kind"] = kinds
    m = matrix[-1].round(2)

    m = m[["field_kind", "added", "removed", "kind", "type", "size", "offset"]]
    
    # Create the Total row
    new_row = ["Total", 
               m.loc[[0,1,4]]["added"].sum(),
               m.loc[[0,1,4]]["removed"].sum(),
               m.loc[[0,1,4]]["kind"].sum(),
               m.loc[[0,1,4]]["type"].sum(),
               m.loc[[0,1,4]]["size"].sum(),
               m.loc[[0,1,4]]["offset"].sum()
              ]
    m.loc[len(m)] = new_row
    m["properties"] = m["kind"] + m["type"] + m["size"] # Aggregate changes of different field properties

    # Get only rows and columns to be printed
    m = m.loc[[0,1,4,6]]
    m = m[["field_kind", "added", "removed", "properties", "offset"]]
    
    print(m.to_latex())


############################################################## Section 3.2.1
print("\n")

matrix_adds = []
matrix_change = []
for idx in  range(0,3):
    c = dataset[idx]["changes"]
    c = c[(c["s_name"].isin(forensics_structs[idx])) & (c["kind"] == "field") & (c["difference"] == "added")]

    s = dataset[idx]["stats"]
    s = s[s["s_name"].isin(forensics_structs[idx])]
    
    # To calculate how many fields are NOT added at the end of a structure we calculate the percentage of fields inserted in the structure at version change
    total = len(c)
    count = 0
    for _, row in c.iterrows():
        try:
            old_size = s[(s["vidx"] == int(row["vidx"])-1) & (s["s_name"] == row["s_name"])]["size"].iloc[0]
        except Exception as e:
            continue
        new_offset =  row["new_val"]
        count += int(int(new_offset) < old_size)

    matrix_adds.append(count/total * 100)
    print(f"########## {os_names[idx]} (Section 3.2.1) Percentage of fields added between other fields {matrix_adds[-1]}" )



#################################################################### Figure 2
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
print("\n")
print("Plotting Figure 2... (output as PDF file)")

for idx, i in enumerate(dataset):

    d = dataset[idx]["changes"]
    d = d[(d["s_name"].isin(forensics_structs[idx])) & (d["kind"] == "field") & (d["property"] == "f_offset")]
    filt = [(x, y) for x,v in forensics_sf[idx].items() for y in v]
    d = d[d[["s_name","f_name"]].apply(tuple, 1).isin(filt)]
    
    all_mods = d.groupby(["vidx", "s_name"]).first().reset_index().groupby("vidx").count().reset_index() # Forensics modified types per version
    total_structs = dataset[idx]["stats"][dataset[idx]["stats"]["s_name"].isin(forensics_structs[idx])].groupby(["vidx", "s_name"]).first().reset_index().groupby("vidx").count().reset_index() # Total number of forensics type per version (some of them are not present in early kernel releases)
    merged_df = pd.merge(all_mods[["vidx", "major"]], total_structs[["vidx", "minor"]], on='vidx')
    all_mods['percentage_changed'] = merged_df['major'] / merged_df['minor'] * 100

    # Divide them in major, minor, patches
    majors_v = all_mods[all_mods["vidx"].isin(list(zip(*tags[idx]))[1])]
    minors_v = all_mods[all_mods["vidx"].isin(list(zip(*minors[idx]))[1]) & (~all_mods["vidx"].isin(list(zip(*tags[idx]))[1]))]
    patches_v = all_mods[(~all_mods["vidx"].isin(list(zip(*minors[idx]))[1])) & (~all_mods["vidx"].isin(list(zip(*tags[idx]))[1]))]

    # Print numeric percentage percentage
    total = majors_v["percentage_changed"].sum() + minors_v["percentage_changed"].sum() + patches_v["percentage_changed"].sum()
    print(f'######## Section 3.2.2 {os_names[idx]}: Percentage of changes in major releases {majors_v["percentage_changed"].sum() / total * 100}')
    print(f'######## Section 3.2.2 {os_names[idx]}: Percentage of changes in minor releases {minors_v["percentage_changed"].sum() / total * 100}')
    print(f'######## Section 3.2.2 {os_names[idx]}: Percentage of changes in patch releases {patches_v["percentage_changed"].sum() / total * 100}')
    print("\n")
    
    # Plot them
    axs[idx].scatter(patches_v["vidx"], patches_v["percentage_changed"], marker=".", s=40, color="red")
    axs[idx].scatter(minors_v["vidx"], minors_v["percentage_changed"], marker="^", s=40, color="green")
    axs[idx].scatter(majors_v["vidx"], majors_v["percentage_changed"], marker="x", s=60)

    axs[idx].set_title(os_names[idx])
    axs[idx].set_ylim(0, 40)
    axs[idx].set_xlim(0,  dataset[idx]["stats"]["vidx"].max())
    axs[idx].set_yticks(range(0,41,5))
   
    tags_vidx = [x[2] for x in tags[idx] if x[2] is not None]
    axs[idx].yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))

    # Plot ticks
    for i in tags[idx]:
        if i[2] is None:
            continue
        axs[idx].axvline(x=i[2], color='black', linestyle='--', alpha=0.5)
    if idx < 2:
        axs[idx].set_xticks(list(zip(*tags[idx]))[1])
        axs[idx].set_xticklabels(list(zip(*tags[idx]))[0], rotation=90)
    else:  
        tags_vidx.extend([x[1] for x in win_minors if x[1] is not None])
        for i in win_minors:
            if i[1] is None:
                continue
            axs[idx].axvline(x=i[1], color='grey', linestyle='--', alpha=0.3)

        ticks = list(zip(*tags[idx]))[1]
        axs[idx].set_xticks(ticks)
        axs[idx].set_xticklabels(list(zip(*tags[idx]))[0], rotation=90)
       
axs[0].set_ylabel("Percentage of forensics data types modified")

plt.tight_layout()
plt.savefig("figure2.pdf")

##################################################################### Table 3 and Table 4
print("\n")
for idx, i in enumerate(dataset):
    d = dataset[idx]["changes"]
    d = d[(d["s_name"].isin(forensics_structs[idx])) & (d["property"] == "f_offset")]
    filt = [(x, y) for x,v in forensics_sf[idx].items() for y in v ]
    d = d[d[["s_name","f_name"]].apply(tuple, 1).isin(filt)]

    k = d[["s_name","f_name"]].groupby(["s_name","f_name"]).size().reset_index() # Count the total number of modification by structure and field
    print(f"######### Table 3 {os_names[idx]} #########")
    t3 = k[["s_name", 0]].groupby("s_name").sum().reset_index().sort_values(0, ascending=False).head(5).to_latex() # Collect by type name
    print(t3)
    print("\n")

    print(f"######### Table 4 {os_names[idx]} #########")
    t4 = k.sort_values([0, "s_name"], ascending=False).head(10).to_latex()
    print(t4)

    

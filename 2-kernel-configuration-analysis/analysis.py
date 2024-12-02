#!/usr/bin/env python3

# import pickle
from collections import defaultdict
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np

########################################### DEFINE LISTS OF VERSION NUMBERS, FORENSICS STRUCTURES ETC
lnx_tags = [["2.6.x", 20, 28], ["3.x", 28, 48], ["4.x", 48, 69], ["5.x", 69, 89], ["6.x", 89, None]]

linux_sf = { # LINUX
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
    }
linux_structs = set(linux_sf.keys())

config_to_group = {
    'CONFIG_LOCK_STAT': 'Kernel hacking',
    'CONFIG_DEBUG_LOCK_ALLOC': 'Kernel hacking',
    'CONFIG_LOCKDEP': 'Kernel hacking',
    'CONFIG_DEBUG_MUTEXES': 'Kernel hacking',
    'CONFIG_TRACING': 'Kernel hacking',
    'CONFIG_DEBUG_RWSEMS': 'Kernel hacking',
    'CONFIG_DEBUG_KOBJECT_RELEASE': 'Kernel hacking',
    'CONFIG_TRACE_IRQFLAGS': 'Kernel hacking',
    'CONFIG_FTRACE_MCOUNT_RECORD': 'Kernel hacking',
    'CONFIG_FUNCTION_GRAPH_TRACER': 'Kernel hacking',
    'CONFIG_SCHEDSTATS': 'Kernel hacking',
    'CONFIG_FAULT_INJECTION': 'Kernel hacking',
    'CONFIG_LATENCYTOP': 'Kernel hacking',
    'CONFIG_BLK_DEV_IO_TRACE': 'Kernel hacking',
    'CONFIG_EVENT_TRACING': 'Kernel hacking',
    'CONFIG_DETECT_HUNG_TASK': 'Kernel hacking',
    'CONFIG_DEBUG_CREDENTIALS': 'Kernel hacking',
    'CONFIG_UNUSED_SYMBOLS': 'Kernel hacking',
    'CONFIG_DEBUG_PREEMPT': 'Kernel hacking',
    'CONFIG_DEBUG_ATOMIC_SLEEP': 'Kernel hacking',
    'CONFIG_SCHED_INFO': 'Kernel hacking',
    'CONFIG_UBSAN': 'Kernel hacking',
    'CONFIG_KCOV': 'Kernel hacking',
    'CONFIG_FUNCTION_ERROR_INJECTION': 'Kernel hacking',
    'CONFIG_KASAN': 'Kernel hacking',
    'CONFIG_BPF_EVENTS': 'Kernel hacking',
    'CONFIG_KUNIT': 'Kernel hacking',
    'CONFIG_KCSAN': 'Kernel hacking',
    'CONFIG_UBSAN_TRAP': 'Kernel hacking',
    'CONFIG_DEBUG_INFO_BTF_MODULES': 'Kernel hacking',
    'CONFIG_PAGE_OWNER': 'Kernel hacking',
    'CONFIG_STACKTRACE_BUILD_ID': 'Kernel hacking',
    'CONFIG_KCSAN_WEAK_MEMORY': 'Kernel hacking',
    'CONFIG_RETHOOK': 'Kernel hacking',
    'CONFIG_DEBUG_PI_LIST': 'Kernel hacking',
    'CONFIG_RV': 'Kernel hacking',
    'CONFIG_KMSAN': 'Kernel hacking',
    'CONFIG_SHRINKER_DEBUG': 'Kernel hacking',
    'CONFIG_DYNAMIC_DEBUG_CORE': 'Kernel hacking',
    'CONFIG_USER_EVENTS': 'Kernel hacking',
    'CONFIG_MMU_NOTIFIER': 'Memory Management options',
    'CONFIG_TRANSPARENT_HUGEPAGE': 'Memory Management options',
    'CONFIG_COMPAT_BRK': 'Memory Management options',
    'CONFIG_READ_ONLY_THP_FOR_FS': 'Memory Management options',
    'CONFIG_COMPACTION': 'Memory Management options',
    'CONFIG_SWAP': 'Memory Management options',
    'CONFIG_KMAP_LOCAL': 'Memory Management options',
    'CONFIG_KSM': 'Memory Management options',
    'CONFIG_LRU_GEN': 'Memory Management options',
    'CONFIG_HMM': 'Memory Management options',
    'CONFIG_NUMA_BALANCING': 'Memory Management options',
    'CONFIG_PER_VMA_LOCK': 'Memory Management options',
    'CONFIG_ANON_VMA_NAME': 'Memory Management options',
    'CONFIG_SLAB_FREELIST_RANDOM': 'Memory Management options',
    'CONFIG_SLUB_CPU_PARTIAL': 'Memory Management options',
    'CONFIG_SLUB_TINY': 'Memory Management options',
    'CONFIG_SLAB_FREELIST_HARDENED': 'Memory Management options',
    'CONFIG_MIGRATION': 'Memory Management options',
    'CONFIG_HMM_MIRROR': 'Memory Management options',
    'CONFIG_UPROBES': 'General architecture-dependent options',
    'CONFIG_VMAP_STACK': 'General architecture-dependent options',
    'CONFIG_ARCH_HAS_SCALED_CPUTIME': 'General architecture-dependent options',
    'CONFIG_HAVE_ARCH_COMPAT_MMAP_BASES': 'General architecture-dependent options',
    'CONFIG_STACKPROTECTOR': 'General architecture-dependent options',
    'CONFIG_JUMP_LABEL': 'General architecture-dependent options',
    'CONFIG_KPROBES': 'General architecture-dependent options',
    'CONFIG_HAVE_STATIC_CALL_INLINE': 'General architecture-dependent options',
    'CONFIG_KRETPROBES': 'General architecture-dependent options',
    'CONFIG_ARCH_HAS_PARANOID_L1D_FLUSH': 'General architecture-dependent options',
    'CONFIG_HAVE_HW_BREAKPOINT': 'General architecture-dependent options',
    'CONFIG_CFI_CLANG': 'General architecture-dependent options',
    'CONFIG_ARCH_USES_CFI_TRAPS': 'General architecture-dependent options',
    'CONFIG_ARCH_WANTS_MODULES_DATA_IN_VMALLOC': 'General architecture-dependent options',
    'CONFIG_SMP': 'Processor type and features',
    'CONFIG_NUMA': 'Processor type and features',
    'CONFIG_LIVEPATCH': 'Processor type and features',
    'CONFIG_VM86': 'Processor type and features',
    'CONFIG_X86_CPU_RESCTRL': 'Processor type and features',
    'CONFIG_HOTPLUG_CPU': 'Processor type and features',
    'CONFIG_X86_MCE': 'Processor type and features',
    'CONFIG_VIRT_CPU_ACCOUNTING': 'Processor type and features',
    'CONFIG_X86_INTEL_MPX': 'Processor type and features',
    'CONFIG_CPU_SUP_INTEL': 'Processor type and features',
    'CONFIG_INTEL_RDT': 'Processor type and features',
    'CONFIG_INTEL_RDT_A': 'Processor type and features',
    'CONFIG_X86_USER_SHADOW_STACK': 'Processor type and features',
    'CONFIG_FSNOTIFY': 'File systems',
    'CONFIG_PROC_FS': 'File systems',
    'CONFIG_FS_POSIX_ACL': 'File systems',
    'CONFIG_FS_ENCRYPTION': 'File systems',
    'CONFIG_SYSFS': 'File systems',
    'CONFIG_FS_VERITY': 'File systems',
    'CONFIG_HUGETLB_PAGE': 'File systems',
    'CONFIG_QUOTA': 'File systems',
    'CONFIG_FILE_LOCKING': 'File systems',
    'CONFIG_UNICODE': 'File systems',
    'CONFIG_INOTIFY': 'File systems',
    'CONFIG_IPV6': 'Networking support',
    'CONFIG_XFRM': 'Networking support',
    'CONFIG_NET_NS': 'Networking support',
    'CONFIG_IP_ROUTE_CLASSID': 'Networking support',
    'CONFIG_SOCK_RX_QUEUE_MAPPING': 'Networking support',
    'CONFIG_XPS': 'Networking support',
    'CONFIG_MPTCP': 'Networking support',
    'CONFIG_NET_CLS_ROUTE': 'Networking support',
    'CONFIG_SECURITY': 'Security options',
    'CONFIG_KEYS': 'Security options',
    'CONFIG_IMA': 'Security options',
    'CONFIG_GCC_PLUGIN_STACKLEAK': 'Security options',
    'CONFIG_HARDENED_USERCOPY': 'Security options',
    'CONFIG_BCACHE': 'Device Drivers',
    'CONFIG_IOMMU_SVA': 'Device Drivers',
    'CONFIG_IOMMU_SUPPORT': 'Device Drivers',
    'CONFIG_BLOCK': 'Enable the block layer',
    'CONFIG_BLK_CGROUP': 'Enable the block layer',
    'CONFIG_CPUMASK_OFFSTACK': 'Library routines',
    'CONFIG_CMPXCHG_LOCKREF': 'Library routines',
    'CONFIG_COMPAT': 'Binary Emulations',
    'CONFIG_TIMER_STATS': 'Collect kernel timers statistics',
    'CONFIG_PREEMPT_NOTIFIERS': 'Preemptible RCU',
    'CONFIG_PREEMPT_RCU': 'Preemptible RCU',
    "CONFIG_TREE_SRCU": "Preemptible RCU",
    "CONFIG_TREE_PREEMPT_RCU": "Preemptible RCU",
    "CONFIG_TASKS_RCU": "Preemptible RCU",
    "CONFIG_TASKS_TRACE_RCU": "Preemptible RCU",
    "CONFIG_RCU_BOOST": "Preemptible RCU",
    'CONFIG_SLOB': 'SLOB (Simple Allocator)',
    'CONFIG_PREEMPT_RT': 'Fully Preemptible Kernel (Real-Time)',
    'CONFIG_DEBUG_WRITECOUNT': 'Debug filesystem writers count',
    'CONFIG_KASAN_GENERIC': 'Generic KASAN',
    'CONFIG_KASAN_SW_TAGS': 'Software Tag-Based KASAN',
    'CONFIG_SCHED_CORE': 'Core Scheduling for SMT',
    'CONFIG_LOCKDEP_CROSSRELEASE': 'Lock Debugging (spinlocks, mutexes, etc...)',
    'CONFIG_MEMCG': "Cgroups",
    'CONFIG_CPUSETS': "Cgroups",
    'CONFIG_CGROUPS': "Cgroups",
    'CONFIG_FAIR_GROUP_SCHED': "Cgroups",
    'CONFIG_CGROUP_SCHED': "Cgroups",
    'CONFIG_RT_GROUP_SCHED': "Cgroups",
    'CONFIG_MEMCG_KMEM': "Cgroups",
    'CONFIG_IO_URING': 'General Setup',
    'CONFIG_POSIX_TIMERS': 'General Setup',
    'CONFIG_EVENTFD': 'General Setup',
    'CONFIG_MEMBARRIER': 'General Setup',
    'CONFIG_EPOLL': 'General Setup',
    'CONFIG_AIO': 'General Setup',
    'CONFIG_FUTEX': 'General Setup',
    'CONFIG_KALLSYMS': 'General Setup',
    "CONFIG_RT_MUTEXES": 'General Setup',
    "CONFIG_BPF_SYSCALL": 'General Setup',
    "CONFIG_UCLAMP_TASK": "General Setup",
    "CONFIG_POSIX_CPU_TIMERS_TASK_WORK": "General Setup",
    "CONFIG_SCHED_MM_CID": "General Setup",
    "CONFIG_RSEQ": "General Setup",
    "CONFIG_AUDIT": "General Setup",
    "CONFIG_THREAD_INFO_IN_TASK": "General Setup",
    'CONFIG_TASK_XACCT': "CPU config",
    'CONFIG_TASK_IO_ACCOUNTING': "CPU config",
    'CONFIG_TASK_DELAY_ACCT': "CPU config",
    'CONFIG_VIRT_CPU_ACCOUNTING_GEN': "CPU config",
    'CONFIG_VIRT_CPU_ACCOUNTING_NATIVE': "CPU config",
    "CONFIG_MODULE_SIG": "Security options",
    "CONFIG_IPV6_MODULE": 'Networking support',
    "CONFIG_PERF_EVENTS": "Kernel Performance Events And Counters",
    "CONFIG_PSI": "Kernel Performance Events And Counters",
    "CONFIG_CGROUP_MEM_RES_CTLR_KMEM": "Cgroups",
    "CONFIG_CGROUP_MEM_RES_CTLR": "Cgroups",
    "CONFIG_CGROUP_WRITEBACK": "Cgroups",


 }

option_ignore = { # OPTION ALWAYS ON/OFF on modern cpus or COMPILE DIRECTIVES
    "CONFIG_MMU", "CONFIG_RWSEM_SPIN_ON_OWNER", "CONFIG_MUTEX_SPIN_ON_OWNER", "CONFIG_X86_64", 
    "CONFIG_CC_STACKPROTECTOR", "CONFIG_GENERIC_BUG", 'CONFIG_PGTABLE_LEVELS',
    "CONFIG_GENERIC_HARDIRQS", "CONFIG_64BIT", "CONFIG_SMP", "CONFIG_ARCH_WANT_BATCHED_UNMAP_TLB_FLUSH", "CONFIG_TRACEPOINTS",
    "CONFIG_MODULE_UNLOAD", "CONFIG_SYSVIPC", "CONFIG_CONSTRUCTORS", "CONFIG_AUDITSYSCALL", "CONFIG_BCACHE_MODULE",
    "CONFIG_PRINTK_INDEX", "CONFIG_GENERIC_HARDIRQS", "CONFIG_MM_OWNER",
    "CONFIG_NO_HZ_FULL", "CONFIG_MODULES_TREE_LOOKUP", "CONFIG_PGTABLE_LEVELS", "CONFIG_X86_32"
}


####################################################################################

# Load datasets
print("Loading datasets...")
dataset = {}
dataset["global_stats"] = pd.read_csv("./3-parser-result-analysis/output/run_1/04-global-statistics/global_statistics.txt", sep=r"\s+")
dataset["stats"] = pd.read_csv("./3-parser-result-analysis/output/run_1/05-stats-csv/structs.csv", sep="|")
dataset["ifdef"] = pd.read_csv("./3-parser-result-analysis/output/run_1/05-stats-csv/struct_ifdef_result.csv", sep="|")

# Filter very old versions to syncronize with debian profiles in the first part of the paper
dataset["stats"] = dataset["stats"][dataset["stats"]["vidx"] >= 20]
dataset["ifdef"] = dataset["ifdef"][dataset["ifdef"]["vidx"] >= 20]
dataset["global_stats"] = dataset["global_stats"].iloc[20:]
dataset["global_stats"]["parsed_p"] = dataset["global_stats"]["parsed"] / dataset["global_stats"]["total"] * 100

dataset["ifdef"] = dataset["ifdef"][dataset["ifdef"]["condition"].notna()]
dataset["ifdef"] = dataset["ifdef"][dataset["ifdef"]["condition"].str.startswith("CONFIG_")]


####################################### Percentage parsed structures
m = dataset["global_stats"]["parsed_p"].mean()
print(f"######## Section 4   Percentage of correct type parsed {m}")

####################################### Figure 3
print("Plotting Figure 3... (output as PDF file)")
max_vidx = int(dataset["ifdef"]["vidx"].max()) # Total number of versions

axs = plt.gca()

e = dataset["stats"]
s = e.groupby("vidx").size().reset_index(name="total")
total = np.array(s["total"]) #  Total data types per version

d = dataset["ifdef"]
t = d.groupby(["vidx", "s_name"]).first().groupby("vidx").size().reset_index(name="total")
influenced = np.array(t["total"])  # Total number of structure per version depending from at least one #IFDEF
ratio = influenced/total * 100 # Percentage

# Plot!
axs.plot(t["vidx"][:42], ratio[:42], "--", color="blue")
axs.plot(t["vidx"][43:], ratio[43:], "--", color="blue")

axs.scatter(t["vidx"][:3], ratio[:3], marker=".", color="blue", s=80)
axs.scatter(t["vidx"][4:7], ratio[4:7], marker=".", color="blue", s=80)
axs.scatter(t["vidx"][8:42], ratio[8:42], marker=".", color="blue", s=80)
axs.scatter(t["vidx"][43:], ratio[43:], marker=".", color="blue", s=80)

# Ticks
for i in lnx_tags:
    if i[2] is None:
        continue
    axs.axvline(x=i[2], color='black', linestyle='--', alpha=0.5)
    axs.set_xticks(list(zip(*lnx_tags))[1])
    axs.set_xticklabels(list(zip(*lnx_tags))[0], rotation=90)

axs.scatter(23, ratio[3], marker="x", s=150, color="green")
axs.scatter(27, ratio[7], marker="x", s=150, color="green")
axs.scatter(62, ratio[42], marker=".", s=200, color="red")

axs.set_ylabel('Percentage of data types\naffected by CONFIG_* options')
axs.set_xlim(19, max_vidx+1)
axs.set_yticks(np.arange(9, 11.26, 0.25))

plt.tight_layout()
plt.savefig("figure3.pdf")

######################################## Figure 4
print("Plotting Figure 4... (output as PDF file)")
plt.clf()
axs = plt.gca()
d = dataset["ifdef"]
vidx = np.array(sorted(set(d["vidx"])))
count = np.array(d[["vidx","condition"]].groupby("vidx").agg(lambda x: len(set(x)))["condition"].reset_index(name="count")["count"]) # Total number of single options per version

axs.scatter(vidx, count, marker=".", color="blue")

pfor =  np.array(d[d["s_name"].isin(linux_sf)][["vidx","condition"]].groupby("vidx").agg(lambda x: len(set(x)))["condition"].reset_index(name="count")["count"]) # Total number of single option only in forensics per version
ratio = pfor/count * 100

ax2 = axs.twinx()
ax2.scatter(vidx, ratio, marker="x", color="red")

# Fits
coefficients = np.polyfit(vidx, count, 1)
slope, intercept = coefficients
axs.plot(vidx, slope * vidx + intercept, "--", color="blue", alpha=0.3)

coefficients = np.polyfit(vidx[:28], ratio[:28], 1)
slope, intercept = coefficients
ax2.plot(vidx[:28], slope * vidx[:28] + intercept, "--", color="red", alpha=0.3)

coefficients = np.polyfit(vidx[28:], ratio[28:], 1)
slope, intercept = coefficients
ax2.plot(vidx[28:], slope * vidx[28:] + intercept, "--", color="red", alpha=0.3)

# Ticks
for i in lnx_tags:
    if i[2] is None:
        continue
    axs.axvline(x=i[2], color='black', linestyle='--', alpha=0.5)
    axs.set_xticks(list(zip(*lnx_tags))[1])
    axs.set_xticklabels(list(zip(*lnx_tags))[0], rotation=90)

axs.set_ylabel('Total number of unique CONFIG_* options')
ax2.set_ylabel('Percentage of CONFIG_* options\nafftecting forensics types')


plt.tight_layout()
plt.savefig("figure4.pdf")

# ####################################### Table 5 and Table 6
print("\n")
d = dataset["ifdef"]
c = d[d["s_name"].isin(linux_structs)].groupby("condition").size().reset_index(name="count")
config_count = dict(c.sort_values("count", ascending=False).values.tolist())

print("##### Table 5")
collect_by_group = defaultdict(int)
for config_name, count in config_count.items():
    if config_name in option_ignore:
        continue
    try:
        collect_by_group[config_to_group[config_name]] += count
    except:
        print(config_name)
        pass

for i in sorted(collect_by_group.items(), key=lambda x: x[1] , reverse=True)[:10]:
    print(i)

print("\n")
print("##### Table 6")
count = 0
for k,v in sorted(config_count.items(), key=lambda x: x[1] , reverse=True):
    if k in option_ignore:
        continue
    group = config_to_group[k]
    if group == "Kernel hacking":
        continue
    count += 1
    print(k, config_to_group[k],  v)
    if count == 10:
        break

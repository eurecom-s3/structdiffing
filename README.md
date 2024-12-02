# Artifact evaluation repository for "A Study on the Evolution of Kernel Data Types Used in Memory Forensics and Their Dependency on Compilation Options"

# Environment Setup
- Use Ubuntu 22.04 x86_64 with at least 64GB of Hard Drive and 16GB of RAM. Other versions of Linux should works (it's Python code only).
- Install python3 and some dependencies (minimum python3 version: 3.8.10)
  ```sudo apt install git python3 python3-pip python3-venv universal-ctags```
- Clone the repository
- ```cd ./structdiff_artifacts```
- Create and activate a python3 virtual environment ```python3 -m venv venv; source ./venv/bin/activate```
- Install python3 dependencies ```pip3 install -r requirements.txt```
- To replicate the experiments, read the guides in READMEs files in each folder
  (following the numerical order)

## List of Forensics Structures and Fields Analyzed

### Linux
    address_space: a_ops, backing_dev_info, page_tree
    anon_vma: root
    cred: egid, euid, gid, uid
    dentry: d_inode, d_name, d_parent, d_sb, d_subdirs, d_u.d_alias, d_u.d_child, d_u.d_in_lookup_hash, d_u.d_rcu
    file: f_count, f_cred, f_ep_links, f_flags, f_lock, f_mapping, f_mode, f_op, f_owner, f_path, f_pos, f_ra, f_sb_list_cpu, f_security, f_tfile_llink, f_u.fu_list, f_u.fu_llist, f_u.fu_rcuhead, f_version, private_data
    file_system_type: name, next
    inet_sock: cmsg_flags, inet_dport, inet_num, inet_saddr, inet_sport, pinet6, sk, uc_ttl
    inode: i_atime, i_ctime, i_gid, i_ino, i_mapping, i_mode, i_mtime, i_size, i_uid
    kmem_cache: kmem_cache_node, list
    mm_struct: arg_end, arg_start, brk, end_code, end_data, env_end, env_start, exe_file, ioctx_list, ioctx_lock, map_count, mm_count, mm_rb, mm_users, mmap, mmap_cache, num_exe_file_vmas, owner, pgd, start_brk, start_code, start_data, start_stack
    module: args, core_size, init_size, kp, list, mkobj, module_core, module_init, name, num_kp, sect_attrs
    module_kobject: kobj
    neighbour: dev, ha, next, tbl
    neigh_table: next
    nf_hook_ops: hook, hooknum, list, pf
    path: dentry, mnt
    proto: name
    resource: child, end, name, sibling, start
    rtable: dst, rt_dst, rt_gateway
    seq_operations: next, show, start, stop
    sk_buff: data, head, len, next
    sock: sk_destruct, sk_socket
    sock_common: skc_daddr, skc_family, skc_prot, skc_rcv_saddr, skc_state
    super_block: s_dev
    task_struct: active_mm, children, comm, cpu_timers, flags, group_leader, mm, parent, pid, ptrace, pushable_tasks, real_cred, replacement_session_keyring, sibling, stack, stack_canary, state, tasks, tgid, usage
    timespec: tv_sec
    tty_struct: dev, ldisc, name, session
    vm_area_struct: anon_vma, anon_vma_chain, shared.linear.rb, shared.linear.rb_subtree_last, shared.nonlinear, shared.rb, shared.vm_set.head, shared.vm_set.list, shared.vm_set.parent, vm_end, vm_file, vm_flags, vm_mm, vm_next, vm_ops, vm_page_prot, vm_pgoff, vm_policy, vm_prev, vm_private_data, vm_rb, vm_start
    vfsmount: mnt_devname, mnt_hash, mnt_mountpoint, mnt_parent, mnt_root, mnt_sb

### macOS
    cpu_data_t: cpu_active_thread, rtclock_timer
    dyld_all_image_infos: infoArray, infoArrayCount
    fileglob: fg_data, fg_ops
    fileproc: f_fglob
    fs_event_watcher: event_list, pid, proc_name
    inpcb: inp_dependfaddr.inp46_foreign, inp_dependfaddr.inp6_foreign, inp_dependladdr.inp46_local, inp_dependladdr.inp6_local
    ifnet: if_flags, if_name, if_unit
    kauth_scope: ks_idata, ks_identifier, ks_link.tqe_next
    kmod_info: address, name, next, size, start, stop
    kmod_info_t: address, name, next, reference_count, version
    mac_policy_list: entries
    mac_policy_list_element: mpc
    memory_object_control: moc_ikot, moc_object
    mount: mnt_list
    pmap: pm_cr3, pm_task_map
    proc: p_argc, p_argslen, p_children.lh_first, p_comm, p_fd, p_gid, p_list.le_next, p_list.le_prev, p_name, p_pid, p_pptr, p_sibling.le_next, p_sibling.le_prev, p_uid, task
    protosw: pr_domain, pr_protocol
    queue_entry: next, prev
    session: s_leader, s_login
    sockaddr: sa_family
    socket: so_pcb, so_proto, so_state
    socket_filter: sf_entry_head, sf_filter, sf_global_next.tqe_next
    sysctl_oid: oid_arg1, oid_handler, oid_link.sle_next, oid_name, oid_number
    task: all_image_info_addr, all_image_info_size, bsd_info, map, tasks, threads
    thread: continuation, next, prev, sched_pri, state, t_task, thread_group, thread_id, threads
    ubc_info: ui_control, ui_pager
    _vm_map: hdr, pmap
    vm_map_header: links, nentries
    vm_map_links: end, next, prev, start
    vm_map_entry: object, offset
    vm_map_object: sub_map, vm_object
    vm_object: memq
    vm_page: next, phys_page
    vnode: v_mntvnodes.tqe_next, v_mntvnodes.tqe_prev, v_name, v_parent, v_un.vu_fifoinfo, v_un.vu_mountedhere, v_un.vu_socket, v_un.vu_specinfo, v_un.vu_ubcinfo
    vnodeopv_desc: opv_desc_ops
    zone: count, elem_size, sum_count, zone_name


## Windows
    _CM_KEY_NODE: SubKeyLists, ValueList
    _CMHIVE: FileFullPath, FileUserName, Hive, HiveList, HiveRootPath
    _CONTROL_AREA: FilePointer, Segment
    _DEVICE_OBJECT: AttachedDevice, CurrentIrp, DeviceExtension, DeviceType, DriverObject, NextDevice
    _DISPATCHER_HEADER: Inserted, Size, Type
    _DRIVER_OBJECT: DeviceObject, DriverExtension, DriverInit, DriverName, DriverSize, DriverStart, DriverUnload
    _EPROCESS: ActiveProcessLinks, ActiveThreads, CreateTime, ExitTime, ImageFileName, InheritedFromUniqueProcessId, InheritedFromUniqueProcessId, ObjectTable, Pcb, Peb, Session, SessionProcessLinks, ThreadListHead, Token, UniqueProcessId, VadRoot
    _ETHREAD: CrossThreadFlags, StartAddress, Tcb, ThreadName
    _FILE_OBJECT: FileName, SectionObjectPointer
    _HHIVE: BaseBlock, Signature, Storage
    _HANDLE_TABLE: HandleCount, HandleTableList, QuotaProcess, TableCode
    _HANDLE_TABLE_ENTRY: GrantedAccess, Object
    _HEAP_ENTRY: Flags
    _KMUTANT: Header
    _KPCR: KdVersionBlock
    _KPRCB: CurrentPrcb
    _KPROCESS: DirectoryTableBase
    _LDR_DATA_TABLE_ENTRY: BaseDllName, DllBase, EntryPoint, FullDllName, LoadCount, SizeOfImage
    _LUID_AND_ATTRIBUTES: Attributes, Luid
    _MM_AVL_TABLE: BalancedRoot
    _MMADDRESS_NODE: EndingVpn, LeftChild, RightChild, StartingVpn
    _MMPFN: PteAddress
    _MM_SESSION_SPACE: ImageList, ProcessList, SessionId
    _MMVAD: LeftChild, Parent, RightChild, StartingVpn
    _MMVAD_FLAGS: CommitCharge, DeleteInProgress
    _OBJECT_HEADER: Body, HandleCount, InfoMask, PointerCount, SecurityDescriptor, TypeIndex
    _OBJECT_SYMBOLIC_LINK: LinkTarget
    _OBJECT_TYPE: Key, Name, TotalNumberOfHandles, TotalNumberOfObjects, TypeInfo
    _PEB: BeingDebugged, ImageBaseAddress, Ldr, NumberOfHeaps, ProcessHeap, ProcessHeaps, ProcessParameters
    _PEB_LDR_DATA: InInitializationOrderModuleList, InLoadOrderModuleList, InMemoryOrderModuleList
    _POOL_HEADER: BlockSize, PoolIndex, PoolTag
    _POOL_TRACKER_BIG_PAGES: Key, NumberOfBytes, PoolType
    _POOL_TRACKER_TABLE: Key
    _RTL_USER_PROCESS_PARAMETERS: CommandLine, CurrentDirectory, Environment, ImagePathName, StandardError, StandardInput, StandardOutput
    _SUBSECTION: ControlArea, NextSubsection, PtesInSubsection, StartingSector, SubsectionBase
    _SECTION_OBJECT_POINTERS: DataSectionObject, ImageSectionObject, SharedCacheMap
    _SEP_TOKEN_PRIVILEGES: Enabled, EnabledByDefault, Present
    _SHARED_CACHE_MAP: FileObjectFastRef, InitialVacbs, SectionSize, Vacbs
    _SID_AND_ATTRIBUTES: Attributes, Sid _SID: IdentifierAuthority, Revision, SubAuthority _SID_IDENTIFIER_AUTHORITY: Value
    _TEB: NtTib
    _TOKEN: AuditPolicy, AuthenticationId, Privileges, RestrictedSids, SessionId, TokenId, TokenSource, UserAndGroupCount, UserAndGroups
    _VACB: BaseAddress, Overlay.ActiveCount, Overlay.FileOffset, Overlay.Links, SharedCacheMap

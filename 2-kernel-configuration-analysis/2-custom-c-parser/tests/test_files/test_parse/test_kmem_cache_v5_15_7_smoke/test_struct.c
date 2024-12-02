struct kmem_cache {
    struct kmem_cache_cpu__percpu *cpu_slab;
    /* Used for retrieving partial slabs, etc. */
    /* slab_flags_t flags; OVO SAM NASILNICKI ZAKOMENTARISAO ZA SAD */
    unsigned long min_partial;
    unsigned int size;	/* The size of an object including metadata */
    unsigned int object_size;/* The size of an object without metadata */
    struct reciprocal_value reciprocal_size;
    unsigned int offset;	/* Free pointer offset */
#ifdef CONFIG_SLUB_CPU_PARTIAL
    /* Number of per cpu partial objects to keep around */
    unsigned int cpu_partial;
#endif
    struct kmem_cache_order_objects oo;

    /* Allocation and freeing of slabs */
    struct kmem_cache_order_objects max;
    struct kmem_cache_order_objects min;
    gfp_t allocflags;	/* gfp flags to use on each alloc */
    int refcount;		/* Refcount for slab cache destroy */
    /*void (*ctor)(void *);*/
    unsigned int inuse;		/* Offset to metadata */
    unsigned int align;		/* Alignment */
    unsigned int red_left_pad;	/* Left redzone padding size */
    const char *name;	/* Name (only for display!) */
    struct list_head list;	/* List of slab caches */
#ifdef CONFIG_SYSFS
    struct kobject kobj;	/* For sysfs */
#endif
#ifdef CONFIG_SLAB_FREELIST_HARDENED
    unsigned long random;
#endif

#ifdef CONFIG_NUMA
    /*
    * Defragmentation by allocating from a remote node.
    */
    unsigned int remote_node_defrag_ratio;
#endif

#ifdef CONFIG_SLAB_FREELIST_RANDOM
    unsigned int *random_seq;
#endif

#ifdef CONFIG_KASAN
    struct kasan_cache kasan_info;
#endif

    unsigned int useroffset;	/* Usercopy region offset */
    unsigned int usersize;		/* Usercopy region size */

    struct kmem_cache_node *node[MAX_NUMNODES];
};
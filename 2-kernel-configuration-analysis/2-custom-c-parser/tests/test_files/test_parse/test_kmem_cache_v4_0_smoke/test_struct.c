            struct kmem_cache {
                struct kmem_cache_cpu__percpu *cpu_slab;
                /* Used for retriving partial slabs etc */
                unsigned long flags;
                unsigned long min_partial;
                int size;		/* The size of an object including meta data */
                int object_size;	/* The size of an object without meta data */
                int offset;		/* Free pointer offset. */
                int cpu_partial;	/* Number of per cpu partial objects to keep around */
                struct kmem_cache_order_objects oo;

                /* Allocation and freeing of slabs */
                struct kmem_cache_order_objects max;
                struct kmem_cache_order_objects min;
                gfp_t allocflags;	/* gfp flags to use on each alloc */
                int refcount;		/* Refcount for slab cache destroy */
                /*void (*ctor)(void *);*/
                int inuse;		/* Offset to metadata */
                int align;		/* Alignment */
                int reserved;		/* Reserved bytes at the end of slabs */
                const char *name;	/* Name (only for display!) */
                struct list_head list;	/* List of slab caches */
            #ifdef CONFIG_SYSFS
                    struct kobject kobj;	/* For sysfs */
            #endif
            #ifdef CONFIG_MEMCG_KMEM
                    struct memcg_cache_params memcg_params;
                    int max_attr_size; /* for propagation, maximum size of a stored attr */
            #ifdef CONFIG_SYSFS
                    struct kset *memcg_kset;
            #endif
            #endif

            #ifdef CONFIG_NUMA
                    /*
                    * Defragmentation by allocating from a remote node.
                    */
                    int remote_node_defrag_ratio;
            #endif
                    struct kmem_cache_node *node[MAX_NUMNODES];
            };
 
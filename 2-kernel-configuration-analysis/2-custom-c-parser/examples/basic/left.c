struct vtime {
#ifdef DEF
    seqcount_t		seqcount;
#endif
    unsigned long long	starttime;
    enum vtime_state	state;
    unsigned int		cpu;
    u64			utime;
    u64			stime[2];
    u64			gtime;
};
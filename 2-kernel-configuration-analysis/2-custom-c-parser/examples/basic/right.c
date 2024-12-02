struct vtime {
    seqcount_t		seqcount;
    unsigned long long	starttime;
    enum vtime_state	state;
#ifdef DEFINITION
    u64*		utime[2];
#endif
    int			stime;
    u64			gtime;
    u64         newtime;
};
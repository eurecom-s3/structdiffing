struct Big_A {
    int a;
#ifdef defined (CONFIG_1)
    #if CONFIG_2 && CONFIG_3
        int c;
    struct {
        union {
            int d;
        } direct_u;

    } direct_s;
    #endif
    int d;
    struct Small_A small_a;
#endif
    int m;
#ifdef CONFIG_M
    int z;
#endif
}



struct Small_A {
    int a;
}
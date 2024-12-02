struct Big_A {
    int a;
#ifdef defined (CONFIG_1)
    #if CONFIG_2 && defined(CONFIG_3_NEW)
        int b;
        int new_p;
    #endif
    struct Small_A small_a;
#endif
    int x;
}

struct Small_A {
#ifdef CONFIG_SMALL_1
    int a;
    #if CONFIG_SMALL_2
        int c;
    #endif
    int b;
#endif
}
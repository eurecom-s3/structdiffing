struct Big_A {
    int a;
#ifdef defined (CONFIG_1)
    #if CONFIG_2 && CONFIG_3
        int b;
        int c;
    #endif
    int d;
    struct Small_A small_a;
#endif
}

struct Small_A {
    int a;
#ifdef CONFIG_SMALL_1
    int b;
#endif
}
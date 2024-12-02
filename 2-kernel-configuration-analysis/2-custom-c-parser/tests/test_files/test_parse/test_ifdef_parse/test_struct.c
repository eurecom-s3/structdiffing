struct test_struct {
    int a;
    int b;
#ifdef PRIM
    int c;
    int d;
#else
    int e;
    int f;
#endif
    int g;
#ifdef OUTER
    int h;
    #ifdef INNER
        int j;
    #endif
    int k;
#endif
    int l;
};
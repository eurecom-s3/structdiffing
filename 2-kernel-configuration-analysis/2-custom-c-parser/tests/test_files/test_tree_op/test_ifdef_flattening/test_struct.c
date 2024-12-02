struct my_struct {
#ifdef PRIM
    int a1;
#else
    int a2;
#endif
    unsigned int a;
#ifdef A
    int b;
    char c;
#else
    #ifdef B
        int d;
    #else
        int d2;
    #endif
    float e;
    float e2;
#endif
    int* f;
#ifdef PRIM
    int p2;
#endif
};

struct test_struct {
    int a; /*this one stays the same*/
    int b; /*this one gets removed */
    /* int c; this one only exists in the right struct */
    int d; /* this one changes type */
    int e; /* this one becomes a pointer */
    int f; /* this one becomes an array */
    int g[2]; /* this one changes array size */
};
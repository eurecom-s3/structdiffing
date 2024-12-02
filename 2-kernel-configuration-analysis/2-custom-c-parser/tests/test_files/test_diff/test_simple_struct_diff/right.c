struct test_struct {
    int a;
    int c;
    double d; /* this one changes type */
    int *e; /* this one becomes a pointer */
    int f[3]; /* this one becomes an array */
    int g[5]; /* this one changes array size */
};
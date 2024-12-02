struct Big_A {
    struct Small_A small_a; //should include
    struct Small_B* small_b; //should not
    struct {
        union {
            struct Small_C small_c; //should include
        };

    } inlined; //should not since is syntax sugar

}

struct Small_A {
    struct Small_D small_d; //shoud include in Big_A too
}

struct Small_B {
    struct Small_D small_d; //should include nly in b
}

struct Small_C {
    struct Small_C1 small_c1; // should include in big a too
}
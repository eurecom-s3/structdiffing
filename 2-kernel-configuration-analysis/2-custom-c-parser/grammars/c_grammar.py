c_grammar = r"""
    ?start: root

    //this rule can be used as a hook for post-processing a completely parsed file
    root: statement* 

    struct: ("typedef")? "struct" (struct_type)? "{" struct_body "}" (struct_typedef)? ";"?

    union: "union" (CNAME)? "{" struct_body "}" (CNAME ","?)* ";"

    struct_type: CNAME
    struct_typedef: CNAME
    variable_name: CNAME 

    struct_body : statement*

    statement : struct
              | ifdef_block
              | ifndef_block
              | function_definition
              | field_definition
              | union
               // STILL MISSING
               // | union

    type: qualifier* type_name 

    qualifier : "const"        -> c_const
              | "volatile"     -> c_volatile
              | "static"       -> c_static
              | "auto"         -> c_auto
              | "extern"       -> c_extern
              | "register"     -> c_register

    type_name : "char" -> c_char
            | "signed" "char" -> c_signed_char
            | "unsigned" "char" -> c_unsigned_char
            | "short" -> c_short
            | "short" "int" -> c_short_int
            | "signed" "short" -> c_signed_short
            | "signed" "short" "int" -> c_signed_short_int
            | "unsigned" "short" -> c_unsigned_short
            | "unsigned" "short" "int" -> c_unsigned_short_int
            | "int" -> c_int
            | "signed" -> c_signed
            | "signed" "int" -> c_signed_int
            | "unsigned" -> c_unsigned
            | "unsigned" "int" -> c_unsigned_int
            | "long" -> c_long
            | "long" "int" -> c_long_int
            | "signed" "long" -> c_signed_long
            | "signed" "long" "int" -> c_signed_long_int
            | "unsigned" "long" -> c_unsigned_long
            | "unsigned" "long" "int" -> c_unsigned_long_int
            | "long" "long" -> c_long_long
            | "long" "long" "int" -> c_long_long_int
            | "signed" "long" "long" -> c_signed_long_long
            | "signed" "long" "long" "int" -> c_signed_long_long_int
            | "unsigned" "long" "long" -> c_unsigned_long_long
            | "unsigned" "long" "long" "int" -> c_unsigned_long_long_int
            | "float" -> c_float
            | "double" -> c_double
            | "long" "double" -> c_long_double
            | "void"             -> c_void
            | "struct" CNAME     -> c_inline_struct
            | "union" CNAME      -> c_inline_union
            | "enum" CNAME       -> c_enum
            | CNAME              -> c_typedef //if none of the before match, assume its a typedef

    pointer_sufix: "*"+     -> c_pointer

    field_definition: type field_name* ";"

    field_name: pointer_sufix? variable_name* array_sufix? bitfield_sufix? ","?

    bitfield_sufix: ":" NUMBER

    ifdef_block: "#" ("ifdef"|"if") CNAME statement* (pragma_else statement*)?  "#" "endif"

    ifndef_block: "#" "ifndef" CNAME statement* (pragma_else statement*)? "#" "endif"

    pragma_else: "#" "else"

    array_sufix: /\[.*\]/


    function_definition: function_return "(" "*" CNAME ")" "(" function_param* ")" ";"

    function_return: type pointer_sufix?

    function_param: type pointer_sufix?  function_param_name? ","?

    function_param_name: CNAME  -> c_function_param_name

    %import common.CNAME
    %import common.WS
    %import common.NUMBER
    %import common.C_COMMENT
    %import common.CPP_COMMENT

    %ignore CPP_COMMENT
    %ignore C_COMMENT
    %ignore WS
"""

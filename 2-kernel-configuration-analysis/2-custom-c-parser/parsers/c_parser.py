from lark import Lark
from transformers.c_transformer import TreeToDataStructure
from grammars.c_grammar import c_grammar

def get_c_parser(mappings={}):
    """
        Method for instantiating and returning a lark parser.
        Mappings represent substituions the parser can use.
        For instance for the dict {'C0': 'defined(A)'}
        Whenever the parser finds the string 'C0' it will treat it as 'defined(A)'.
    """
    parser = Lark(
        c_grammar, parser='lalr',
        lexer='standard',
        propagate_positions=False,
        maybe_placeholders=False,

        transformer=TreeToDataStructure(mappings)
    )
    return parser

from lark import UnexpectedToken
from utils.utils import handle_generic_exception, handle_parsing_exception, parse_diff_arguments, validate_diff_arguments
from pipeline.pipeline import diff_pipeline_entry

def main():
    """
        Entry point for application.
    """
    try:
        args = parse_diff_arguments()
        validate_diff_arguments(args)
        diff_pipeline_entry(args)
    except UnexpectedToken as e:
        print(handle_parsing_exception(e))
    except Exception as e:
        handle_generic_exception(e)

if __name__ == '__main__':
    main()

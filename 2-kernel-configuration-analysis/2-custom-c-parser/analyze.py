from lark import UnexpectedToken
from utils.utils import handle_generic_exception, handle_parsing_exception, parse_analysis_arguments, parse_diff_arguments, validate_analysis_arguments, validate_diff_arguments
from pipeline.pipeline import diff_pipeline_entry, analysis_pipeline_entry

def main():
    """
        Entry point for application.
    """
    try:
        args = parse_analysis_arguments()
        validate_analysis_arguments(args)
        analysis_pipeline_entry(args)
    except UnexpectedToken as e:
        print(handle_parsing_exception(e))
    except Exception as e:
        handle_generic_exception(e)

if __name__ == '__main__':
    main()


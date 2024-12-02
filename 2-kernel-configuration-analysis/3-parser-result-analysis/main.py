from pipeline.filter_ctags import filter_ctags
from pipeline.util import initialize_output_dir, parse_analysis_arguments, validate_analysis_arguments, create_run_specific_output_folder
from pipeline.size_calculator import calculate_sizes
from pipeline.important_structs import create_important_struct_reports
from pipeline.build_global_statistic import build_global_statistics
from pipeline.create_stats_csv import build_stats_csv
from pipeline.create_stats_embedded_structs import build_embedded_structs_csv
from pipeline.create_stats_csv_ifdef import build_ifdef_stats_csv
from pipeline.create_stats_csv_ifdef_per_field import build_ifdef_per_field_csv
from pipeline.create_diff_csv import vertical_diff

def main():
    args = parse_analysis_arguments()
    validate_analysis_arguments(args)
    initialize_output_dir()
    run_parent_output_dir = create_run_specific_output_folder()
    filtered_ctags = filter_ctags(args.inputFolder, run_parent_output_dir)
    calculator_output_dir = calculate_sizes(filtered_ctags, run_parent_output_dir)
    create_important_struct_reports(calculator_output_dir, run_parent_output_dir)
    build_global_statistics(calculator_output_dir, run_parent_output_dir)
    build_stats_csv(calculator_output_dir, run_parent_output_dir)
    build_embedded_structs_csv(calculator_output_dir, run_parent_output_dir)
    build_ifdef_stats_csv(calculator_output_dir, run_parent_output_dir)
    build_ifdef_per_field_csv(calculator_output_dir, run_parent_output_dir)
    vertical_diff(calculator_output_dir, run_parent_output_dir)
    print('Analysis completed. All results stored in: ', run_parent_output_dir)




if __name__ == '__main__':
    main()

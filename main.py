import os
import subprocess

def prompt_for_path(message):
    return input(f"Enter the {message}: ").strip()

def run_script(script_path, args):
    try:
        subprocess.run(['python', script_path] + args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {script_path}: {e}")

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    # input directory for CCRL .pgn files, e.g., from https://computerchess.org.uk/ccrl/4040/games.html
    ccrl_input_dir = ''
    # output directory for PGN files
    pgn_output_dir = ''
    # input directory for PGN files
    input_pgn_dir = pgn_output_dir
    # folder path for the output JSON file (from PGN files)
    json_output_dir = '' 
    # dir path for the input JSON files (from PGN files)
    json_dir = json_output_dir
    # path for the output CSV file (from JSON file)
    csv_output_dir = ''
    # input CSV file path for calculating statistics
    csv_all_games_path = '.../engine_aggregated_game_data.csv'
    # input CSV file path for calculating merged statistics
    csv_merged_file_path = '.../engine_aggregated_game_data_merged_engines.csv'
    # output directory for statistics
    stats_output_dir = csv_output_dir


    # Define the paths and arguments for each script
    scripts = [
        ('eval_corrector_ccrl.py', [ccrl_input_dir, pgn_output_dir]), 
        ('pgn_engine_vs_engine_eval_analyzer.py', [input_pgn_dir, json_output_dir]),
        ('json_to_csv_converter.py', [json_dir, csv_output_dir]),
        ('json_to_csv_merge_versions.py', [json_dir, csv_output_dir]),
        ('chess_stats_summarizer.py', [csv_all_games_path, stats_output_dir]),
        #('csv_to_player_stats.py', [csv_all_games_path, stats_output_dir]),
        ('csv_to_player_stats.py', [csv_merged_file_path, player_stats_output_dir])
    ]

    # Sequentially run the scripts with their full paths and arguments
    for script_name, args in scripts:
        script_path = os.path.join(base_path, script_name)
        print(f"Running {script_path}...")
        run_script(script_path, args)

if __name__ == "__main__":
    main()

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
    # input directory for CCRL files (.pgn files)
    ccrl_input_dir = 'C:\\Users\\admin_chess\\Downloads\\CCRL-4040-commented.[1743565].pgn'
    # output directory for PGN files
    pgn_output_dir = '/workspaces/Engine-vs-engine-chess-stats/Full'
    # input directory for PGN files
    input_pgn_dir = pgn_output_dir
    # folder path for the output JSON file (from PGN files)
    json_output_dir = '/workspaces/Chess-Data-Processing/CCRL/Stats' 
    # path for the input JSON file (from PGN files)
    json_file_path = '/workspaces/Engine-vs-engine-chess-stats/PGNs/engine_aggregated_game_data.json'
    # path for the output CSV file (from JSON file)
    csv_output_dir = '/workspaces/Engine-vs-engine-chess-stats/PGNs'
    # input CSV file path for calculating statistics
    csv_file_path = '/workspaces/Engine-vs-engine-chess-stats/PGNs/engine_aggregated_game_data.csv'
    # output directory for statistics
    stats_output_dir = csv_output_dir
    # input CSV file for player statistics
    csv_all_games_path = csv_file_path 
    # output CSV file for player statistics
    player_stats_output_dir = csv_output_dir

    # Define the paths and arguments for each script
    scripts = [
        ('eval_corrector_ccrl.py', [ccrl_input_dir, pgn_output_dir]), 
        #('pgn_engine_vs_engine_analyzer.py', [input_pgn_dir, json_output_dir]')
        #('pgn_evaluation_analyzer.py', [pgn_output_dir, json_output_dir]),
        #('json_to_csv_converter.py', [json_file_path, csv_output_dir]),
        #('chess_stats_summarizer.py', [csv_file_path, stats_output_dir]),
        #('csv_to_player_stats.py', [csv_all_games_path, player_stats_output_dir])
    ]

    # Sequentially run the scripts with their full paths and arguments
    for script_name, args in scripts:
        script_path = os.path.join(base_path, script_name)
        print(f"Running {script_path}...")
        run_script(script_path, args)

if __name__ == "__main__":
    main()

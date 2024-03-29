"""This script inputs the CSV file generated by json_to_csv_converter.py and outputs a CSV file 
containing the following statistics:
- Average and median of each numeric column
- Average and median of the merged white and black columns
- Total number of moves
- Total number of games
It also outputs a density distribution plot for each merged column.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import glob

def combine_csv_files(input_dir, output_filename='combined.csv'):
    csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
    combined_df = pd.DataFrame()

    for file in csv_files:
        df = pd.read_csv(file)
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    output_path = os.path.join(input_dir, output_filename)
    combined_df.to_csv(output_path, index=False)
    print(f"Combined CSV created at {output_path}")
    return output_path

def calculate_statistics(csv_input_file, output_directory):
    # Reading the CSV file
    df = pd.read_csv(csv_input_file)

    # Calculating the total number of games
    total_games = len(df)

    # Selecting numeric columns except specified ones
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    excluded_cols = ['WhiteElo', 'BlackElo', 'WhiteResult', 'BlackResult']
    cols_to_analyze = [col for col in numeric_cols if col not in excluded_cols]

    # Calculating average and median for individual columns
    averages = df[cols_to_analyze].mean()
    medians = df[cols_to_analyze].median()

    # Merging white and black columns and calculating overall statistics
    merge_cols = ['sgi', 'sgpl', 'stcpl', 'gi', 'gpl']
    overall_averages = {}
    overall_medians = {}
    merged_data = {}
    for col in merge_cols:
        white_col = f'white_{col}'
        black_col = f'black_{col}'
        merged = pd.concat([df[white_col], df[black_col]])
        overall_averages[col] = merged.mean()
        overall_medians[col] = merged.median()
        merged_data[col] = merged

    # Calculating the total sum of moves
    total_moves = df['white_move_number'].sum() + df['black_move_number'].sum()

    # Preparing the DataFrame for CSV output
    result_data = {
        'Metric': cols_to_analyze + merge_cols + ['total_move_number', 'total_games'],
        'Average': averages.tolist() + list(overall_averages.values()) + [None, None],
        'Median': medians.tolist() + list(overall_medians.values()) + [None, None],
        'Total Moves': [None] * (len(cols_to_analyze) + len(merge_cols)) + [total_moves, None],
        'Total Games': [None] * (len(cols_to_analyze) + len(merge_cols)) + [None, total_games]
    }

    output_df = pd.DataFrame(result_data)
    output_csv_file = f"{output_directory}/summarized_game_data.csv"
    output_df.to_csv(output_csv_file, index=False)

    # Graphing the density distribution of merged data and showing averages
    for col in merge_cols:
        plt.figure()
        sns.kdeplot(merged_data[col], fill=True)  # Updated from shade=True to fill=True
        plt.axvline(overall_averages[col], color='r', linestyle='--')
        plt.title(f'Density Distribution of {col.upper()} (Avg: {overall_averages[col]:.2f})')
        plt.xlabel(col)
        plt.ylabel('Density')
        plot_file = f"{output_directory}/{col}_density_distribution.png"
        # plt.savefig(plot_file)
        plt.show()


def main(input_csv_path, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    calculate_statistics(input_csv_path, output_directory)

if __name__ == "__main__":
    # If multiple CSVs: 
    # input_dir = ""
    # csv_all_games_path = combine_csv_files(input_dir, output_filename='combined.csv')
    if len(sys.argv) < 3:
        print("Usage: python chess_stats_summarizer.py <input_csv_path> <output_directory>")
        sys.exit(1)

    input_csv_path = sys.argv[1]
    output_directory = sys.argv[2]
    main(input_csv_path, output_directory)

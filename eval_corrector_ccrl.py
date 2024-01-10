"""This script input the PGN file with evals from the CCRL dataset and outputs a PGN file with corrected evals,
where all evals are from White's perspective as is standard."""

import chess.pgn
import re
import sys
import os
import time

def extract_eval_from_comment(comment):
    match = re.search(r"[\+\-]\d+\.\d+", comment)
    if match:
        eval_str = match.group()
        try:
            return float(eval_str)
        except ValueError:
            print(f"Failed to parse eval: {eval_str}")
            return None
    else:
        # If no eval is found, then it must be a book move, so return 0
        return 0
        #return None

def process_game(game):
    node = game
    while node.variations:
        next_node = node.variation(0)
        eval_score = extract_eval_from_comment(next_node.comment)

        # Invert the evaluation score for Black's moves
        if eval_score is not None and node.board().turn == chess.BLACK:
            eval_score = -eval_score

        if eval_score is not None:
            # Update the comment with the corrected evaluation score in the desired format
            next_node.comment = f"[%eval {eval_score}]"
        node = next_node

def main(ccrl_input_dir, pgn_output_dir):
    # Ensure the output directory exists
    if not os.path.exists(pgn_output_dir):
        os.makedirs(pgn_output_dir)

    for input_file in os.listdir(ccrl_input_dir):
        if input_file.endswith(".pgn"):
            input_pgn_file_path = os.path.join(ccrl_input_dir, input_file)
            output_pgn_file_name = os.path.splitext(input_file)[0] + "_corrected.pgn"
            output_pgn_file_path = os.path.join(pgn_output_dir, output_pgn_file_name)

            try:
                with open(input_pgn_file_path) as pgn_text, open(output_pgn_file_path, "w") as output_pgn_file:
                    exporter = chess.pgn.FileExporter(output_pgn_file)
                    while True:
                        game = chess.pgn.read_game(pgn_text)
                        if game is None:
                            break
                        process_game(game)
                        game.accept(exporter)
                print(f"Updated games written to {output_pgn_file_path}")
            except FileNotFoundError:
                print(f"File not found: {input_pgn_file_path}")
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    start_time = time.time()
    if len(sys.argv) < 3:
        print("Usage: python eval_corrector_ccrl.py <ccrl_input_dir> <pgn_output_dir>")
        sys.exit(1)

    ccrl_input_dir = sys.argv[1]
    pgn_output_dir = sys.argv[2]
    main(ccrl_input_dir, pgn_output_dir)
    end_time = time.time()
    print("Script finished in {:.2f} minutes".format((end_time - start_time) / 60.0))
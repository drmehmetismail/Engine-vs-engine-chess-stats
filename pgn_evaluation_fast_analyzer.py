"""This script inputs the PGN files and outputs a JSON file including calculations
of various stats such as GI, GPL, ACPL, etc. for each game. 
The stats are simpler and the script works faster than the pgn_evaluation_analyzer.py"""

import chess
import chess.pgn
import chess.engine
import json
import os
from chess.engine import Cp, Wdl
import time
import sys

# Function to extract the evaluation from a node
def extract_eval_from_node(node):
    node_evaluation = node.eval()
    #print("node_evaluation: ", node_evaluation)
    if node_evaluation:
        cp_value = node_evaluation.pov(chess.WHITE).score(mate_score=10000) / 100.0
        return cp_value
    else:
        return None

# Function to extract the evaluations from a PGN file
def extract_pawn_evals_from_pgn(game):
    pawns_list = [0]
    for node in game.mainline():
        eval_value = extract_eval_from_node(node)
        if eval_value is not None:
            pawns_list.append(eval_value)
    if len(pawns_list) > 1:
        pawns_list[0] = pawns_list[1]
    #print("pawns_list: ", pawns_list)
    return pawns_list

# Function to calculate the ACPL for both players
def calculate_acpl(pawns_list):
    white_losses, black_losses = [], []
    for i in range(1, len(pawns_list)):
        centipawn_loss = 100*(pawns_list[i] - pawns_list[i - 1])
        if i % 2 == 1:  # White's turn
            white_losses.append(-centipawn_loss)
        else:  # Black's turn
            black_losses.append(centipawn_loss)
    white_acpl = sum(white_losses) / len(white_losses) if white_losses else 0
    black_acpl = sum(black_losses) / len(black_losses) if black_losses else 0
    return white_acpl, black_acpl

def calculate_gi_by_result(white_gpl, black_gpl, game_result):
    # Calculate GI based on game result
    if game_result == '1/2-1/2':
        white_gi = 0.5 - white_gpl
        black_gi = 0.5 - black_gpl
    elif game_result == '1-0':
        white_gi = 1 - white_gpl
        black_gi = -black_gpl
    elif game_result == '0-1':
        black_gi = 1 - black_gpl
        white_gi = -white_gpl
    else:
        white_gi = postmove_exp_white - white_gpl
        black_gi = postmove_exp_black - black_gpl

    return white_gi, black_gi

# Function to calculate GI and GPL in the usual way
def gi_and_gpl(pawns_list, game_result):
    white_gpl, black_gpl = 0, 0
    white_gi, black_gi = 0, 0
    white_move_number, black_move_number = 0, 0

    for i, cp in enumerate(pawns_list):
        # Determine whose turn it is
        #print("i: ", i)
        turn = "White" if i % 2 == 0 else "Black"
        
        # Convert centipawn value to probability
        # handle the initial case
        premove_eval = Cp(int(100 * pawns_list[i-1] if i > 0 else 100 * pawns_list[1]))
        #print("premove_eval: ", premove_eval)
        postmove_eval = Cp(int(100 * cp))
        #print("cp: ", cp)
        #print("postmove_eval: ", postmove_eval)

        # Calculate expected values before the move
        win_draw_loss = premove_eval.wdl()
        win_prob, draw_prob, loss_prob = win_draw_loss.wins / 1000, win_draw_loss.draws / 1000, win_draw_loss.losses / 1000
        premove_exp_white, premove_exp_black = calculate_expected_value(win_prob, draw_prob, loss_prob, turn)

        # Calculate expected values after the move
        win_draw_loss = postmove_eval.wdl()
        win_prob, draw_prob, loss_prob = win_draw_loss.wins / 1000, win_draw_loss.draws / 1000, win_draw_loss.losses / 1000
        postmove_exp_white, postmove_exp_black = calculate_expected_value(win_prob, draw_prob, loss_prob, turn)

        # Calculate GPL and update move number
        if turn == "Black":
            exp_white_point_loss = postmove_exp_white - premove_exp_white
            white_gpl += exp_white_point_loss
            #print("white_move_number: ", white_move_number)
            #print("premove_eval: ", premove_eval)
            #print("postmove_eval: ", postmove_eval)
            white_move_number += 1
        else:
            exp_black_point_loss = premove_exp_black - postmove_exp_black
            black_gpl += exp_black_point_loss
            black_move_number += 1
    # Calculate GI based on game result
    white_gi, black_gi = calculate_gi_by_result(white_gpl, black_gpl, game_result)

    return white_gi, black_gi, white_gpl, black_gpl, white_move_number, black_move_number-1

# Function to calculate the expected value of a position
def calculate_expected_value(win_prob, draw_prob, loss_prob, turn):
    if turn == "White":
        expected_value_white = win_prob * 1 + draw_prob * 0.5
        expected_value_black = loss_prob * 1 + draw_prob * 0.5
    else:
        expected_value_white = loss_prob * 1 + draw_prob * 0.5
        expected_value_black = win_prob * 1 + draw_prob * 0.5
    return expected_value_white, expected_value_black


def write_json(data, file_path, file_counter):
    new_file_path = file_path.replace('.json', f'{file_counter}.json')
    with open(new_file_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)

def main(input_pgn_dir, output_json_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_json_dir):
        os.makedirs(output_json_dir)
    
    base_output_json = os.path.join(output_json_dir, 'engine_aggregated_game_data.json')
    aggregated_data = {}
    key_counter = 1
    file_counter = 1
    max_size = 50 * 1024 * 1024 # 50 MB in bytes
    # Number of games to process before checking file size. Set batch_size = 2 * KB size or 1 game = 590 byte  
    # so that it doesn't check before satisfying the constraint.
    batch_size = 90000 
    batch_counter = 0  # Counter for the current batch
    
    for dirpath, dirnames, filenames in os.walk(input_pgn_dir):
        for filename in filenames:
            if filename.endswith('.pgn'):
                pgn_file_path = os.path.join(dirpath, filename)
                with open(pgn_file_path) as pgn:
                    while True:
                        game = chess.pgn.read_game(pgn)
                        if game is None:
                            break
                        # Get the headers of the game
                        game_result = game.headers.get('Result', None)
                        if game_result == '1-0':
                            whiteResult = 1
                            blackResult = 0
                        elif game_result == '0-1':
                            whiteResult = 0
                            blackResult = 1
                        elif game_result == '1/2-1/2':
                            whiteResult = 0.5
                            blackResult = 0.5
                        else:
                            whiteResult = '...'
                            blackResult = '...'
                        # Further game details
                        game_details = {
                            "White": game.headers.get("White", None),
                            "Black": game.headers.get("Black", None),
                            "Event": game.headers.get("Event", None),
                            "Site": game.headers.get("Site", None),
                            "Round": game.headers.get("Round", None),
                            "WhiteElo": game.headers.get("WhiteElo", None),
                            "BlackElo": game.headers.get("BlackElo", None),
                            "WhiteResult": whiteResult,
                            "BlackResult": blackResult,
                            "Date": game.headers.get("Date", None),
                                }

                        pawns_list = extract_pawn_evals_from_pgn(game)
                        white_acpl, black_acpl = calculate_acpl(pawns_list)

                        #black_moves = (len(pawns_list) - 1) // 2
                        #white_moves = len(pawns_list) - 1 - black_moves

                        # Calculate GI and GPL for both players
                        white_gi, black_gi, white_gpl, black_gpl, white_move_number, black_move_number = gi_and_gpl(pawns_list, game_result)
                        key = key_counter
                        game_data = {
                            "white_gi": round(white_gi, 4), "black_gi": round(black_gi, 4),
                            "white_gpl": round(white_gpl, 4), "black_gpl": round(black_gpl, 4),
                            "white_acpl": round(white_acpl, 4), "black_acpl": round(black_acpl, 4),
                            "white_move_number": white_move_number, "black_move_number": black_move_number,
                            **game_details,
                        }
                        aggregated_data[key] = game_data
                        key_counter += 1
                        batch_counter += 1
                        # Check size of aggregated_data after processing a batch of games
                        if batch_counter >= batch_size:
                            if json.dumps(aggregated_data).encode('utf-8').__sizeof__() >= max_size:
                                write_json(aggregated_data, base_output_json, file_counter)
                                file_counter += 1
                                print("file_counter: ", file_counter)
                                aggregated_data = {}  # Reset data for next file
                            batch_counter = 0  # Reset batch counter
    if aggregated_data:
        write_json(aggregated_data, base_output_json, file_counter)

    print(f"Aggregated data saved to {base_output_json}")
    print(f"#Games = {key_counter - 1}")

if __name__ == "__main__":
    start_time = time.time()
    input_pgn_dir = r"C:\Users\k1767099\_LichessDB\Test\test"
    output_json_dir = r"C:\Users\k1767099\_LichessDB\Test\new"
    main(input_pgn_dir, output_json_dir)
    end_time = time.time()
    print("Script finished in {:.2f} minutes".format((end_time - start_time) / 60.0))
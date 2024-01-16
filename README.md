# Engine-vs-engine Chess Stats
This Python codebase processes computer chess game data, such as from CCRL ([Computer Chess Rating Lists](https://computerchess.org.uk/ccrl/4040/)) and computes insightful stats including Game Intelligence (GI), Game Point Loss (GPL), and Average Centipawn Loss (ACPL). Importantly, the scripts takes into account the fact that evaluations in engine-vs-engine competitions are often engine-specific, and hence the stats such as ACPL cannot be reasonably calculated in the usual way because two different engine's centipawns are usually incompatible. Centipawn loss of an engine's move m_i is calculated as the difference between the centipawn evaluations of the **opponent** engine's moves m_{i-1} and m_{i+1}. This uses the fact that each engine plays its best move and hence the difference in the evaluations of moves m_{i-1} and m_{i+1} are due to the opponent's move move m_{i}.

## Scripts
1. `eval_corrector_ccrl.py`: Inputs the PGN file with evals from the CCRL dataset and outputs a PGN file with corrected evals, where all evals are from white's perspective.
2. `pgn_engine_vs_engine_analyzer.py`: Inputs the PGN file generated by eval_corrector_ccrl.py and outputs a JSON file with calculations of various stats such as GI, GPL, and ACPL for each game.
3. `json_to_csv_converter.py`: Converts JSON data to CSV format for aggregated chess game stats.
4. `csv_to_player_stats.py`: Inputs the CSV file generated by json_to_csv_converter.py and outputs a CSV with player (engine) specific stats.
5. `chess_stats_summarizer.py`: Inputs the CSV file generated by json_to_csv_converter.py and outputs a summary stats.
6. `main.py`: Main script to run the entire data processing pipeline.

## Additional scripts

7. `split_large_pgn.py`: # Splits large PGN file into smaller files based on size and content
9. `player_stats_summarizer.py`: Inputs the CSV file generated by csv_to_player_stats.py and outputs a summary stats.
10. `normalize_gi.py`: Inputs a CSV generated from csv_to_player_stats.py and outputs a CSV with the normalized_gi column using the linear function initially obtained from the normalize_player_stats.py. This script can be used independently for any dataset.


## Usage
Run the `main.py` script to process data through all stages:

## Reference
For more information, see https://doi.org/10.48550/arXiv.2302.13937

## Citation
Please cite the following paper if you find this helpful.
```
@article{ismail2023human,
  title={Human and Machine: Practicable Mechanisms for Measuring Performance in Partial Information Games},
  author={Ismail, Mehmet S},
  journal={arXiv preprint arXiv:2302.13937},
  year={2023}
}
```

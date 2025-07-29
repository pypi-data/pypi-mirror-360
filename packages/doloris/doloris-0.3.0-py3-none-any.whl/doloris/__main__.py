import os
import sys
import argparse

from doloris.panel import DolorisPanel
from doloris.algorithm import run_doloris_algorithm

VERSION = "0.3.0"
DOLORIS = R"""  ____          _               _      
 |  _ \   ___  | |  ___   _ __ (_) ___ 
 | | | | / _ \ | | / _ \ | '__|| |/ __|
 | |_| || (_) || || (_) || |   | |\__ \
 |____/  \___/ |_| \___/ |_|   |_||___/
"""

def argument_parser():
    parser = argparse.ArgumentParser(
        description="Doloris: Detection Of Learning Obstacles via Risk-aware Interaction Signals"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # version 命令
    subparsers.add_parser("version", help="Print the version of Doloris")

    # panel 命令
    panel_parser = subparsers.add_parser("panel", help="start the Doloris panel")
    panel_parser.add_argument(
        "--cache-path",
        type=str,
        default=os.path.abspath(".doloris"),
        help="Path to the cached data directory"
    )
    panel_parser.add_argument(
        "--share",
        type=bool,
        default=False,
        help="Set 'True' to create a public link"
    )

    # algorithm 命令
    algorithm_parser = subparsers.add_parser("algorithm", help="run the Doloris algorithm")
    algorithm_parser.add_argument(
        "--cache-path",
        type=str,
        default=os.path.abspath(".doloris"),
        help="Path to the cached data directory"
    )
    algorithm_parser.add_argument(
        "--label-type",
        type=str,
        choices=["binary", "multiclass"],
        default="binary",
        help="Type of label: 'binary' or 'multiclass'"
    )
    algorithm_parser.add_argument(
        "--feature-cols",
        type=lambda s: s.split(","),
        default=[
            "age_band",
            "highest_education",
            "imd_band",
            "num_of_prev_attempts",
            "studied_credits",
            "total_n_days",
            "avg_total_sum_clicks",
            "n_days_oucontent",
            "avg_sum_clicks_quiz",
            "avg_sum_clicks_forumng",
            "avg_sum_clicks_homepage"
        ],
        help="Comma-separated list of feature columns"
    )
    algorithm_parser.add_argument(
        "--model-name",
        type=str,
        choices=["logistic_regression", "random_forest", "knn", "svm", "sgd", "mlp"],
        default="logistic_regression",
        help="Name of the model to use"
    )

    args = parser.parse_args()
    return parser, args

def main():
    parser, args = argument_parser()

    print(DOLORIS)

    if args.command == "version":
        print(f"Doloris version {VERSION}")
    elif args.command == "panel":
        panel = DolorisPanel(args.cache_path)
        panel.launch(args.share)
    elif args.command == "algorithm":
        run_doloris_algorithm(
            args.cache_path,
            args.label_type,
            args.feature_cols,
            args.model_name,
        )
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

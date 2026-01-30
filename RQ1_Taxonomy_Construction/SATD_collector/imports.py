import sys
import argparse
from pathlib import Path

project_path=Path(__file__).resolve().parent

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Process GitHub repo URL.')
    parser.add_argument('repo_url', metavar='repo_url', type=str,
                        help='GitHub repository URL')
    parser.add_argument('detect_type', metavar='detect_type', type=int,
                        help='Detection type (1 for KeywordList1, 2 for KeywordList2, 3 for SatdDetectorModel)')
    return parser.parse_args()

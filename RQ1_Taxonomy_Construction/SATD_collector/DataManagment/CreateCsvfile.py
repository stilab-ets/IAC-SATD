import os
import csv
from urllib.parse import urlparse
from datetime import datetime
from operator import itemgetter

def create_csv_1_from_repo(repo_url :str, detect_type :int):
    # Extract the repository name from the URL
    repo_name = urlparse(repo_url).path.strip('/').replace('/', '_')

    # Remove "https://github.com" from the repo name
    if repo_name.startswith("https_github_com"):
        repo_name = repo_name[len("https_github_com"):]
    
    # Create the current date and time in YYYYMMDD_HHMMSS format
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Create the file name for the CSV file
    file_name = f"{repo_name}.{detect_type}.{current_datetime}.csv"

    # Create the output directory if it doesn't exist
    output_directory = 'Data_extracted_comments'
    os.makedirs(output_directory, exist_ok=True)

    # Path to the CSV file within the 'data' directory
    csv_file_path = os.path.join(output_directory, file_name)

    # Create the CSV file with headers
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Repo URL','Old File Path', 'New File Path', 'Comment', 'Line ID', 'Num of lines', 'Commit Hash', 'Commit Message', 'Developer Email', 'Commit Date', 'Is SATD'])

    return csv_file_path



def create_csv_2_from_repo(repo_url :str, detect_type :int):
    # Extract the repository name from the URL
    repo_name = urlparse(repo_url).path.strip('/').replace('/', '_')

    # Remove "https://github.com" from the repo name
    if repo_name.startswith("https_github_com"):
        repo_name = repo_name[len("https_github_com"):]
    
    # Create the current date and time in YYYYMMDD_HHMMSS format
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Create the file name for the CSV file
    file_name = f"{repo_name}.{detect_type}.{current_datetime}.csv"

    # Create the output directory if it doesn't exist
    output_directory = 'Data_tracked_satd_comments'
    os.makedirs(output_directory, exist_ok=True)

    # Path to the CSV file within the 'data' directory
    csv_file_path = os.path.join(output_directory, file_name)

    # Create the CSV file with headers
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Repo URL','Satd Comment Id', 'Old File Path', 'New File Path', 'SATD Comment', 'context', 'bloc', 'bloc type', 'Line ID', 'Num of lines', 'Commit Hash', 'Commit Message', 'Commit Date', 'Developer Email', 'Tracking type'])

    return csv_file_path
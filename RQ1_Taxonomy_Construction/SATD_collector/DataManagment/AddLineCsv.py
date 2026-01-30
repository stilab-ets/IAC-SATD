import csv

def add_line_to_csv(row_data, csv_file_path):
    with open(csv_file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(row_data)

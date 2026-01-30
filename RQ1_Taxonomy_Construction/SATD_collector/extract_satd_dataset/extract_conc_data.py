import os
import csv

def extract_IDs_Satd_Comments(csv_file):
    unique_values = set()  # Initialize an empty set to store unique values
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > 1 and row[1] != "Satd Comment Id":  # Check if the row has at least two columns
                unique_values.add(row[1])  # Add the value from the second column to the set
    return unique_values


def count_csv_rows(csv_file_path):
    try:
        with open(csv_file_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            row_count = sum(1 for row in csv_reader)
        return row_count
    except FileNotFoundError:
        print("File not found.")
        return -1  # Return -1 to indicate an error
    except Exception as e:
        print("An error occurred:", e)
        return -1  # Return -1 to indicate an error
    


def add_row_to_projects_details(row_data):
    try:
        # Define the path to the CSV file
        data_folder = "Data"
        csv_file_name = "projects_details.csv"
        csv_file_path = os.path.join(data_folder, csv_file_name)
        
        # Check if the CSV file exists, if not create it with headers
        if not os.path.exists(csv_file_path):
            with open(csv_file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                #writer.writerow(['Repo URL', 'Number of Comments', 'Number of Satd Comments', 'Percentage of Satd Comments Over All Comments', 'Number of different Satd Comments'])  # Adjust column names as needed
                writer.writerow(['Repo URL', 'Number of Comments', 'Number of Satd Comments', 'Percentage of Satd Comments Over All Comments', 'Number of different Satd Comments', 'adressed ones', 'not yet adressed', 'deleted from its file'])

        # Append the new row to the CSV file
        with open(csv_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row_data)
        
        #print("Row added successfully to", csv_file_path)
    except Exception as e:
        print("An error occurred:", e)


def add_row_to_satd_data_all_projects(satd_csv_file, satd_id):
        
    # Define the path to the CSV file
    data_folder = "Data"
    csv_file_name = "satd_data_all_projects.csv"
    csv_file_path = os.path.join(data_folder, csv_file_name)

    # Check if the CSV file exists, if not create it with headers
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            #writer.writerow(['Repo URL', 'Satd Comment Id', 'File Path Of First Occurence', 'File Path Of Last Occurence', 'SATD Comment', 'context', 'bloc', 'bloc type', 'SATD Comment Line Of First Occurence', 'SATD Comment Line Of Last Occurence', 'first Commit Hash', 'last Commit Hash','Link To The File Of First Occurence', 'Link To The File Of Last Occurence/When Adressed', 'Introduction Time', 'Last Occurence (even solved or not)', 'number of commits' , 'adressed ?'])
            writer.writerow(['Repo URL', 'Satd Comment Id', 'File Path Of First Occurence', 'File Path Of Last Occurence', 'SATD Comment', 'context', 'bloc of first occurence', 'bloc type of first occurence', 'bloc of last occurence', 'bloc type of last occurence', 'SATD Comment Line Of First Occurence', 'SATD Comment Line Of Last Occurence', 'first Commit Hash', 'last Commit Hash','Link To The File Of First Occurence', 'Link To The File Of Last Occurence/When Adressed', 'Introduction Time', 'Last Occurence (even solved or not)', 'number of commits' , 'adressed ?'])


    # Initialize variables
    row_data = []
    count = 0

    #satd_type
    satd_type=0

    # Read the CSV file
    with open(satd_csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > 1 and row[1] == satd_id:
                # Process the row
                if count == 0:
                    repo_URL = row[0]
                    comment_id = row[1]
                    comment_Line_Id_first = row[8]
                    comment_Line_Id_last = row[8]
                    comment_msg = row[4]
                    comment_context = row[5]
                    bloc_first_occurence = row[6]
                    bloc_type_first_occurence = row[7]
                    bloc_last_occurence = row[6]
                    bloc_type_last_occurence = row[7]
                    time_intro = row[12]
                    last_time = row[12]
                    first_commit_hash = row[10]
                    last_commit_hash = row[10]
                    is_adressed = 0
                    if(row[2]):
                        file_path_first_occurence = row[2]
                        file_path_last_occurence = row[2]
                    else:
                        file_path_first_occurence = row[3]
                        file_path_last_occurence = row[3]

                    link_first_occurence = f"{repo_URL}/blob/{first_commit_hash}/{file_path_first_occurence}"
                    link_last_occurence = f"{repo_URL}/blob/{last_commit_hash}/{file_path_last_occurence}"
                    if comment_Line_Id_first:
                        link_first_occurence += f"#L{comment_Line_Id_first}"
                    if comment_Line_Id_last:
                        link_last_occurence += f"#L{comment_Line_Id_last}"

                else:
                    bloc_last_occurence = row[6]
                    bloc_type_last_occurence = row[7]
                    last_time = row[12]
                    last_commit_hash = row[10]
                    if(row[3]):
                        file_path_last_occurence = row[3]
                    else:
                        file_path_last_occurence = row[2]

                is_adressed = 1 if row[14] == "0" else 0
                if(is_adressed == 1):
                    comment_Line_Id_last=""
                    link_last_occurence = f"{repo_URL}/blob/{last_commit_hash}/{file_path_last_occurence}"
                else:
                    comment_Line_Id_last=row[8]
                    link_last_occurence = f"{repo_URL}/blob/{last_commit_hash}/{file_path_last_occurence}"
                    link_last_occurence += f"#L{comment_Line_Id_last}"
                count += 1

                #check the type of the satd comment
                if(row[14]=="3"):
                    satd_type=2
                elif(row[14]=="2"):
                    satd_type=0
                elif(row[14]=="0"):
                    satd_type=1

                renamed=0
                #check if the file got renamed
                if(file_path_first_occurence==file_path_last_occurence):
                    renamed=0
                else:
                    renamed=1


    # Form the row_data
    row_data = [repo_URL, comment_id, file_path_first_occurence, file_path_last_occurence, renamed, comment_msg, comment_context, bloc_first_occurence, bloc_type_first_occurence, bloc_last_occurence, bloc_type_last_occurence, comment_Line_Id_first, comment_Line_Id_last, first_commit_hash, last_commit_hash, link_first_occurence, link_last_occurence, time_intro, last_time, count, satd_type]
    
    # Append the new row to the CSV file
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row_data)

    
    return satd_type



import os
import sys
from imports import parse_arguments
from imports import project_path
from pydriller import Repository
from Model.Project import Project
from Model.File import File
from Model.SatdCommentList import SatdCommentList
from Model.FilesList import FilesList
from Model.Commit import Commit
from SatdTracking.AddExecutor import AddExecutor
from SatdTracking.ModifyExecutor import ModifyExecutor
from SatdTracking.RenameExecutor import RenameExecutor
from SatdTracking.DeleteExecutor import DeleteExecutor
from CommentsMining.CommentExtractor import extract_comments, trier_par_numero_ligne, fusionner_commentaires_en_bloc
from CommentsMining.SatdDetector import KeywordList1Detector, KeywordList2Detector, KeywordListsDetector, MLModelDetector
from DataManagment.CreateCsvfile import create_csv_1_from_repo, create_csv_2_from_repo
from DataManagment.Utils import count_lines
from DataManagment.AddLineCsv import add_line_to_csv
from extract_satd_dataset.extract_conc_data import extract_IDs_Satd_Comments, count_csv_rows, add_row_to_satd_data_all_projects, add_row_to_projects_details

# Main function
def main():

    args = parse_arguments()
    repo_url = args.repo_url

    #create Project instance
    Project_inst = Project(repo_url)

    #define extract type method 1 <-> keywordList1, 2 <-> keywordList2, 3 <-> SatdDetectorModel
    detect_type = args.detect_type

    # Create CSV files from GitHub repo
    csv_comments_file_path = create_csv_1_from_repo(repo_url, detect_type)
    csv_tracked_satd_file_path = create_csv_2_from_repo(repo_url, detect_type)

    # Create empty SatdCommentList and FilesList objects
    satd_comment_list = SatdCommentList()
    file_list = FilesList()

    # Iterate through commits and modified files
    for commit in Repository(repo_url).traverse_commits():
        commit_inst=Commit(commit.hash,Project_inst, commit.msg, commit.committer.email, commit.committer_date)
        for modified_file in commit.modified_files:
            if modified_file.filename.endswith('.tf'):
                #extract all comments
                extracted_comments=[]
                if not(modified_file.source_code=='' or modified_file.source_code is None):
                    extracted_comments= extract_comments(modified_file.source_code)

                if(modified_file.source_code=='' or modified_file.source_code is None):
                    number_lines = 0
                else:
                    number_lines = count_lines(modified_file.source_code)

    
                #choose detection type
                if(detect_type==1):
                    detector=KeywordList1Detector()
                elif(detect_type==2):
                    detector=KeywordList2Detector()
                elif(detect_type==3):
                    detector=KeywordListsDetector()
                elif(detect_type==4):
                    detector=MLModelDetector()
                else:
                    raise ValueError("Invalid detector type")
                
                if modified_file.change_type.name == 'ADD':

                    # Modify the file instance in the satdCommentList
                    file_instance = file_list.get_file_by_new_path(modified_file.new_path)

                    if(file_instance is None):
                        # Create File instance and add it to FilesList instance
                        file_instance = File(filename=modified_file.filename, source_code=modified_file.source_code, old_file_path=modified_file.old_path, new_file_path=modified_file.new_path,num_lines=number_lines,modification_type='ADD', commit=commit_inst)
                        #print(file_instance.get_new_file_path())
                        file_list.add_file(file_instance)

                        # Call the detect method of the selected detector
                        satd_comments = SatdCommentList()

                        satd_comments.create_satd_comments_from_list(detector.detect(extracted_comments), file_instance)

                        # Create instance of AddExecutor class and execute its method
                        add_executor = AddExecutor()
                        add_executor.executeModification(file_instance, satd_comment_list, satd_comments, csv_tracked_satd_file_path, csv_comments_file_path)
                    else:
                        # Modify the file instance in the satdCommentList
                        file_instance = file_list.get_file_by_new_path(modified_file.new_path)
                        #details about the file in the list to modify

                        file_instance.modify_attributes(filename=modified_file.filename, source_code=modified_file.source_code, old_file_path=modified_file.new_path, new_file_path=modified_file.new_path,num_lines=number_lines,modification_type='MODIFY', commit=commit_inst)
                        #details about the file in the list to modify

                        # Call the detect method of the selected detector
                        satd_comments = SatdCommentList()
                        satd_comments.create_satd_comments_from_list(detector.detect(extracted_comments), file_instance)
        
                        # Create instance of ModifyExecutor class and execute its method
                        modify_executor = ModifyExecutor()
                        modify_executor.executeModification(file_instance, satd_comment_list, satd_comments, csv_tracked_satd_file_path,file_list, csv_comments_file_path)


                elif modified_file.change_type.name == 'MODIFY':

                    file_instance = file_list.get_file_by_new_path(modified_file.new_path)
                    if(file_instance is not None):
                        file_instance.modify_attributes(filename=modified_file.filename, source_code=modified_file.source_code, old_file_path=modified_file.old_path, new_file_path=modified_file.new_path,num_lines=number_lines,modification_type='MODIFY', commit=commit_inst)

                        # Call the detect method of the selected detector
                        satd_comments = SatdCommentList()
                        satd_comments.create_satd_comments_from_list(detector.detect(extracted_comments), file_instance)
            
                        # Create instance of ModifyExecutor class and execute its method
                        modify_executor = ModifyExecutor()
                        modify_executor.executeModification(file_instance, satd_comment_list, satd_comments, csv_tracked_satd_file_path,file_list, csv_comments_file_path)
                    
                    else:
                        file_instance = file_list.get_file_by_old_path(modified_file.new_path)
                        if(file_instance is not None):
                            #print("here is here is here is")
                            file_instance.modify_attributes(filename=modified_file.filename, source_code=modified_file.source_code, old_file_path=modified_file.old_path, new_file_path=modified_file.new_path,num_lines=number_lines,modification_type='MODIFY', commit=commit_inst)

                            # Call the detect method of the selected detector
                            satd_comments = SatdCommentList()
                            satd_comments.create_satd_comments_from_list(detector.detect(extracted_comments), file_instance)
                
                            # Create instance of ModifyExecutor class and execute its method
                            modify_executor = ModifyExecutor()
                            modify_executor.executeModification(file_instance, satd_comment_list, satd_comments, csv_tracked_satd_file_path,file_list, csv_comments_file_path)


                elif modified_file.change_type.name == 'RENAME':
                    # Modify the file instance in the satdCommentList
                    file_instance = file_list.get_file_by_new_path(modified_file.old_path)

                    #check if the file exists before as tf file
                    if(file_instance is not None):

                        file_instance.modify_attributes(filename=modified_file.filename, source_code=modified_file.source_code, old_file_path=modified_file.old_path, new_file_path=modified_file.new_path,num_lines=number_lines,modification_type='RENAME', commit=commit_inst)
                    
                    else:
                        file_instance = File(filename=modified_file.filename, source_code=modified_file.source_code, old_file_path='', new_file_path=modified_file.new_path,num_lines=number_lines,modification_type='ADD', commit=commit_inst)
                        file_list.add_file(file_instance)

                        # Call the detect method of the selected detector
                        satd_comments = SatdCommentList()

                        satd_comments.create_satd_comments_from_list(detector.detect(extracted_comments), file_instance)

                        # Create instance of AddExecutor class and execute its method
                        add_executor = AddExecutor()
                        add_executor.executeModification(file_instance, satd_comment_list, satd_comments, csv_tracked_satd_file_path, csv_comments_file_path)


                elif modified_file.change_type.name == 'DELETE':
                    # Modify the file instance in the satdCommentList
                    file_instance = file_list.get_file_by_new_path(modified_file.old_path)
                    if(file_instance is not None):
                        file_instance.modify_attributes(filename=modified_file.filename, source_code=modified_file.source_code, old_file_path=modified_file.old_path, new_file_path=modified_file.new_path,num_lines=number_lines,modification_type='DELETE', commit=commit_inst)

                    # Create instance of DeleteExecutor class and execute its method
                    delete_executor = DeleteExecutor()
                    delete_executor.executeModification(file_instance, satd_comment_list, csv_tracked_satd_file_path)

                    #delete the file from the file_list
                    file_list.remove_file_from_list(file_instance)


                #print comments which are not satd
                for elt in extracted_comments:
                    row = [repo_url, modified_file.old_path, modified_file.new_path,elt[0] ,elt[1],number_lines, commit_inst.get_commit_hash(), commit_inst.get_commit_msg(), commit_inst.get_developer_email(), commit_inst.get_committer_date(),0]
                    add_line_to_csv(row, csv_comments_file_path)


    #count the number of comments
    num_comments = count_csv_rows(csv_comments_file_path)-1

    #count the number of satd comments
    num_satd_comments = count_csv_rows(csv_tracked_satd_file_path)-1

    #count the percentage
    if(num_comments!=0):
        percentage=num_satd_comments/num_comments*100
    else:
        percentage=0

    #extract and count the different satd comments in the file
    diff_Satd_IDs=extract_IDs_Satd_Comments(csv_tracked_satd_file_path)
    num_diff_Satd=len(diff_Satd_IDs)


    #count the adressed satd comments
    adressed_satd_counter=0
    #count the not yet adressed
    not_yet_adressed_satd_counter=0
    #count the satd where its satd get removed
    satd_file_deleted=0

    #for each ID insert its data in the file
    for elt in diff_Satd_IDs:
        satd_type=add_row_to_satd_data_all_projects(csv_tracked_satd_file_path, elt)

        #handle
        if(satd_type==0):
            not_yet_adressed_satd_counter+=1
        elif(satd_type==1):
            adressed_satd_counter+=1
        elif(satd_type==2):
            satd_file_deleted+=1


    #insert into the projects details 
    row=[repo_url, num_comments, num_satd_comments, '{:.3f} %'.format(percentage), num_diff_Satd, adressed_satd_counter, not_yet_adressed_satd_counter, satd_file_deleted]
    add_row_to_projects_details(row)


    print("whole process ended with success state")


if __name__ == "__main__":
    main()
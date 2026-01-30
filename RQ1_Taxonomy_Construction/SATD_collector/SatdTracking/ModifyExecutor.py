from RQ1_Taxonomy_Construction.SATD_collector.CommentsMining.CommentExtractor import extract_comment_block
from RQ1_Taxonomy_Construction.SATD_collector.DataManagment.AddLineCsv import add_line_to_csv
from RQ1_Taxonomy_Construction.SATD_collector.DataManagment.Utils import get_first_line
from RQ1_Taxonomy_Construction.SATD_collector.Model.SatdCommentList import SatdCommentList
from RQ1_Taxonomy_Construction.SATD_collector.SatdTracking.LogicExecutor import LogicExecutor
from RQ1_Taxonomy_Construction.SATD_collector.terrametrics_dependency.terrametrics_loader import TerraMetricsLoader
from RQ1_Taxonomy_Construction.SATD_collector.terrametrics_dependency.utils import write_to_file, \
    extract_associated_block, extract_code, extract_associated_block_from_name


class ModifyExecutor(LogicExecutor):
    def executeModification(self, file, satdCommentList: SatdCommentList, satd_comments: SatdCommentList, csv_tracked_satd_file_path, file_list, csv_comments_file_path):
  
        l1=SatdCommentList()
        l1.set_satd_comment_list_dep_cp(satdCommentList.get_satd_comments_map_file(file))

        for satdComment in satd_comments.get_satd_comment_list():


            if(l1.check_satd_comment_in_list(satdComment)):

                #update the object with value #2 print to csv it is existing then delete the object 
                l1.check_satd_comment_in_list(satdComment).set_modification_type(2)
                satdComment.set_modification_type(2)

                #terrametrics integration
                write_to_file(file.get_source_code())

                #path to the tmp file
                tmp_path="terrametrics_dependency/tmp.tf"
                #print(tmp_path)

                #terrametrics integration
                terrametrics_instance = TerraMetricsLoader(pathToLocalEmp=tmp_path)
                terrametrics_instance.call_service_locator()

                #return the pair
                block_extracted=extract_associated_block(satdComment.get_line_number())

                if(block_extracted!=-1):
                    #find the ranges
                    bloc=extract_code(block_extracted['start_block'],block_extracted['end_block'])
                    bloc_type=block_extracted['block']
                else:
                    #bloc=file.get_source_code()
                    bloc=""
                    bloc_type=''


                #add the row to the tracked satd csv #2
                row = [satdComment.get_file().get_commit().get_project().get_project_url(),l1.check_satd_comment_in_list(satdComment).get_ref_id(), satdComment.get_file().get_old_file_path(), satdComment.get_file().get_new_file_path(), satdComment.get_comment_content() ,extract_comment_block(file.get_source_code(),satdComment.get_line_number()) ,bloc ,bloc_type , satdComment.get_line_number() ,satdComment.get_file().get_num_lines(), satdComment.get_file().get_commit().get_commit_hash(), satdComment.get_file().get_commit().get_commit_msg(), satdComment.get_file().get_commit().get_developer_email(), satdComment.get_file().get_commit().get_committer_date(), satdComment.get_modification_type()]
                add_line_to_csv(row, csv_tracked_satd_file_path)

                #output to the csv of the file
                row_1 = [satdComment.get_file().get_commit().get_project().get_project_url(), satdComment.get_file().get_old_file_path(), satdComment.get_file().get_new_file_path(), satdComment.get_comment_content(), satdComment.get_line_number(), satdComment.get_file().get_num_lines(), satdComment.get_file().get_commit().get_commit_hash(), get_first_line(satdComment.get_file().get_commit().get_commit_msg()), satdComment.get_file().get_commit().get_developer_email(), satdComment.get_file().get_commit().get_committer_date(),1]
                add_line_to_csv(row_1, csv_comments_file_path)

                #remove from satd list comments
                l1.remove_comment_from_list(l1.check_satd_comment_in_list(satdComment))
            else:
                #create the object with the modification type #1 (already with one) and print it to csv
                satdCommentList.add_comment_to_map(file, satdComment)

                #terrametrics integration
                write_to_file(file.get_source_code())

                #path to the tmp file
                tmp_path="terrametrics_dependency/tmp.tf"
                #print(tmp_path)

                #terrametrics integration
                terrametrics_instance = TerraMetricsLoader(pathToLocalEmp=tmp_path)
                terrametrics_instance.call_service_locator()

                #return the pair
                block_extracted=extract_associated_block(satdComment.get_line_number())

                if(block_extracted!=-1):
                    #find the ranges
                    bloc=extract_code(block_extracted['start_block'],block_extracted['end_block'])
                    bloc_type=block_extracted['block']
                else:
                    #bloc=file.get_source_code()
                    bloc=""
                    bloc_type=''


                #set satd comment block
                satdComment.set_bock_associated(block_extracted)

                #add the row to the tracked satd csv #1
                row = [satdComment.get_file().get_commit().get_project().get_project_url(), satdComment.get_satd_comment_id(), satdComment.get_file().get_old_file_path(), satdComment.get_file().get_new_file_path(), satdComment.get_comment_content(), extract_comment_block(file.get_source_code(),satdComment.get_line_number()), bloc, bloc_type , satdComment.get_line_number() ,satdComment.get_file().get_num_lines(), satdComment.get_file().get_commit().get_commit_hash(), satdComment.get_file().get_commit().get_commit_msg(), satdComment.get_file().get_commit().get_developer_email(), satdComment.get_file().get_commit().get_committer_date(), satdComment.get_modification_type()]
                add_line_to_csv(row, csv_tracked_satd_file_path)

                #output to the csv of the file
                row_1 = [satdComment.get_file().get_commit().get_project().get_project_url(), satdComment.get_file().get_old_file_path(), satdComment.get_file().get_new_file_path(), satdComment.get_comment_content(), satdComment.get_line_number(), satdComment.get_file().get_num_lines(), satdComment.get_file().get_commit().get_commit_hash(), get_first_line(satdComment.get_file().get_commit().get_commit_msg()), satdComment.get_file().get_commit().get_developer_email(), satdComment.get_file().get_commit().get_committer_date(),1]
                add_line_to_csv(row_1, csv_comments_file_path)

        
        while len(l1.get_satd_comment_list()) >0:
            for satdComment in l1.get_satd_comment_list():
                #set modification type to #0
                satdComment.set_modification_type(0)
                
                #terrametrics integration
                write_to_file(file.get_source_code())

                #path to the tmp file
                tmp_path="terrametrics_dependency/tmp.tf"
                #print(tmp_path)

                #todo get the satd comment associated block
                block_to_satd = satdComment.get_block_associated()

                #terrametrics integration
                terrametrics_instance = TerraMetricsLoader(pathToLocalEmp=tmp_path)
                terrametrics_instance.call_service_locator()

                #return the pair
                if isinstance(block_to_satd, dict) and ('block_identifiers' in block_to_satd):
                    block_extracted=extract_associated_block_from_name(block_to_satd['block_identifiers'])
                else:
                    block_extracted=-1

                #find the ranges
                if(block_extracted!=-1):
                    #find the ranges
                    bloc=extract_code(block_extracted['start_block'],block_extracted['end_block'])
                    bloc_type=block_extracted['block']
                else:
                    #bloc=file.get_source_code()
                    bloc="the block associated got renamed or deleted"
                    bloc_type=''
                

                satdComment.set_bock_associated(block_extracted)

                #add the row to the tracked satd csv #0
                row = [satdComment.get_file().get_commit().get_project().get_project_url(), satdComment.get_ref_id(), satdComment.get_file().get_old_file_path(), satdComment.get_file().get_new_file_path(), satdComment.get_comment_content() , satdComment.get_comment_content(), bloc, bloc_type ,0,satdComment.get_file().get_num_lines(), satdComment.get_file().get_commit().get_commit_hash(),satdComment.get_file().get_commit().get_commit_msg(), satdComment.get_file().get_commit().get_developer_email(), satdComment.get_file().get_commit().get_committer_date(), satdComment.get_modification_type()]
                add_line_to_csv(row, csv_tracked_satd_file_path)
                
                #print the object to csv with the modification type #0 then delete it 
                l1.remove_comment_from_list(satdComment)

                #delete the element from the list of comments of the map
                satdCommentList.remove_comment_from_map(file, satdCommentList.check_satd_comment_in_file(file,satdComment))

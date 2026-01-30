from RQ1_Taxonomy_Construction.SATD_collector.CommentsMining.CommentExtractor import extract_comment_block
from RQ1_Taxonomy_Construction.SATD_collector.DataManagment.AddLineCsv import add_line_to_csv
from RQ1_Taxonomy_Construction.SATD_collector.DataManagment.Utils import get_first_line
from RQ1_Taxonomy_Construction.SATD_collector.SatdTracking.LogicExecutor import LogicExecutor
from RQ1_Taxonomy_Construction.SATD_collector.terrametrics_dependency.terrametrics_loader import TerraMetricsLoader
from RQ1_Taxonomy_Construction.SATD_collector.terrametrics_dependency.utils import extract_associated_block, \
    extract_code, write_to_file


class AddExecutor(LogicExecutor):
    def executeModification(self, file, satdCommentList, satd_comments, csv_tracked_satd_file_path, csv_comments_file_path):
        satdCommentList.add_file(file)

        for satdComment in satd_comments.get_satd_comment_list():

           #add satd comment to the map
           satdCommentList.add_comment_to_map(file,satdComment)

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
                bloc=''
                bloc_type=''

           #set satd comment block
           satdComment.set_bock_associated(block_extracted)

           #output to the csv of satd
           row = [satdComment.get_file().get_commit().get_project().get_project_url(),satdComment.get_satd_comment_id(), satdComment.get_file().get_old_file_path(), satdComment.get_file().get_new_file_path(), satdComment.get_comment_content() ,extract_comment_block(file.get_source_code(),satdComment.get_line_number()) ,bloc , bloc_type ,satdComment.get_line_number() ,satdComment.get_file().get_num_lines() , satdComment.get_file().get_commit().get_commit_hash(), satdComment.get_file().get_commit().get_commit_msg(), satdComment.get_file().get_commit().get_developer_email(), satdComment.get_file().get_commit().get_committer_date(), satdComment.get_modification_type()]
           add_line_to_csv(row, csv_tracked_satd_file_path)

           #output to the csv of the file
           row_1 = [satdComment.get_file().get_commit().get_project().get_project_url(), satdComment.get_file().get_old_file_path(), satdComment.get_file().get_new_file_path(), satdComment.get_comment_content(), satdComment.get_line_number(), satdComment.get_file().get_num_lines(), satdComment.get_file().get_commit().get_commit_hash(), get_first_line(satdComment.get_file().get_commit().get_commit_msg()), satdComment.get_file().get_commit().get_developer_email(), satdComment.get_file().get_commit().get_committer_date(),1]
           add_line_to_csv(row_1, csv_comments_file_path)
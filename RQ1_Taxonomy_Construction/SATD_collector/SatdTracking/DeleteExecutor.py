from RQ1_Taxonomy_Construction.SATD_collector.DataManagment.AddLineCsv import add_line_to_csv
from RQ1_Taxonomy_Construction.SATD_collector.SatdTracking.LogicExecutor import LogicExecutor


class DeleteExecutor(LogicExecutor):
    def executeModification(self, file, satdCommentList, csv_tracked_satd_file_path):
        while(len(satdCommentList.get_satd_comments_map_file(file))>0):
            for satdComment in satdCommentList.get_satd_comments_map_file(file):
                #update object with #0 
                #file deleted
                satdComment.set_modification_type(3)

                #print the object to csv with the modification type #0 then delete it 
                row = [satdComment.get_file().get_commit().get_project().get_project_url(), satdComment.get_satd_comment_id(), satdComment.get_file().get_old_file_path(), satdComment.get_file().get_new_file_path(), satdComment.get_comment_content() ,satdComment.get_comment_content(), '', '',0,satdComment.get_file().get_num_lines(), satdComment.get_file().get_commit().get_commit_hash(), satdComment.get_file().get_commit().get_commit_msg(), satdComment.get_file().get_commit().get_developer_email(), satdComment.get_file().get_commit().get_committer_date(), satdComment.get_modification_type()]
                add_line_to_csv(row, csv_tracked_satd_file_path)
            
                #delete the satd comment
                satdCommentList.remove_comment_from_map(file, satdComment)

        satdCommentList.remove_file(file)


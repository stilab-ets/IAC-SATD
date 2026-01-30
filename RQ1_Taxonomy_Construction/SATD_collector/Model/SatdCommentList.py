from RQ1_Taxonomy_Construction.SATD_collector.CommentsMining.SatdKeyWordLists import keywordList1
from RQ1_Taxonomy_Construction.SATD_collector.Model.SatdComment import SatdComment


class SatdCommentList:

    def __init__(self):
        self.satd_comments_map = {}
        self.satd_comment_list = []

    def get_satd_comments_map(self):
        return self.satd_comments_map

    def set_satd_comments_map(self, satd_comments_map):
        self.satd_comments_map = satd_comments_map

    def get_satd_comments_map_file(self,file):
        return self.satd_comments_map.get(file, [])
    
    def set_satd_comments_map_file(self,file, satd_comments):
        self.satd_comments_map[file]=list(satd_comments)
    '''
    def set_satd_comments_map_file_dp_cp(self, satd_comments):
        for elt in satd_comments:
            satd_comment_iter = SatdComment(elt.get_file(), elt.get_modification_type(), elt.get_comment_content(), elt.get_line_number())
            self.add_comment_to_list(satd_comment_iter)'''

    def get_satd_comment_list(self):
        return self.satd_comment_list

    def set_satd_comment_list(self, satd_comment_list):
        self.satd_comment_list = satd_comment_list

    def set_satd_comment_list_dep_cp(self, satd_comment_list):
        #self.satd_comment_list = copy.deepcopy(satd_comment_list)
        for elt in satd_comment_list:
            satd_comment_iter = SatdComment(elt.get_file(), elt.get_modification_type(), elt.get_comment_content(), elt.get_block_associated() ,elt.get_line_number(), elt.get_satd_comment_id())
            self.add_comment_to_list(satd_comment_iter)

    def add_comment_to_map(self, file, satd_comment):
        if file in self.satd_comments_map:
            self.satd_comments_map[file].append(satd_comment)

    def remove_comment_from_map(self, file, satd_comment):
        if file in self.satd_comments_map:
            if satd_comment in self.satd_comments_map[file]:
                self.satd_comments_map[file].remove(satd_comment)

    def add_comment_to_list(self, satdComment):
        self.satd_comment_list.append(satdComment)

    def remove_comment_from_list(self, satdComment):
        #if satdComment in self.satd_comment_list:
        self.satd_comment_list.remove(satdComment)
    
    def empty_satd_comment_list(self):
        self.satd_comment_list = []

    def add_file(self, file):
        if file not in self.satd_comments_map:
            self.satd_comments_map[file] = []
    
    def remove_file(self, file):
        if file in self.satd_comments_map.keys():
            del self.satd_comments_map[file]

    def filter_comments(self, commentList):
        # Filter comments that contain at least one word from the word list
        filtered_comments = [comment for comment in commentList.get_comment_list() if any(word in comment for word in keywordList1)]
        self.satd_comment_list = filtered_comments

    def check_satd_comment_in_file(self,file, satdComment):
        for satdComment1 in self.get_satd_comments_map_file(file):
            if satdComment1.get_comment_content()==satdComment.get_comment_content():
                return satdComment1
        return None
    
    def check_satd_comment_in_list(self, satdComment):
        for satdCommentItr in self.get_satd_comment_list():
            if satdCommentItr.get_comment_content()==satdComment.get_comment_content():
                return satdCommentItr
        return 0
    
    def create_satd_comments_from_list(self, satd_comment_list, file):
        for comment_content, line_number in satd_comment_list:
            # Create Comment instance with provided parameters
            satd_comment = SatdComment(file=file, modification_type=1, comment_content=comment_content, block_associated='', line_number=line_number)
            # Add the comment to the satd_comment_list
            self.add_comment_to_list(satd_comment)

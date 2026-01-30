from RQ1_Taxonomy_Construction.SATD_collector.Model.File import File


class SatdComment:
    # Static variable to keep track of the last assigned ID
    id_counter = 0

    def __init__(self, file : File, modification_type, comment_content, block_associated, line_number,ref_id=None):
        SatdComment.id_counter+=1
        self.id = SatdComment.id_counter
        self.file=file
        self.modification_type=modification_type
        self.comment_content = comment_content
        self.block_associated = block_associated
        self.line_number = line_number
        self.ref_id=ref_id

    def __repr__(self):
        return f"<SatdComment(id={self.id},file_id={self.get_file_id()},modification_type={self.modification_type}, content={self.comment_content},line_number={self.line_number})>"

    def get_satd_comment_id(self):
        return self.id

    def get_ref_id(self):
        return self.ref_id
    
    def set_ref_id(self, ref_id):
        self.ref_id=ref_id
    
    def get_file(self):
        return self.file
    
    def get_file_id(self):
        return self.file.get_id()

    def set_file_id(self, file_id):
        self.file_id = file_id

    def set_modification_type(self, modification_type):
        self.modification_type = modification_type

    def get_modification_type(self):
        return self.modification_type

    def get_comment_content(self):
        return self.comment_content

    def set_comment_content(self, comment_content):
        self.comment_content = comment_content

    def get_line_number(self):
        return self.line_number

    def set_line_number(self, line_number):
        self.line_number = line_number


    def get_block_associated(self):
        return self.block_associated
    
    def set_bock_associated(self, block_associated):
        self.block_associated = block_associated


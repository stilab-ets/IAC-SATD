from RQ1_Taxonomy_Construction.SATD_collector.Model.File import File


class Comment:
    # Static variable to keep track of the last assigned ID
    id_counter = 0

    def __init__(self, file: File, comment_content: str, line_number: int):
        Comment.id_counter +=1
        self.id = Comment.id_counter
        self.file = file
        self.comment_content = comment_content
        self.line_number = line_number

    def __repr__(self):
        return f"<Comment(id={self.id}, project_id={self.file.get_id()}, file_id={self.comment_content}, commit_id={self.line_number})>"

    # Getters and setters
    def get_id(self):
        return self.id

    def get_file_id(self):
        return self.file.get_id()

    def set_file_id(self, file_id: int):
        self.file_id = file_id

    def get_comment_content(self):
        return self.comment_content

    def set_comment_content(self, comment_content: str):
        self.comment_content = comment_content

    def get_line_number(self):
        return self.line_number

    def set_line_number(self, line_number: int):
        self.line_number = line_number

from RQ1_Taxonomy_Construction.SATD_collector.Model.Commit import Commit


class File:
    # Static variable to keep track of the last assigned ID
    id_counter = 0

    def __init__(self, filename, source_code, old_file_path, new_file_path, num_lines, modification_type, commit: Commit):

        # Increment the static ID counter and assign it to the current instance
        File.id_counter += 1
        self.id = File.id_counter
        self.filename = filename
        self.source_code = source_code
        self.old_file_path = old_file_path
        self.new_file_path = new_file_path
        self.modification_type = modification_type
        self.num_lines = num_lines
        self.commit = commit

    def __repr__(self):
        return f"<File(filename={self.filename}, file_source_code={self.source_code},old_file_path={self.old_file_path},new_file_path={self.new_file_path} , modification_type={self.modification_type}, num_lines={self.num_lines}, commit_hash={self.commit.get_commit_hash()}, commit_msg={self.commit.get_commit_msg()}, commit_author_email={self.commit.get_developer_email()}, commit_committer_date={self.commit.get_committer_date()})>"

    def get_id(self):
        return self.id
    
    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        self.filename = filename

    def get_source_code(self):
        return self.source_code

    def set_source_code(self, source_code):
        self.source_code = source_code

    def get_old_file_path(self):
        return self.old_file_path

    def set_old_file_path(self, old_file_path):
        self.old_file_path = old_file_path

    def get_new_file_path(self):
        return self.new_file_path

    def set_new_file_path(self, new_file_path):
        self.new_file_path = new_file_path

    def get_modification_type(self):
        return self.modification_type

    def set_modification_type(self, modification_type):
        self.modification_type = modification_type

    def get_num_lines(self):
        return self.num_lines
    
    def set_num_lines(self, num_lines):
        self.num_lines = num_lines

    def get_commit(self):
        return self.commit

    def modify_attributes(self, filename=None, source_code=None, old_file_path=None, new_file_path=None,num_lines=None,modification_type=None, commit=None):
        if filename is not None:
            self.filename = filename
        if source_code is not None:
            self.source_code = source_code
        if old_file_path is not None:
            self.old_file_path = old_file_path
        if new_file_path is not None:
            self.new_file_path = new_file_path
        if num_lines is not None:
            self.num_lines = num_lines
        if modification_type is not None:
            self.modification_type=modification_type
        if commit is not None:
            self.commit = commit

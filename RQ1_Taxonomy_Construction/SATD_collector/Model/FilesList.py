from RQ1_Taxonomy_Construction.SATD_collector.Model.File import File


class FilesList:
    def __init__(self):
        self.fileslist = []

    def get_files_list(self):
        return self.fileslist

    def set_files_list(self, filesList):
        self.fileslist=filesList

    def add_file(self, file):
        self.fileslist.append(file)

    def remove_file_from_list(self, file: File):
        if file in self.fileslist:
            self.fileslist.remove(file)

    def get_file_by_old_path(self, old_path):
        for file in self.fileslist:
            if file.get_old_file_path() == old_path:
                return file
        return None
    
    def get_file_by_new_path(self, path):
        for file in self.fileslist:
            if file.get_new_file_path() == path:
                return file
        return None

class Project:
    # Static variable to keep track of the last assigned ID
    id_counter = 0

    def __init__(self, project_url):
        Project.id_counter+=1
        self.id=Project.id_counter
        self.project_url = project_url

    def __repr__(self):
        return f"<Project(id={self.project_id}, name={self.project_name})>"

    # Getters and setters
    def get_project_id(self):
        return self.project_id

    def set_project_id(self, project_id):
        self.project_id = project_id

    def get_project_url(self):
        return self.project_url

    def set_project_name(self, project_url):
        self.project_url = project_url
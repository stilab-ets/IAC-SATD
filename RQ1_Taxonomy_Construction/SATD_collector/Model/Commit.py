from RQ1_Taxonomy_Construction.SATD_collector.Model.Project import Project


class Commit:

    def __init__(self, commit_hash: str, project:Project, commit_msg: str, committer_date, developer_email: str):

        self.id = commit_hash
        self.project = project
        self.commit_msg = commit_msg
        self.developer_email = developer_email
        self.committer_date = committer_date

    def __repr__(self):
        return f"<Commit(commit_project={self.project}, commit_hash={self.commit_hash}, commit_msg={self.commit_msg}, developer_email={self.developer_email}, committer_date={self.committer_date})>"

    def get_id(self):
        return self.id

    def get_commit_hash(self):
        return self.id
    
    def get_project(self):
        return self.project
    
    def set_commit_hash(self, commit_hash: str):
        self.commit_hash = commit_hash

    def get_commit_msg(self):
        return self.commit_msg
        
    def set_commit_msg(self, commit_msg: str):
        self.commit_msg = commit_msg

    def get_developer_email(self):
        return self.developer_email

    def set_developer_email(self, developer_email):
        self.developer_email = developer_email

    def get_committer_date(self):
        return self.committer_date

    def set_committer_date(self, committer_date):
        self.committer_date = committer_date

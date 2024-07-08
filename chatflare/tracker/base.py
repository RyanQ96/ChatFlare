import uuid 
import datetime 
import json 

class Task: 
    def __init__(self, task_type, result, embedding=None):
        self.id = str(uuid.uuid4())
        self.task_type = task_type
        self.timestamp = datetime.datetime.now().isoformat()
        self.result = result
        self.embedding = embedding

    def to_dict(self):
        return {
            "id": self.id,
            "task_type": self.task_type,
            "timestamp": self.timestamp,
            "result": self.result,
            "embedding": self.embedding,
        }

    def save_task(self, path="./test_history_control/task"):
        """save task to disk with the file being named with the task id"""
        with open(f"{path}/{self.id}.json", "w") as f:
            f.write(json.dumps(self.to_dict()))

    @classmethod
    def load_action_from_disk(cls, task_id, path="./test_history_control/task"):
        with open(f"{path}/{Task_id}.json", "r") as f:
            task_dict = json.loads(f.read())
        return Task(**task_dict)    



class Commit: 
    """commit can potentially involve multiple action, so it should have its own id"""
    def __init__(self, action_ids, parent_commit_id=None):
        self.id = str(uuid.uuid4())
        self.action_ids = action_ids
        self.parent_commit = parent_commit_id
        self.timestamp = datetime.datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "action_ids": self.action_ids,
            "parent_commit_id": self.parent_commit,
            "timestamp": self.timestamp,
        }

    def __repr__(self):
        return f"Commit {self.id[:8]}"


class Branch: 
    def __init__(self, branch_name='main', head_commit=None, commits=[]):
        self.id = str(uuid.uuid4())
        self.branch_name = branch_name
        self.head_commit = head_commit
        self.commits = commits

    def add_commit(self, commit_id):
        self.commits.append(commit_id)
        self.head_commit = commit_id

    def to_dict(self):
        return {
            "id": self.id,
            "branch_name": self.branch_name,
            "commits": [commit.to_dict() for commit in self.commits],
        }   
    
    def create_new_branch_from_commit(self, branch_name, commit_id):
        if commit_id not in self.commits:
            raise ValueError("The commit_id provided is not in the list of commits")
        # create a new branch from the commit_id
        idx = self.commits.index(commit_id) 
        new_commits = self.commits[:idx+1]
        new_branch = Branch(branch_name, head_commit=commit_id, commits=new_commits)
        return new_branch   
    
    def __repr__(self):
        commits_display_str = "" 
        for commit_idx in range(len(self.commits) - 1, -1, -1):
            if commit_idx == len(self.commits) - 1:
                commits_display_str += f"{self.commits[commit_idx]}\t(*HEAD)\n"
            else:
                commits_display_str += f"{self.commits[commit_idx]}\n"
                
            if commit_idx != 0:
                commits_display_str += "     Ʌ\n"
                commits_display_str += "     |\n"
        return f"Branch: {self.branch_name}\n{'='*25}\n{commits_display_str}"

    
    

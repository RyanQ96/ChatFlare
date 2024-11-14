from typing import List, Union
import uuid 
import datetime 
import json 


class Blob: 
    """Blob is the smallest unit of action that can be performed in the system"""
    def __init__(self, task_type=None, result=None, embedding=None):
        self.id = str(uuid.uuid4())
        self.task_type = task_type
        self.timestamp = datetime.datetime.now().isoformat()
        self.result = result
        """
        result: {
            "meta": {}, 
            "output": {}, // usually the finding itself, the part need to saved 
            "content": str, // the content of the task
            "update_longterm_memory": bool, // whether to update the longterm memory
            "agent_current_position": document_id, // the current position of the agent
        }
        """
        self.embedding = embedding

    def to_dict(self):
        return {
            "id": self.id,
            "task_type": self.task_type,
            "timestamp": self.timestamp,
            "result": self.result,
            "embedding": self.embedding
        }

    def save_task(self, path="./test_history_control/task"):
        """save task to disk with the file being named with the task id"""
        with open(f"{path}/{self.id}.json", "w") as f:
            f.write(json.dumps(self.to_dict()))

    def __repr__(self):
        return f"Blob {self.id[:8]}, type: {self.task_type}, timestamp: {self.timestamp}, result: {'...' if self.result is not None else 'None'}"

    @classmethod
    def load_action_from_disk(cls, task_id, path="./test_history_control/task"):
        with open(f"{path}/{Blob_id}.json", "r") as f:
            task_dict = json.loads(f.read())
        return Blob(**task_dict)    



class Commit: 
    """commit can potentially involve multiple action, so it should have its own id"""
    def __init__(self, action_ids: Union[str, List[str]], parent_commit_id=None, blobs: Union[Blob, List[Blob]]=None):
        self.id = str(uuid.uuid4())
        self.action_ids = action_ids if isinstance(action_ids, list) else [action_ids]
        self.parent_commit = parent_commit_id
        self.timestamp = datetime.datetime.now().isoformat()
        if blobs is not None:
            self.blobs = blobs if isinstance(blobs, list) else [blobs]
        else:
            self.blobs = None 

    def to_dict(self):
        return {
            "id": self.id,
            "action_ids": self.action_ids,
            "parent_commit_id": self.parent_commit,
            "timestamp": self.timestamp,
        }

    def __repr__(self):
        return f"Commit {self.id[:8]}"
    
    @classmethod 
    def from_blobs(cls, blobs: Union[Blob, List[Blob]]):
        if isinstance(blobs, list):
            return cls([b.id for b in blobs], parent_commit_id=None, blobs=blobs)
        return cls([blobs.id], parent_commit_id=None, blobs=[blobs])


class Branch: 
    def __init__(self, branch_name='main', head_commit=None, commits: List[Commit]=[]):
        self.id = str(uuid.uuid4())
        self.branch_name = branch_name
        self.head_commit = head_commit
        self.commits = commits
        if head_commit is None and len(commits) > 0:
            self.head_commit = commits[-1]

    @property
    def length(self):
        return len(self.commits)
    
    def add_commit(self, commit_id):
        self.commits.append(commit_id)
        self.head_commit = commit_id

    def rollback(self, commitOrId: Union[str, Commit], inplace=True, new_branch_name=None):
        if isinstance(commitOrId, Commit):
            commitId = commitOrId.id
        else:
            commitId = commitOrId 
        
        commit = self._get_commit_with_commitid(commitId)
        if commit is None:
            raise ValueError("The commit_id provided is not in the list of commits")
        idx = self.commits.index(commit)
        if inplace:
            self.commits = self.commits[:idx+1]
            self.head_commit = commit
        else:   
            new_commits = self.commits[:idx+1]
            new_branch_name = new_branch_name if new_branch_name is not None else self.branch_name + str(uuid.uuid4())[:4]
            new_branch = Branch(new_branch_name, head_commit=commit, commits=new_commits)
            return new_branch
    
    def _get_commit_with_commitid(self, commit_id):
        for commit in self.commits:
            if commit.id == commit_id:
                return commit
        return None
    
    
    def to_dict(self):
        return {
            "id": self.id,
            "branch_name": self.branch_name,
            "commits": [commit.to_dict() for commit in self.commits],
        }   
    
    def create_new_branch_from_commit(self, branch_name, commit):
        if commit not in self.commits:
            raise ValueError("The commit_id provided is not in the list of commits")
        # create a new branch from the commit_id
        idx = self.commits.index(commit) 
        new_commits = self.commits[:idx+1]
        new_branch = Branch(branch_name, head_commit=commit, commits=new_commits)
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
        return f"Branch: {self.branch_name if len(self.branch_name) < 17 else self.branch_name[:14] + '...'}\n{'='*25}\n{commits_display_str}"

    
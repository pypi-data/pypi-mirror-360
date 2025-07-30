import os
from typing import List, Dict, Optional, Tuple
from git import Repo, GitCommandError
from pathlib import Path


class GitOperations:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.repo: Optional[Repo] = None
        self._initialize_repo()
    
    def _initialize_repo(self):
        try:
            self.repo = Repo(self.repo_path, search_parent_directories=True)
        except:
            self.repo = None
    
    def is_git_repo(self) -> bool:
        return self.repo is not None
    
    def get_current_branch(self) -> str:
        if not self.repo:
            return ""
        try:
            return self.repo.active_branch.name
        except:
            return "HEAD (detached)"
    
    def get_branches(self) -> List[Dict[str, any]]:
        if not self.repo:
            return []
        
        branches = []
        current_branch = self.get_current_branch()
        
        for branch in self.repo.branches:
            branches.append({
                'name': branch.name,
                'is_current': branch.name == current_branch,
                'commit': str(branch.commit)[:7],
                'message': branch.commit.message.strip().split('\n')[0]
            })
        
        for remote in self.repo.remotes:
            for ref in remote.refs:
                branch_name = ref.name.replace(f"{remote.name}/", "")
                branches.append({
                    'name': ref.name,
                    'is_current': False,
                    'is_remote': True,
                    'commit': str(ref.commit)[:7],
                    'message': ref.commit.message.strip().split('\n')[0]
                })
        
        return branches
    
    def get_status(self) -> Dict[str, List[str]]:
        if not self.repo:
            return {'staged': [], 'unstaged': [], 'untracked': []}
        
        status = {
            'staged': [],
            'unstaged': [],
            'untracked': []
        }
        
        for item in self.repo.index.diff("HEAD"):
            status['staged'].append({
                'path': item.a_path,
                'change_type': item.change_type
            })
        
        for item in self.repo.index.diff(None):
            status['unstaged'].append({
                'path': item.a_path,
                'change_type': item.change_type
            })
        
        status['untracked'] = [{'path': path, 'change_type': 'A'} for path in self.repo.untracked_files]
        
        return status
    
    def stage_file(self, file_path: str):
        if not self.repo:
            return
        self.repo.index.add([file_path])
    
    def unstage_file(self, file_path: str):
        if not self.repo:
            return
        self.repo.index.reset(paths=[file_path])
    
    def stage_all(self):
        if not self.repo:
            return
        self.repo.git.add(A=True)
    
    def unstage_all(self):
        if not self.repo:
            return
        self.repo.index.reset()
    
    def commit(self, message: str):
        if not self.repo:
            return
        self.repo.index.commit(message)
    
    def get_commits(self, max_count: int = 50) -> List[Dict[str, any]]:
        if not self.repo:
            return []
        
        commits = []
        for commit in self.repo.iter_commits(max_count=max_count):
            commits.append({
                'sha': str(commit)[:7],
                'author': str(commit.author),
                'date': commit.committed_datetime,
                'message': commit.message.strip().split('\n')[0],
                'full_message': commit.message.strip()
            })
        
        return commits
    
    def get_diff(self, file_path: Optional[str] = None, staged: bool = False) -> str:
        if not self.repo:
            return ""
        
        if staged:
            diff = self.repo.git.diff('--cached', file_path if file_path else None)
        else:
            diff = self.repo.git.diff(file_path if file_path else None)
        
        return diff
    
    def checkout_branch(self, branch_name: str):
        if not self.repo:
            return
        self.repo.git.checkout(branch_name)
    
    def create_branch(self, branch_name: str):
        if not self.repo:
            return
        self.repo.create_head(branch_name)
        self.checkout_branch(branch_name)
    
    def delete_branch(self, branch_name: str, force: bool = False):
        if not self.repo:
            return
        if force:
            self.repo.git.branch('-D', branch_name)
        else:
            self.repo.git.branch('-d', branch_name)
    
    def pull(self):
        if not self.repo:
            return
        origin = self.repo.remotes.origin
        origin.pull()
    
    def push(self, set_upstream: bool = False):
        if not self.repo:
            return
        origin = self.repo.remotes.origin
        if set_upstream:
            origin.push(set_upstream=True)
        else:
            origin.push()
    
    def fetch(self):
        if not self.repo:
            return
        for remote in self.repo.remotes:
            remote.fetch()
    
    def stash(self, message: Optional[str] = None):
        if not self.repo:
            return
        if message:
            self.repo.git.stash('save', message)
        else:
            self.repo.git.stash()
    
    def stash_pop(self):
        if not self.repo:
            return
        self.repo.git.stash('pop')
    
    def get_stashes(self) -> List[Dict[str, str]]:
        if not self.repo:
            return []
        
        try:
            stash_list = self.repo.git.stash('list').strip().split('\n')
            if stash_list == ['']:
                return []
            
            stashes = []
            for stash in stash_list:
                parts = stash.split(': ', 2)
                if len(parts) >= 2:
                    stashes.append({
                        'index': parts[0],
                        'branch': parts[1].split(' ')[-1],
                        'message': parts[2] if len(parts) > 2 else ''
                    })
            return stashes
        except:
            return []
    
    def merge(self, branch_name: str):
        if not self.repo:
            return
        self.repo.git.merge(branch_name)
    
    def rebase(self, branch_name: str):
        if not self.repo:
            return
        self.repo.git.rebase(branch_name)
    
    def abort_rebase(self):
        if not self.repo:
            return
        self.repo.git.rebase('--abort')
    
    def continue_rebase(self):
        if not self.repo:
            return
        self.repo.git.rebase('--continue')
    
    def get_remotes(self) -> List[Dict[str, str]]:
        if not self.repo:
            return []
        
        remotes = []
        for remote in self.repo.remotes:
            remotes.append({
                'name': remote.name,
                'url': list(remote.urls)[0] if remote.urls else ''
            })
        return remotes
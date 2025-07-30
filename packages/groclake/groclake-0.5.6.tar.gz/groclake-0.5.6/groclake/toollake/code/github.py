import requests
from typing import Dict, Any
import ast
from urllib.parse import urlparse

class GitHub:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize the GitHubRevert class with repository details.
        
        Args:
            owner (str): GitHub repository owner/username
            repo (str): GitHub repository name
            github_token (str, optional): GitHub personal access token. If None, will try to load from environment.
        """
        self.owner = tool_config.get("owner")
        self.repo = tool_config.get("repo")
        self.branch = tool_config.get("branch", "main")
        self.path = tool_config.get("path", "")
        self.base_api = tool_config.get("base_api", "https://api.github.com")
        
        # Load token from argument or environment
        if tool_config.get("token"):
            self.github_token = tool_config.get("token")
            
        if not self.github_token:
            raise ValueError("GitHub token not provided and not found in environment variables")
            
        # Set up API headers
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_last_merged_pr(self):
        """Get the last merged pull request in the repository."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls?state=closed&sort=updated&direction=desc"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            prs = response.json()
            for pr in prs:
                if pr.get("merged_at"):
                    return pr
        
        print("No merged PRs found.")
        return None

    def branch_exists(self, branch_name):
        """Check if a branch exists in the repository."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200

    def delete_branch(self, branch_name):
        """Delete a branch from the repository."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 204

    def create_branch(self, branch_name, base_sha):
        """Create a new branch in the repository."""
        if self.branch_exists(branch_name):
            print(f"Branch '{branch_name}' already exists. Deleting it...")
            if not self.delete_branch(branch_name):
                print(f"Failed to delete branch '{branch_name}'.")
                return False
        
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs"
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 201:
            print(f"Branch '{branch_name}' created successfully.")
            return True
        else:
            print(f"Failed to create branch: {response.json()}")
            return False

    def get_commit_details(self, commit_sha):
        """Get details of a specific commit."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{commit_sha}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch commit details: {response.json()}")
            return None
        
        return response.json()

    def create_revert_commit(self, branch_name, merge_commit_sha):
        """Create a commit that reverts changes from a merge commit."""
        commit_data = self.get_commit_details(merge_commit_sha)
        if not commit_data:
            return False

        parent_sha = commit_data["parents"][0]["sha"]
        parent_commit_data = self.get_commit_details(parent_sha)
        if not parent_commit_data:
            return False
        
        parent_tree_sha = parent_commit_data["commit"]["tree"]["sha"]
        
        revert_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/commits"
        revert_payload = {
            "message": f"Revert PR changes from commit {merge_commit_sha}",
            "parents": [commit_data["sha"]],
            "tree": parent_tree_sha
        }

        revert_response = requests.post(revert_url, json=revert_payload, headers=self.headers)
        
        if revert_response.status_code != 201:
            print(f"Failed to create revert commit: {revert_response.json()}")
            return False

        revert_commit_sha = revert_response.json()["sha"]
        
        update_branch_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
        update_payload = {
            "sha": revert_commit_sha,
            "force": True
        }
        update_response = requests.patch(update_branch_url, json=update_payload, headers=self.headers)
        
        if update_response.status_code == 200:
            print(f"Branch '{branch_name}' updated with correct revert commit.")
            return True
        else:
            print(f"Failed to update branch: {update_response.json()}")
            return False

    def create_revert_pr(self, branch_name, pr):
        """Create a pull request to revert changes."""
        pr_number = pr["number"]
        pr_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls"
        payload = {
            "title": f"Revert PR #{pr_number}",
            "head": f"{self.owner}:{branch_name}",
            "base": "main",
            "body": f"This PR reverts the changes from PR #{pr_number}."
        }
        response = requests.post(pr_url, json=payload, headers=self.headers)
        
        if response.status_code == 201:
            pr_data = response.json()
            print(f"Revert PR created: {pr_data['html_url']}")
            return pr_data["number"]
        else:
            print(f"Failed to create revert PR: {response.json()}")
            return None

    def automerge_pr(self, pr_number):
        """Automatically merge a pull request."""
        merge_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_number}/merge"
        merge_payload = {"commit_title": f"Auto-merging PR #{pr_number}"}
        response = requests.put(merge_url, json=merge_payload, headers=self.headers)
        
        if response.status_code == 200:
            print(f"PR #{pr_number} merged successfully.")
            return True
        else:
            print(f"Failed to merge PR: {response.json()}")
            return False

    def revert_pr(self, pr_number=None):
        """
        Revert a specific PR by number, or the last merged PR if no number provided.
        
        Args:
            pr_number (int, optional): PR number to revert. If None, reverts the last merged PR.
            
        Returns:
            bool: True if revert was successful, False otherwise
        """
        if pr_number:
            # Get specific PR details
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200 or not response.json().get("merged"):
                print(f"PR #{pr_number} not found or not merged.")
                return False
            pr = response.json()
        else:
            # Get last merged PR
            pr = self.get_last_merged_pr()
            
        if not pr:
            return False
        
        pr_number = pr["number"]
        merge_commit_sha = pr["merge_commit_sha"]
        branch_name = f"revert-pr-{pr_number}"

        # Get main branch SHA
        main_branch_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/main"
        main_response = requests.get(main_branch_url, headers=self.headers)
        
        if main_response.status_code != 200:
            print(f"Failed to fetch main branch details: {main_response.json()}")
            return False
        
        main_sha = main_response.json()["object"]["sha"]
        
        # Create branch, revert commit, create PR and merge
        if not self.create_branch(branch_name, main_sha):
            return False
        
        if not self.create_revert_commit(branch_name, merge_commit_sha):
            return False
        
        new_pr_id = self.create_revert_pr(branch_name, pr)
        if not new_pr_id:
            return False
        
        return self.automerge_pr(new_pr_id)

    
    def fetch_repo_files(self, path="", branch="main", owner="", repo=""):
        """Fetch all files recursively and build the directory structure."""
        if path:
            path = f"{path}"
        else:
            path = self.path

        if owner:
            owner = f"{owner}"
        else:
            owner = f"{self.owner}"

        if repo:
            repo = f"{repo}"
        else:
            repo = f"{self.repo}"

        if branch:
            branch = f"{branch}"
        else:
            branch = f"{self.branch}"

        url = f"{self.base_api}/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return {}

        files = response.json()
        file_structure = []

        for file in files:
            if file['type'] == 'file' and file['name'].endswith('.py') and not file['name'].startswith('.') and not file['name'].startswith('_'):
                commit_info = self.get_file_commit_details(file['html_url'])
                
                file_structure.append({
                    'name': file['name'],
                    'path': file['path'],
                    'type': 'codebase',
                    'subtype': 'python_file',
                    'url': file['download_url'],
                    'html_url': file['html_url'],
                    'last_modified_time': commit_info.get('last_modified_time'),
                    'commit_message': commit_info.get('commit_message'),
                    'committer_name': commit_info.get('committer_name')
                })
            elif file['type'] == 'dir':
                file_structure_dir = self.fetch_repo_files(file['path'])
                file_structure.append(file_structure_dir)

        return file_structure

    def traverse_and_analyze(self, node, path_prefix=""):
        """Recursively traverse the file tree and analyze .py files."""
        results = []
        for name, info in node.items():
            if info['type'] == 'file':
                response = requests.get(info['url'], headers=self.headers)
                if response.status_code == 200:
                    content = response.text
                    analysis = self.analyze_code(content, name)
                    if analysis:
                        commit_info = self.get_file_commit_details(info['html_url'])
                        results.append({
                            'repo': f"{self.github_user}/{self.repo_name}",
                            'repo_url': f"https://github.com/{self.github_user}/{self.repo_name}",
                            'file_url': analysis['file_url'],
                            'imports': analysis['imports'],
                            'classes': analysis['classes'],
                            'last_modified_time': commit_info.get('last_modified_time'),
                            'commit_message': commit_info.get('commit_message'),
                            'committer_name': commit_info.get('committer_name')
                        })
            elif info['type'] == 'dir':
                results.extend(self.traverse_and_analyze(info['children'], path_prefix=name + '/'))
        return results

    def analyze_code(self, file_content, file_url):
        """Analyze Python code for imports and classes."""
        try:
            tree = ast.parse(file_content)
        except SyntaxError as e:
            print(f"Syntax error in file {file_url}: {e}")
            return {}

        imports = []
        classes = {}

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                methods = []
                for n in node.body:
                    if isinstance(n, ast.FunctionDef):
                        methods.append(n.name)
                classes[class_name] = methods

        return {
            "file_url": file_url,
            "imports": imports,
            "classes": classes
        }

    def get_file_commit_details(self, github_file_url: str):
        """
        Fetch file's last modified time, commit message, and committer name from GitHub file URL.
        """
        parsed = urlparse(github_file_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 5 or path_parts[2] != 'blob':
            raise ValueError("Invalid GitHub file URL. Expected format: https://github.com/{owner}/{repo}/blob/{branch}/{file_path}")

        owner, repo, _, branch_from_url, *file_path_parts = path_parts
        repo_full_name = f"{owner}/{repo}"
        file_path = '/'.join(file_path_parts)

        url = f"https://api.github.com/repos/{repo_full_name}/commits"
        params = {"path": file_path, "sha": branch_from_url, "per_page": 1}
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                commit = data[0]['commit']
                author = commit['author']
                return {
                    "last_modified_time": commit['committer']['date'],
                    "commit_message": commit['message'],
                    "committer_name": author['name']
                }
            else:
                return {
                    "last_modified_time": None,
                    "commit_message": None,
                    "committer_name": None
                }
        else:
            print(f"Failed to fetch commit info for {file_path}: {response.status_code}")
            return {
                "last_modified_time": None,
                "commit_message": None,
                "committer_name": None
            }

    def analyze_repo(self):
        """Analyze the entire repository."""
        file_structure = self.fetch_repo_files()
        return self.traverse_and_analyze(file_structure)

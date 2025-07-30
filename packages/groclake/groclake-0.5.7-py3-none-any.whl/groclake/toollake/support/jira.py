from jira import JIRA
import re
from typing import Dict, Any

class Jira:
    def __init__(self, tool_config: Dict[str, Any]):
        """Initialize Jira connection"""
        self.jira = JIRA(server=tool_config.get("server"), basic_auth=(tool_config.get("username"), tool_config.get("api_token")))

    def _validate_email(self, email):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, str(email)))

    def _validate_project_key(self, project_key):
        """Validate Jira project key format (e.g., 'PROJ')"""
        return bool(re.match(r'^[A-Za-z][A-Za-z0-9_-]+$', str(project_key)))

    def create_issue(self, payload):
        """Create a new Jira issue"""
        required_fields = ["summary", "description", "project", "issuetype"]
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            return {"message": "Missing required fields", "error": ", ".join(missing_fields)}

        issue_dict = {
            'fields': {
                'project': {'key': payload['project']},
                'summary': payload['summary'],
                'description': payload['description'],
                'issuetype': {'name': payload['issuetype']}
            }
        }

        try:
            issue = self.jira.create_issue(fields=issue_dict)
            return {"message": "Issue created successfully", "issue_id": issue.key}
        except Exception as e:
            return {"message": "Error creating issue", "error": str(e)}

    def fetch_issue(self, issue_id):
        """Fetch issue details"""
        try:
            issue = self.jira.issue(issue_id)
            return {
                "message": "Issue fetched successfully",
                "data": {
                    "id": issue.key,
                    "summary": issue.fields.summary,
                    "description": issue.fields.description,
                    "status": issue.fields.status.name,
                    "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None
                }
            }
        except Exception as e:
            return {"message": "Error fetching issue", "error": str(e)}

    def update_issue(self, issue_id, update_fields):
        """Update a Jira issue"""
        try:
            issue = self.jira.issue(issue_id)
            issue.update(fields=update_fields)
            return {"message": f"Issue {issue_id} updated successfully"}
        except Exception as e:
            return {"message": "Error updating issue", "error": str(e)}

    def fetch_project_issues(self, project_key):
        """Fetch all issues for a given project"""
        try:
            jql = f'project = "{project_key}" ORDER BY created DESC'
            issues = self.jira.search_issues(jql, maxResults=10, fields="*all")
            return {"message": "Project issues fetched successfully", "data": [
                {"id": issue.key, "summary": issue.fields.summary, "status": issue.fields.status.name}
                for issue in issues
            ]}
        except Exception as e:
            return {"message": "Error fetching project issues", "error": str(e)}

    def fetch_user_issues(self, email):
        """Fetch all issues assigned to a user"""
        if not self._validate_email(email):
            return {"message": "Invalid email format", "error": email}

        try:
            jql = f'assignee = "{email}" ORDER BY created DESC'
            issues = self.jira.search_issues(jql, maxResults=10, fields="*all")
            return {"message": "User issues fetched successfully", "data": [
                {"id": issue.key, "summary": issue.fields.summary, "status": issue.fields.status.name}
                for issue in issues
            ]}
        except Exception as e:
            return {"message": "Error fetching user issues", "error": str(e)}

    def get_available_issue_types(self, project_key):
        """Get available issue types for a specific project"""
        try:
            meta = self.jira.createmeta(projectKeys=project_key, expand="projects.issuetypes")
            if meta["projects"]:
                project = meta["projects"][0]
                return {"message": "Issue types fetched successfully", "data": [issuetype["name"] for issuetype in project["issuetypes"]]}
            return {"message": "No issue types found"}
        except Exception as e:
            return {"message": "Error fetching issue types", "error": str(e)}

    def attach_file(self, issue_id, file_path):
        """Attach a file to an existing Jira issue."""
        try:
            with open(file_path, "rb") as file:
                self.jira.add_attachment(issue=issue_id, attachment=file)
            return {"message": f"File '{file_path}' attached successfully to issue {issue_id}"}
        except Exception as e:
            return {"message": "Error attaching file", "error": str(e)}

    def update_issue_status(self, issue_id, new_status):
        """Update Jira issue status via transition"""
        try:
            transitions = self.jira.transitions(issue_id)
            transition_id = next(
                (t["id"] for t in transitions if t["name"].lower() == new_status.lower()), None
            )

            if not transition_id:
                return {"message": "Invalid status transition", "error": f"Status '{new_status}' not found"}

            self.jira.transition_issue(issue_id, transition_id)
            return {"message": f"Issue {issue_id} status updated to '{new_status}'"}

        except Exception as e:
            return {"message": "Error updating issue status", "error": str(e)}
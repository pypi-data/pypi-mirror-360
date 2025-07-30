# src/diagram_to_iac/agents/git_langgraph/pr.py
import git
import os

class GitPrCreator:
    def __init__(self, repo_path: str, remote_name: str = "origin", copilot_assignee: str = None, default_assignees: list = None):
        self.repo_path = repo_path
        self.remote_name = remote_name
        self.copilot_assignee = copilot_assignee
        self.default_assignees = default_assignees if default_assignees else []
        try:
            self.repo = git.Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            print(f"Warning: {self.repo_path} is not a valid git repository.")
            self.repo = None
        except Exception as e:
            print(f"An unexpected error occurred during GitPrCreator initialization: {e}")
            self.repo = None


    def create_draft_pr(self, error_type: str, title: str, body: str):
        if not self.repo:
            print(f"Error: Git repository not initialized at {self.repo_path}. Cannot create PR.")
            return {"status": "error", "message": "Git repository not initialized", "branch_name": None, "pr_url": None, "title": title, "body": body, "assignees": []}

        branch_name = f"feature/auto-fix-{error_type}"
        original_branch_name = "Unknown"

        try:
            # Store the original branch name
            if not self.repo.head.is_detached:
                original_branch_name = self.repo.active_branch.name
            else:
                # If HEAD is detached, decide on a fallback strategy.
                # For now, we'll attempt to use 'main' or 'master' if they exist, otherwise error out or use a default.
                # This part might need more sophisticated logic depending on desired behavior.
                print("Warning: HEAD is detached. Attempting to find a default branch (main/master) to return to.")
                found_default = False
                for default_name in ['main', 'master']:
                    if default_name in self.repo.heads:
                        original_branch_name = default_name
                        found_default = True
                        break
                if not found_default:
                    print("Error: HEAD is detached and could not determine a default branch to return to. PR creation will proceed but checkout back might fail.")
                    # original_branch_name will remain "Unknown" or could be set to a specific commit SHA if needed.

            print(f"Original branch context: {original_branch_name}")

            # Fetch from origin to have up-to-date refs
            # Ensure remote 'origin' (or self.remote_name) exists
            if self.remote_name in [remote.name for remote in self.repo.remotes]:
                origin = self.repo.remote(name=self.remote_name)
                print(f"Fetching from remote '{self.remote_name}'...")
                origin.fetch()
            else:
                print(f"Warning: Remote '{self.remote_name}' not found. Skipping fetch.")


            # Check if branch already exists, if so, check it out. Otherwise, create it.
            if branch_name in self.repo.heads:
                print(f"Branch '{branch_name}' already exists. Checking it out.")
                new_branch = self.repo.heads[branch_name]
            else:
                print(f"Creating new branch: '{branch_name}'")
                new_branch = self.repo.create_head(branch_name)

            new_branch.checkout()
            print(f"Checked out branch: {new_branch.name}")

            # Stage changes and commit
            if self.repo.is_dirty(untracked_files=True):
                self.repo.git.add(A=True)
                commit_message = f"Auto-fix for {error_type}: {title}"
                self.repo.index.commit(commit_message)
                print(f"Committed changes with message: '{commit_message}'")
            else:
                commit_message = f"Initial commit for auto-fix branch {error_type}: {title}"
                self.repo.git.commit(m=commit_message, allow_empty=True)
                print(f"Created an empty commit with message: '{commit_message}'")

            # Push the new branch to the remote and set upstream
            if self.remote_name in [remote.name for remote in self.repo.remotes]:
                origin = self.repo.remote(name=self.remote_name)
                print(f"Pushing branch {branch_name} to remote {self.remote_name} and setting upstream.")
                self.repo.git.push('--set-upstream', origin.name, new_branch.name)
            else:
                print(f"Warning: Remote '{self.remote_name}' not found. Cannot push branch.")
                # Depending on requirements, may want to error out here or proceed without push
                # For now, we'll allow it to proceed and the PR URL will be local only.


            # Determine assignee
            assignees_to_set = []
            if self.copilot_assignee: # Prioritize copilot_assignee
                assignees_to_set.append(self.copilot_assignee)
            elif self.default_assignees: # Fallback to default_assignees
                assignees_to_set.extend(self.default_assignees)

            assignee_text = f"Assignees: {', '.join(assignees_to_set)}" if assignees_to_set else "Assignees: None"

            # Placeholder for creating the actual PR
            pr_url = f"https://github.com/your-org/your-repo/pull/new/{branch_name}" # Example URL, adapt as needed
            print(f"Branch {branch_name} pushed to {self.remote_name}.")
            print(f"To create a Pull Request (manual step for now):")
            print(f"  URL: {pr_url}")
            print(f"  Title: {title}")
            print(f"  Body: {body}")
            print(f"  Base Branch: {original_branch_name if original_branch_name != 'Unknown' else 'your_default_branch'}") # Clarify base
            print(assignee_text)

            # Checkout back to original branch if it was known and not detached (or a known default)
            if original_branch_name != "Unknown" and original_branch_name in self.repo.heads:
                print(f"Checking out back to original branch: {original_branch_name}")
                self.repo.git.checkout(original_branch_name)
            elif not self.repo.head.is_detached:
                 # If original_branch_name was 'Unknown' but we are not detached, try to go back to active_branch before this method.
                 # This case should ideally not happen if original_branch_name is captured correctly.
                 print(f"Attempting to checkout back to the branch active before this operation: {self.repo.active_branch.name}")
                 # This might be risky if the active branch changed unexpectedly.
            else:
                print(f"Could not check out back to a specific branch (original was detached or unknown). Current branch: {self.repo.active_branch.name}")


            return {"status": "success", "branch_name": branch_name, "pr_url": pr_url, "title": title, "body": body, "assignees": assignees_to_set}

        except git.exc.GitCommandError as e:
            print(f"Git command failed: {e}")
            if original_branch_name != "Unknown" and original_branch_name in self.repo.heads:
                try:
                    if self.repo.active_branch.name != original_branch_name:
                        self.repo.git.checkout(original_branch_name)
                        print(f"Checked out back to original branch: {original_branch_name} after GitCommandError.")
                except Exception as ex_inner:
                    print(f"Failed to checkout back to {original_branch_name} after GitCommandError: {ex_inner}")
            return {"status": "error", "message": str(e), "branch_name": branch_name, "pr_url": None, "title": title, "body": body, "assignees": []}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if original_branch_name != "Unknown" and original_branch_name in self.repo.heads:
                try:
                    if self.repo.active_branch.name != original_branch_name:
                        self.repo.git.checkout(original_branch_name)
                        print(f"Checked out back to original branch: {original_branch_name} after unexpected error.")
                except Exception as ex_inner:
                    print(f"Failed to checkout back to {original_branch_name} after unexpected error: {ex_inner}")
            return {"status": "error", "message": str(e), "branch_name": branch_name, "pr_url": None, "title": title, "body": body, "assignees": []}

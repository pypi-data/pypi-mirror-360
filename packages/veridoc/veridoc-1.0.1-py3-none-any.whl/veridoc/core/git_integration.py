"""
VeriDoc Git Integration
Git operations for documentation change tracking
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

class GitIntegration:
    """Handles Git operations for documentation tracking"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path) if isinstance(base_path, str) else base_path
        self.git_dir = self.base_path / ".git"
        self._is_git_repo = None
    
    @property
    def is_git_repository(self) -> bool:
        """Check if the base path is a Git repository"""
        if self._is_git_repo is None:
            self._is_git_repo = self.git_dir.exists() or self._find_git_root() is not None
        return self._is_git_repo
    
    def _find_git_root(self) -> Optional[Path]:
        """Find the Git root directory by traversing up"""
        current = self.base_path
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return None
    
    async def get_file_status(self, file_path: Path) -> Dict[str, Any]:
        """Get Git status information for a file"""
        if not self.is_git_repository:
            return {"tracked": False, "status": "untracked"}
        
        try:
            rel_path = file_path.relative_to(self.base_path)
            
            # Get file status
            result = await self._run_git_command(["status", "--porcelain", str(rel_path)])
            
            if not result.strip():
                # File is tracked and clean
                return {
                    "tracked": True,
                    "status": "clean",
                    "modified": False,
                    "staged": False
                }
            
            status_line = result.strip()
            index_status = status_line[0] if len(status_line) > 0 else ' '
            working_status = status_line[1] if len(status_line) > 1 else ' '
            
            return {
                "tracked": index_status != '?' and working_status != '?',
                "status": self._parse_status_code(index_status, working_status),
                "modified": working_status in ['M', 'D', 'A'],
                "staged": index_status in ['M', 'D', 'A', 'R', 'C'],
                "index_status": index_status,
                "working_status": working_status
            }
            
        except Exception as e:
            return {"tracked": False, "status": "error", "error": str(e)}
    
    async def get_file_history(self, file_path: Path, limit: int = 10) -> List[Dict[str, Any]]:
        """Get commit history for a file"""
        if not self.is_git_repository:
            return []
        
        try:
            rel_path = file_path.relative_to(self.base_path)
            
            # Get commit history
            result = await self._run_git_command([
                "log", 
                "--follow",
                f"--max-count={limit}",
                "--pretty=format:%H|%an|%ae|%ad|%s",
                "--date=iso",
                str(rel_path)
            ])
            
            commits = []
            for line in result.strip().split('\n'):
                if line:
                    parts = line.split('|', 4)
                    if len(parts) == 5:
                        commits.append({
                            "hash": parts[0],
                            "author_name": parts[1],
                            "author_email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        })
            
            return commits
            
        except Exception as e:
            return []
    
    async def get_file_diff(self, file_path: Path, commit_hash: Optional[str] = None) -> str:
        """Get diff for a file"""
        if not self.is_git_repository:
            return ""
        
        try:
            rel_path = file_path.relative_to(self.base_path)
            
            if commit_hash:
                # Diff against specific commit
                result = await self._run_git_command(["diff", commit_hash, str(rel_path)])
            else:
                # Diff against HEAD (uncommitted changes)
                result = await self._run_git_command(["diff", "HEAD", str(rel_path)])
            
            return result
            
        except Exception:
            return ""
    
    async def get_repository_info(self) -> Dict[str, Any]:
        """Get general repository information"""
        if not self.is_git_repository:
            return {"is_repo": False}
        
        try:
            # Get current branch
            branch_result = await self._run_git_command(["branch", "--show-current"])
            current_branch = branch_result.strip()
            
            # Get remote URL
            remote_result = await self._run_git_command(["remote", "get-url", "origin"])
            remote_url = remote_result.strip() if remote_result.strip() else None
            
            # Get commit count
            commit_count_result = await self._run_git_command(["rev-list", "--count", "HEAD"])
            commit_count = int(commit_count_result.strip()) if commit_count_result.strip().isdigit() else 0
            
            # Get last commit info
            last_commit_result = await self._run_git_command([
                "log", "-1", "--pretty=format:%H|%an|%ad|%s", "--date=iso"
            ])
            
            last_commit = None
            if last_commit_result.strip():
                parts = last_commit_result.strip().split('|', 3)
                if len(parts) == 4:
                    last_commit = {
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    }
            
            # Get status summary
            status_result = await self._run_git_command(["status", "--porcelain"])
            modified_files = len([line for line in status_result.strip().split('\n') if line])
            
            return {
                "is_repo": True,
                "current_branch": current_branch,
                "remote_url": remote_url,
                "commit_count": commit_count,
                "last_commit": last_commit,
                "modified_files": modified_files
            }
            
        except Exception as e:
            return {"is_repo": True, "error": str(e)}
    
    async def get_changed_files(self) -> List[Dict[str, Any]]:
        """Get list of changed files in the repository"""
        if not self.is_git_repository:
            return []
        
        try:
            result = await self._run_git_command(["status", "--porcelain"])
            
            files = []
            for line in result.strip().split('\n'):
                if line:
                    index_status = line[0] if len(line) > 0 else ' '
                    working_status = line[1] if len(line) > 1 else ' '
                    file_path = line[3:].strip()
                    
                    files.append({
                        "path": file_path,
                        "status": self._parse_status_code(index_status, working_status),
                        "index_status": index_status,
                        "working_status": working_status
                    })
            
            return files
            
        except Exception:
            return []
    
    async def _run_git_command(self, args: List[str]) -> str:
        """Run a Git command and return the output"""
        try:
            # Find git root if different from base_path
            git_root = self._find_git_root() or self.base_path
            
            process = await asyncio.create_subprocess_exec(
                "git",
                *args,
                cwd=str(git_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode('utf-8', errors='ignore')
            else:
                raise subprocess.CalledProcessError(
                    process.returncode, 
                    ["git"] + args, 
                    stderr.decode('utf-8', errors='ignore')
                )
                
        except Exception as e:
            raise e
    
    def _parse_status_code(self, index_status: str, working_status: str) -> str:
        """Parse Git status codes into human-readable status"""
        if index_status == '?' and working_status == '?':
            return "untracked"
        elif index_status == 'A':
            return "added"
        elif index_status == 'M':
            return "modified"
        elif index_status == 'D':
            return "deleted"
        elif index_status == 'R':
            return "renamed"
        elif index_status == 'C':
            return "copied"
        elif working_status == 'M':
            return "modified"
        elif working_status == 'D':
            return "deleted"
        else:
            return "clean"
    
    def get_relative_path(self, file_path: Path) -> str:
        """Get relative path from repository root"""
        try:
            git_root = self._find_git_root() or self.base_path
            return str(file_path.relative_to(git_root))
        except ValueError:
            return str(file_path)
    
    def get_git_status(self) -> Optional[Dict[str, Any]]:
        """Get Git status information (synchronous version for tests)"""
        if not self.is_git_repository:
            return None
        
        try:
            # Run synchronously for tests
            result = subprocess.run(
                ["git", "status", "--porcelain", "-b"],
                cwd=str(self._find_git_root() or self.base_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            lines = result.stdout.strip().split('\n')
            branch = "main"
            modified = []
            untracked = []
            added = []
            deleted = []
            
            for line in lines:
                if line.startswith('##'):
                    # Branch information
                    parts = line[3:].split('...')
                    if parts:
                        branch = parts[0].strip()
                elif line.strip():
                    # File status
                    index_status = line[0] if len(line) > 0 else ' '
                    working_status = line[1] if len(line) > 1 else ' '
                    file_path = line[3:].strip()
                    
                    if index_status == 'A' or working_status == 'A':
                        added.append(file_path)
                    elif index_status == 'M' or working_status == 'M':
                        modified.append(file_path)
                    elif index_status == 'D' or working_status == 'D':
                        deleted.append(file_path)
                    elif index_status == '?' and working_status == '?':
                        untracked.append(file_path)
            
            return {
                "modified": modified,
                "untracked": untracked,
                "added": added,
                "deleted": deleted,
                "branch": branch,
                "clean": len(modified) == 0 and len(added) == 0 and len(deleted) == 0
            }
            
        except Exception:
            return None
    
    def get_git_log(self, limit: int = 10, file_path: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get Git log information (synchronous version for tests)"""
        if not self.is_git_repository:
            return None
        
        try:
            args = ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%an|%ad|%s", "--date=iso"]
            if file_path:
                args.extend(["--", file_path])
            
            result = subprocess.run(
                args,
                cwd=str(self._find_git_root() or self.base_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            
            return commits
            
        except Exception:
            return None
    
    def get_git_diff(self, file_path: Optional[str] = None, commit_hash: Optional[str] = None) -> Optional[str]:
        """Get Git diff information (synchronous version for tests)"""
        if not self.is_git_repository:
            return None
        
        try:
            args = ["git", "diff"]
            if commit_hash:
                args.append(commit_hash)
            if file_path:
                args.extend(["--", file_path])
            
            result = subprocess.run(
                args,
                cwd=str(self._find_git_root() or self.base_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            return result.stdout
            
        except Exception:
            return None
    
    def get_current_branch(self) -> Optional[str]:
        """Get current Git branch (synchronous version for tests)"""
        if not self.is_git_repository:
            return None
        
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=str(self._find_git_root() or self.base_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            branch = result.stdout.strip()
            return branch if branch != "HEAD" else None
            
        except Exception:
            return None
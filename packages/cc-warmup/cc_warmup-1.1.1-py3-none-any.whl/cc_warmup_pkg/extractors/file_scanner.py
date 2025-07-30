"""File system scanner for Claude data directories and JSONL files."""

import os
from pathlib import Path
from typing import List, Dict, Optional, Set
import logging

from ..data_structures import AnalysisResult


class ClaudeFileScanner:
    """Scans Claude data directories to discover JSONL files following ccusage patterns."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def discover_claude_directories(self) -> List[Path]:
        """
        Discover Claude data directories following ccusage priority order.
        
        Returns:
            List of valid Claude data directories
        """
        directories = []
        
        # Check environment variable first
        env_dirs = os.environ.get('CLAUDE_CONFIG_DIR')
        if env_dirs:
            for dir_path in env_dirs.split(','):
                path = Path(dir_path.strip()).expanduser()
                if path.exists() and path.is_dir():
                    directories.append(path)
                    self.logger.debug(f"Added CLAUDE_CONFIG_DIR: {path}")
        
        # Default directory discovery (priority order)
        default_paths = [
            Path.home() / ".config" / "claude",  # Claude Code v2+ default
            Path.home() / ".claude",             # Claude Code v1 legacy
        ]
        
        for path in default_paths:
            if path.exists() and path.is_dir() and path not in directories:
                directories.append(path)
                self.logger.debug(f"Added default directory: {path}")
        
        if not directories:
            self.logger.warning("No Claude data directories found")
        else:
            self.logger.info(f"Discovered {len(directories)} Claude data directories")
        
        return directories
    
    def scan_project_directories(self, claude_dirs: List[Path]):
        """
        Scan Claude directories for project subdirectories.
        
        Args:
            claude_dirs: List of Claude data directories to scan
            
        Returns:
            AnalysisResult containing dict mapping encoded project names to their paths
        """
        projects = {}
        total_scanned = 0
        errors = []
        
        for claude_dir in claude_dirs:
            projects_dir = claude_dir / "projects"
            if not projects_dir.exists():
                self.logger.debug(f"No projects directory in {claude_dir}")
                continue
            
            try:
                for project_dir in projects_dir.iterdir():
                    total_scanned += 1
                    if project_dir.is_dir():
                        encoded_name = project_dir.name
                        projects[encoded_name] = project_dir
                        self.logger.debug(f"Found project: {encoded_name}")
            except Exception as e:
                error_msg = f"Error scanning {projects_dir}: {e}"
                errors.append(error_msg)
                self.logger.warning(error_msg)
        
        if not projects and errors:
            return AnalysisResult.error_result(
                f"Failed to scan any projects. Errors: {'; '.join(errors)}",
                metadata={'errors': errors}
            )
        
        return AnalysisResult.success_result(
            projects,
            metadata={
                'total_scanned': total_scanned,
                'projects_found': len(projects),
                'errors': errors,
                'claude_dirs_checked': len(claude_dirs)
            }
        )
    
    def find_project_jsonl_files(self, project_dir: Path, 
                                max_depth: int = 3):
        """
        Find all JSONL files within a project directory.
        
        Args:
            project_dir: Project directory to scan
            max_depth: Maximum directory depth to scan
            
        Returns:
            AnalysisResult containing list of JSONL file paths
        """
        if not project_dir.exists() or not project_dir.is_dir():
            return AnalysisResult.error_result(f"Project directory does not exist: {project_dir}")
        
        jsonl_files = []
        errors = []
        
        try:
            # First check for JSONL files directly in the project directory
            for jsonl_file in project_dir.glob("*.jsonl"):
                if jsonl_file.is_file():
                    jsonl_files.append(jsonl_file)
                    self.logger.debug(f"Found JSONL file: {jsonl_file}")
            
            # Also check subdirectories (session directories) up to max_depth
            for depth in range(1, max_depth + 1):
                pattern = "*/" * depth + "*.jsonl"
                for jsonl_file in project_dir.glob(pattern):
                    if jsonl_file.is_file() and jsonl_file not in jsonl_files:
                        jsonl_files.append(jsonl_file)
                        self.logger.debug(f"Found JSONL file: {jsonl_file}")
        
        except Exception as e:
            return AnalysisResult.error_result(f"Error scanning {project_dir}: {e}")
        
        # Sort by modification time (newest first)
        try:
            jsonl_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        except Exception as e:
            self.logger.warning(f"Could not sort files by modification time: {e}")
        
        return AnalysisResult.success_result(
            jsonl_files,
            metadata={
                'project_dir': str(project_dir),
                'files_found': len(jsonl_files),
                'max_depth_used': max_depth
            }
        )
    
    def scan_all_project_files(self, encoded_project_names: Optional[List[str]] = None,
                              max_depth: int = 3):
        """
        Scan all projects for JSONL files.
        
        Args:
            encoded_project_names: Optional list of specific projects to scan
            max_depth: Maximum directory depth to scan
            
        Returns:
            AnalysisResult containing dict mapping project names to JSONL file lists
        """
        # Discover directories
        claude_dirs = self.discover_claude_directories()
        if not claude_dirs:
            return AnalysisResult.error_result("No Claude data directories found")
        
        # Find project directories
        projects_result = self.scan_project_directories(claude_dirs)
        if not projects_result.success:
            return AnalysisResult.error_result(
                f"Failed to scan project directories: {projects_result.error}",
                metadata=projects_result.metadata
            )
        
        all_projects = projects_result.data
        
        # Filter projects if specific names requested
        if encoded_project_names:
            filtered_projects = {
                name: path for name, path in all_projects.items() 
                if name in encoded_project_names
            }
            if not filtered_projects:
                return AnalysisResult.error_result(
                    f"None of the requested projects found: {encoded_project_names}",
                    metadata={'available_projects': list(all_projects.keys())}
                )
            all_projects = filtered_projects
        
        # Scan each project for JSONL files
        project_files = {}
        scan_errors = []
        
        for project_name, project_dir in all_projects.items():
            files_result = self.find_project_jsonl_files(project_dir, max_depth)
            if files_result.success:
                project_files[project_name] = files_result.data
                self.logger.info(f"Project {project_name}: {len(files_result.data)} JSONL files")
            else:
                scan_errors.append(f"{project_name}: {files_result.error}")
                self.logger.warning(f"Failed to scan {project_name}: {files_result.error}")
        
        if not project_files and scan_errors:
            return AnalysisResult.error_result(
                f"Failed to scan any projects. Errors: {'; '.join(scan_errors)}",
                metadata={'errors': scan_errors}
            )
        
        return AnalysisResult.success_result(
            project_files,
            metadata={
                'projects_scanned': len(all_projects),
                'projects_with_files': len(project_files),
                'scan_errors': scan_errors,
                'total_files': sum(len(files) for files in project_files.values())
            }
        )
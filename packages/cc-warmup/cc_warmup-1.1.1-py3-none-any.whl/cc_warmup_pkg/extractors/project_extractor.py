"""Function 1: Per-project timestamp extraction from JSONL files.

This module implements the first of the three main functions requested:
Extract timestamps and project names from JSONL files with robust error handling.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from .file_scanner import ClaudeFileScanner
from .jsonl_parser import JSONLParser
from ..data_structures import ProjectRawData, AnalysisResult


class ProjectExtractor:
    """Extracts timestamps and project metadata from Claude usage JSONL files."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.file_scanner = ClaudeFileScanner(logger)
        self.jsonl_parser = JSONLParser(logger)
    
    def extract_project_timestamps(self, 
                                 encoded_project_name: str,
                                 lookback_hours: int = 168):
        """
        Extract timestamps and metadata for a single project.
        
        This is Function 1 as requested: per-project timestamps and project-name 
        extraction from JSONL files.
        
        Args:
            encoded_project_name: Encoded directory name (e.g., "-Users-...")
            lookback_hours: How many hours back to look for data (default: 7 days)
            
        Returns:
            AnalysisResult containing ProjectRawData or error details
        """
        extraction_start = datetime.utcnow()
        cutoff_time = extraction_start - timedelta(hours=lookback_hours)
        
        # Find project directory and JSONL files
        claude_dirs = self.file_scanner.discover_claude_directories()
        if not claude_dirs:
            return AnalysisResult.error_result("No Claude data directories found")
        
        project_dir = None
        for claude_dir in claude_dirs:
            potential_dir = claude_dir / "projects" / encoded_project_name
            if potential_dir.exists() and potential_dir.is_dir():
                project_dir = potential_dir
                break
        
        if not project_dir:
            return AnalysisResult.error_result(
                f"Project directory not found: {encoded_project_name}",
                metadata={'searched_directories': [str(d) for d in claude_dirs]}
            )
        
        # Find JSONL files in project
        files_result = self.file_scanner.find_project_jsonl_files(project_dir)
        if not files_result.success:
            return AnalysisResult.error_result(
                f"Failed to find JSONL files: {files_result.error}",
                metadata=files_result.metadata
            )
        
        jsonl_files = files_result.data
        if not jsonl_files:
            return AnalysisResult.error_result(
                f"No JSONL files found in project: {encoded_project_name}",
                metadata={'project_dir': str(project_dir)}
            )
        
        # Parse JSONL files
        parse_result = self.jsonl_parser.parse_files(jsonl_files)
        if not parse_result.success:
            return AnalysisResult.error_result(
                f"Failed to parse JSONL files: {parse_result.error}",
                metadata=parse_result.metadata
            )
        
        all_entries = parse_result.data
        
        # Filter by time cutoff
        recent_entries = [
            entry for entry in all_entries 
            if entry.timestamp >= cutoff_time
        ]
        
        # Extract project metadata
        project_metadata = self._extract_project_metadata(project_dir, recent_entries)
        
        # Prepare timestamps and metadata, separating warmup from user messages
        timestamps = [entry.timestamp for entry in recent_entries]
        entries_metadata = [entry.raw_data for entry in recent_entries]
        
        # Count warmup vs user messages
        warmup_count = sum(1 for entry in recent_entries if entry.is_warmup)
        user_count = len(recent_entries) - warmup_count
        
        processing_time = (datetime.utcnow() - extraction_start).total_seconds()
        
        # Create ProjectRawData
        project_data = ProjectRawData(
            project_name=project_metadata['display_name'],
            encoded_name=encoded_project_name,
            project_path=project_metadata['project_path'],
            timestamps=timestamps,
            entries_metadata=entries_metadata,
            extraction_time=extraction_start,
            extraction_stats={
                'jsonl_files_found': len(jsonl_files),
                'total_entries_parsed': len(all_entries),
                'recent_entries_kept': len(recent_entries),
                'user_messages': user_count,
                'warmup_messages': warmup_count,
                'warmup_ratio': warmup_count / len(recent_entries) if recent_entries else 0,
                'lookback_hours': lookback_hours,
                'processing_time_seconds': processing_time,
                'parse_stats': self.jsonl_parser.get_stats()
            }
        )
        
        self.logger.info(
            f"Extracted {len(timestamps)} timestamps for {project_metadata['display_name']} "
            f"({encoded_project_name}) from {len(jsonl_files)} files "
            f"({user_count} user messages, {warmup_count} warm-ups)"
        )
        
        return AnalysisResult.success_result(
            project_data,
            processing_time=processing_time,
            metadata={
                'project_dir': str(project_dir),
                'jsonl_files_processed': len(jsonl_files),
                'entries_extracted': len(timestamps)
            }
        )
    
    def extract_multiple_projects(self, 
                                encoded_project_names: Optional[List[str]] = None,
                                lookback_hours: int = 168):
        """
        Extract timestamps for multiple projects in batch.
        
        Args:
            encoded_project_names: Specific projects to extract, or None for all
            lookback_hours: How many hours back to look for data
            
        Returns:
            AnalysisResult containing list of ProjectRawData objects
        """
        extraction_start = datetime.utcnow()
        
        # Discover all projects if none specified
        if encoded_project_names is None:
            scan_result = self.file_scanner.scan_all_project_files()
            if not scan_result.success:
                return AnalysisResult.error_result(
                    f"Failed to discover projects: {scan_result.error}",
                    metadata=scan_result.metadata
                )
            encoded_project_names = list(scan_result.data.keys())
        
        # Extract each project
        project_data_list = []
        extraction_errors = []
        
        for encoded_name in encoded_project_names:
            result = self.extract_project_timestamps(encoded_name, lookback_hours)
            if result.success:
                project_data_list.append(result.data)
            else:
                extraction_errors.append(f"{encoded_name}: {result.error}")
                self.logger.warning(f"Failed to extract {encoded_name}: {result.error}")
        
        processing_time = (datetime.utcnow() - extraction_start).total_seconds()
        
        if not project_data_list and extraction_errors:
            return AnalysisResult.error_result(
                f"Failed to extract any projects. Errors: {'; '.join(extraction_errors)}",
                processing_time=processing_time,
                metadata={'extraction_errors': extraction_errors}
            )
        
        self.logger.info(
            f"Successfully extracted {len(project_data_list)} projects "
            f"({len(extraction_errors)} failed) in {processing_time:.2f}s"
        )
        
        return AnalysisResult.success_result(
            project_data_list,
            processing_time=processing_time,
            metadata={
                'projects_requested': len(encoded_project_names) if encoded_project_names else 0,
                'projects_extracted': len(project_data_list),
                'extraction_errors': extraction_errors,
                'total_timestamps': sum(len(p.timestamps) for p in project_data_list)
            }
        )
    
    def _extract_project_metadata(self, project_dir: Path, 
                                 entries: List) -> Dict[str, Any]:
        """Extract project metadata from directory and entries."""
        
        # Try to get actual project path from JSONL entries
        project_path = None
        display_name = project_dir.name
        
        # Look for 'cwd' field in entries to get real project path
        for entry in entries[:5]:  # Check first few entries
            if 'cwd' in entry.raw_data:
                try:
                    cwd_path = Path(entry.raw_data['cwd'])
                    # Skip if cwd is pointing to .claude/projects (warmup artifacts)
                    if '.claude/projects' not in str(cwd_path):
                        project_path = cwd_path
                        display_name = project_path.name
                        break
                except Exception:
                    continue
        
        # Fallback: try to decode the directory name
        if project_path is None:
            encoded_name = project_dir.name
            if encoded_name.startswith('-'):
                try:
                    decoded_path = encoded_name[1:].replace('-', '/')
                    potential_path = Path(decoded_path)
                    # Use the last part of the decoded path as project name
                    display_name = potential_path.name
                    if potential_path.exists():
                        project_path = potential_path
                except Exception:
                    pass
        
        # Final fallback: use project directory as project path
        if project_path is None:
            project_path = project_dir.parent.parent  # Go up from projects/encoded_name
            # If we still have the encoded name, try harder to decode it
            if display_name == project_dir.name and display_name.startswith('-'):
                # Extract the last meaningful part of the encoded name
                parts = display_name.split('-')
                if len(parts) > 1:
                    display_name = parts[-1]  # Take the last part
        
        return {
            'project_path': project_path,
            'display_name': display_name,
            'project_dir': project_dir
        }
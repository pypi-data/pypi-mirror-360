"""Global session processor - processes all projects together to create global sessions."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from .project_extractor import ProjectExtractor
from .improved_warmup_detector import ImprovedWarmupDetector
from ..data_structures import GlobalSessionResult, SessionData, ProjectSessionData, AnalysisResult, CategoryBreakdown, MessageCategory
from ..categorizers import MessageCategorizer


class GlobalSessionProcessor:
    """Processes all projects together to create global sessions across project boundaries."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.project_extractor = ProjectExtractor(logger)
        self.warmup_detector = ImprovedWarmupDetector()
        self.message_categorizer = MessageCategorizer(logger)
    
    def process_global_sessions(self, 
                              encoded_project_names: Optional[List[str]] = None,
                              lookback_hours: int = 168) -> AnalysisResult[GlobalSessionResult]:
        """
        Process all projects together to create global sessions.
        
        Args:
            encoded_project_names: Specific projects to process, or None for all
            lookback_hours: How many hours back to look for data
            
        Returns:
            AnalysisResult containing GlobalSessionResult or error details
        """
        processing_start = datetime.utcnow()
        
        # Step 1: Extract all projects' raw data
        self.logger.info("Extracting data from all projects...")
        projects_result = self.project_extractor.extract_multiple_projects(
            encoded_project_names, lookback_hours
        )
        
        if not projects_result.success:
            return AnalysisResult.error_result(f"Failed to extract projects: {projects_result.error}")
        
        project_data_list = projects_result.data
        if not project_data_list:
            return AnalysisResult.error_result("No projects found with data")
        
        # Step 2: Merge all entries chronologically with project tracking
        self.logger.info(f"Merging {len(project_data_list)} projects chronologically...")
        merged_entries = self._merge_all_project_entries(project_data_list)
        
        if not merged_entries:
            return AnalysisResult.success_result(GlobalSessionResult(
                global_sessions=[],
                project_lookup={},
                projects_metadata={},
                processing_time=0.0,
                total_entries=0,
                total_projects=len(project_data_list)
            ))
        
        # Step 3: Run global session grouping on merged timeline
        self.logger.info(f"Creating global sessions from {len(merged_entries)} merged entries...")
        global_sessions = self._group_entries_into_global_sessions(merged_entries)
        
        # Step 4: Create project lookup map
        project_lookup = self._create_project_lookup(global_sessions)
        
        # Step 5: Create projects metadata
        projects_metadata = {
            project.project_name: {
                'encoded_name': project.encoded_name,
                'project_path': str(project.project_path),
                'total_timestamps': len(project.timestamps),
                'extraction_stats': project.extraction_stats
            }
            for project in project_data_list
        }
        
        processing_time = (datetime.utcnow() - processing_start).total_seconds()
        
        self.logger.info(
            f"Created {len(global_sessions)} global sessions across {len(project_data_list)} projects "
            f"in {processing_time:.2f}s"
        )
        
        result = GlobalSessionResult(
            global_sessions=global_sessions,
            project_lookup=project_lookup,
            projects_metadata=projects_metadata,
            processing_time=processing_time,
            total_entries=len(merged_entries),
            total_projects=len(project_data_list)
        )
        
        return AnalysisResult.success_result(result, processing_time=processing_time)
    
    def _merge_all_project_entries(self, project_data_list: List) -> List[Tuple[str, Any, datetime, Dict, bool]]:
        """
        Merge all project entries chronologically.
        
        Returns:
            List of tuples: (project_name, entry_index, timestamp, raw_data, is_warmup)
        """
        merged_entries = []
        
        for project_data in project_data_list:
            project_name = project_data.project_name
            
            # Create merged entries with project tracking
            for i, (timestamp, raw_data) in enumerate(zip(project_data.timestamps, project_data.entries_metadata)):
                # Detect if this is a warmup (simple heuristic based on timing patterns)
                is_warmup = self._detect_warmup_entry(raw_data, timestamp)
                
                merged_entries.append((
                    project_name,
                    i,
                    timestamp,
                    raw_data,
                    is_warmup
                ))
        
        # Sort chronologically by timestamp
        merged_entries.sort(key=lambda x: x[2])  # Sort by timestamp (index 2)
        
        return merged_entries
    
    def _detect_warmup_entry(self, raw_data: Dict, timestamp: datetime) -> bool:
        """Detect if an entry is a warmup using STRICT detection."""
        
        # Use the improved warmup detector with STRICT checking
        return self.warmup_detector.detect_warmup_message(raw_data)
    
    def _group_entries_into_global_sessions(self, merged_entries: List[Tuple]) -> List[SessionData]:
        """
        Group merged entries into global sessions using sequential algorithm.
        
        Algorithm:
        1. Club current timestamp with existing session (if any) if timestamp is within endtime
        2. If no session or timestamp beyond endtime, create new session
        
        Sessions start from first activity timestamp (floored to hour) lasting exactly 5 hours.
        """
        if not merged_entries:
            return []
        
        global_sessions = []
        current_session_entries = []
        current_session_start = None
        current_session_end = None
        
        for project_name, entry_index, timestamp, raw_data, is_warmup in merged_entries:
            
            # If no current session or timestamp is beyond current session end, create new session
            if (current_session_start is None or 
                current_session_end is None or 
                timestamp >= current_session_end):
                
                # Save previous session if it exists
                if current_session_entries:
                    session_data = self._create_global_session_data(
                        current_session_start, 
                        current_session_end,
                        current_session_entries
                    )
                    global_sessions.append(session_data)
                
                # Start new session
                # Session start is floored to hour
                current_session_start = timestamp.replace(minute=0, second=0, microsecond=0)
                # Session end is exactly 5 hours later
                current_session_end = current_session_start + timedelta(hours=5)
                current_session_entries = [(project_name, entry_index, timestamp, raw_data, is_warmup)]
                
            else:
                # Add to current session (timestamp is within session endtime)
                current_session_entries.append((project_name, entry_index, timestamp, raw_data, is_warmup))
        
        # Don't forget the last session
        if current_session_entries:
            session_data = self._create_global_session_data(
                current_session_start,
                current_session_end, 
                current_session_entries
            )
            global_sessions.append(session_data)
        
        return global_sessions
    
    def _create_global_session_data(self, start_time: datetime, end_time: datetime, 
                                   entries: List[Tuple]) -> SessionData:
        """Create global SessionData from session parameters and entries."""
        
        # Extract global data
        all_timestamps = [entry[2] for entry in entries]  # timestamp is index 2
        all_entries_metadata = [entry[3] for entry in entries]  # raw_data is index 3
        
        # Calculate global aggregates
        total_message_count = len(entries)
        total_warmup_count = sum(1 for entry in entries if entry[4])  # is_warmup is index 4
        total_user_message_count = total_message_count - total_warmup_count
        latest_activity = max(all_timestamps) if all_timestamps else start_time
        
        # Categorize all messages
        self.logger.debug(f"Categorizing {len(all_entries_metadata)} messages...")
        global_categories = []
        global_category_breakdown = CategoryBreakdown()
        
        for entry_data in all_entries_metadata:
            category_result = self.message_categorizer.categorize_message(entry_data)
            if category_result:
                message_category = MessageCategory(
                    category=category_result.category,
                    confidence=category_result.confidence,
                    keywords_matched=category_result.keywords_matched,
                    context_clues=category_result.context_clues
                )
                global_categories.append(message_category)
                
                # Update breakdown
                if category_result.category == 'planning':
                    global_category_breakdown.planning += 1
                elif category_result.category == 'development':
                    global_category_breakdown.development += 1
                elif category_result.category == 'debugging':
                    global_category_breakdown.debugging += 1
                elif category_result.category == 'testing':
                    global_category_breakdown.testing += 1
            else:
                global_categories.append(None)
                global_category_breakdown.uncategorized += 1
        
        # Group by project
        projects_data = {}
        for project_name, entry_index, timestamp, raw_data, is_warmup in entries:
            if project_name not in projects_data:
                projects_data[project_name] = {
                    'timestamps': [],
                    'entries_metadata': [],
                    'warmup_count': 0,
                    'user_message_count': 0,
                    'entry_indices': []  # Track indices for category mapping
                }
            
            projects_data[project_name]['timestamps'].append(timestamp)
            projects_data[project_name]['entries_metadata'].append(raw_data)
            projects_data[project_name]['entry_indices'].append(entry_index)
            
            if is_warmup:
                projects_data[project_name]['warmup_count'] += 1
            else:
                projects_data[project_name]['user_message_count'] += 1
        
        # Create ProjectSessionData objects with categorization
        projects = {}
        for project_name, project_data in projects_data.items():
            # Create project-specific category breakdown
            project_category_breakdown = CategoryBreakdown()
            project_categories = []
            
            # Map global categories to project-specific entries
            for i, entry_data in enumerate(project_data['entries_metadata']):
                # Find the corresponding global category
                global_index = None
                for j, global_entry in enumerate(all_entries_metadata):
                    if global_entry == entry_data:
                        global_index = j
                        break
                
                if global_index is not None and global_index < len(global_categories):
                    category = global_categories[global_index]
                    project_categories.append(category)
                    
                    if category:
                        if category.category == 'planning':
                            project_category_breakdown.planning += 1
                        elif category.category == 'development':
                            project_category_breakdown.development += 1
                        elif category.category == 'debugging':
                            project_category_breakdown.debugging += 1
                        elif category.category == 'testing':
                            project_category_breakdown.testing += 1
                    else:
                        project_category_breakdown.uncategorized += 1
                else:
                    project_categories.append(None)
                    project_category_breakdown.uncategorized += 1
            
            projects[project_name] = ProjectSessionData(
                project_name=project_name,
                timestamps=project_data['timestamps'],
                entries_metadata=project_data['entries_metadata'],
                message_count=len(project_data['timestamps']),
                warmup_count=project_data['warmup_count'],
                user_message_count=project_data['user_message_count'],
                category_breakdown=project_category_breakdown,
                message_categories=project_categories
            )
        
        return SessionData(
            start_time=start_time,
            end_time=end_time,
            timestamps=all_timestamps,
            entries_metadata=all_entries_metadata,
            message_count=total_message_count,
            warmup_count=total_warmup_count,
            user_message_count=total_user_message_count,
            latest_activity=latest_activity,
            is_active=False,  # Will be calculated later by analysis layers
            projects=projects,
            category_breakdown=global_category_breakdown,
            message_categories=global_categories
        )
    
    def _create_project_lookup(self, global_sessions: List[SessionData]) -> Dict[str, List[int]]:
        """Create project lookup map: project_name -> list of session indices."""
        project_lookup = {}
        
        for session_index, session in enumerate(global_sessions):
            for project_name in session.projects.keys():
                if project_name not in project_lookup:
                    project_lookup[project_name] = []
                project_lookup[project_name].append(session_index)
        
        return project_lookup
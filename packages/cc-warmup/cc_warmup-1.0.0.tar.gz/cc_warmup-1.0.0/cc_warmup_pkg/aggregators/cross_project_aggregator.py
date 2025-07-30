#!/usr/bin/env python3
"""Phase 3: Cross-project aggregation with parallel processing."""

import asyncio
import concurrent.futures
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import sys
import time
from tabulate import tabulate

from ..data_structures import AnalysisResult
from ..analyzers.session_analyzer import SessionAnalyzer, SessionBlock
from ..extractors.global_session_processor import GlobalSessionProcessor
from ..extractors.file_scanner import ClaudeFileScanner


@dataclass
class ProjectSummary:
    """Summary of a project's session activity."""
    project_name: str
    encoded_name: str
    last_activity: Optional[datetime]
    time_since_last: Optional[str]  # Human readable
    session_start_time: Optional[datetime]  # Start of current/latest session
    ends_time: Optional[str]  # When current session/block ends
    warm_up_status: str  # "-" or latest warmup timestamp
    gain_status: str  # "-" or gain info  
    remarks: str  # Status description with proper messages
    
    # Metadata
    total_sessions: int = 0
    total_messages: int = 0
    warmup_count: int = 0
    latest_warmup_time: Optional[datetime] = None
    is_inside_token_block: bool = False
    is_artificially_warmed: bool = False
    needs_warmup: bool = False


class CrossProjectAggregator:
    """Phase 3: Cross-project aggregation with parallel processing."""
    
    def __init__(self, max_workers: int = 4):
        self.session_analyzer = SessionAnalyzer()
        self.global_session_processor = GlobalSessionProcessor()
        self.file_scanner = ClaudeFileScanner()
        self.max_workers = max_workers
        
    async def analyze_all_projects(
        self, 
        lookback_hours: int = 168,  # 7 days
        claude_dir: Optional[Path] = None
    ) -> AnalysisResult[List[ProjectSummary]]:
        """Analyze all projects with parallel processing."""
        
        try:
            # Use global session processor to get all sessions across all projects
            print("🔍 Processing global sessions across all projects...")
            
            global_result = self.global_session_processor.process_global_sessions(
                encoded_project_names=None,  # Process all projects
                lookback_hours=lookback_hours
            )
            
            if not global_result.success:
                return AnalysisResult.failure(f"Failed to process global sessions: {global_result.error}")
            
            global_session_data = global_result.data
            print(f"🔍 Found {len(global_session_data.global_sessions)} global sessions across {global_session_data.total_projects} projects")
            
            # Create project summaries from global sessions
            project_summaries = self._create_project_summaries_from_global_sessions(
                global_session_data
            )
            
            # Sort by last activity (most recent first)
            project_summaries.sort(
                key=lambda p: p.last_activity or datetime.min.replace(tzinfo=UTC),
                reverse=True
            )
            
            return AnalysisResult.success(project_summaries)
            
        except Exception as e:
            return AnalysisResult.failure(f"Cross-project analysis failed: {str(e)}")
    
    async def _process_projects_parallel(
        self, 
        projects: List[Tuple[str, str]], 
        lookback_hours: int
    ) -> List[ProjectSummary]:
        """Process multiple projects in parallel using thread pool."""
        
        # Use ThreadPoolExecutor for CPU-bound work
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_project = {
                executor.submit(self._analyze_single_project, encoded_name, lookback_hours): 
                encoded_name
                for encoded_name, _ in projects
            }
            
            project_summaries = []
            completed = 0
            total = len(projects)
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_project):
                encoded_name = future_to_project[future]
                completed += 1
                
                try:
                    summary = future.result()
                    if summary:
                        project_summaries.append(summary)
                        print(f"   ✅ {summary.project_name} ({completed}/{total})")
                    else:
                        print(f"   ⚠️  {encoded_name} - no data ({completed}/{total})")
                except Exception as e:
                    print(f"   ❌ {encoded_name}: {str(e)}")
            
            return project_summaries
    
    def _analyze_single_project(
        self, 
        encoded_name: str, 
        lookback_hours: int
    ) -> Optional[ProjectSummary]:
        """Analyze a single project (runs in thread pool)."""
        
        try:
            # Get session blocks for this project
            result = self.session_analyzer.analyze_project_sessions(
                encoded_project_name=encoded_name,
                lookback_hours=lookback_hours
            )
            
            if not result.success:
                return None
            
            session_blocks = result.data
            if not session_blocks:
                return None  # Skip projects with no activity
            
            # Get the actual project name from the session analyzer result
            # The session analyzer gets it from JSONL files via project extractor
            actual_project_name = result.data[0].project_name if result.data else encoded_name
            
            # Generate summary
            return self._create_project_summary(
                actual_project_name, encoded_name, session_blocks
            )
            
        except Exception as e:
            # Log error but don't fail entire operation
            return None
    
    def _create_project_summary(
        self, 
        project_name: str, 
        encoded_name: str, 
        session_blocks: List[SessionBlock]
    ) -> ProjectSummary:
        """Create project summary from session blocks."""
        
        if not session_blocks:
            return ProjectSummary(
                project_name=project_name,
                encoded_name=encoded_name,
                last_activity=None,
                time_since_last="-",
                session_start_time=None,
                ends_time="-",
                warm_up_status="-",
                gain_status="-",
                remarks="No recent activity"
            )
        
        # Get latest session
        latest_session = max(session_blocks, key=lambda s: s.last_activity or s.end_time)
        
        # Calculate aggregated stats
        total_sessions = len(session_blocks)
        total_messages = sum(block.message_count for block in session_blocks)
        warmup_count = sum(block.warmup_count for block in session_blocks)
        
        # Determine status
        current_time = datetime.now(UTC)
        last_activity = latest_session.last_activity or latest_session.end_time
        
        # Ensure timezone awareness for comparison
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=UTC)
        
        # Time since last activity
        time_since_minutes = int((current_time - last_activity).total_seconds() / 60)
        time_since_last = self._format_time_since(time_since_minutes)
        
        # Session start time (in local time)
        session_start_time = latest_session.start_time
        if session_start_time.tzinfo is None:
            session_start_time = session_start_time.replace(tzinfo=UTC)
        
        # Active status and session end time
        ends_time = self._determine_ends_time(latest_session)
        
        # Warmup status - show latest warmup timestamp, not count
        warm_up_status = "-"
        if latest_session.latest_warmup_time:
            # Convert to local time and format
            warmup_local = latest_session.latest_warmup_time.astimezone()
            warm_up_status = warmup_local.strftime("%H:%M")
        elif warmup_count > 0:
            warm_up_status = "Warmed"
        
        # Remarks - focus on latest session status
        remarks = self._determine_remarks(latest_session)
        
        return ProjectSummary(
            project_name=project_name,
            encoded_name=encoded_name,
            last_activity=last_activity,
            time_since_last=time_since_last,
            session_start_time=session_start_time,
            ends_time=ends_time,
            warm_up_status=warm_up_status,
            gain_status="-",  # Can be enhanced based on token usage
            remarks=remarks,
            total_sessions=total_sessions,
            total_messages=total_messages,
            warmup_count=warmup_count,
            latest_warmup_time=latest_session.latest_warmup_time,
            is_inside_token_block=latest_session.is_inside_token_block,
            is_artificially_warmed=latest_session.is_artificially_warmed,
            needs_warmup=latest_session.needs_warmup
        )
    
    def _format_time_since(self, minutes: int) -> str:
        """Format time since last activity in human readable form."""
        
        if minutes < 1:
            return "< 1 minute"
        elif minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif minutes < 1440:  # 24 hours
            hours = minutes // 60
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = minutes // 1440
            return f"{days} day{'s' if days != 1 else ''}"
    
    
    def format_summary_table(
        self, 
        project_summaries: List[ProjectSummary],
        execution_time: Optional[float] = None
    ) -> str:
        """Format project summaries into a table using tabulate library."""
        
        if not project_summaries:
            return "No projects found with recent activity."
        
        # Prepare table data
        table_data = []
        warmed_count = 0
        skipped_count = 0
        
        for summary in project_summaries:
            # Project name with color coding
            project_display = summary.project_name
            
            # Apply colors based on status
            if summary.is_inside_token_block:
                project_display = f"\033[36m{project_display}\033[0m"  # Cyan
            elif summary.needs_warmup:
                project_display = f"\033[33m{project_display}\033[0m"  # Yellow
            
            # Active column shows session start time in local time
            if summary.session_start_time:
                local_start = summary.session_start_time.astimezone()
                active_display = f"{local_start.strftime('%H:%M')}\n(user session)"
            else:
                active_display = "-"
            
            # Ends time formatting
            ends_display = summary.ends_time if summary.ends_time else "-"
            
            table_data.append([
                project_display,
                summary.time_since_last,
                active_display, 
                ends_display,
                summary.warm_up_status,
                summary.gain_status,
                summary.remarks
            ])
            
            # Count for summary
            if summary.warmup_count > 0:
                warmed_count += 1
            else:
                skipped_count += 1
        
        # Create table with headers
        headers = ["Project", "Last", "Active", "Ends", "Warm-up", "Gain", "Remarks"]
        table_str = tabulate(table_data, headers=headers, tablefmt="grid")
        
        # Add summary line
        total_projects = len(project_summaries)
        exec_time_str = f"{execution_time:.2f}s" if execution_time else "N/A"
        summary_line = f"\nSummary: {total_projects} projects scanned, {warmed_count} warmed up, {skipped_count} skipped (Execution: {exec_time_str})"
        
        return table_str + summary_line
    
    def _determine_ends_time(self, session: SessionBlock) -> str:
        """Determine when the current session/block ends."""
        if session.token_block_end:
            # Convert to local time and show when the 5-hour token block ends
            local_end = session.token_block_end.astimezone()
            if session.is_inside_token_block:
                return f"{local_end.strftime('%H:%M')}\n(token block)"
            else:
                return f"{local_end.strftime('%H:%M')}\n(ended)"
        else:
            return "-"
    
    def _determine_remarks(self, session: SessionBlock) -> str:
        """Determine appropriate remarks for the latest session."""
        if session.is_inside_token_block:
            if session.is_artificially_warmed:
                return "Artificially warmed-up! ✅✅"
            else:
                return "Already warm! ✅"
        else:
            return "-"
    
    def _decode_project_name(self, encoded_name: str) -> str:
        """Decode project name from encoded directory name."""
        # Remove leading dash and replace dashes with path separators
        if encoded_name.startswith('-'):
            encoded_name = encoded_name[1:]
        
        # Convert back to readable path
        decoded = encoded_name.replace('-', '/')
        
        # Extract just the project name (last component)
        if '/' in decoded:
            return decoded.split('/')[-1]
        else:
            return decoded


def main():
    """Test the cross-project aggregator."""
    
    print("🌐 PHASE 3: CROSS-PROJECT AGGREGATION")
    print("=" * 60)
    
    start_time = time.time()
    
    async def run_analysis():
        aggregator = CrossProjectAggregator(max_workers=4)
        
        result = await aggregator.analyze_all_projects(
            lookback_hours=168  # 7 days
        )
        
        if result.success:
            project_summaries = result.data
            execution_time = time.time() - start_time
            
            print(f"\n✅ Analyzed {len(project_summaries)} projects")
            
            # Display table
            table_output = aggregator.format_summary_table(
                project_summaries, execution_time
            )
            print(f"\n{table_output}")
            
        else:
            print(f"❌ Analysis failed: {result.error}")
    
    # Run async analysis
    asyncio.run(run_analysis())


if __name__ == "__main__":
    main()
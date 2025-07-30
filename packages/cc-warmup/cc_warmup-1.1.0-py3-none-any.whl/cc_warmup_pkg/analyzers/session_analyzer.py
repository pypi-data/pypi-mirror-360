#!/usr/bin/env python3
"""Session block analysis with rich metadata - Phase 2 implementation."""

import json
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import sys

from ..data_structures import AnalysisResult, GlobalSessionResult
from ..extractors.global_session_processor import GlobalSessionProcessor


@dataclass
class SessionBlock:
    """Rich session block with comprehensive metadata."""
    project_name: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    message_count: int
    warmup_count: int
    is_artificially_warmed: bool
    session_id: Optional[str] = None
    
    # Token block analysis
    token_block_start: Optional[datetime] = None
    token_block_end: Optional[datetime] = None
    is_inside_token_block: bool = False
    
    # Activity analysis
    last_activity: Optional[datetime] = None
    time_since_last: Optional[int] = None  # minutes
    is_active_now: bool = False
    
    # Warmup analysis
    latest_warmup_time: Optional[datetime] = None  # Most recent warmup timestamp
    needs_warmup: bool = False
    warmup_window: Optional[str] = None  # "HH:55-HH:59"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with ISO string timestamps."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() + 'Z'
        return data


class SessionAnalyzer:
    """Phase 2: Session block analysis with rich metadata."""
    
    def __init__(self):
        self.global_session_processor = GlobalSessionProcessor()
        
    def analyze_all_projects_sessions(
        self, 
        encoded_project_names: Optional[List[str]] = None,
        lookback_hours: int = 168  # 7 days default
    ) -> AnalysisResult[List[SessionBlock]]:
        """Analyze global sessions across all projects with rich metadata."""
        
        try:
            # Process global sessions using the new processor
            result = self.global_session_processor.process_global_sessions(
                encoded_project_names=encoded_project_names,
                lookback_hours=lookback_hours
            )
            
            if not result.success:
                return AnalysisResult.failure(f"Failed to process global sessions: {result.error}")
            
            global_result: GlobalSessionResult = result.data
            if not global_result.global_sessions:
                return AnalysisResult.success([])  # No sessions
            
            # Analyze each global session
            session_blocks = []
            for session_data in global_result.global_sessions:
                block = self._analyze_global_session_block(session_data)
                session_blocks.append(block)
            
            return AnalysisResult.success(session_blocks)
            
        except Exception as e:
            return AnalysisResult.failure(f"Global session analysis failed: {str(e)}")
    
    def analyze_project_sessions(
        self, 
        encoded_project_name: str,
        lookback_hours: int = 168  # 7 days default
    ) -> AnalysisResult[List[SessionBlock]]:
        """Analyze sessions for a single project (filtered from global sessions)."""
        
        try:
            # Get all global sessions
            global_result = self.analyze_all_projects_sessions(
                encoded_project_names=None,  # Get all projects
                lookback_hours=lookback_hours
            )
            
            if not global_result.success:
                return global_result
            
            # Filter sessions that include the specified project
            all_session_blocks = global_result.data
            project_session_blocks = []
            
            for block in all_session_blocks:
                # Check if this session involves the specified project
                # We need to look at the original session data for this
                # For now, include all sessions - this needs refinement
                project_session_blocks.append(block)
            
            return AnalysisResult.success(project_session_blocks)
            
        except Exception as e:
            return AnalysisResult.failure(f"Project session analysis failed: {str(e)}")
    
    def _analyze_global_session_block(self, session_data) -> SessionBlock:
        """Analyze a global session block from SessionData."""
        
        start_time = session_data.start_time
        end_time = session_data.end_time
        timestamps = session_data.timestamps
        
        # Ensure timezone awareness
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=UTC)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=UTC)
            
        # Calculate actual end time from latest activity
        actual_end_time = session_data.latest_activity
        if actual_end_time.tzinfo is None:
            actual_end_time = actual_end_time.replace(tzinfo=UTC)
            
        duration_minutes = int((actual_end_time - start_time).total_seconds() / 60)
        
        # Create project name from involved projects
        project_names = list(session_data.projects.keys())
        project_name = ", ".join(project_names) if project_names else "Global"
        
        # Token block analysis - sessions already align with token blocks
        token_block_start = start_time
        token_block_end = end_time
        current_time = datetime.now(UTC)
        
        is_inside_token_block = (
            token_block_start <= current_time <= token_block_end
        )
        
        # Activity analysis
        time_since_last = int((current_time - actual_end_time).total_seconds() / 60)
        is_active_now = time_since_last < 60  # Active if < 1 hour
        
        # Warmup analysis - find most recent warmup timestamp
        latest_warmup_time = None
        if session_data.warmup_count > 0:
            # Look for timestamps at x:55+ which are typical warmup times
            for timestamp in timestamps:
                if timestamp.minute >= 55:  # Warmups typically occur at x:55+
                    if latest_warmup_time is None or timestamp > latest_warmup_time:
                        latest_warmup_time = timestamp
        
        # Warmup recommendations
        needs_warmup, warmup_window = self._analyze_warmup_needs(
            actual_end_time, current_time, is_inside_token_block
        )
        
        return SessionBlock(
            project_name=project_name,
            start_time=start_time,
            end_time=actual_end_time,  # Use actual end time, not theoretical
            duration_minutes=duration_minutes,
            message_count=session_data.message_count,
            warmup_count=session_data.warmup_count,
            is_artificially_warmed=session_data.warmup_count > 0,
            token_block_start=token_block_start,
            token_block_end=token_block_end,
            is_inside_token_block=is_inside_token_block,
            last_activity=actual_end_time,
            time_since_last=time_since_last,
            is_active_now=is_active_now,
            latest_warmup_time=latest_warmup_time,
            needs_warmup=needs_warmup,
            warmup_window=warmup_window
        )

    def _analyze_session_block_from_session_data(
        self,
        project_name: str,
        session_data
    ) -> SessionBlock:
        """Analyze a session block from pre-grouped SessionData."""
        
        start_time = session_data.start_time
        end_time = session_data.end_time
        timestamps = session_data.timestamps
        
        # Ensure timezone awareness
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=UTC)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=UTC)
            
        # Calculate actual end time from latest activity
        actual_end_time = session_data.latest_activity
        if actual_end_time.tzinfo is None:
            actual_end_time = actual_end_time.replace(tzinfo=UTC)
            
        duration_minutes = int((actual_end_time - start_time).total_seconds() / 60)
        
        # Token block analysis - sessions already align with token blocks
        token_block_start = start_time
        token_block_end = end_time
        current_time = datetime.now(UTC)
        
        is_inside_token_block = (
            token_block_start <= current_time <= token_block_end
        )
        
        # Activity analysis
        time_since_last = int((current_time - actual_end_time).total_seconds() / 60)
        is_active_now = time_since_last < 60  # Active if < 1 hour
        
        # Warmup analysis - find most recent warmup timestamp
        latest_warmup_time = None
        if session_data.warmup_count > 0:
            # Look for timestamps at x:55+ which are typical warmup times
            for timestamp in timestamps:
                if timestamp.minute >= 55:  # Warmups typically occur at x:55+
                    if latest_warmup_time is None or timestamp > latest_warmup_time:
                        latest_warmup_time = timestamp
        
        # Warmup recommendations
        needs_warmup, warmup_window = self._analyze_warmup_needs(
            actual_end_time, current_time, is_inside_token_block
        )
        
        return SessionBlock(
            project_name=project_name,
            start_time=start_time,
            end_time=actual_end_time,  # Use actual end time, not theoretical
            duration_minutes=duration_minutes,
            message_count=session_data.message_count,
            warmup_count=session_data.warmup_count,
            is_artificially_warmed=session_data.warmup_count > 0,
            token_block_start=token_block_start,
            token_block_end=token_block_end,
            is_inside_token_block=is_inside_token_block,
            last_activity=actual_end_time,
            time_since_last=time_since_last,
            is_active_now=is_active_now,
            latest_warmup_time=latest_warmup_time,
            needs_warmup=needs_warmup,
            warmup_window=warmup_window
        )
    
    
    def _analyze_warmup_needs(
        self, 
        last_activity: datetime, 
        current_time: datetime,
        is_inside_token_block: bool
    ) -> Tuple[bool, Optional[str]]:
        """Analyze if warmup is needed and when."""
        
        # No warmup needed if already inside active token block
        if is_inside_token_block:
            return False, None
        
        # Calculate time until next warmup window (x:55)
        current_minute = current_time.minute
        
        if current_minute >= 55:
            # Already in warmup window
            return True, f"{current_time.hour:02d}:55-{current_time.hour:02d}:59"
        else:
            # Next warmup window
            return True, f"{current_time.hour:02d}:55-{current_time.hour:02d}:59"
    
    def format_session_summary(self, session_blocks: List[SessionBlock]) -> Dict[str, Any]:
        """Format session blocks into summary statistics."""
        
        if not session_blocks:
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "total_warmups": 0,
                "average_duration": 0,
                "sessions_warmed": 0,
                "last_activity": None
            }
        
        total_sessions = len(session_blocks)
        total_messages = sum(block.message_count for block in session_blocks)
        total_warmups = sum(block.warmup_count for block in session_blocks)
        average_duration = sum(block.duration_minutes for block in session_blocks) / total_sessions
        sessions_warmed = sum(1 for block in session_blocks if block.is_artificially_warmed)
        last_activity = max(block.last_activity for block in session_blocks)
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages, 
            "total_warmups": total_warmups,
            "average_duration": round(average_duration, 1),
            "sessions_warmed": sessions_warmed,
            "last_activity": last_activity.isoformat() + 'Z' if last_activity else None
        }


def main():
    """Test the session analyzer."""
    
    print("🔍 PHASE 2: SESSION BLOCK ANALYSIS")
    print("=" * 50)
    
    analyzer = SessionAnalyzer()
    
    # Test with cc-warmup project
    result = analyzer.analyze_project_sessions(
        encoded_project_name="-Users-divygarima-Documents-Mayank-Docs-Cursor-Projects-cc-warmup",
        lookback_hours=168  # 7 days
    )
    
    if result.success:
        session_blocks = result.data
        print(f"✅ Found {len(session_blocks)} session blocks")
        
        # Show first few sessions
        for i, block in enumerate(session_blocks[:3]):
            print(f"\n📊 Session {i+1}:")
            print(f"   Start: {block.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Duration: {block.duration_minutes} minutes")
            print(f"   Messages: {block.message_count}")
            print(f"   Warmups: {block.warmup_count}")
            print(f"   Inside token block: {block.is_inside_token_block}")
            print(f"   Needs warmup: {block.needs_warmup}")
        
        # Summary
        summary = analyzer.format_session_summary(session_blocks)
        print(f"\n📈 SUMMARY:")
        print(f"   Total sessions: {summary['total_sessions']}")
        print(f"   Total messages: {summary['total_messages']}")
        print(f"   Average duration: {summary['average_duration']} minutes")
        print(f"   Sessions warmed: {summary['sessions_warmed']}")
        
    else:
        print(f"❌ Analysis failed: {result.error}")


if __name__ == "__main__":
    main()
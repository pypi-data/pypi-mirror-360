"""
Core data structures for modular session analysis pipeline.

This module defines the data contracts between different layers of the session analysis system.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, TypeVar, Generic
from dataclasses import dataclass, field

T = TypeVar('T')


@dataclass
class CategoryBreakdown:
    """Breakdown of messages by category."""
    planning: int = 0
    development: int = 0
    debugging: int = 0
    testing: int = 0
    uncategorized: int = 0
    
    @property
    def total_categorized(self) -> int:
        """Total messages that were successfully categorized."""
        return self.planning + self.development + self.debugging + self.testing
    
    @property
    def total_messages(self) -> int:
        """Total messages including uncategorized."""
        return self.total_categorized + self.uncategorized
    
    @property
    def categorization_rate(self) -> float:
        """Percentage of messages that were successfully categorized."""
        if self.total_messages == 0:
            return 0.0
        return self.total_categorized / self.total_messages
    
    def get_category_percentages(self) -> Dict[str, float]:
        """Get percentage breakdown of each category."""
        if self.total_messages == 0:
            return {category: 0.0 for category in ['planning', 'development', 'debugging', 'testing', 'uncategorized']}
        
        return {
            'planning': (self.planning / self.total_messages) * 100,
            'development': (self.development / self.total_messages) * 100,
            'debugging': (self.debugging / self.total_messages) * 100,
            'testing': (self.testing / self.total_messages) * 100,
            'uncategorized': (self.uncategorized / self.total_messages) * 100
        }


@dataclass
class MessageCategory:
    """Individual message categorization result."""
    category: str
    confidence: float
    keywords_matched: List[str] = field(default_factory=list)
    context_clues: List[str] = field(default_factory=list)


@dataclass
class ProjectSessionData:
    """Project-specific data within a global session."""
    project_name: str
    timestamps: List[datetime]      # This project's timestamps in the session
    entries_metadata: List[Dict]    # This project's JSONL entries in the session
    message_count: int              # This project's message count in session
    warmup_count: int               # This project's warmup count in session
    user_message_count: int         # This project's user message count in session
    category_breakdown: CategoryBreakdown = field(default_factory=CategoryBreakdown)
    message_categories: List[Optional[MessageCategory]] = field(default_factory=list)


@dataclass
class SessionData:
    """Global session with per-project breakdown from JSON extractor."""
    start_time: datetime           # Session start (floor to hour)
    end_time: datetime            # Theoretical end (start + 5 hours)
    timestamps: List[datetime]    # All timestamps across projects in this session
    entries_metadata: List[Dict]  # All JSONL entries across projects for this session
    
    # Global aggregates
    message_count: int            # Total messages across all projects in session
    warmup_count: int             # Total warmup messages across all projects  
    user_message_count: int       # Total user messages across all projects
    latest_activity: datetime     # Last timestamp across all projects in session
    is_active: bool = False       # Calculated active status
    
    # Per-project breakdown
    projects: Dict[str, ProjectSessionData] = field(default_factory=dict)  # project_name -> ProjectSessionData
    
    # Category analytics
    category_breakdown: CategoryBreakdown = field(default_factory=CategoryBreakdown)
    message_categories: List[Optional[MessageCategory]] = field(default_factory=list)


@dataclass
class ProjectRawData:
    """Raw data extracted from a single project's JSONL files."""
    project_name: str              # Display name (e.g., "cc-warmup")
    encoded_name: str              # Directory name (e.g., "-Users-...")
    project_path: Path             # Actual filesystem path
    timestamps: List[datetime]     # All timestamps from this project
    entries_metadata: List[Dict]   # All JSONL entries from this project
    extraction_time: datetime      # When this data was extracted
    extraction_stats: Dict = field(default_factory=dict)
    
    @property
    def total_entries(self) -> int:
        return len(self.timestamps)
    
    @property
    def date_range(self) -> Optional[tuple[datetime, datetime]]:
        if not self.timestamps:
            return None
        return (min(self.timestamps), max(self.timestamps))


@dataclass
class GlobalSessionResult:
    """Result of global session processing across all projects."""
    global_sessions: List[SessionData]      # All global sessions
    project_lookup: Dict[str, List[int]]    # project_name -> list of session indices
    projects_metadata: Dict[str, Dict]      # project_name -> metadata
    processing_time: float
    total_entries: int
    total_projects: int


@dataclass
class SessionBlockMetadata:
    """Detailed metadata for a single session block."""
    # Time boundaries
    block_start: datetime          # ccusage block start (floor hour)
    block_end: datetime           # ccusage block end (start + 5hrs)
    user_start: datetime          # First user activity in block
    actual_end: datetime          # Last activity in block
    
    # Message counts
    total_messages: int           # Total entries in block
    warmup_messages: int          # Artificial warm-up entries
    user_messages: int            # Real user interaction entries
    
    # Session characteristics
    artificially_warmed: bool     # Block extended by warm-ups
    is_active: bool              # Currently active per ccusage rules
    is_continuous: bool          # No significant gaps in activity
    
    # Detailed analysis
    gap_analysis: Dict = field(default_factory=dict)  # Gap durations, patterns
    activity_pattern: Dict = field(default_factory=dict)  # Activity distribution
    warmup_details: Dict = field(default_factory=dict)  # When warm-ups occurred
    
    @property
    def duration_hours(self) -> float:
        return (self.actual_end - self.user_start).total_seconds() / 3600
    
    @property
    def user_activity_ratio(self) -> float:
        if self.total_messages == 0:
            return 0.0
        return self.user_messages / self.total_messages


@dataclass
class ProjectSessionBlocks:
    """Complete session block analysis for a single project."""
    project_name: str
    encoded_name: str
    all_blocks: List[SessionBlockMetadata]
    active_block: Optional[SessionBlockMetadata]
    processing_time: float        # Time taken to analyze this project
    
    # Aggregated statistics
    session_summary: Dict = field(default_factory=dict)
    
    @property
    def total_blocks(self) -> int:
        return len(self.all_blocks)
    
    @property
    def has_active_session(self) -> bool:
        return self.active_block is not None
    
    @property
    def total_activity_time(self) -> float:
        """Total hours of activity across all blocks."""
        return sum(block.duration_hours for block in self.all_blocks)


@dataclass
class GlobalSessionState:
    """Aggregated state across all projects."""
    projects: List[ProjectSessionBlocks]
    global_active_block: Optional[tuple[datetime, datetime]]
    processing_stats: Dict = field(default_factory=dict)
    
    # Cross-project analytics
    cross_project_analytics: Dict = field(default_factory=dict)
    
    @property
    def active_projects(self) -> List[ProjectSessionBlocks]:
        return [p for p in self.projects if p.has_active_session]
    
    @property
    def total_projects(self) -> int:
        return len(self.projects)
    
    @property
    def total_active_projects(self) -> int:
        return len(self.active_projects)


@dataclass
class ProcessingConfiguration:
    """Configuration for the session analysis pipeline."""
    # Data extraction settings
    lookback_hours: int = 168  # 7 days
    max_parallel_projects: int = 4
    
    # Gap analysis settings
    session_gap_threshold_minutes: int = 30
    warmup_gap_threshold_minutes: int = 5
    
    # Block analysis settings
    session_duration_hours: int = 5
    
    # Performance settings
    enable_caching: bool = True
    cache_ttl_minutes: int = 5


@dataclass
class AnalysisResult(Generic[T]):
    """Result container for any analysis operation."""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: Dict = field(default_factory=dict)
    
    @classmethod
    def success_result(cls, data: T, processing_time: float = 0.0, **metadata):
        return cls(success=True, data=data, processing_time=processing_time, metadata=metadata)
    
    @classmethod
    def error_result(cls, error: str, processing_time: float = 0.0, **metadata):
        return cls(success=False, error=error, processing_time=processing_time, metadata=metadata)
    
    @classmethod 
    def success(cls, data: T, processing_time: float = 0.0, **metadata):
        return cls(success=True, data=data, processing_time=processing_time, metadata=metadata)
    
    @classmethod
    def failure(cls, error: str, processing_time: float = 0.0, **metadata):
        return cls(success=False, error=error, processing_time=processing_time, metadata=metadata)
#!/usr/bin/env python3
"""Production cc-warmup tool - Complete implementation with warmup integration."""

import argparse
import asyncio
import json
import signal
import sys
import time
from datetime import datetime, UTC
from pathlib import Path
from typing import Optional, List, Dict, Any
from tabulate import tabulate

from .extractors.global_session_processor import GlobalSessionProcessor
from .analyzers.session_analyzer import SessionAnalyzer
from .warmup_integration import ProperWarmupIntegration


# Color and Terminal Utilities
class Colors:
    """ANSI color codes for terminal output."""
    # Reset
    RESET = '\033[0m'
    
    # Text Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright Colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background Colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'


def colored_text(text: str, color: str = "", style: str = "") -> str:
    """Apply color and style to text."""
    if not sys.stdout.isatty():  # Don't colorize if output is redirected
        return text
    return f"{style}{color}{text}{Colors.RESET}"


def clear_screen():
    """Clear the terminal screen."""
    if sys.stdout.isatty():
        print('\033[2J\033[H', end='')


def move_cursor_up(lines: int):
    """Move cursor up by specified number of lines."""
    if sys.stdout.isatty():
        print(f'\033[{lines}A', end='')


def hide_cursor():
    """Hide terminal cursor."""
    if sys.stdout.isatty():
        print('\033[?25l', end='')


def show_cursor():
    """Show terminal cursor."""
    if sys.stdout.isatty():
        print('\033[?25h', end='')


class CCWarmupTool:
    """Production cc-warmup tool with session analysis and warmup capabilities."""
    
    def __init__(self):
        self.global_session_processor = GlobalSessionProcessor()
        self.session_analyzer = SessionAnalyzer()
        self.warmup_integration = ProperWarmupIntegration()
        self.running = True
        self.watch_mode = False
        
    async def run_analysis(
        self, 
        lookback_hours: int = 168,
        claude_dir: Optional[Path] = None,
        dry_run: bool = False,
        send_warmups: bool = False,
        detailed_sessions: bool = True,
        categories_only: bool = False,
        specific_project: Optional[str] = None,
        watch_mode: bool = False,
        refresh_interval: int = 30
    ) -> None:
        """Run complete cc-warmup analysis with optional warmup sending."""
        
        self.watch_mode = watch_mode
        
        if watch_mode:
            await self._run_watch_mode(
                lookback_hours, claude_dir, dry_run, send_warmups,
                detailed_sessions, categories_only, specific_project, refresh_interval
            )
            return
        
        await self._run_single_analysis(
            lookback_hours, claude_dir, dry_run, send_warmups,
            detailed_sessions, categories_only, specific_project
        )
    
    async def _run_single_analysis(
        self,
        lookback_hours: int,
        claude_dir: Optional[Path],
        dry_run: bool,
        send_warmups: bool,
        detailed_sessions: bool,
        categories_only: bool,
        specific_project: Optional[str]
    ) -> None:
        """Run a single analysis cycle."""
        
        print(colored_text("🤖 cc-warmup Project Analysis", Colors.BRIGHT_CYAN, Colors.BOLD))
        print(colored_text("=" * 80, Colors.BLUE))
        
        start_time = time.time()
        
        # 1. Process global sessions across all projects
        result = self.global_session_processor.process_global_sessions(
            encoded_project_names=None,
            lookback_hours=lookback_hours
        )
        
        if not result.success:
            print(f"❌ Analysis failed: {result.error}")
            sys.exit(1)
        
        global_session_data = result.data
        execution_time = time.time() - start_time
        
        # 2. Display rich results 
        self._display_global_session_analysis(global_session_data, execution_time, detailed_sessions, categories_only, specific_project)
        
        # 3. Check for warmup opportunities (using project statistics)
        if send_warmups and not dry_run:
            project_stats = self._calculate_project_statistics(global_session_data)
            await self._process_warmup_opportunities(project_stats)
        elif dry_run:
            project_stats = self._calculate_project_statistics(global_session_data)
            self._show_warmup_opportunities(project_stats)
    
    async def _run_watch_mode(
        self,
        lookback_hours: int,
        claude_dir: Optional[Path],
        dry_run: bool,
        send_warmups: bool,
        detailed_sessions: bool,
        categories_only: bool,
        specific_project: Optional[str],
        refresh_interval: int
    ) -> None:
        """Run continuous watch mode with periodic refresh."""
        
        # Setup signal handler for graceful exit
        def signal_handler(signum, frame):
            self.running = False
            show_cursor()
            print(f"\n{colored_text('👋 Exiting cc-warmup watch mode...', Colors.YELLOW)}")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Hide cursor for cleaner display
        hide_cursor()
        
        try:
            iteration = 0
            while self.running:
                # Clear screen for fresh display
                clear_screen()
                iteration += 1
                
                # Display header with watch mode info
                current_time = datetime.now()
                warmup_status = "🔥 Auto-warmup ON" if send_warmups else "❄️ Auto-warmup OFF"
                warmup_color = Colors.BRIGHT_GREEN if send_warmups else Colors.BRIGHT_BLACK
                
                print(colored_text("🔄 cc-warmup Watch Mode", Colors.BRIGHT_CYAN, Colors.BOLD))
                print(colored_text(f"⏰ Last updated: {current_time.strftime('%Y-%m-%d %H:%M:%S')} | Refresh: {refresh_interval}s | {colored_text(warmup_status, warmup_color)} | Press Ctrl+C to exit", Colors.BRIGHT_BLACK))
                print(colored_text("=" * 80, Colors.BLUE))
                
                # Run analysis
                await self._run_single_analysis_quiet(
                    lookback_hours, claude_dir, dry_run, send_warmups,
                    detailed_sessions, categories_only, specific_project
                )
                
                # Display next refresh info
                # Note: This was a buggy line, let me fix it
        # next_refresh calculation isn't actually used in display
                print(f"\n{colored_text(f'⏳ Next refresh in {refresh_interval}s...', Colors.BRIGHT_BLACK)}")
                
                # Wait for next refresh
                try:
                    await asyncio.sleep(refresh_interval)
                except asyncio.CancelledError:
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            show_cursor()
            print(f"\n{colored_text('👋 Watch mode stopped', Colors.YELLOW)}")
    
    async def _run_single_analysis_quiet(
        self,
        lookback_hours: int,
        claude_dir: Optional[Path],
        dry_run: bool,
        send_warmups: bool,
        detailed_sessions: bool,
        categories_only: bool,
        specific_project: Optional[str]
    ) -> None:
        """Run analysis without the main header (for watch mode)."""
        
        start_time = time.time()
        
        # Process global sessions
        result = self.global_session_processor.process_global_sessions(
            encoded_project_names=None,
            lookback_hours=lookback_hours
        )
        
        if not result.success:
            print(colored_text(f"❌ Analysis failed: {result.error}", Colors.RED))
            return
        
        global_session_data = result.data
        execution_time = time.time() - start_time
        
        # Display results
        self._display_global_session_analysis(global_session_data, execution_time, detailed_sessions, categories_only, specific_project)
        
        # Handle warmup opportunities
        if send_warmups and not dry_run:
            project_stats = self._calculate_project_statistics(global_session_data)
            await self._process_warmup_opportunities(project_stats)
        elif dry_run:
            project_stats = self._calculate_project_statistics(global_session_data)
            self._show_warmup_opportunities(project_stats)
    
    def _display_global_session_analysis(self, global_session_data, execution_time: float, show_detailed_sessions: bool = True, categories_only: bool = False, specific_project: Optional[str] = None) -> None:
        """Display rich analysis of global sessions with project-level and session-level views."""
        
        # Header  
        if not self.watch_mode:  # Only show in single mode, watch mode has its own header
            print(f"\n{colored_text('📊 GLOBAL SESSION ANALYSIS', Colors.BRIGHT_BLUE, Colors.BOLD)}")
            print(colored_text("=" * 80, Colors.BLUE))
        
        # Summary stats
        total_sessions = len(global_session_data.global_sessions)
        total_projects = global_session_data.total_projects
        total_entries = global_session_data.total_entries
        
        print(f"{colored_text('🔍', Colors.CYAN)} Discovered {colored_text(str(total_projects), Colors.BRIGHT_WHITE, Colors.BOLD)} projects with {colored_text(str(total_sessions), Colors.BRIGHT_WHITE, Colors.BOLD)} global sessions ({colored_text(f'{total_entries:,}', Colors.BRIGHT_WHITE)} total entries)")
        print(f"{colored_text('⏱️', Colors.YELLOW)}  Processing time: {colored_text(f'{execution_time:.2f}s', Colors.BRIGHT_GREEN)}")
        
        if not global_session_data.global_sessions:
            print("\n⚠️  No sessions found")
            return
        
        # Handle specific project analysis
        if specific_project:
            self._display_project_specific_analysis(global_session_data, specific_project)
            return
        
        # Handle categories-only mode
        if categories_only:
            self._display_detailed_category_analysis(global_session_data)
            return
        
        # PROJECT-LEVEL VIEW
        print(f"\n{colored_text('📋 PROJECT-LEVEL SUMMARY', Colors.BRIGHT_MAGENTA, Colors.BOLD)}")
        print(colored_text("-" * 80, Colors.MAGENTA))
        
        project_stats = self._calculate_project_statistics(global_session_data)
        project_table = self._format_project_table(project_stats)
        print(project_table)
        
        # CATEGORY ANALYTICS
        print(f"\n{colored_text('🏷️  CATEGORY ANALYTICS', Colors.BRIGHT_GREEN, Colors.BOLD)}")
        print(colored_text("-" * 80, Colors.GREEN))
        
        category_analytics = self._format_category_analytics(project_stats, global_session_data)
        print(category_analytics)
        
        # SESSION-LEVEL VIEW (optional)
        if show_detailed_sessions:
            print(f"\n{colored_text('🎯 SESSION-LEVEL DETAILS', Colors.BRIGHT_YELLOW, Colors.BOLD)}")
            print(colored_text("-" * 80, Colors.YELLOW))
            
            session_table = self._format_session_table(global_session_data.global_sessions)
            print(session_table)
        
        # WARMUP STATUS
        print(f"\n{colored_text('🔥 WARMUP STATUS', Colors.BRIGHT_RED, Colors.BOLD)}")
        print(colored_text("-" * 80, Colors.RED))
        
        warmup_summary = self._format_warmup_summary(global_session_data)
        print(warmup_summary)
    
    def _display_project_specific_analysis(self, global_session_data, project_name: str) -> None:
        """Display detailed analysis for a specific project."""
        
        print(f"\n{colored_text(f'🎯 DETAILED PROJECT ANALYSIS: {project_name}', Colors.BRIGHT_CYAN, Colors.BOLD)}")
        print(colored_text("=" * 80, Colors.CYAN))
        
        # Find project in sessions
        project_sessions = []
        total_messages = 0
        categorized_messages = 0
        category_counts = {"planning": 0, "development": 0, "debugging": 0, "testing": 0}
        message_timeline = []
        
        for session in global_session_data.global_sessions:
            if project_name in session.projects:
                project_data = session.projects[project_name]
                project_sessions.append((session, project_data))
                total_messages += project_data.message_count
                
                # Collect category data
                for i, category_result in enumerate(project_data.message_categories):
                    if category_result is not None:  # Only count categorized messages
                        categorized_messages += 1
                        category_counts[category_result.category] += 1
                        # Add to timeline with timestamp
                        if i < len(project_data.timestamps):
                            message_timeline.append((project_data.timestamps[i], category_result.category))
        
        if not project_sessions:
            print(f"❌ Project '{project_name}' not found in current analysis")
            print("Available projects:")
            for session in global_session_data.global_sessions:
                for proj in session.projects.keys():
                    print(f"   • {proj}")
            return
        
        # Project overview
        print(f"{colored_text('📈 Project Overview:', Colors.BRIGHT_BLUE, Colors.BOLD)}")
        print(f"   • Total Sessions: {colored_text(str(len(project_sessions)), Colors.BRIGHT_WHITE)}")
        print(f"   • Total Messages: {colored_text(f'{total_messages:,}', Colors.BRIGHT_WHITE)}")
        print(f"   • Categorized: {colored_text(f'{categorized_messages:,}', Colors.BRIGHT_GREEN)} ({colored_text(f'{categorized_messages/total_messages*100:.1f}%', Colors.GREEN)})")
        
        # Category breakdown
        print(f"\n{colored_text('📊 Category Distribution:', Colors.BRIGHT_MAGENTA, Colors.BOLD)}")
        if categorized_messages > 0:
            for category, count in category_counts.items():
                percentage = (count / categorized_messages) * 100
                emoji = {"planning": "🎯", "development": "💻", "debugging": "🐛", "testing": "🧪"}[category]
                print(f"   {emoji} {colored_text(category.title(), Colors.BRIGHT_WHITE)}: {colored_text(str(count), Colors.BRIGHT_GREEN)} messages ({colored_text(f'{percentage:.1f}%', Colors.GREEN)})")
        else:
            print(colored_text("   No categorized messages found", Colors.BRIGHT_BLACK))
        
        # Recent activity timeline (last 20 categorized messages)
        if message_timeline:
            print(f"\n{colored_text('⏰ Recent Activity Timeline (Last 20 categorized):', Colors.BRIGHT_YELLOW, Colors.BOLD)}")
            sorted_timeline = sorted(message_timeline, key=lambda x: x[0], reverse=True)[:20]
            for timestamp, category in sorted_timeline:
                local_time = timestamp.astimezone()
                emoji = {"planning": "🎯", "development": "💻", "debugging": "🐛", "testing": "🧪"}[category]
                print(f"   {colored_text(local_time.strftime('%m-%d %H:%M'), Colors.BRIGHT_BLACK)} {emoji} {colored_text(category, Colors.BRIGHT_WHITE)}")
        
        # Session breakdown
        print(f"\n{colored_text('📋 Session Breakdown:', Colors.BRIGHT_BLUE, Colors.BOLD)}")
        for i, (session, project_data) in enumerate(project_sessions, 1):
            start_time = session.start_time.astimezone()
            duration = (session.latest_activity - session.start_time).total_seconds() / 3600
            cat_count = len([cat for cat in project_data.message_categories if cat is not None])
            print(f"   Session {colored_text(str(i), Colors.BRIGHT_WHITE)}: {colored_text(start_time.strftime('%m-%d %H:%M'), Colors.BRIGHT_BLACK)} ({colored_text(f'{duration:.1f}h', Colors.YELLOW)}) - {colored_text(str(project_data.message_count), Colors.BRIGHT_GREEN)} msgs, {colored_text(str(cat_count), Colors.GREEN)} categorized")
    
    def _display_detailed_category_analysis(self, global_session_data) -> None:
        """Display detailed category analytics for all projects."""
        
        print(f"\n{colored_text('🏷️  DETAILED CATEGORY ANALYTICS', Colors.BRIGHT_GREEN, Colors.BOLD)}")
        print(colored_text("=" * 80, Colors.GREEN))
        
        # Collect all project category data
        project_categories = {}
        total_global_categorized = 0
        global_category_counts = {"planning": 0, "development": 0, "debugging": 0, "testing": 0}
        
        for session in global_session_data.global_sessions:
            for project_name, project_data in session.projects.items():
                if project_name not in project_categories:
                    project_categories[project_name] = {
                        "total_messages": 0,
                        "categorized": 0,
                        "categories": {"planning": 0, "development": 0, "debugging": 0, "testing": 0},
                        "sessions": 0
                    }
                
                proj_stats = project_categories[project_name]
                proj_stats["total_messages"] += project_data.message_count
                proj_stats["sessions"] += 1
                
                for category_result in project_data.message_categories:
                    if category_result is not None:  # Only count categorized messages
                        proj_stats["categorized"] += 1
                        proj_stats["categories"][category_result.category] += 1
                        total_global_categorized += 1
                        global_category_counts[category_result.category] += 1
        
        # Global category summary
        print(f"{colored_text('📈 Global Category Summary:', Colors.BRIGHT_BLUE, Colors.BOLD)}")
        print(f"   Total categorized: {colored_text(f'{total_global_categorized:,}', Colors.BRIGHT_WHITE)} messages")
        for category, count in global_category_counts.items():
            if total_global_categorized > 0:
                percentage = (count / total_global_categorized) * 100
                emoji = {"planning": "🎯", "development": "💻", "debugging": "🐛", "testing": "🧪"}[category]
                print(f"   {emoji} {colored_text(category.title(), Colors.BRIGHT_WHITE)}: {colored_text(str(count), Colors.BRIGHT_GREEN)} ({colored_text(f'{percentage:.1f}%', Colors.GREEN)})")
        
        # Project-by-project breakdown
        print(f"\n{colored_text('📊 Project Category Breakdown:', Colors.BRIGHT_MAGENTA, Colors.BOLD)}")
        
        # Sort projects by categorization rate
        sorted_projects = sorted(
            project_categories.items(),
            key=lambda x: x[1]["categorized"] / max(x[1]["total_messages"], 1),
            reverse=True
        )
        
        for project_name, stats in sorted_projects:
            if stats["categorized"] > 0:
                cat_rate = (stats["categorized"] / stats["total_messages"]) * 100
                print(f"\n   📁 {colored_text(project_name, Colors.BRIGHT_CYAN)}:")
                print(f"      Rate: {colored_text(f"{stats['categorized']}/{stats['total_messages']}", Colors.BRIGHT_WHITE)} ({colored_text(f'{cat_rate:.1f}%', Colors.CYAN)})")
                
                # Category distribution for this project
                for category, count in stats["categories"].items():
                    if count > 0:
                        percentage = (count / stats["categorized"]) * 100
                        emoji = {"planning": "🎯", "development": "💻", "debugging": "🐛", "testing": "🧪"}[category]
                        print(f"      {emoji} {colored_text(category.title(), Colors.BRIGHT_WHITE)}: {colored_text(str(count), Colors.BRIGHT_GREEN)} ({colored_text(f'{percentage:.1f}%', Colors.GREEN)})")
        
        # Show top insights
        print(f"\n{colored_text('💡 Category Insights:', Colors.BRIGHT_YELLOW, Colors.BOLD)}")
        if project_categories:
            # Find most debugging-heavy project
            max_debug_project = max(
                [(name, stats) for name, stats in project_categories.items() if stats["categorized"] > 5],
                key=lambda x: x[1]["categories"]["debugging"] / max(x[1]["categorized"], 1),
                default=(None, None)
            )
            if max_debug_project[0]:
                debug_rate = (max_debug_project[1]["categories"]["debugging"] / max_debug_project[1]["categorized"]) * 100
                print(f"   🐛 Most debugging activity: {colored_text(max_debug_project[0], Colors.BRIGHT_RED)} ({colored_text(f'{debug_rate:.1f}%', Colors.RED)})")
            
            # Find most planning-heavy project  
            max_plan_project = max(
                [(name, stats) for name, stats in project_categories.items() if stats["categorized"] > 5],
                key=lambda x: x[1]["categories"]["planning"] / max(x[1]["categorized"], 1),
                default=(None, None)
            )
            if max_plan_project[0]:
                plan_rate = (max_plan_project[1]["categories"]["planning"] / max_plan_project[1]["categorized"]) * 100
                print(f"   🎯 Most planning activity: {colored_text(max_plan_project[0], Colors.BRIGHT_BLUE)} ({colored_text(f'{plan_rate:.1f}%', Colors.BLUE)})")
    
    def _calculate_project_statistics(self, global_session_data) -> List[Dict[str, Any]]:
        """Calculate comprehensive per-project statistics from global sessions."""
        
        project_stats = {}
        
        # Initialize stats for all projects
        for project_name in global_session_data.project_lookup.keys():
            project_stats[project_name] = {
                'project_name': project_name,
                'sessions_count': 0,
                'total_messages': 0,
                'user_messages': 0,
                'last_activity': None,
                'first_activity': None,
                'total_duration_hours': 0,
                'avg_messages_per_session': 0,
                'is_active': False,
                'needs_warmup': False,
                'session_indices': [],
                # Category analytics
                'planning': 0,
                'development': 0,
                'debugging': 0,
                'testing': 0,
                'uncategorized': 0,
                'categorization_rate': 0.0
            }
        
        # Aggregate statistics from global sessions
        for session_idx, session in enumerate(global_session_data.global_sessions):
            for project_name, project_session_data in session.projects.items():
                if project_name not in project_stats:
                    continue
                    
                stats = project_stats[project_name]
                stats['sessions_count'] += 1
                stats['total_messages'] += project_session_data.message_count
                stats['user_messages'] += project_session_data.user_message_count
                stats['session_indices'].append(session_idx)
                
                # Aggregate category statistics
                breakdown = project_session_data.category_breakdown
                stats['planning'] += breakdown.planning
                stats['development'] += breakdown.development
                stats['debugging'] += breakdown.debugging
                stats['testing'] += breakdown.testing
                stats['uncategorized'] += breakdown.uncategorized
                
                # Track activity times
                if project_session_data.timestamps:
                    first_ts = min(project_session_data.timestamps)
                    last_ts = max(project_session_data.timestamps)
                    
                    if stats['first_activity'] is None or first_ts < stats['first_activity']:
                        stats['first_activity'] = first_ts
                    if stats['last_activity'] is None or last_ts > stats['last_activity']:
                        stats['last_activity'] = last_ts
        
        # Calculate derived statistics
        current_time = datetime.now(UTC)
        for stats in project_stats.values():
            if stats['sessions_count'] > 0:
                stats['avg_messages_per_session'] = stats['total_messages'] / stats['sessions_count']
            
            # Calculate categorization rate
            total_categorized = stats['planning'] + stats['development'] + stats['debugging'] + stats['testing']
            if stats['total_messages'] > 0:
                stats['categorization_rate'] = total_categorized / stats['total_messages']
            
            # Calculate activity status
            if stats['last_activity']:
                # Ensure timezone awareness for comparison
                last_activity = stats['last_activity']
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=UTC)
                time_since_last = (current_time - last_activity).total_seconds() / 3600  # hours
                stats['time_since_last_hours'] = time_since_last
                stats['is_active'] = time_since_last < 1  # Active if < 1 hour
                stats['needs_warmup'] = time_since_last > 4 and time_since_last < 5  # Need warmup if 4-5 hours
            
            # Calculate total duration
            if stats['first_activity'] and stats['last_activity']:
                duration = (stats['last_activity'] - stats['first_activity']).total_seconds() / 3600
                stats['total_duration_hours'] = duration
        
        # Filter out projects with no activity and convert to list
        active_projects = [stats for stats in project_stats.values() if stats['sessions_count'] > 0]
        
        # Sort by last activity (most recent first)
        active_projects.sort(
            key=lambda p: p['last_activity'] or datetime.min.replace(tzinfo=UTC),
            reverse=True
        )
        
        return active_projects
    
    def _format_project_table(self, project_stats: List[Dict[str, Any]]) -> str:
        """Format project statistics into a rich table."""
        
        if not project_stats:
            return "No active projects found."
        
        headers = [
            "Project", "Sessions", "Total Msgs", "User Msgs", 
            "Avg Msgs/Session", "Last Activity", "Status", "Remarks"
        ]
        
        rows = []
        for stats in project_stats:
            # Format project name (truncate if too long)
            project_name = stats['project_name']
            if len(project_name) > 20:
                project_name = project_name[:17] + "..."
            
            # Format last activity (convert to local time - treat naive as UTC)
            if stats['last_activity']:
                last_activity_dt = stats['last_activity']
                # Ensure timezone awareness (treat naive as UTC)
                if last_activity_dt.tzinfo is None:
                    last_activity_dt = last_activity_dt.replace(tzinfo=UTC)
                last_activity_local = last_activity_dt.astimezone()
                last_activity = last_activity_local.strftime('%H:%M')
                time_since = f"{stats.get('time_since_last_hours', 0):.1f}h ago"
            else:
                last_activity = "-"
                time_since = "-"
            
            # Status indicators
            if stats['is_active']:
                status = colored_text("🟢 Active", Colors.BRIGHT_GREEN)
                remarks = colored_text("Currently active", Colors.GREEN)
            elif stats['needs_warmup']:
                status = colored_text("🟡 Warmup", Colors.BRIGHT_YELLOW)
                remarks = colored_text("Needs warmup", Colors.YELLOW)
            elif stats.get('time_since_last_hours', 0) > 5:
                status = colored_text("🔴 Inactive", Colors.BRIGHT_RED)  
                remarks = colored_text("Token block expired", Colors.RED)
            else:
                status = colored_text("⚫ Recent", Colors.BRIGHT_BLACK)
                remarks = colored_text("Recently active", Colors.BRIGHT_BLACK)
            
            rows.append([
                project_name,
                stats['sessions_count'],
                stats['total_messages'],
                stats['user_messages'],
                f"{stats['avg_messages_per_session']:.1f}",
                last_activity,
                status,
                remarks
            ])
        
        return tabulate(rows, headers=headers, tablefmt="grid", stralign="left")
    
    def _format_category_analytics(self, project_stats: List[Dict[str, Any]], global_session_data) -> str:
        """Format category analytics with project-level and global-level breakdowns."""
        
        if not project_stats:
            return "No project data for category analysis."
        
        analytics_output = []
        
        # Global category summary
        total_planning = sum(stats['planning'] for stats in project_stats)
        total_development = sum(stats['development'] for stats in project_stats)
        total_debugging = sum(stats['debugging'] for stats in project_stats)
        total_testing = sum(stats['testing'] for stats in project_stats)
        total_uncategorized = sum(stats['uncategorized'] for stats in project_stats)
        total_messages = sum(stats['total_messages'] for stats in project_stats)
        
        global_categorized = total_planning + total_development + total_debugging + total_testing
        global_categorization_rate = (global_categorized / total_messages * 100) if total_messages > 0 else 0
        
        analytics_output.append(colored_text("📈 GLOBAL BREAKDOWN:", Colors.BRIGHT_BLUE, Colors.BOLD))
        analytics_output.append(f"   Total Messages: {colored_text(f'{total_messages:,}', Colors.BRIGHT_WHITE)}")
        analytics_output.append(f"   Categorization Rate: {colored_text(f'{global_categorization_rate:.1f}%', Colors.BRIGHT_GREEN)}")
        analytics_output.append("")
        
        # Category distribution table
        if total_messages > 0:
            planning_pct = (total_planning / total_messages) * 100
            development_pct = (total_development / total_messages) * 100
            debugging_pct = (total_debugging / total_messages) * 100
            testing_pct = (total_testing / total_messages) * 100
            uncategorized_pct = (total_uncategorized / total_messages) * 100
            
            category_headers = ["Category", "Count", "Percentage", "Indicator"]
            category_rows = [
                ["🎯 Planning", f"{total_planning:,}", f"{planning_pct:.1f}%", "📋" if planning_pct > 15 else "-"],
                ["💻 Development", f"{total_development:,}", f"{development_pct:.1f}%", "🚀" if development_pct > 40 else "-"],
                ["🐛 Debugging", f"{total_debugging:,}", f"{debugging_pct:.1f}%", "⚠️" if debugging_pct > 25 else "-"],
                ["🧪 Testing", f"{total_testing:,}", f"{testing_pct:.1f}%", "✅" if testing_pct > 10 else "-"],
                ["❓ Uncategorized", f"{total_uncategorized:,}", f"{uncategorized_pct:.1f}%", "🔍" if uncategorized_pct > 30 else "-"]
            ]
            
            analytics_output.append(tabulate(category_rows, headers=category_headers, tablefmt="grid", stralign="left"))
        
        # Per-project category insights (top 3 most active projects)
        active_projects = [p for p in project_stats if p['total_messages'] > 10]  # Focus on meaningful data
        if active_projects:
            analytics_output.append(f"\n{colored_text('📊 PROJECT-LEVEL INSIGHTS (Top 3 Most Active):', Colors.BRIGHT_MAGENTA, Colors.BOLD)}")
            
            # Sort by total messages and take top 3
            top_projects = sorted(active_projects, key=lambda p: p['total_messages'], reverse=True)[:3]
            
            project_headers = ["Project", "Category Rate", "Primary Category", "Distribution"]
            project_rows = []
            
            for stats in top_projects:
                project_name = stats['project_name']
                if len(project_name) > 15:
                    project_name = project_name[:12] + "..."
                
                categorization_rate = stats['categorization_rate'] * 100
                
                # Find primary category
                categories = {
                    'Planning': stats['planning'],
                    'Development': stats['development'], 
                    'Debugging': stats['debugging'],
                    'Testing': stats['testing']
                }
                primary_category = max(categories.keys(), key=lambda k: categories[k]) if any(categories.values()) else "None"
                
                # Create distribution string
                if stats['total_messages'] > 0:
                    p_pct = (stats['planning'] / stats['total_messages']) * 100
                    d_pct = (stats['development'] / stats['total_messages']) * 100
                    b_pct = (stats['debugging'] / stats['total_messages']) * 100
                    t_pct = (stats['testing'] / stats['total_messages']) * 100
                    distribution = f"P:{p_pct:.0f}% D:{d_pct:.0f}% B:{b_pct:.0f}% T:{t_pct:.0f}%"
                else:
                    distribution = "No data"
                
                project_rows.append([
                    project_name,
                    f"{categorization_rate:.1f}%",
                    primary_category,
                    distribution
                ])
            
            analytics_output.append(tabulate(project_rows, headers=project_headers, tablefmt="grid", stralign="left"))
        
        return "\n".join(analytics_output)
    
    def _format_session_table(self, global_sessions) -> str:
        """Format global sessions into a detailed table."""
        
        if not global_sessions:
            return "No sessions found."
        
        headers = [
            "Session", "Start Time", "End Time", "Duration", "Projects", "Total Msgs", 
            "Extended By", "User Msgs", "Latest Activity", "Status"
        ]
        
        rows = []
        current_time = datetime.now(UTC)
        
        # Sort sessions by start time (newest first)
        sorted_sessions = sorted(global_sessions, key=lambda s: s.start_time, reverse=True)
        
        for idx, session in enumerate(sorted_sessions, 1):
            # Session timing (convert ALL to local time - treat naive datetimes as UTC)
            start_time = session.start_time
            end_time = session.end_time
            latest_activity = session.latest_activity
            
            # Ensure timezone awareness (treat naive as UTC)
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=UTC)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=UTC)
            if latest_activity.tzinfo is None:
                latest_activity = latest_activity.replace(tzinfo=UTC)
            
            # Convert to local time
            start_time_local = start_time.astimezone()
            end_time_local = end_time.astimezone()
            latest_activity_local = latest_activity.astimezone()
            
            start_time_str = start_time_local.strftime('%m-%d %H:%M')
            end_time_str = end_time_local.strftime('%H:%M')
            duration_hours = (session.latest_activity - session.start_time).total_seconds() / 3600
            duration_str = f"{duration_hours:.1f}h"
            latest_activity_str = latest_activity_local.strftime('%H:%M')
            
            # Projects involved
            project_names = list(session.projects.keys())
            if len(project_names) > 2:
                projects_str = f"{project_names[0]}, +{len(project_names)-1} more"
            else:
                projects_str = ", ".join(project_names)
            
            # Analyze warmup extension
            warmup_extension = self._analyze_warmup_extension(session)
            
            # Status
            # Ensure timezone awareness for comparison
            latest_activity_dt = session.latest_activity
            if latest_activity_dt.tzinfo is None:
                latest_activity_dt = latest_activity_dt.replace(tzinfo=UTC)
            time_since_last = (current_time - latest_activity_dt).total_seconds() / 3600
            
            # Ensure timezone awareness for session start/end times
            session_start = session.start_time
            session_end = session.end_time
            if session_start.tzinfo is None:
                session_start = session_start.replace(tzinfo=UTC)
            if session_end.tzinfo is None:
                session_end = session_end.replace(tzinfo=UTC)
                
            if session_start <= current_time <= session_end:
                if time_since_last < 1:
                    status = "🟢 Active"
                else:
                    status = "🟡 Token Block"
            else:
                status = "⚫ Ended"
            
            rows.append([
                f"#{idx}",
                start_time_str,
                end_time_str,
                duration_str,
                projects_str,
                session.message_count,
                warmup_extension,
                session.user_message_count,
                latest_activity_str,
                status
            ])
        
        return tabulate(rows, headers=headers, tablefmt="grid", stralign="left")
    
    def _analyze_warmup_extension(self, session) -> str:
        """
        Analyze if warmup messages actually extended this session.
        
        Logic:
        1. Find actual warmup messages in timeline
        2. Check if warmup was sent during activity gap (proves extension)
        3. Check if warmup was sent near end of hour (x:55-x:59)
        4. Return timestamp of effective warmup
        
        Returns: Timestamp of effective warmup or "-" if no extension
        """
        if session.warmup_count == 0:
            return "-"
        
        # Collect all timestamps and identify warmups from all projects in this session
        all_entries = []
        for project_name, project_data in session.projects.items():
            for i, timestamp in enumerate(project_data.timestamps):
                entry_metadata = project_data.entries_metadata[i] if i < len(project_data.entries_metadata) else {}
                all_entries.append({
                    'timestamp': timestamp,
                    'metadata': entry_metadata,
                    'project': project_name
                })
        
        # Sort by timestamp
        all_entries.sort(key=lambda x: x['timestamp'])
        
        # Find warmup messages and analyze gaps
        warmup_detector = self.global_session_processor.warmup_detector
        effective_warmups = []
        
        for i, entry in enumerate(all_entries):
            # Check if this is a warmup message
            if warmup_detector.detect_warmup_message(entry['metadata']):
                warmup_time = entry['timestamp']
                
                # Check if warmup was sent during activity gap (key indicator of extension)
                gap_before = self._check_activity_gap_before_warmup(all_entries, i)
                is_near_hour_end = warmup_time.minute >= 55
                
                if gap_before and is_near_hour_end:
                    # Convert to local time for display
                    if warmup_time.tzinfo is None:
                        warmup_time = warmup_time.replace(tzinfo=UTC)
                    warmup_local = warmup_time.astimezone()
                    effective_warmups.append(warmup_local.strftime('%H:%M'))
        
        if effective_warmups:
            # Return the first effective warmup time
            return effective_warmups[0]
        elif session.warmup_count > 0:
            return "No gap"  # Warmups present but didn't extend (user was already active)
        
        return "-"
    
    def _check_activity_gap_before_warmup(self, all_entries, warmup_index) -> bool:
        """Check if there was an activity gap before the warmup (indicating extension)."""
        if warmup_index == 0:
            return False  # No previous activity to compare
        
        warmup_time = all_entries[warmup_index]['timestamp']
        
        # Look for the last user activity before this warmup
        last_user_activity = None
        for i in range(warmup_index - 1, -1, -1):
            entry = all_entries[i]
            # Skip other warmup messages
            if not self.global_session_processor.warmup_detector.detect_warmup_message(entry['metadata']):
                last_user_activity = entry['timestamp']
                break
        
        if last_user_activity is None:
            return False
        
        # Check if there was a significant gap (>30 minutes) before warmup
        gap_minutes = (warmup_time - last_user_activity).total_seconds() / 60
        return gap_minutes > 30  # 30+ minute gap suggests user was inactive
    
    def _format_warmup_summary(self, global_session_data) -> str:
        """Format warmup opportunities and status."""
        
        current_time_utc = datetime.now(UTC)
        current_time_local = current_time_utc.astimezone()
        current_minute = current_time_local.minute
        
        # Check warmup window
        in_warmup_window = 55 <= current_minute <= 59
        next_warmup = f"{current_time_local.hour:02d}:55" if current_minute < 55 else f"{current_time_local.hour+1:02d}:55"
        
        summary = []
        summary.append(f"Current time: {current_time_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        if in_warmup_window:
            summary.append(f"Warmup window: 🟢 ACTIVE (x:55-x:59)")
        else:
            summary.append(f"Warmup window: ⏰ WAITING (next: {next_warmup})")
        
        # Count projects needing warmup (use UTC for comparisons)
        active_sessions = []
        for s in global_session_data.global_sessions:
            # Ensure timezone awareness for comparison
            start_time = s.start_time
            end_time = s.end_time
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=UTC)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=UTC)
            
            if start_time <= current_time_utc <= end_time:
                active_sessions.append(s)
        
        if active_sessions:
            summary.append(f"Projects in token blocks: {len(active_sessions)}")
            for session in active_sessions:
                project_list = ", ".join(session.projects.keys())
                # Convert to local time for display
                start_time = session.start_time
                end_time = session.end_time
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=UTC)
                if end_time.tzinfo is None:
                    end_time = end_time.replace(tzinfo=UTC)
                
                start_time_local = start_time.astimezone()
                end_time_local = end_time.astimezone()
                summary.append(f"  • Session {start_time_local.strftime('%H:%M')}-{end_time_local.strftime('%H:%M')}: {project_list}")
        else:
            summary.append("Projects needing warmup: 0")
            summary.append("Total projects analyzed: " + str(global_session_data.total_projects))
        
        return "\n".join(summary)

    async def _process_warmup_opportunities(self, project_stats) -> None:
        """Process and send warmups for projects that need them."""
        
        current_time_utc = datetime.now(UTC)
        current_time_local = current_time_utc.astimezone()
        current_minute = current_time_local.minute
        
        # Check if we're in warmup window (x:55-x:59)
        if current_minute < 55:
            print(f"\n⏰ Not in warmup window (current: {current_time_local.strftime('%H:%M')}, next: {current_time_local.hour:02d}:55)")
            return
        
        # Find projects needing warmup
        warmup_candidates = [
            p for p in project_stats 
            if p.get('needs_warmup', False) and not p.get('is_active', False)
        ]
        
        if not warmup_candidates:
            print("\n✅ No projects need warmup")
            return
        
        print(f"\n🔥 Found {len(warmup_candidates)} projects needing warmup:")
        for project in warmup_candidates:
            time_since = f"{project.get('time_since_last_hours', 0):.1f}h"
            print(f"   • {project['project_name']} (last activity: {time_since})")
        
        # Send warmup message
        print(f"\n📤 Sending warmup message...")
        success = self.warmup_integration.send_warmup_message()
        
        if success:
            print("✅ Warmup sent successfully")
            
            # Wait and verify detection
            print("🔍 Verifying warmup detection...")
            time.sleep(3)
            
            detection_success = self.warmup_integration.verify_warmup_detection()
            if detection_success:
                print("🎯 Warmup verified in session logs")
            else:
                print("⚠️  Warmup detection needs manual verification")
        else:
            print("❌ Failed to send warmup")
    
    def _show_warmup_opportunities(self, project_stats) -> None:
        """Show warmup opportunities in dry-run mode."""
        
        current_time_utc = datetime.now(UTC)
        current_time_local = current_time_utc.astimezone()
        current_minute = current_time_local.minute
        
        print(f"\n🧪 DRY RUN MODE - Warmup Analysis")
        print(f"Current time: {current_time_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Warmup window: {'✅ ACTIVE' if current_minute >= 55 else '⏰ WAITING'} (x:55-x:59)")
        
        # Analyze warmup needs from project statistics
        warmup_candidates = [
            p for p in project_stats 
            if p.get('needs_warmup', False) and not p.get('is_active', False)
        ]
        
        active_projects = [
            p for p in project_stats 
            if p.get('is_active', False)
        ]
        
        print(f"\n📊 Warmup Status:")
        print(f"   • Projects needing warmup: {len(warmup_candidates)}")
        print(f"   • Projects currently active: {len(active_projects)}")
        print(f"   • Total projects analyzed: {len(project_stats)}")
        
        if warmup_candidates:
            print(f"\n🔥 Projects that would receive warmup:")
            for project in warmup_candidates[:5]:  # Show top 5
                time_since = f"{project.get('time_since_last_hours', 0):.1f}h"
                print(f"   • {project['project_name']} (last: {time_since})")
        
        if active_projects:
            print(f"\n📱 Projects currently active:")
            for project in active_projects[:3]:  # Show top 3
                print(f"   • {project['project_name']} (active)")
    
    def send_manual_warmup(self) -> None:
        """Send a manual warmup message for testing."""
        
        print("🧪 MANUAL WARMUP TEST")
        print("=" * 40)
        
        # Setup warmup project
        self.warmup_integration.setup_warmup_project()
        
        # Send warmup
        print("📤 Sending test warmup...")
        success = self.warmup_integration.send_warmup_message()
        
        if success:
            print("✅ Warmup sent successfully")
            
            # Find and display logs
            print("\n📄 Finding warmup logs...")
            log_files = self.warmup_integration.find_warmup_logs()
            
            if log_files:
                print(f"✅ Found {len(log_files)} log files:")
                for log_file in log_files:
                    print(f"   📄 {log_file}")
            
            # Verify detection
            print("\n🔍 Testing detection...")
            detection_success = self.warmup_integration.verify_warmup_detection()
            
            if detection_success:
                print("🎯 SUCCESS: Manual warmup test completed!")
            else:
                print("⚠️  Detection test needs verification")
        else:
            print("❌ Failed to send warmup")


def main():
    """Main entry point for cc-warmup tool."""
    
    parser = argparse.ArgumentParser(
        description="cc-warmup: Maximize Claude Code usage blocks with intelligent session warming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cc-warmup                              # Default: watch mode with auto-warmup
  cc-warmup --no-watch                   # Run once and exit (legacy mode)
  cc-warmup --no-warmup                  # Watch mode without sending warmups
  cc-warmup --dry-run --no-watch         # Show warmup analysis without sending
  cc-warmup --test-warmup                # Test warmup message sending
  cc-warmup --lookback 24                # Analyze last 24 hours only
  cc-warmup --refresh-interval 60        # Watch mode with 60s refresh
  cc-warmup --categories-only            # Show detailed category analytics
  cc-warmup --project "my-app"            # Analyze specific project
        """
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what warmups would be sent without actually sending them"
    )
    
    parser.add_argument(
        "--warmup",
        action="store_true", 
        help="Send warmup messages for projects that need them (for cron usage)"
    )
    
    parser.add_argument(
        "--test-warmup",
        action="store_true",
        help="Send a test warmup message and verify detection"
    )
    
    parser.add_argument(
        "--lookback",
        type=int,
        default=168,
        help="Hours to look back for activity analysis (default: 168 = 7 days)"
    )
    
    parser.add_argument(
        "--claude-dir",
        type=Path,
        help="Custom Claude projects directory (default: ~/.claude/projects)"
    )
    
    parser.add_argument(
        "--sessions-only",
        action="store_true",
        help="Show only project-level summary, skip detailed session table"
    )
    
    parser.add_argument(
        "--categories-only",
        action="store_true",
        help="Show detailed category analytics for each project"
    )
    
    parser.add_argument(
        "--project",
        type=str,
        help="Show detailed analysis for a specific project"
    )
    
    parser.add_argument(
        "--no-watch",
        action="store_true",
        help="Disable default watch mode - run once and exit"
    )
    
    parser.add_argument(
        "--no-warmup",
        action="store_true",
        help="Disable automatic warmup sending in watch mode"
    )
    
    parser.add_argument(
        "--refresh-interval",
        type=int,
        default=30,
        help="Refresh interval in seconds for watch mode (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Set default modes
    watch_mode = not args.no_watch  # Default to watch mode unless --no-watch
    auto_warmup = not args.no_warmup and not args.dry_run  # Auto-warmup unless disabled or dry-run
    
    # Override warmup mode if explicitly set
    if args.warmup:
        auto_warmup = True
    
    # Create tool instance
    tool = CCWarmupTool()
    
    if args.test_warmup:
        # Manual warmup test
        tool.send_manual_warmup()
    else:
        # Run main analysis
        asyncio.run(tool.run_analysis(
            lookback_hours=args.lookback,
            claude_dir=args.claude_dir,
            dry_run=args.dry_run,
            send_warmups=auto_warmup,
            detailed_sessions=not args.sessions_only,
            categories_only=args.categories_only,
            specific_project=args.project,
            watch_mode=watch_mode,
            refresh_interval=args.refresh_interval
        ))


if __name__ == "__main__":
    main()
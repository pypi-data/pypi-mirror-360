"""Robust JSONL parser for Claude usage logs with comprehensive error handling."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass

from ..data_structures import AnalysisResult
from .improved_warmup_detector import ImprovedWarmupDetector


@dataclass
class JSONLEntry:
    """Parsed JSONL entry with normalized fields."""
    timestamp: datetime
    raw_data: Dict[str, Any]
    file_path: Path
    line_number: int
    is_warmup: bool = False  # Flag to identify artificial warm-up messages


class JSONLParser:
    """Robust parser for Claude usage JSONL files with error tolerance."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.warmup_detector = ImprovedWarmupDetector()
        self.stats = {
            'files_processed': 0,
            'lines_processed': 0,
            'entries_parsed': 0,
            'parse_errors': 0,
            'missing_timestamps': 0,
            'warmup_messages_detected': 0
        }
    
    def parse_file(self, file_path: Path):
        """
        Parse a single JSONL file with error tolerance.
        
        Args:
            file_path: Path to JSONL file to parse
            
        Returns:
            AnalysisResult containing list of JSONLEntry objects or error
        """
        if not file_path.exists():
            return AnalysisResult.error_result(f"File does not exist: {file_path}")
        
        if not file_path.is_file():
            return AnalysisResult.error_result(f"Path is not a file: {file_path}")
        
        entries = []
        line_number = 0
        file_errors = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_number += 1
                    self.stats['lines_processed'] += 1
                    
                    line = line.strip()
                    if not line:
                        continue  # Skip empty lines
                    
                    try:
                        # Parse JSON
                        raw_data = json.loads(line)
                        
                        # Extract and validate timestamp
                        timestamp = self._extract_timestamp(raw_data)
                        if timestamp is None:
                            self.stats['missing_timestamps'] += 1
                            self.logger.debug(f"Missing timestamp in {file_path}:{line_number}")
                            continue
                        
                        # Detect if this is an artificial warm-up message
                        is_warmup = self._detect_warmup_message(raw_data)
                        if is_warmup:
                            self.stats['warmup_messages_detected'] += 1
                        
                        # Create entry
                        entry = JSONLEntry(
                            timestamp=timestamp,
                            raw_data=raw_data,
                            file_path=file_path,
                            line_number=line_number,
                            is_warmup=is_warmup
                        )
                        entries.append(entry)
                        self.stats['entries_parsed'] += 1
                        
                    except json.JSONDecodeError as e:
                        file_errors += 1
                        self.stats['parse_errors'] += 1
                        self.logger.debug(f"JSON parse error in {file_path}:{line_number}: {e}")
                    except Exception as e:
                        file_errors += 1
                        self.stats['parse_errors'] += 1
                        self.logger.debug(f"Unexpected error in {file_path}:{line_number}: {e}")
        
        except Exception as e:
            return AnalysisResult.error_result(f"Failed to read file {file_path}: {e}")
        
        self.stats['files_processed'] += 1
        
        # Log summary for this file
        self.logger.debug(f"Parsed {file_path}: {len(entries)} entries, {file_errors} errors")
        
        return AnalysisResult.success_result(
            entries,
            metadata={
                'file_path': str(file_path),
                'entries_count': len(entries),
                'parse_errors': file_errors,
                'lines_processed': line_number
            }
        )
    
    def parse_files(self, file_paths: List[Path]):
        """
        Parse multiple JSONL files and combine results.
        
        Args:
            file_paths: List of JSONL file paths to parse
            
        Returns:
            AnalysisResult containing combined list of JSONLEntry objects
        """
        all_entries = []
        total_errors = 0
        failed_files = []
        
        for file_path in file_paths:
            result = self.parse_file(file_path)
            if result.success:
                all_entries.extend(result.data)
            else:
                total_errors += 1
                failed_files.append(str(file_path))
                self.logger.warning(f"Failed to parse {file_path}: {result.error}")
        
        # Sort all entries by timestamp
        all_entries.sort(key=lambda x: x.timestamp)
        
        success = len(failed_files) < len(file_paths)  # Success if at least one file parsed
        
        if success:
            return AnalysisResult.success_result(
                all_entries,
                metadata={
                    'files_attempted': len(file_paths),
                    'files_succeeded': len(file_paths) - len(failed_files),
                    'files_failed': len(failed_files),
                    'failed_files': failed_files,
                    'total_entries': len(all_entries),
                    'parse_stats': self.stats.copy()
                }
            )
        else:
            return AnalysisResult.error_result(
                f"Failed to parse any files. Errors: {failed_files}",
                metadata={'failed_files': failed_files}
            )
    
    def _extract_timestamp(self, raw_data: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract timestamp from raw JSONL data with multiple fallback strategies.
        
        Args:
            raw_data: Raw parsed JSON data
            
        Returns:
            Parsed datetime object or None if not found/parseable
        """
        # Try common timestamp field names
        timestamp_fields = ['timestamp', 'time', 'created_at', 'date']
        
        for field in timestamp_fields:
            if field in raw_data:
                timestamp_str = raw_data[field]
                if timestamp_str:
                    return self._parse_timestamp_string(timestamp_str)
        
        return None
    
    def _parse_timestamp_string(self, timestamp_str: str) -> Optional[datetime]:
        """
        Parse timestamp string with multiple format strategies.
        
        Args:
            timestamp_str: String representation of timestamp
            
        Returns:
            Parsed datetime object or None if unparseable
        """
        # Common timestamp formats to try
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',      # ISO 8601 with microseconds and Z
            '%Y-%m-%dT%H:%M:%S.%f',       # ISO 8601 with microseconds
            '%Y-%m-%dT%H:%M:%SZ',         # ISO 8601 with Z
            '%Y-%m-%dT%H:%M:%S',          # ISO 8601 basic
            '%Y-%m-%d %H:%M:%S.%f',       # Space-separated with microseconds
            '%Y-%m-%d %H:%M:%S',          # Space-separated basic
        ]
        
        for fmt in formats:
            try:
                # Parse and ensure timezone awareness (convert to UTC)
                dt = datetime.strptime(timestamp_str, fmt)
                # If timezone-naive, assume UTC
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=None)  # Keep as UTC-naive for consistency
                return dt
            except ValueError:
                continue
        
        # If all formats fail, log debug message
        self.logger.debug(f"Failed to parse timestamp: {timestamp_str}")
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get parsing statistics."""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset parsing statistics."""
        self.stats = {
            'files_processed': 0,
            'lines_processed': 0,
            'entries_parsed': 0,
            'parse_errors': 0,
            'missing_timestamps': 0,
            'warmup_messages_detected': 0
        }
    
    def _detect_warmup_message(self, raw_data: Dict[str, Any]) -> bool:
        """
        Detect if a JSONL entry represents an artificial warm-up message.
        
        Uses improved detection with specific cc-warmup tool patterns to eliminate
        all false positives from conversations about warmups.
        
        Args:
            raw_data: Raw parsed JSON data from JSONL entry
            
        Returns:
            True ONLY if this contains actual cc-warmup tool patterns
        """
        return self.warmup_detector.detect_warmup_message(raw_data)
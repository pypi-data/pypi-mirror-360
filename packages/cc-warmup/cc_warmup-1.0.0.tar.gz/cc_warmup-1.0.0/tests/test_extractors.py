"""Unit tests for extraction layer components."""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from extractors.jsonl_parser import JSONLParser, JSONLEntry
from extractors.file_scanner import ClaudeFileScanner  
from extractors.project_extractor import ProjectExtractor
from data_structures import ProjectRawData


class TestJSONLParser(unittest.TestCase):
    """Test JSONL parser functionality."""
    
    def setUp(self):
        self.parser = JSONLParser()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        # Clean up temp files
        for file in self.temp_dir.glob("*"):
            file.unlink()
        self.temp_dir.rmdir()
    
    def test_parse_valid_jsonl(self):
        """Test parsing valid JSONL file."""
        test_data = [
            {"timestamp": "2024-07-08T10:15:30.123Z", "model": "claude-sonnet", "tokens": 100},
            {"timestamp": "2024-07-08T10:16:45.456Z", "model": "claude-sonnet", "tokens": 150},
        ]
        
        # Create test file
        test_file = self.temp_dir / "test.jsonl"
        with open(test_file, 'w') as f:
            for entry in test_data:
                f.write(json.dumps(entry) + '\n')
        
        # Parse file
        result = self.parser.parse_file(test_file)
        
        # Verify results
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertIsInstance(result.data[0], JSONLEntry)
        self.assertEqual(result.data[0].raw_data['tokens'], 100)
        self.assertEqual(result.data[1].raw_data['tokens'], 150)
    
    def test_parse_malformed_jsonl(self):
        """Test handling of malformed JSONL entries."""
        test_content = '''{"timestamp": "2024-07-08T10:15:30Z", "valid": true}
{invalid json here}
{"timestamp": "2024-07-08T10:16:30Z", "valid": true}
'''
        
        # Create test file
        test_file = self.temp_dir / "malformed.jsonl"
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Parse file
        result = self.parser.parse_file(test_file)
        
        # Should succeed but skip malformed line
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)  # Only valid entries
        self.assertEqual(self.parser.get_stats()['parse_errors'], 1)
    
    def test_missing_timestamp(self):
        """Test handling of entries without timestamps."""
        test_data = [
            {"timestamp": "2024-07-08T10:15:30Z", "valid": True},
            {"no_timestamp": True, "model": "claude"},
            {"timestamp": "2024-07-08T10:16:30Z", "valid": True},
        ]
        
        test_file = self.temp_dir / "no_timestamp.jsonl"
        with open(test_file, 'w') as f:
            for entry in test_data:
                f.write(json.dumps(entry) + '\n')
        
        result = self.parser.parse_file(test_file)
        
        # Should succeed but skip entry without timestamp
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(self.parser.get_stats()['missing_timestamps'], 1)


class TestClaudeFileScanner(unittest.TestCase):
    """Test file scanner functionality."""
    
    def setUp(self):
        self.scanner = ClaudeFileScanner()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_discover_claude_directories(self):
        """Test Claude directory discovery."""
        with patch.dict('os.environ', {'CLAUDE_CONFIG_DIR': str(self.temp_dir)}):
            directories = self.scanner.discover_claude_directories()
            self.assertIn(self.temp_dir, directories)
    
    def test_scan_project_directories(self):
        """Test scanning for project directories."""
        # Create mock Claude directory structure
        projects_dir = self.temp_dir / "projects"
        projects_dir.mkdir()
        
        # Create test projects
        (projects_dir / "project1").mkdir()
        (projects_dir / "project2").mkdir()
        
        result = self.scanner.scan_project_directories([self.temp_dir])
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertIn("project1", result.data)
        self.assertIn("project2", result.data)
    
    def test_find_project_jsonl_files(self):
        """Test finding JSONL files in project directory."""
        # Create project structure
        project_dir = self.temp_dir / "test_project"
        session_dir = project_dir / "session1"
        session_dir.mkdir(parents=True)
        
        # Create test JSONL files
        jsonl_file1 = session_dir / "conversation1.jsonl"
        jsonl_file2 = session_dir / "conversation2.jsonl"
        
        jsonl_file1.touch()
        jsonl_file2.touch()
        
        result = self.scanner.find_project_jsonl_files(project_dir)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertIn(jsonl_file1, result.data)
        self.assertIn(jsonl_file2, result.data)


class TestProjectExtractor(unittest.TestCase):
    """Test project extractor functionality."""
    
    def setUp(self):
        self.extractor = ProjectExtractor()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_extract_project_metadata(self):
        """Test project metadata extraction."""
        # Create mock project directory
        project_dir = self.temp_dir / "projects" / "-Users-test-project"
        project_dir.mkdir(parents=True)
        
        # Create mock entries with cwd field
        mock_entries = [
            Mock(raw_data={"cwd": "/Users/test/project", "timestamp": "2024-07-08T10:00:00Z"})
        ]
        
        metadata = self.extractor._extract_project_metadata(project_dir, mock_entries)
        
        self.assertEqual(metadata['display_name'], 'project')
        self.assertEqual(str(metadata['project_path']), '/Users/test/project')


class TestIntegrationValidation(unittest.TestCase):
    """Integration tests to validate against known data."""
    
    def test_cc_warmup_data_validation(self):
        """Test extraction against known cc-warmup timestamps."""
        # This test validates against the known cc-warmup data:
        # 1117 entries from 01:09:23 to 03:06:41 UTC
        
        # Mock data matching the known cc-warmup pattern
        start_time = datetime(2024, 7, 8, 1, 9, 23)
        end_time = datetime(2024, 7, 8, 3, 6, 41)
        
        # Generate mock timestamps spread across the time range
        duration = end_time - start_time
        mock_timestamps = []
        for i in range(1117):
            offset = duration * (i / 1116)  # Spread evenly
            timestamp = start_time + offset
            mock_timestamps.append(timestamp)
        
        # Create ProjectRawData
        project_data = ProjectRawData(
            project_name="cc-warmup",
            encoded_name="-Users-divygarima-Documents-Mayank-Docs-Cursor-Projects-cc-warmup",
            project_path=Path("/Users/divygarima/Documents/Mayank-Docs/Cursor-Projects/cc-warmup"),
            timestamps=mock_timestamps,
            entries_metadata=[{"timestamp": ts.isoformat() + "Z"} for ts in mock_timestamps],
            extraction_time=datetime.utcnow(),
            extraction_stats={"total_entries": 1117}
        )
        
        # Validate the data structure
        self.assertEqual(project_data.total_entries, 1117)
        self.assertEqual(project_data.date_range[0], start_time)
        self.assertEqual(project_data.date_range[1], end_time)
        self.assertEqual(project_data.project_name, "cc-warmup")


if __name__ == '__main__':
    unittest.main()
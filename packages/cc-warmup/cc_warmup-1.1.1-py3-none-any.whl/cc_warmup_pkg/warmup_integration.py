#!/usr/bin/env python3
"""Proper warmup integration using claude -p with dedicated project directory."""

import subprocess
import time
import json
from pathlib import Path
from datetime import datetime, UTC
import sys


class ProperWarmupIntegration:
    """Correct implementation using claude -p with dedicated warmup project."""
    
    def __init__(self):
        self.warmup_project_dir = Path.home() / ".cc-warmup" / "warmup_project"
        self.claude_cli_path = "/Users/divygarima/.claude/local/claude"
        
    def setup_warmup_project(self):
        """Create dedicated warmup project directory."""
        self.warmup_project_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Warmup project directory: {self.warmup_project_dir}")
        
    def generate_warmup_message(self) -> str:
        """Generate proper warmup message with timestamp."""
        timestamp = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
        return f"WARM_UP_MSG_{timestamp}"
    
    def send_warmup_message(self) -> bool:
        """Send warmup message using claude -p from warmup project directory."""
        
        warmup_msg = self.generate_warmup_message()
        print(f"📤 Sending warmup: {warmup_msg}")
        
        try:
            # Run claude -p from the dedicated warmup project directory
            result = subprocess.run([
                self.claude_cli_path, '-p', warmup_msg
            ], 
            cwd=self.warmup_project_dir,  # This creates the project based on this directory
            capture_output=True, 
            text=True, 
            timeout=60
            )
            
            print(f"✅ Claude CLI completed (exit code: {result.returncode})")
            if result.stdout:
                print(f"📝 Response: {result.stdout.strip()[:200]}...")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("⏱️  Claude CLI timed out")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def find_warmup_logs(self):
        """Find the JSONL logs for our warmup project."""
        
        # The project directory will be based on the warmup_project_dir path
        encoded_name = self._encode_path(self.warmup_project_dir)
        claude_project_dir = Path.home() / ".claude" / "projects" / encoded_name
        
        print(f"🔍 Looking for logs in: {claude_project_dir}")
        
        if not claude_project_dir.exists():
            print("❌ Warmup project logs not found yet")
            return []
        
        jsonl_files = list(claude_project_dir.glob("*.jsonl"))
        print(f"📄 Found {len(jsonl_files)} JSONL files")
        
        return jsonl_files
    
    def _encode_path(self, path: Path) -> str:
        """Encode path the same way Claude does for project directories."""
        # Claude encodes paths by replacing '/' with '-' and adding '-' prefix
        # For /Users/divygarima/.cc-warmup/warmup_project -> -Users-divygarima--cc-warmup-warmup-project
        encoded = str(path).replace('/', '-')
        return f'-{encoded}'
    
    def verify_warmup_detection(self):
        """Verify our warmup messages are properly detected."""
        
        print("\n🔍 VERIFYING WARMUP DETECTION")
        print("-" * 40)
        
        from .extractors.project_extractor import ProjectExtractor
        
        # Get the encoded name for our warmup project
        encoded_name = self._encode_path(self.warmup_project_dir)
        
        extractor = ProjectExtractor()
        result = extractor.extract_project_timestamps(
            encoded_project_name=encoded_name,
            lookback_hours=1  # Just last hour
        )
        
        if result.success:
            data = result.data
            stats = data.extraction_stats
            
            print(f"✅ Project: {data.project_name}")
            print(f"📊 Total messages: {len(data.timestamps)}")
            print(f"🤖 Warmup messages: {stats.get('warmup_messages', 0)}")
            print(f"📈 Warmup ratio: {stats.get('warmup_ratio', 0)*100:.1f}%")
            
            if stats.get('warmup_messages', 0) > 0:
                print("🎯 SUCCESS: Warmup messages detected correctly!")
                return True
            else:
                print("⚠️  No warmup messages detected")
                return False
        else:
            print(f"❌ Failed to extract data: {result.error}")
            return False



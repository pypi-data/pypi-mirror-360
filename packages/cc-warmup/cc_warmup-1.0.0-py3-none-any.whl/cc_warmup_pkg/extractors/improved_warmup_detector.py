"""Improved warmup detection specifically for cc-warmup tool messages."""

import re
from datetime import datetime
from typing import Dict, Any


class ImprovedWarmupDetector:
    """Enhanced warmup detection that focuses on actual cc-warmup tool patterns."""
    
    def __init__(self):
        # Specific patterns that indicate actual cc-warmup tool usage
        self.cc_warmup_patterns = [
            # Primary pattern: WARM_UP_MSG_{timestamp} from claude -p command
            r'WARM_UP_MSG_\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?'
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.cc_warmup_patterns]
    
    def detect_warmup_message(self, raw_data: Dict[str, Any]) -> bool:
        """
        Detect if a JSONL entry represents an actual cc-warmup tool message.
        
        STRICTLY checks ONLY for messages of the form "WARM_UP_MSG_{timestamp}"
        from "claude -p 'WARM_UP_MSG_{timestamp}'" commands.
        
        Args:
            raw_data: Raw parsed JSON data from JSONL entry
            
        Returns:
            True if this is an actual cc-warmup tool message
        """
        # STRICT: Only check for exact WARM_UP_MSG_{timestamp} pattern in message content
        return self._check_strict_warmup_pattern(raw_data)
    
    def _check_strict_warmup_pattern(self, raw_data: Dict[str, Any]) -> bool:
        """
        STRICT check for exact WARM_UP_MSG_{timestamp} pattern.
        
        Only matches user messages that contain EXACTLY "WARM_UP_MSG_{timestamp}"
        as the primary content, indicating a "claude -p 'WARM_UP_MSG_{timestamp}'" command.
        """
        # Must be a user message
        if raw_data.get('type') != 'user':
            return False
        
        # Get message content from the user message
        message_content = ""
        if 'message' in raw_data and isinstance(raw_data['message'], dict):
            if 'content' in raw_data['message']:
                content = raw_data['message']['content']
                if isinstance(content, str):
                    message_content = content.strip()
                elif isinstance(content, list):
                    # Handle list of content objects
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            message_content += " " + str(item['text']).strip()
                    message_content = message_content.strip()
        
        if not message_content:
            return False
        
        # STRICT: Check if the message content matches EXACTLY the WARM_UP_MSG pattern
        # The entire message should be just "WARM_UP_MSG_{timestamp}" with minimal variation
        for pattern in self.compiled_patterns:
            match = pattern.search(message_content)
            if match:
                # Additional check: the matched pattern should be the primary content
                # Allow for minor whitespace but not other significant text
                cleaned_content = message_content.replace('\n', ' ').replace('\t', ' ').strip()
                if len(cleaned_content) <= len(match.group()) + 10:  # Allow 10 chars padding for whitespace
                    return True
        
        return False
    
    def _check_tool_metadata(self, raw_data: Dict[str, Any]) -> bool:
        """Check for explicit cc-warmup tool identification in metadata."""
        
        # Check for cc-warmup in source/tool/userAgent fields
        metadata_fields = ['source', 'tool', 'userAgent', 'client']
        for field in metadata_fields:
            if field in raw_data:
                value = str(raw_data[field]).lower()
                if 'cc-warmup' in value and ('tool' in value or 'cli' in value):
                    return True
        
        # Check for session type
        if raw_data.get('sessionType') == 'warmup':
            return True
        
        # Check for cc-warmup specific command metadata
        if 'command' in raw_data and 'cc-warmup' in str(raw_data['command']).lower():
            return True
        
        return False
    
    def _check_message_patterns(self, raw_data: Dict[str, Any]) -> bool:
        """Check message content for specific cc-warmup tool patterns."""
        
        # Get all text content from the message
        text_fields = ['input', 'output', 'prompt', 'response', 'message', 'content']
        full_text = ""
        
        for field in text_fields:
            if field in raw_data and raw_data[field]:
                full_text += " " + str(raw_data[field])
        
        # Also check nested message.content structure (from actual JSONL files)
        if 'message' in raw_data and isinstance(raw_data['message'], dict):
            message_obj = raw_data['message']
            if 'content' in message_obj:
                content = message_obj['content']
                if isinstance(content, str):
                    full_text += " " + content
                elif isinstance(content, list):
                    # Handle list of content objects
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            full_text += " " + str(item['text'])
        
        if not full_text.strip():
            return False
        
        # Check against specific cc-warmup patterns
        for pattern in self.compiled_patterns:
            if pattern.search(full_text):
                return True
        
        return False
    
    def _check_timing_characteristics(self, raw_data: Dict[str, Any]) -> bool:
        """Check for timing patterns characteristic of cc-warmup tool."""
        
        # Check if timestamp is at x:55+ (cc-warmup runs at x:55)
        timestamp_str = raw_data.get('timestamp')
        if timestamp_str:
            try:
                # Parse timestamp
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                minute = dt.minute
                
                # cc-warmup tool runs at x:55+, so messages at 55-59 minutes are suspicious
                if 55 <= minute <= 59:
                    # Additional checks for cc-warmup characteristics
                    
                    # Very minimal content (cc-warmup sends minimal messages)
                    text_content = self._get_text_content(raw_data)
                    if len(text_content.strip()) < 50:  # Short message
                        
                        # Check for basic warmup indicators in minimal message
                        if any(word in text_content.lower() for word in ['ping', 'warm', 'extend']):
                            return True
                
            except Exception:
                pass  # Invalid timestamp format
        
        return False
    
    def _get_text_content(self, raw_data: Dict[str, Any]) -> str:
        """Extract all text content from a JSONL entry."""
        text_fields = ['input', 'output', 'prompt', 'response', 'message', 'content']
        content_parts = []
        
        for field in text_fields:
            if field in raw_data and raw_data[field]:
                content_parts.append(str(raw_data[field]))
        
        return " ".join(content_parts)
    
    def get_detection_reason(self, raw_data: Dict[str, Any]) -> str:
        """Get human-readable reason why a message was detected as warmup."""
        
        if self._check_strict_warmup_pattern(raw_data):
            return "STRICT: exact WARM_UP_MSG_{timestamp} pattern in user message"
        else:
            return "no detection (strict mode)"


# Test the improved detector
def test_improved_detection():
    """Test the improved warmup detection against known patterns."""
    
    detector = ImprovedWarmupDetector()
    
    test_cases = [
        # Should be detected as warmup
        {
            'input': 'console.log("warm-up ping @ " + new Date().toISOString());',
            'timestamp': '2025-07-08T03:55:30Z',
            'should_detect': True,
            'description': 'Actual cc-warmup console.log pattern'
        },
        
        {
            'content': 'cc-warmup ping @ 2025-07-08T03:55:00Z',
            'source': 'cc-warmup-tool',
            'timestamp': '2025-07-08T03:55:00Z',
            'should_detect': True,
            'description': 'cc-warmup tool with timestamp'
        },
        
        {
            'message': 'Warm-up at 2025-07-08 03:55:00 UTC',
            'timestamp': '2025-07-08T03:55:00Z',
            'should_detect': True,
            'description': 'Warm-up message with UTC timestamp'
        },
        
        # Should NOT be detected as warmup
        {
            'content': 'Let me check the actual warmup messages being detected',
            'timestamp': '2025-07-08T03:45:30Z',
            'should_detect': False,
            'description': 'Conversation about warmups (not actual warmup)'
        },
        
        {
            'input': 'ping',
            'timestamp': '2025-07-08T03:45:30Z',
            'should_detect': False,
            'description': 'Generic ping (not cc-warmup)'
        },
        
        {
            'content': 'Hi there! How can I help?',
            'timestamp': '2025-07-08T03:55:30Z',
            'should_detect': False,
            'description': 'Normal conversation at x:55'
        }
    ]
    
    print("🧪 Testing Improved Warmup Detection")
    print("=" * 60)
    
    correct = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        # Remove test metadata
        test_data = {k: v for k, v in test_case.items() 
                    if k not in ['should_detect', 'description']}
        
        detected = detector.detect_warmup_message(test_data)
        expected = test_case['should_detect']
        
        status = "✅ PASS" if detected == expected else "❌ FAIL"
        if detected == expected:
            correct += 1
        
        print(f"{i}. {status} - {test_case['description']}")
        print(f"   Expected: {expected}, Got: {detected}")
        
        if detected:
            reason = detector.get_detection_reason(test_data)
            print(f"   Reason: {reason}")
        
        print()
    
    print(f"🎯 Results: {correct}/{total} tests passed ({correct/total*100:.1f}%)")
    
    if correct == total:
        print("✅ All tests passed! Improved detection is working correctly.")
    else:
        print("⚠️  Some tests failed. Detection logic needs refinement.")


if __name__ == "__main__":
    test_improved_detection()
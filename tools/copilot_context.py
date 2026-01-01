"""
Context usage tracker for Copilot CLI
Tracks token usage and provides percentage to truncation
"""
from typing import Optional


class ContextTracker:
    """Track context window usage"""
    
    def __init__(self, max_tokens: int = 200000):
        """
        Initialize context tracker
        
        Args:
            max_tokens: Maximum context window size in tokens
        """
        self.max_tokens = max_tokens
        self.used_tokens = 0
        self.last_request_tokens = 0
    
    def update(self, tokens: int):
        """
        Update token usage
        
        Args:
            tokens: Number of tokens used in last request
        """
        self.last_request_tokens = tokens
        self.used_tokens += tokens
    
    def get_usage_percentage(self) -> float:
        """
        Get current usage as percentage (0.0 - 1.0)
        
        Returns:
            Percentage of context window used
        """
        if self.max_tokens == 0:
            return 0.0
        return min(1.0, self.used_tokens / self.max_tokens)
    
    def get_percentage_to_truncation(self) -> float:
        """
        Get percentage remaining until truncation
        
        Returns:
            Percentage remaining (0.0 - 1.0)
        """
        return 1.0 - self.get_usage_percentage()
    
    def reset(self):
        """Reset context usage"""
        self.used_tokens = 0
        self.last_request_tokens = 0
    
    def get_display_string(self) -> str:
        """
        Get formatted display string for footer
        
        Returns:
            String like "13% to truncation"
        """
        remaining = self.get_percentage_to_truncation()
        percentage = int(remaining * 100)
        return f"{percentage}% to truncation"


class RequestQuotaTracker:
    """Track API request quota"""
    
    def __init__(self, max_requests: int = 1000):
        """
        Initialize quota tracker
        
        Args:
            max_requests: Maximum requests per period
        """
        self.max_requests = max_requests
        self.requests_made = 0
    
    def increment(self):
        """Increment request count"""
        self.requests_made += 1
    
    def get_remaining_percentage(self) -> float:
        """
        Get remaining requests as percentage
        
        Returns:
            Percentage remaining (0.0 - 100.0)
        """
        if self.max_requests == 0:
            return 0.0
        remaining = self.max_requests - self.requests_made
        return (remaining / self.max_requests) * 100.0
    
    def reset(self):
        """Reset request count"""
        self.requests_made = 0
    
    def get_display_string(self) -> str:
        """
        Get formatted display string
        
        Returns:
            String like "Remaining requests: 98.2%"
        """
        return f"Remaining requests: {self.get_remaining_percentage():.1f}%"


# Global trackers
_context_tracker: Optional[ContextTracker] = None
_quota_tracker: Optional[RequestQuotaTracker] = None


def get_context_tracker() -> ContextTracker:
    """Get or create global context tracker"""
    global _context_tracker
    if _context_tracker is None:
        _context_tracker = ContextTracker()
    return _context_tracker


def get_quota_tracker() -> RequestQuotaTracker:
    """Get or create global quota tracker"""
    global _quota_tracker
    if _quota_tracker is None:
        _quota_tracker = RequestQuotaTracker()
    return _quota_tracker


def reset_trackers():
    """Reset all trackers"""
    get_context_tracker().reset()
    get_quota_tracker().reset()

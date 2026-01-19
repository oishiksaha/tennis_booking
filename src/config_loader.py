"""Configuration loader for the tennis booking bot."""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any
from datetime import datetime

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the booking bot."""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration from YAML file and environment variables."""
        if config_path is None:
            # Default to config/config.yaml relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self._load_config()
        self._load_env()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    
    def _load_env(self):
        """Load configuration from environment variables."""
        self.booking_url = os.getenv('BOOKING_URL', self._config['urls']['program'])
        self.browser_state_path = Path(os.getenv('BROWSER_STATE_PATH', 'data/browser_state'))
        self.timezone = os.getenv('TIMEZONE', 'America/New_York')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/booking_bot.log')
        
        # Microsoft Graph API (optional)
        self.ms_client_id = os.getenv('MS_CLIENT_ID')
        self.ms_client_secret = os.getenv('MS_CLIENT_SECRET')
        self.ms_tenant_id = os.getenv('MS_TENANT_ID')
    
    @property
    def booking_times(self) -> List[str]:
        """Get list of target booking times."""
        return self._config['booking_times']
    
    @property
    def booking_window_days(self) -> int:
        """Get booking window in days."""
        return self._config['booking_window_days']
    
    @property
    def court_preference(self) -> str:
        """Get court preference setting."""
        return self._config['court_preference']
    
    @property
    def preferred_courts(self) -> List[str]:
        """Get list of preferred courts."""
        return self._config.get('preferred_courts', [])
    
    @property
    def urls(self) -> Dict[str, str]:
        """Get URL configuration."""
        return self._config['urls']
    
    @property
    def selectors(self) -> Dict[str, str]:
        """Get CSS selector configuration."""
        return self._config['selectors']
    
    @property
    def booking(self) -> Dict[str, Any]:
        """Get booking behavior configuration."""
        return self._config['booking']
    
    @property
    def scheduler(self) -> Dict[str, Any]:
        """Get scheduler configuration."""
        return self._config['scheduler']
    
    @property
    def test_mode_enabled(self) -> bool:
        """Check if test mode is enabled."""
        return self._config.get('test_mode', {}).get('enabled', False)
    
    @property
    def test_target_date(self) -> datetime:
        """Get target date for test mode (parsed from YYYY-MM-DD format)."""
        if not self.test_mode_enabled:
            return None
        date_str = self._config.get('test_mode', {}).get('target_date')
        if date_str:
            return datetime.strptime(date_str, '%Y-%m-%d')
        return None
    
    @property
    def test_target_court(self) -> str:
        """Get target court name for test mode."""
        if not self.test_mode_enabled:
            return None
        return self._config.get('test_mode', {}).get('target_court')
    
    @property
    def test_target_time(self) -> List[str]:
        """Get target time for test mode as a list (e.g., ["11:00"])."""
        if not self.test_mode_enabled:
            return None
        time_str = self._config.get('test_mode', {}).get('target_time')
        if time_str:
            return [time_str]
        return None
    
    def get_browser_state_path(self) -> Path:
        """Get path to browser state directory."""
        return self.browser_state_path
    
    def get_browser_state_file(self) -> Path:
        """Get path to browser state file."""
        return self.browser_state_path / "browser_state.json"


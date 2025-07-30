#!/usr/bin/python

import os
import yaml
from typing import Dict, Optional
from robot.api.deco import keyword, library

class Board:
    """YAML-based configuration handler - loads everything from config.yml"""

    def __init__(self, config_file: str = "config.yml"):
        self.config_file = config_file
        self.config_data = {}
        self.current_board = None
        
        # All values will be set from config.yml
        self.DEFAULT_BOARD_TYPE = None
        self.DEFAULT_IMAGE_TYPE = None
        self.BOARD = None
        self.SERIAL_PORT = None
        self.BAUD_RATE = None
        self.PLATFORM = None
        self.IP_ADDR_1 = None
        self.IP_ADDR_2 = None
        self.SERVER_ADDR = None
        self.RESTART_IF_FAILED = None
        self.FAIL_MEG = None
        
        # Load configuration and auto-detect defaults
        self._load_config()
        self._detect_defaults()
        # Don't set board type yet - will be set by test_handler

    def _load_config(self):
        """Load YAML configuration file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', self.config_file)
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self.config_data = yaml.safe_load(file) or {}
                print(f"Loaded config from {config_path}")
            else:
                print(f"Config file not found: {config_path}")
                self.config_data = {}
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config_data = {}

    def _detect_defaults(self):
        """Auto-detect all defaults from config.yml"""
        board_configs = self.config_data.get('board_configs', {})
        
        if not board_configs:
            print("Warning: No board_configs found in config.yml")
            return
        
        # Find first enabled board for defaults
        default_board = None
        for board_name, board_config in board_configs.items():
            if board_config.get('enabled', False):
                default_board = board_config
                self.DEFAULT_BOARD_TYPE = board_name
                print(f"Auto-detected default board: {self.DEFAULT_BOARD_TYPE}")
                break
        
        # If no enabled boards, use first available board
        if not default_board and board_configs:
            first_board_name = list(board_configs.keys())[0]
            default_board = board_configs[first_board_name]
            self.DEFAULT_BOARD_TYPE = first_board_name
            print(f"No enabled boards found, using first available: {self.DEFAULT_BOARD_TYPE}")
        
        # Set values directly from detected board config - no hardcode fallbacks
        if default_board:
            self.SERIAL_PORT = default_board.get('serial_port')
            self.BAUD_RATE = default_board.get('baud_rate')
            self.PLATFORM = default_board.get('platform')
            self.IP_ADDR_1 = default_board.get('ip_addr_1')
            self.IP_ADDR_2 = default_board.get('ip_addr_2')
            self.SERVER_ADDR = default_board.get('server_addr')
            
            # Detect default image from board's images
            images = default_board.get('images', {})
            for img_name, img_config in images.items():
                if img_config.get('enabled', False):
                    self.DEFAULT_IMAGE_TYPE = img_name
                    break
            
            # If no enabled images, use first available
            if not self.DEFAULT_IMAGE_TYPE and images:
                self.DEFAULT_IMAGE_TYPE = list(images.keys())[0]
        
        # Only set these if still None after config loading
        if not self.DEFAULT_IMAGE_TYPE:
            print("Warning: No images found in config, using fallback image type")
            self.DEFAULT_IMAGE_TYPE = "core-image-bsp"
        
        self.RESTART_IF_FAILED = False
        self.FAIL_MEG = "Test failed after retries"
        
        print(f"Detected defaults - Board: {self.DEFAULT_BOARD_TYPE}, Image: {self.DEFAULT_IMAGE_TYPE}")
        print(f"Board settings - Platform: {self.PLATFORM}, Port: {self.SERIAL_PORT}, Baud: {self.BAUD_RATE}")

    @keyword('Set Board Type')
    def set_board_type(self, board_type: str = None):
        """Sets the current board type and updates all info from config"""
        self.current_board = board_type or self.DEFAULT_BOARD_TYPE
        self.BOARD = self.current_board
        
        # Update all values from current board config
        board_config = self.get_board_config(self.current_board)
        if board_config:
            self.PLATFORM = board_config.get('platform', self.PLATFORM)
            self.SERIAL_PORT = board_config.get('serial_port', self.SERIAL_PORT)
            self.BAUD_RATE = board_config.get('baud_rate', self.BAUD_RATE)
            self.IP_ADDR_1 = board_config.get('ip_addr_1', self.IP_ADDR_1)
            self.IP_ADDR_2 = board_config.get('ip_addr_2', self.IP_ADDR_2)
            self.SERVER_ADDR = board_config.get('server_addr', self.SERVER_ADDR)

    @keyword('Get Board Config')
    def get_board_config(self, board_type: str = None) -> dict:
        """Returns the full configuration dictionary for the specified board type"""
        board = board_type or self.current_board or self.DEFAULT_BOARD_TYPE
        return self.config_data.get('board_configs', {}).get(board, {})

    @keyword('Get Board Images')
    def get_board_images(self, board_type: str = None) -> dict:
        """Returns all image configurations for the specified board"""
        return self.get_board_config(board_type).get('images', {})

    @keyword('Get Feature Config')
    def get_feature_config(self, feature_name: str, board_type: str = None, image_type: str = None) -> dict:
        """Returns the raw feature configuration from YAML for a given feature"""
        images = self.get_board_images(board_type)
        img = images.get(image_type or self.DEFAULT_IMAGE_TYPE, {})
        return img.get('features', {}).get(feature_name, {})

    @keyword('Get Feature Instances')
    def get_feature_instances(self, feature_name: str, board_type: str = None, image_type: str = None) -> dict:
        """Returns instance-specific configurations for a feature"""
        feat = self.get_feature_config(feature_name, board_type, image_type)
        return feat.get('instances', {})

    @keyword('Get USB Relay Config')
    def get_usb_relay_config(self, board_type: str = None) -> dict:
        """Returns USB relay configuration for board"""
        board_config = self.get_board_config(board_type)
        return board_config.get('usb_relay_config', {})

    @keyword('Get WiFi Config')
    def get_wifi_config(self) -> dict:
        """Returns WiFi configuration"""
        return self.config_data.get('wifi_config', {})

    @keyword('Get Bluetooth Config')
    def get_bluetooth_config(self) -> dict:
        """Returns Bluetooth configuration"""
        return self.config_data.get('bluetooth_config', {})

# Global configuration management with board context
_config_instance = None
_config_file = "config.yml"
_current_board_type = None  # Track current board being tested

def load_yaml(config_file: str) -> dict:
    """Load YAML configuration file and return as dictionary"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', config_file)
        if not os.path.exists(config_path):
            print(f"Warning: Configuration file {config_file} not found at {config_path}")
            return {}
        
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file) or {}
        
        print(f"Loaded {config_file}: {len(config_data)} top-level keys")
        return config_data
    except Exception as e:
        print(f"Error loading {config_file}: {e}")
        return {}

def get_config(config_file: str = None, board_type: str = None):
    """Get singleton config instance with board context"""
    global _config_instance, _config_file, _current_board_type

    # If config file changed, recreate instance
    if config_file and config_file != _config_file:
        _config_file = config_file
        _config_instance = Board(config_file)
    elif _config_instance is None:
        _config_instance = Board(_config_file)

    # If board_type provided, update current board context
    if board_type:
        _current_board_type = board_type
        _config_instance.set_board_type(board_type)
        print(f"Config context set to board: {board_type}")
    
    # If board context exists but config instance doesn't have it set
    elif _current_board_type and _config_instance.BOARD != _current_board_type:
        _config_instance.set_board_type(_current_board_type)
        print(f"Config context restored to board: {_current_board_type}")

    return _config_instance

def set_config_file(config_file: str) -> None:
    """Set configuration file and force recreation of config instance"""
    global _config_instance, _config_file
    _config_file = config_file
    _config_instance = None

def set_board_type(board_type: str = None) -> None:
    """Set board type on global config instance and maintain context"""
    global _current_board_type
    
    _current_board_type = board_type
    config = get_config()
    config.set_board_type(board_type)
    print(f"Global board context set to: {board_type}")

def get_board_config(board_type: str = None) -> dict:
    """Get board configuration from global config instance"""
    # Use current board context if no board_type specified
    effective_board = board_type or _current_board_type
    config = get_config()
    return config.get_board_config(effective_board)

def get_current_board_type() -> str:
    """Get the current board type in context"""
    global _current_board_type
    return _current_board_type

def __getattr__(name):
    """Dynamic attribute access to global config instance"""
    config = get_config()
    if hasattr(config, name):
        return getattr(config, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
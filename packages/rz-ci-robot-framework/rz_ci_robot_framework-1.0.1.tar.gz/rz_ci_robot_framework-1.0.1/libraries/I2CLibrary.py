#!/usr/bin/env python3
import time
import os
import sys
import re
from robot.api.deco import keyword, library
from robot.api import logger

# Add parent directories to Python path for module imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

# Import consistent config system
try:
    from board_config import get_config, get_current_board_type
    logger.info("Imported get_config from board_config successfully")
except ImportError as e:
    logger.error(f"Failed to import board_config: {e}")
    raise

@library(scope='GLOBAL', version='1.0')
class I2CLibrary:
    """Robot Framework library for I2C bus testing, fully dynamic based on board configuration."""

    def __init__(self):
        """
        Initializes the I2CLibrary instance.
        This method is called automatically by Robot Framework when the library is imported.
        """
        logger.info("I2CLibrary: __init__ method called. Initializing configuration system.")
        self.serial = None
        self._config = None
        self.current_board_type = None
        self.i2c_defaults = {}

        try:
            # Use same config system as other libraries
            self._config = get_config()
            logger.info("I2CLibrary: Configuration system initialized successfully.")
            
            # Get current board type and load defaults
            self._load_board_defaults()
            
        except Exception as e:
            logger.error(f"I2CLibrary: Failed to initialize configuration system: {e}")
            raise

        logger.info(f"I2CLibrary: Instance initialized for board type: {self.current_board_type}")

    def _load_board_defaults(self):
        """Load I2C defaults from board configuration"""
        try:
            self.current_board_type = get_current_board_type()
            if not self.current_board_type:
                logger.warn("No current board type set, will use runtime board type")
                return
            
            # Get board configuration
            board_config = self._config.get_board_config(self.current_board_type)
            if not board_config:
                logger.warn(f"No configuration found for board: {self.current_board_type}")
                return
                
            # Look for I2C configuration in board config
            i2c_config = board_config.get('i2c', {})
            if i2c_config:
                # Use first I2C instance as defaults
                for instance_name, instance_config in i2c_config.items():
                    if isinstance(instance_config, dict) and instance_config.get('enabled') is True:
                        self.i2c_defaults = {
                            'i2c_bus': instance_config.get('i2c_bus', 1),
                            'expected_addr': str(instance_config.get('expected_addr', '')),
                            'retry_count': instance_config.get('retry_count', 3),
                            'delay_between_commands': instance_config.get('delay_between_commands', 1)
                        }
                        logger.info(f"Loaded I2C defaults from config: {self.i2c_defaults}")
                        return
                
                logger.warn("No enabled I2C instances found in configuration")
            else:
                logger.warn("No I2C configuration found in board config")
                
        except Exception as e:
            logger.error(f"Failed to load board defaults: {e}")

    @keyword("Init I2C Library")
    def init(self, serial_conn, board_type=None):
        """
        Initializes the serial connection for I2C operations.
        Optionally specify board_type to override current board configuration.
        """
        self.serial = serial_conn
        
        if board_type:
            self.current_board_type = board_type
            self._config.set_board_type(board_type)
            self._load_board_defaults()
            
        logger.info(f"I2C Library initialized with serial connection for board: {self.current_board_type}")

    @keyword("Set I2C Parameters")
    def set_i2c_parameters(self, i2c_bus=None, expected_addr=None, retry_count=None, delay_between_commands=None):
        """
        Set I2C runtime parameters.
        Uses board configuration defaults if parameters not provided.
        """
        # Use provided values or fall back to board defaults or system defaults
        self.i2c_bus = int(i2c_bus) if i2c_bus is not None else self.i2c_defaults.get('i2c_bus', 1)
        self.expected_addr = str(expected_addr) if expected_addr is not None else self.i2c_defaults.get('expected_addr', "")
        self.retry_count = int(retry_count) if retry_count is not None else self.i2c_defaults.get('retry_count', 3)
        self.delay_between_commands = int(delay_between_commands) if delay_between_commands is not None else self.i2c_defaults.get('delay_between_commands', 1)
        
        logger.info(f"I2C parameters set: bus={self.i2c_bus}, expected_addr=0x{self.expected_addr}, "
                    f"retries={self.retry_count}, delay={self.delay_between_commands}s")

    @keyword("Detect I2C Adapter")
    def detect_i2c_adapter(self, delay=None):
        """
        Detect available I2C adapters using `i2cdetect -l` and return output.
        Requires an active serial connection.
        """
        if not self.serial:
            raise Exception("Serial connection not initialized. Call 'Init I2C Library' first.")

        # Use the provided delay or the default delay_between_commands
        delay = delay or getattr(self, 'delay_between_commands', self.i2c_defaults.get('delay_between_commands', 1))

        try:
            target_bus = getattr(self, 'i2c_bus', self.i2c_defaults.get('i2c_bus', 1))
            logger.info(f"[I2C] Detecting adapters (focusing on i2c-{target_bus})...")

            # Clear any pending input from the serial buffer before sending a new command
            self.serial.reset_input_buffer()
            cmd = "i2cdetect -l\n" # Command to list I2C adapters
            self.serial.write(cmd.encode()) # Send command over serial

            # Wait for output. Adding 2 seconds to the configured delay for robustness.
            time.sleep(delay + 2)
            # Read all available data from the serial port
            output = self.serial.read(self.serial.in_waiting).decode(errors='ignore')

            logger.info(f"[I2C] Adapter list:\n{output}")
            return output

        except Exception as e:
            logger.error(f"[I2C] Adapter detection failed: {e}")
            return "" # Return empty string on failure

    @keyword("Scan I2C Device")
    def scan_i2c_device(self, i2c_bus: int, delay=2):
        """
        Run i2cdetect to scan I2C devices on a specific bus.
        Requires an active serial connection.
        """
        if not self.serial:
            raise Exception("Serial connection not initialized. Call 'Init I2C Library' first.")
        try:
            self.serial.reset_input_buffer()
            cmd = f"i2cdetect -y -r {i2c_bus}\n" # Command to scan a specific I2C bus
            self.serial.write(cmd.encode());
            time.sleep(delay + 2) # Wait for scan to complete and output to arrive

            output = self.serial.read(self.serial.in_waiting).decode(errors='ignore')
            logger.info(f"[I2C] Scan result for bus {i2c_bus}:\n{output}")
            return output
        except Exception as e:
            logger.error(f"I2C scan failed: {e}")
            return ""

    @keyword("Verify I2C Address Present")
    def verify_i2c_address_present(self, i2c_bus: int, expected_addr: str, delay=2):
        """
        Scan I2C bus and verify that expected address is present.
        Returns True if found, else False.
        """
        output = self.scan_i2c_device(i2c_bus, delay)
        # Check if the expected address (case-insensitive) is in the scan output
        if expected_addr.lower() in output.lower():
            logger.info(f"[I2C] ✓ Found expected address 0x{expected_addr} on i2c-{i2c_bus}")
            return True
        else:
            logger.warn(f"[I2C] ✗ Address 0x{expected_addr} not found on i2c-{i2c_bus}")
            return False

    @keyword("Get I2C Bus Address Pairs")
    def get_i2c_bus_address_pairs(self, board_type):
        """
        Retrieves I2C bus and address pairs based on the board configuration.
        """
        if not self._config:
            logger.error("Configuration system not initialized. Cannot retrieve I2C bus address pairs.")
            return []
        
        effective_board = board_type or self.current_board_type
        if not effective_board:
            logger.error("No board type specified and no current board type set")
            return []
        
        try:
            # Get board configuration
            board_config = self._config.get_board_config(effective_board)
            if not board_config:
                logger.error(f"No configuration found for board: {effective_board}")
                return []
            
            logger.info(f"Board config structure: {list(board_config.keys())}")
            
            # Look for I2C configuration in the nested structure
            pairs = []
            
            # Check for images in board config
            images = board_config.get('images', {})
            if not images:
                logger.warn(f"No images found in board configuration for: {effective_board}")
                return []
            
            # Search through all enabled images
            for image_name, image_config in images.items():
                if not isinstance(image_config, dict):
                    continue
                    
                if not image_config.get('enabled', False):
                    logger.info(f"Skipping disabled image: {image_name}")
                    continue
                    
                logger.info(f"Checking image '{image_name}' for I2C features")
                
                # Look for features in this image
                features = image_config.get('features', {})
                i2c_feature = features.get('i2c', {})
                
                if not i2c_feature:
                    logger.info(f"No I2C feature found in image: {image_name}")
                    continue
                    
                if not i2c_feature.get('enabled', False):
                    logger.info(f"I2C feature disabled in image: {image_name}")
                    continue
                    
                logger.info(f"Found enabled I2C feature in image: {image_name}")
                
                # Get I2C instances from this feature
                instances = i2c_feature.get('instances', {})
                if not instances:
                    logger.warn(f"No I2C instances found in {image_name}")
                    continue
                
                logger.info(f"I2C instances in {image_name}: {instances}")
                
                # Process each I2C instance
                for instance_name, instance_config in instances.items():
                    if not isinstance(instance_config, dict):
                        continue
                        
                    # Check if this instance is enabled (handle string "disable" vs boolean False)
                    enabled = instance_config.get("enabled")
                    if enabled != True and enabled != "true":
                        logger.info(f"Skipping I2C instance '{instance_name}' - enabled: {enabled}")
                        continue
                    
                    bus = instance_config.get("i2c_bus")
                    addr = instance_config.get("expected_addr")
                    
                    if bus is not None and addr is not None:
                        pairs.append((int(bus), str(addr)))
                        logger.info(f"Added I2C pair from instance '{instance_name}' in image '{image_name}': bus={bus}, addr={addr}")
                    else:
                        logger.warn(f"Skipping I2C instance '{instance_name}' due to missing 'i2c_bus' or 'expected_addr'.")
            
            logger.info(f"Final I2C bus/address pairs for {effective_board}: {pairs}")
            return pairs
            
        except Exception as e:
            logger.error(f"Failed to get I2C configuration for board type '{effective_board}': {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
# [MermaidChart: 45b3052b-a61b-4c90-8164-e715cea84e11]
            return []
#!/usr/bin/env python3
"""
Command-line interface for rz-ci-robot-framework package
"""

import argparse
import sys
import os
from pathlib import Path

from .version import __version__

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='RZ-CI Robot Framework - Board testing framework for Renesas RZ boards',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version=f'rz-ci-robot-framework {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--config', help='Configuration file path')
    test_parser.add_argument('--board', help='Board type')
    
    # List features command  
    list_parser = subparsers.add_parser('list-features', help='List available features')
    
    # Validate config command
    validate_parser = subparsers.add_parser('validate-config', help='Validate configuration file')
    validate_parser.add_argument('config_file', help='Configuration file to validate')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
        
    if args.command == 'test':
        print(f"RZ-CI Robot Framework v{__version__}")
        print("Test command - functionality coming soon!")
        return 0
        
    elif args.command == 'list-features':
        print("Available features:")
        print("- I2C communication testing")
        print("- SPI communication testing") 
        print("- GPIO testing")
        print("- Serial communication testing")
        print("- Board configuration management")
        return 0
        
    elif args.command == 'validate-config':
        print(f"Validating configuration file: {args.config_file}")
        if not os.path.exists(args.config_file):
            print(f"Error: Configuration file {args.config_file} not found")
            return 1
        print("Configuration validation - functionality coming soon!")
        return 0
        
    return 0

def list_features_main():
    """CLI entry point for listing features"""
    print("Available features:")
    print("- I2C communication testing")
    print("- SPI communication testing") 
    print("- GPIO testing")
    print("- Serial communication testing")
    print("- Board configuration management")
    return 0

def validate_config_main():
    """CLI entry point for validating configuration"""
    parser = argparse.ArgumentParser(description='Validate RZ-CI configuration file')
    parser.add_argument('config_file', help='Configuration file to validate')
    args = parser.parse_args()
    
    if not os.path.exists(args.config_file):
        print(f"Error: Configuration file {args.config_file} not found")
        return 1
        
    print(f"Validating configuration file: {args.config_file}")
    print("Configuration validation - functionality coming soon!")
    return 0

if __name__ == '__main__':
    sys.exit(main())

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='RZ-CI Robot Framework - Board Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rz-ci-test rzsbc                    # Run all tests for rzsbc board
  rz-ci-test rzv2h --dry-run         # Show what tests would run
  rz-ci-test rzsbc --config my.yml   # Use custom configuration
        """
    )
    
    parser.add_argument(
        'board_type',
        help='Board type to test (e.g., rzsbc, rzv2h)'
    )
    
    parser.add_argument(
        '--config',
        default='config.yml',
        help='Configuration file path (default: config.yml)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what tests would run without executing them'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'rz-ci-robot-framework {__version__}'
    )
    
    parser.add_argument(
        '--list-features',
        action='store_true',
        help='List available features for the board'
    )
    
    parser.add_argument(
        '--output-dir',
        default='logs',
        help='Output directory for test results (default: logs)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize test handler
        runner = TestHandler(
            board_type=args.board_type,
            config_file=args.config
        )
        
        if args.list_features:
            runner.list_features()
        else:
            # Run tests
            result = runner.run_board(dry_run=args.dry_run)
            sys.exit(result)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def list_features_main():
    """CLI entry point for listing features"""
    parser = argparse.ArgumentParser(
        description='List available features for RZ boards'
    )
    
    parser.add_argument(
        'board_type',
        help='Board type to list features for'
    )
    
    parser.add_argument(
        '--config',
        default='config.yml',
        help='Configuration file path'
    )
    
    args = parser.parse_args()
    
    try:
        runner = TestHandler(
            board_type=args.board_type,
            config_file=args.config
        )
        runner.list_features()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def validate_config_main():
    """CLI entry point for validating configuration"""
    parser = argparse.ArgumentParser(
        description='Validate RZ-CI configuration file'
    )
    
    parser.add_argument(
        '--config',
        default='config.yml',
        help='Configuration file path to validate'
    )
    
    args = parser.parse_args()
    
    try:
        config_data = load_yaml(args.config)
        
        if not config_data:
            print("❌ Configuration file is empty or invalid")
            sys.exit(1)
        
        # Validate structure
        required_keys = ['board_configs']
        missing_keys = [key for key in required_keys if key not in config_data]
        
        if missing_keys:
            print(f"❌ Missing required keys: {missing_keys}")
            sys.exit(1)
        
        # Validate board configs
        board_configs = config_data.get('board_configs', {})
        if not board_configs:
            print("❌ No board configurations found")
            sys.exit(1)
        
        print("✅ Configuration file is valid")
        print(f"📊 Found {len(board_configs)} board configurations:")
        
        for board_name, board_config in board_configs.items():
            enabled = board_config.get('enabled', False)
            status = "✅ Enabled" if enabled else "⚠️  Disabled"
            images = board_config.get('images', {})
            image_count = len(images)
            print(f"  - {board_name}: {status} ({image_count} images)")
        
    except Exception as e:
        print(f"❌ Error validating configuration: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

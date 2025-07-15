#!/usr/bin/env python3
"""
Comprehensive test script for mylogger functionality.
Tests various logging scenarios, configurations, and edge cases.

COPY TO PARENT FOLDER (MAIN PROJECT FOLDER)
"""

import logging
import sys
import os
import traceback
from datetime import datetime
from mylogger.mylogger import MyLogger


def test_basic_logging():
    """Test basic logging functionality."""
    print("=== Testing Basic Logging ===")
    
    # Create log directory
    os.makedirs("log", exist_ok=True)
    
    # Setup logger with default configuration
    logger = logging.getLogger("test_basic")
    logger.handlers.clear()  # Clear any existing handlers
    logger.propagate = False
    
    MyLogger.setup_logger(logger, "log/test_basic.log", logging.DEBUG)
    
    # Test direct logging
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    print("✓ Basic logging test completed")


def test_stdout_stderr_redirection():
    """Test stdout and stderr redirection."""
    print("=== Testing Stdout/Stderr Redirection ===")
    
    # Setup logger
    logger = logging.getLogger("test_redirect")
    logger.handlers.clear()
    logger.propagate = False
    
    MyLogger.setup_logger(logger, "log/test_redirect.log", logging.INFO)
    
    # Store original stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        # Redirect stdout and stderr
        sys.stdout = MyLogger(logger, logging.INFO)
        sys.stderr = MyLogger(logger, logging.ERROR)
        
        # Test print statements
        print("This goes to stdout -> INFO level")
        print("Multiple", "arguments", "in", "print")
        
        # Test stderr
        print("This goes to stderr -> ERROR level", file=sys.stderr)
        
        # Test empty lines (should be filtered)
        print("")
        print("   ")
        print("\n")
        print("Non-empty line after empty lines")
        
        # Test exception handling
        try:
            raise ValueError("Test exception")
        except ValueError:
            print("Caught exception:", traceback.format_exc(), file=sys.stderr)
    
    finally:
        # Restore original stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
    
    print("✓ Stdout/stderr redirection test completed")


def test_custom_handler_config():
    """Test custom handler configurations."""
    print("=== Testing Custom Handler Configuration ===")
    
    # Test with custom handler dictionary
    custom_handler_config = {
        'when': 'D',  # Daily rotation
        'atTime': datetime.now().time(),
        'backupCount': 2
    }
    
    logger = logging.getLogger("test_custom")
    logger.handlers.clear()
    logger.propagate = False
    
    MyLogger.setup_logger(
        logger, 
        "log/test_custom.log", 
        logging.WARNING,
        handler=custom_handler_config
    )
    
    logger.warning("Custom handler test message")
    logger.error("Another custom handler message")
    
    print("✓ Custom handler configuration test completed")


def test_custom_formatter():
    """Test custom formatter configurations."""
    print("=== Testing Custom Formatter ===")
    
    # Test with custom formatter
    custom_formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    logger = logging.getLogger("test_formatter")
    logger.handlers.clear()
    logger.propagate = False
    
    MyLogger.setup_logger(
        logger,
        "log/test_formatter.log",
        logging.INFO,
        formatter=custom_formatter
    )
    
    logger.info("Custom formatter test message")
    logger.error("Error with custom format")
    
    print("✓ Custom formatter test completed")


def test_multiple_loggers():
    """Test multiple logger instances."""
    print("=== Testing Multiple Loggers ===")
    
    # Create multiple loggers
    logger1 = logging.getLogger("app.module1")
    logger2 = logging.getLogger("app.module2")
    
    for logger in [logger1, logger2]:
        logger.handlers.clear()
        logger.propagate = False
    
    MyLogger.setup_logger(logger1, "log/module1.log", logging.DEBUG)
    MyLogger.setup_logger(logger2, "log/module2.log", logging.INFO)
    
    logger1.debug("Module1 debug message")
    logger1.info("Module1 info message")
    
    logger2.info("Module2 info message")
    logger2.warning("Module2 warning message")
    
    print("✓ Multiple loggers test completed")


def test_edge_cases():
    """Test edge cases and error conditions."""
    print("=== Testing Edge Cases ===")
    
    logger = logging.getLogger("test_edge")
    logger.handlers.clear()
    logger.propagate = False
    
    MyLogger.setup_logger(logger, "log/test_edge.log", logging.INFO)
    
    # Test with MyLogger redirection
    original_stdout = sys.stdout
    sys.stdout = MyLogger(logger, logging.INFO)
    
    try:
        # Test various edge cases
        print("Normal message")
        print("")  # Empty string
        print("   ")  # Only whitespace
        print("\n")  # Only newline
        print("Message with\nnewline")
        print("Message with\ttab")
        print("Very " * 100 + "long message")  # Long message
        
        # Test unicode
        print("Unicode: 🐍 Python logging test")
        
    finally:
        sys.stdout = original_stdout
    
    print("✓ Edge cases test completed")


def verify_log_files():
    """Verify that log files were created and contain expected content."""
    print("=== Verifying Log Files ===")
    
    log_files = [
        "log/test_basic.log",
        "log/test_redirect.log", 
        "log/test_custom.log",
        "log/test_formatter.log",
        "log/module1.log",
        "log/module2.log",
        "log/test_edge.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                line_count = len(content.strip().split('\n')) if content.strip() else 0
                print(f"✓ {log_file}: {line_count} lines")
        else:
            print(f"✗ {log_file}: File not found")


def cleanup_test_files():
    """Clean up test log files."""
    print("=== Cleaning Up Test Files ===")
    
    if os.path.exists("log"):
        for file in os.listdir("log"):
            if file.startswith("test_") or file.startswith("module"):
                file_path = os.path.join("log", file)
                try:
                    os.remove(file_path)
                    print(f"✓ Removed {file_path}")
                except OSError as e:
                    print(f"✗ Failed to remove {file_path}: {e}")


def main():
    """Run all tests."""
    print("MyLogger Test Suite")
    print("=" * 50)
    
    try:
        test_basic_logging()
        test_stdout_stderr_redirection()
        test_custom_handler_config()
        test_custom_formatter()
        test_multiple_loggers()
        test_edge_cases()
        
        print("\n" + "=" * 50)
        verify_log_files()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print(f'Current directory: {os.getcwd()}')
        print(f'log ls: {os.listdir("log")}')
        # Ask user if they want to clean up
        cleanup_response = input("\nClean up test log files? (y/N): ")
        if cleanup_response.lower() == 'y':
            cleanup_test_files()
        else:
            print("Test log files preserved in log/ directory")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
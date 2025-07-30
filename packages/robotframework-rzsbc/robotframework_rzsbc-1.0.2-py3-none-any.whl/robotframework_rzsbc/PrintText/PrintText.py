#!/usr/bin/env python3
"""
PrintText Library for Robot Framework testing with RZSBC boards
"""

from robot.api.deco import keyword, library
from robot.api import logger

@library(scope='GLOBAL', version='1.0.2')
class PrintText:
    """Robot Framework library for basic text operations and testing on RZSBC boards."""

    def __init__(self):
        """Initialize the PrintText library."""
        logger.info("PrintText Library: Initialized for RZSBC testing")

    @keyword("Echo Hello World")
    def echo_hello_world(self):
        """
        Returns a simple 'Hello World' string.
        
        Returns:
            str: "Hello World"
            
        Example:
            | ${result}= | Echo Hello World |
            | Should Be Equal | ${result} | Hello World |
        """
        result = "Hello World"
        logger.info(f"Echo Hello World called, returning: {result}")
        return result

    @keyword("Print Text")
    def print_text(self, message):
        """
        Returns the provided message text.
        
        Args:
            message (str): The text message to return
            
        Returns:
            str: The same message that was provided
            
        Example:
            | ${result}= | Print Text | Testing custom message |
            | Should Be Equal | ${result} | Testing custom message |
        """
        logger.info(f"Print Text called with message: {message}")
        return str(message)

    @keyword("Get Current Time")
    def get_current_time(self):
        """
        Returns the current timestamp.
        
        Returns:
            str: Current time in ISO format
            
        Example:
            | ${current_time}= | Get Current Time |
            | Should Not Be Empty | ${current_time} |
        """
        from datetime import datetime
        current_time = datetime.now().isoformat()
        logger.info(f"Current time: {current_time}")
        return current_time

    @keyword("Add Numbers")
    def add_numbers(self, num1, num2):
        """
        Adds two numbers together.
        
        Args:
            num1: First number
            num2: Second number
            
        Returns:
            int/float: Sum of the two numbers
            
        Example:
            | ${sum}= | Add Numbers | 5 | 3 |
            | Should Be Equal As Numbers | ${sum} | 8 |
        """
        try:
            result = float(num1) + float(num2)
            # Return as int if it's a whole number
            if result.is_integer():
                result = int(result)
            logger.info(f"Adding {num1} + {num2} = {result}")
            return result
        except (ValueError, TypeError) as e:
            logger.error(f"Error adding numbers: {e}")
            raise ValueError(f"Cannot add {num1} and {num2}: {e}")

    @keyword("Multiply Text")
    def multiply_text(self, text, count):
        """
        Repeats text a specified number of times.
        
        Args:
            text (str): Text to repeat
            count (int): Number of times to repeat
            
        Returns:
            str: Repeated text
            
        Example:
            | ${repeated}= | Multiply Text | Hello | 3 |
            | Should Be Equal | ${repeated} | HelloHelloHello |
        """
        try:
            count = int(count)
            result = str(text) * count
            logger.info(f"Multiplying '{text}' by {count} = '{result}'")
            return result
        except (ValueError, TypeError) as e:
            logger.error(f"Error multiplying text: {e}")
            raise ValueError(f"Cannot multiply '{text}' by '{count}': {e}")

    @keyword("Format Message")
    def format_message(self, template, *args):
        """
        Format a message template with arguments.
        
        Args:
            template (str): Message template with {} placeholders
            *args: Arguments to format into template
            
        Returns:
            str: Formatted message
            
        Example:
            | ${message}= | Format Message | Hello {} from {} | World | RZSBC |
            | Should Be Equal | ${message} | Hello World from RZSBC |
        """
        try:
            result = template.format(*args)
            logger.info(f"Formatted message: {result}")
            return result
        except Exception as e:
            logger.error(f"Error formatting message: {e}")
            raise ValueError(f"Cannot format message '{template}' with args {args}: {e}")

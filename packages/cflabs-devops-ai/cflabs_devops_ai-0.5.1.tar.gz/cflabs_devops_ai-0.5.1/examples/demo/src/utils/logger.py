import logging
import time
import functools
from typing import Callable, Any
import os

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with proper configuration."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(name)s.%(funcName)s:%(lineno)d - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set log level from environment variable or default to INFO
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Prevent duplicate logs
        logger.propagate = False
    
    return logger

def time_function(func: Callable) -> Callable:
    """
    Decorator to time function execution and log the duration.
    
    Args:
        func: The function to be timed
        
    Returns:
        Wrapped function with timing functionality
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger(func.__module__)
        
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in {func.__name__} after {execution_time:.4f} seconds: {str(e)}")
            raise
    
    return wrapper

def log_function_call(func: Callable) -> Callable:
    """
    Decorator to log function calls with parameters.
    
    Args:
        func: The function to be logged
        
    Returns:
        Wrapped function with logging functionality
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger(func.__module__)
        
        # Log function call with parameters (be careful with sensitive data)
        args_repr = [repr(arg) if not hasattr(arg, '__dict__') else f"{type(arg).__name__}()" for arg in args]
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        
        logger.debug(f"Calling {func.__name__}({signature})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Returned from {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {str(e)}")
            raise
    
    return wrapper
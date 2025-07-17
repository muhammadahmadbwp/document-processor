import logging
import traceback
import sys
import os
import json
from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)

def get_logger_info():
    """Get information about the current logging configuration."""
    root_logger = logging.getLogger()
    
    # Get all loggers
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    
    logger_info = {
        'root_logger': {
            'level': logging.getLevelName(root_logger.level),
            'handlers': [h.__class__.__name__ for h in root_logger.handlers],
            'disabled': root_logger.disabled,
        },
        'loggers': {}
    }
    
    for log in loggers:
        if log.name:  # Skip empty names
            logger_info['loggers'][log.name] = {
                'level': logging.getLevelName(log.level),
                'handlers': [h.__class__.__name__ for h in log.handlers],
                'propagate': log.propagate,
                'disabled': log.disabled,
            }
    
    return logger_info

def get_log_files():
    """Get a list of log files and their sizes."""
    log_files = {}
    
    # Check common log directories
    log_dirs = []
    
    # Add Django's log directory if configured
    if hasattr(settings, 'LOGGING') and 'handlers' in settings.LOGGING:
        for handler in settings.LOGGING['handlers'].values():
            if 'filename' in handler:
                log_file = Path(handler['filename'])
                log_dirs.append(log_file.parent)
    
    # Add Celery log directory if configured
    if hasattr(settings, 'CELERY_LOG_DIR'):
        log_dirs.append(settings.CELERY_LOG_DIR)
    
    # Add current directory and logs subdirectory
    log_dirs.extend([Path('.'), Path('./logs')])
    
    # Deduplicate
    log_dirs = list(set(log_dirs))
    
    for log_dir in log_dirs:
        if log_dir.exists():
            for file in log_dir.glob('*.log'):
                try:
                    log_files[str(file)] = {
                        'size': file.stat().st_size,
                        'size_human': f"{file.stat().st_size / 1024:.2f} KB",
                        'modified': file.stat().st_mtime,
                    }
                except Exception as e:
                    log_files[str(file)] = {'error': str(e)}
    
    return log_files

def test_all_log_levels():
    """Test logging at all levels."""
    results = {}
    
    # Test each log level
    logger.debug("This is a DEBUG test message from diagnostics")
    results['debug'] = "Message sent"
    
    logger.info("This is an INFO test message from diagnostics")
    results['info'] = "Message sent"
    
    logger.warning("This is a WARNING test message from diagnostics")
    results['warning'] = "Message sent"
    
    logger.error("This is an ERROR test message from diagnostics")
    results['error'] = "Message sent"
    
    try:
        raise ValueError("This is a test exception for logging")
    except Exception as e:
        logger.exception("This is an EXCEPTION test message from diagnostics")
        results['exception'] = "Message sent with traceback"
    
    logger.critical("This is a CRITICAL test message from diagnostics")
    results['critical'] = "Message sent"
    
    return results

def test_celery_logging():
    """Test Celery task logging."""
    from .celery_tests import test_success_task
    
    # Submit a task that will log messages
    task = test_success_task.delay(1)
    
    return {
        'task_id': task.id,
        'status': 'submitted',
        'message': 'Check Celery logs for messages from this task'
    }

def get_recent_log_entries(log_file_path, num_lines=50):
    """Get the most recent entries from a log file."""
    try:
        with open(log_file_path, 'r') as f:
            # Read the last num_lines lines
            lines = f.readlines()[-num_lines:]
            return ''.join(lines)
    except Exception as e:
        return f"Error reading log file: {str(e)}"

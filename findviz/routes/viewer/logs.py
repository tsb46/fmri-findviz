"""
Log retrieval routes
"""
import os
import re
import glob
from datetime import datetime, timedelta
from typing import List, Dict

from flask import Blueprint, request, jsonify

from findviz.logger_config import setup_logger
from findviz.routes.utils import handle_route_errors, Routes

# Set up a logger for the app
logger = setup_logger(__name__)

logs_bp = Blueprint('logs', __name__)

@logs_bp.route(Routes.GET_LOG_ENTRIES.value, methods=['GET'])
@handle_route_errors(
    error_msg='Error retrieving log entries',
    log_msg='Log entries request successful',
    route=Routes.GET_LOG_ENTRIES
)
def get_log_entries():
    """Get recent log entries"""
    # Get parameters with defaults
    max_entries = int(request.args.get('max_entries', 100))
    since_minutes = int(request.args.get('since_minutes', 15))
    log_file = request.args.get('log_file', None)  # Allow specifying which log file
    
    # Limit max_entries to a reasonable value to prevent performance issues
    max_entries = min(max_entries, 1000)
    
    # If no log file specified, find the most recent one
    if log_file is None:
        log_file = find_most_recent_log_file()
    
    # Get log entries
    log_entries = get_recent_log_entries(
        max_entries=max_entries,
        since_minutes=since_minutes,
        log_file_path=os.path.join('logs', log_file)
    )
    
    return jsonify(log_entries)

@logs_bp.route(Routes.GET_LOG_FILES.value, methods=['GET'])
@handle_route_errors(
    error_msg='Error retrieving log files',
    log_msg='Log files request successful',
    route=Routes.GET_LOG_FILES
)
def get_log_files():
    """Get available log files"""
    log_dir = os.path.join(os.getcwd(), 'logs')
    
    if not os.path.exists(log_dir):
        return jsonify([])
    
    # Get all log files and their modification times
    log_files = []
    
    # Get all run-specific log files (app-run-*.log)
    run_log_files = glob.glob(os.path.join(log_dir, 'app-run-*.log'))
    
    for file_path in run_log_files:
        file_name = os.path.basename(file_path)
        mod_time = os.path.getmtime(file_path)
        size = os.path.getsize(file_path)
        
        # Extract timestamp from filename
        timestamp_match = re.search(r'app-run-(\d{8}-\d{6})\.log', file_name)
        timestamp_str = None
        if timestamp_match:
            # Convert YYYYMMDD-HHMMSS to a readable format
            ts = timestamp_match.group(1)
            try:
                dt = datetime.strptime(ts, "%Y%m%d-%H%M%S")
                timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                timestamp_str = None
        
        log_files.append({
            'name': file_name,
            'modified': datetime.fromtimestamp(mod_time).isoformat(),
            'size': size,
            'timestamp': timestamp_str or "Unknown"
        })
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: x['modified'], reverse=True)
    
    return jsonify(log_files)


def find_most_recent_log_file() -> str:
    """
    Find the most recent run log file in the logs directory.
    
    Returns
    -------
    str
        The name of the most recent log file, or None if none found
    """
    log_dir = os.path.join(os.getcwd(), 'logs')
    
    if not os.path.exists(log_dir):
        logger.warning(f"Log directory not found: {log_dir}")
        return None
    
    # Look for all run-specific log files
    run_log_files = glob.glob(os.path.join(log_dir, 'app-run-*.log'))
    
    if not run_log_files:
        logger.warning("No run log files found")
        return None
    
    # Find the most recently modified file
    most_recent = max(run_log_files, key=os.path.getmtime)
    return os.path.basename(most_recent)


def get_recent_log_entries(
    max_entries: int = 100, 
    since_minutes: int = 15, 
    log_file_path: str = None
) -> List[Dict]:
    """
    Retrieve recent log entries from the log file.
    
    Parameters
    ----------
    max_entries : int
        Maximum number of log entries to return
    since_minutes : int
        Only return entries from the last N minutes
    log_file_path : str
        Path to the log file
    
    Returns
    -------
    List[Dict]
        List of log entries with timestamp, level, source, and message
    """
    entries = []
    
    # Check if log file exists
    if log_file_path is None or not os.path.exists(log_file_path):
        return [{"timestamp": datetime.now().isoformat(), 
                "level": "WARNING", 
                "source": "log_utils", 
                "message": f"Log file not found: {log_file_path}"}]
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(minutes=since_minutes)
    
    try:
        with open(log_file_path, 'r') as log_file:
            # Read the file from the end, which is more efficient for large logs
            lines = log_file.readlines()
            
            # Process the most recent lines first (reversed)
            for line in reversed(lines):
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Parse log entry with regex
                # Format: 2023-05-21 14:30:45,123 - module_name - LEVEL - Message
                match = re.match(
                    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - ([\w\._]+) - (\w+) - (.*)', 
                    line
                )

                if match:
                    timestamp_str, source, level, message = match.groups()
                    
                    try:
                        # Parse timestamp - handle milliseconds correctly
                        timestamp_str = timestamp_str.replace(',', '.')
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                        
                        # For run-specific logs, we might want to show all entries
                        # regardless of time, since each run is a discrete session
                        # But we'll keep the time filter as an option
                        if since_minutes > 0 and timestamp < cutoff_time:
                            continue
                        
                        entries.append({
                            "timestamp": timestamp.isoformat(),
                            "level": level,
                            "source": source,
                            "message": message.strip()
                        })
                        
                        # Stop if we have enough entries
                        if len(entries) >= max_entries:
                            break
                    except ValueError as e:
                        # Log the error but continue processing
                        logger.warning(f"Error parsing timestamp '{timestamp_str}': {e}")
                        continue
                else:
                    # For multiline log entries, append to the last entry's message
                    if entries:
                        entries[0]["message"] += "\n" + line.strip()
        
        # Return entries in chronological order (oldest first)
        return list(reversed(entries))
    
    except Exception as e:
        return [{"timestamp": datetime.now().isoformat(), 
                "level": "ERROR", 
                "source": "log_utils", 
                "message": f"Error reading log file: {str(e)}"}]
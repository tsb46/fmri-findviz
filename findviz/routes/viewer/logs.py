"""
Log retrieval routes
"""
import os
import re

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
    
    # Limit max_entries to a reasonable value to prevent performance issues
    max_entries = min(max_entries, 1000)
    
    # Get log entries
    log_entries = get_recent_log_entries(
        max_entries=max_entries,
        since_minutes=since_minutes
    )
    
    return jsonify(log_entries)


def get_recent_log_entries(
    max_entries: int = 100, 
    since_minutes: int = 15, 
    log_file_path: str = 'app.log'
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
    if not os.path.exists(log_file_path):
        return [{"timestamp": datetime.now().isoformat(), 
                "level": "ERROR", 
                "source": "log_utils", 
                "message": f"Log file not found: {log_file_path}"}]
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(minutes=since_minutes)
    
    try:
        with open(log_file_path, 'r') as log_file:
            # Read the file from the end, which is more efficient for large logs
            # This is a simple approach - for very large logs, consider more sophisticated solutions
            lines = log_file.readlines()
            
            # Process the most recent lines first (reversed)
            for line in reversed(lines):
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Parse log entry with regex
                # Format: 2023-05-21 14:30:45,123 - module_name - LEVEL - Message
                match = re.match(
                    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - ([\w\.]+) - (\w+) - (.*)', 
                    line
                )
                
                if match:
                    timestamp_str, source, level, message = match.groups()
                    
                    try:
                        # Parse timestamp
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        
                        # Skip entries older than cutoff time
                        if timestamp < cutoff_time:
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
                    except ValueError:
                        # Skip entries with invalid timestamp format
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
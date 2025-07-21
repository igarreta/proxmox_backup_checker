"""Configuration and environment variable management."""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment(env_path="~/etc/grsrv03.env"):
    """
    Load environment variables from the specified file.
    
    Args:
        env_path (str): Path to the .env file. Defaults to ~/etc/grsrv03.env
        
    Returns:
        bool: True if the file was loaded successfully, False otherwise
    """
    # Expand the ~ to the user's home directory
    env_path = os.path.expanduser(env_path)
    
    # Check if the file exists
    if not os.path.isfile(env_path):
        print(f"Warning: Environment file not found at {env_path}")
        return False
    
    # Load the environment variables
    load_dotenv(env_path, override=True)
    print(f"Loaded environment variables from {env_path}")
    return True

# Load environment variables when this module is imported
load_environment()

"""Configuration management for Grasp SDK Python implementation.

This module provides configuration loading from environment variables
and default configuration constants.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from ..models import ISandboxConfig, IBrowserConfig

# Load environment variables from .env.grasp file
load_dotenv('.env.grasp')


def get_config() -> Dict[str, Any]:
    """Gets application configuration from environment variables.
    
    Returns:
        Dict[str, Any]: Application configuration object containing
                       sandbox and logger configurations.
    """
    return {
        'sandbox': {
            'key': os.getenv('GRASP_KEY', ''),
            'templateId': 'playwright-pnpm-template',
            'timeout': int(os.getenv('GRASP_SERVICE_TIMEOUT', '900000')),
            'debug': os.getenv('GRASP_DEBUG', 'false').lower() == 'true',
        },
        'logger': {
            'level': os.getenv('GRASP_LOG_LEVEL', 'info'),
            'console': True,
            'file': os.getenv('GRASP_LOG_FILE'),
        },
    }


def get_sandbox_config() -> ISandboxConfig:
    """Gets sandbox-specific configuration.
    
    Returns:
        ISandboxConfig: Sandbox configuration object.
    """
    config = get_config()
    sandbox_config = ISandboxConfig(
        key=config['sandbox']['key'],
        templateId=config['sandbox']['templateId'],
        timeout=config['sandbox']['timeout'],
        debug=config['sandbox'].get('debug', False),
    )
    
    # Only add workspace if it exists
    workspace = os.getenv('GRASP_WORKSPACE')
    if workspace:
        sandbox_config['workspace'] = workspace
    
    return sandbox_config


def get_browser_config() -> IBrowserConfig:
    """Gets browser-specific configuration.
    
    Returns:
        IBrowserConfig: Browser configuration object.
    """
    return IBrowserConfig(
        cdpPort=int(os.getenv('GRASP_CDP_PORT', '9222')),
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--remote-debugging-port=9222',
            '--remote-debugging-address=0.0.0.0',
        ],
        headless=os.getenv('GRASP_HEADLESS', 'true').lower() == 'true',
        launchTimeout=int(os.getenv('GRASP_LAUNCH_TIMEOUT', '30000')),
        envs={
            'PLAYWRIGHT_BROWSERS_PATH': '0',
            'DISPLAY': ':99',
        },
    )


# Default configuration constants
DEFAULT_CONFIG = {
    'PLAYWRIGHT_BROWSERS_PATH': '0',
    'WORKING_DIRECTORY': '/home/user',
    'SCREENSHOT_PATH': '/home/user',
    'DEFAULT_VIEWPORT': {
        'width': 1280,
        'height': 720,
    },
}


# Environment variable names for easy reference
ENV_VARS = {
    'GRASP_KEY': 'GRASP_KEY',
    'GRASP_WORKSPACE': 'GRASP_WORKSPACE',
    'GRASP_SERVICE_TIMEOUT': 'GRASP_SERVICE_TIMEOUT',
    'GRASP_DEBUG': 'GRASP_DEBUG',
    'GRASP_LOG_LEVEL': 'GRASP_LOG_LEVEL',
    'GRASP_LOG_FILE': 'GRASP_LOG_FILE',
    'GRASP_CDP_PORT': 'GRASP_CDP_PORT',
    'GRASP_HEADLESS': 'GRASP_HEADLESS',
    'GRASP_LAUNCH_TIMEOUT': 'GRASP_LAUNCH_TIMEOUT',
}


def validate_config() -> bool:
    """Validates that required configuration is present.
    
    Returns:
        bool: True if configuration is valid, False otherwise.
    """
    config = get_config()
    
    # Check required fields
    if not config['sandbox']['key']:
        return False
        
    # Validate timeout values
    if config['sandbox']['timeout'] <= 0:
        return False
        
    return True


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """Gets an environment variable with optional default.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        str or None: Environment variable value or default
    """
    return os.getenv(key, default)


def set_env_var(key: str, value: str) -> None:
    """Sets an environment variable.
    
    Args:
        key: Environment variable name
        value: Environment variable value
    """
    os.environ[key] = value
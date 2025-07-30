"""Grasp E2B Python SDK

A Python SDK for E2B platform providing secure command execution 
and browser automation in isolated cloud environments.
"""

import asyncio
import signal
import sys
from typing import Dict, Optional, Any, Literal

# Import utilities
from .utils.logger import init_logger, get_logger
from .utils.config import get_config
from .services.browser import BrowserService
from .services.sandbox import SandboxService

# Import models and types
from .models import (
    ISandboxConfig,
    IBrowserConfig,
    ICommandOptions,
    IScriptOptions,
    SandboxStatus,
)

__version__ = "0.1.6"
__author__ = "Grasp Team"
__email__ = "team@grasp.dev"


class GraspServer:
    """Main Grasp E2B class for browser automation."""
    
    def __init__(self, sandbox_config: Optional[Dict[str, Any]] = None):
        """Initialize GraspServer with configuration.
        
        Args:
            sandbox_config: Optional sandbox configuration overrides
        """
        if sandbox_config is None:
            sandbox_config = {}
        
        # Extract browser-specific options
        browser_type = sandbox_config.pop('type', 'chromium')
        headless = sandbox_config.pop('headless', True)
        adblock = sandbox_config.pop('adblock', False)
        logLevel = sandbox_config.pop('logLevel', '')
        keepAliveMS = sandbox_config.pop('keepAliveMS', 0)

        # Set default log level
        if not logLevel:
            logLevel = 'debug' if sandbox_config.get('debug', False) else 'info'

        self.__browser_type = browser_type
        
        # Create browser task
        self.__browser_config = {
            'headless': headless,
            'envs': {
                'ADBLOCK': 'true' if adblock else 'false',
                'KEEP_ALIVE_MS': str(keepAliveMS),
            }
        }
            
        config = get_config()
        config['sandbox'].update(sandbox_config)
        self.config = config

        logger = config['logger']
        logger['level'] = logLevel
        
        # Initialize logger first
        init_logger(logger)
        self.logger = get_logger().child('GraspE2B')
        
        self.browser_service: Optional[BrowserService] = None
        
        self.logger.info(
            f'GraspE2B initialized (templateId: {config["sandbox"]["templateId"]})'
        )
    
    async def __aenter__(self):
        connection = await self.create_browser_task()
    
        # Register server
        # if connection['id']:
        #    _servers[connection['id']] = self
            
        return connection
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.browser_service and self.browser_service.id:
            service_id = self.browser_service.id
            self.logger.info(f'Closing browser service {service_id}')
            await _servers[service_id].cleanup()
            del _servers[service_id]
    
    @property
    def sandbox(self) -> Optional[SandboxService]:
        """Get the underlying sandbox service.
        
        Returns:
            SandboxService instance or None
        """
        return self.browser_service.get_sandbox() if self.browser_service else None
    
    def get_status(self) -> Optional[SandboxStatus]:
        """Get current sandbox status.
        
        Returns:
            Sandbox status or None
        """
        return self.sandbox.get_status() if self.sandbox else None
    
    def get_sandbox_id(self) -> Optional[str]:
        """Get sandbox ID.
        
        Returns:
            Sandbox ID or None
        """
        return self.sandbox.get_sandbox_id() if self.sandbox else None
    
    async def create_browser_task(
        self, 
    ) -> Dict[str, Any]:
        """Create and launch a browser task.
        
        Args:
            browser_type: Type of browser to launch
            config: Browser configuration overrides
            
        Returns:
            Dictionary containing browser connection info
            
        Raises:
            RuntimeError: If browser service is already initialized
        """
        if self.browser_service:
            raise RuntimeError('Browser service can only be initialized once')
        
        config = self.__browser_config
        browser_type = self.__browser_type

        if config is None:
            config = {}
            
        # Create base browser config
        browser_config: IBrowserConfig = {
            'cdpPort': 9222,
            'headless': True,
            'launchTimeout': 30000,
            'args': [
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ],
            'envs': {},
        }
        
        # Apply user config overrides with type safety
        if 'cdpPort' in config:
            browser_config['cdpPort'] = config['cdpPort']
        if 'headless' in config:
            browser_config['headless'] = config['headless']
        if 'launchTimeout' in config:
            browser_config['launchTimeout'] = config['launchTimeout']
        if 'args' in config:
            browser_config['args'] = config['args']
        if 'envs' in config:
            browser_config['envs'] = config['envs']
        
        self.browser_service = BrowserService(
            self.config['sandbox'],
            browser_config
        )
        await self.browser_service.initialize()

        # Register server
        _servers[str(self.browser_service.id)] = self
        self.logger.info("🚀 Browser service initialized", {
            'id': self.browser_service.id,
        })
        
        self.logger.info('🌐 Launching Chromium browser with CDP...')
        cdp_connection = await self.browser_service.launch_browser(browser_type)
        
        self.logger.info('✅ Browser launched successfully!')
        self.logger.debug(
            f'CDP Connection Info (wsUrl: {cdp_connection.ws_url}, httpUrl: {cdp_connection.http_url})'
        )
        
        return {
            'id': self.browser_service.id,
            'ws_url': cdp_connection.ws_url,
            'http_url': cdp_connection.http_url
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources.
        
        Returns:
            Promise that resolves when cleanup is complete
        """
        self.logger.info('Starting cleanup process')
        
        try:
            # Cleanup browser service
            if self.browser_service:
                await self.browser_service.cleanup()
                
            self.logger.info('Cleanup completed successfully')
        except Exception as error:
            self.logger.error(f'Cleanup failed: {error}')
            raise


# Global server registry
_servers: Dict[str, GraspServer] = {}


async def launch_browser(
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Launch a browser instance.
    
    Args:
        options: Launch options including type, headless, adblock settings
        
    Returns:
        Dictionary containing connection information
    """    
    # Create server instance
    server = GraspServer(options)
    
    connection = await server.create_browser_task()
    
    # Register server
    if connection['id']:
        _servers[connection['id']] = server
        
    return connection


async def _graceful_shutdown(signal_name: str) -> None:
    """Handle graceful shutdown.
    
    Args:
        signal_name: Name of the signal received
    """
    print(f'Received {signal_name}, starting cleanup...')
    
    # Cleanup all GraspServer instances
    for server_id in list(_servers.keys()):
        await _servers[server_id].cleanup()
        del _servers[server_id]
    
    print('All servers cleaned up, exiting...')
    sys.exit(0)


def _setup_signal_handlers() -> None:
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        signal_name = signal.Signals(signum).name
        asyncio.create_task(_graceful_shutdown(signal_name))
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal


# Setup signal handlers on import
_setup_signal_handlers()


# Export all public APIs
__all__ = [
    'GraspServer',
    'launch_browser',
    'ISandboxConfig',
    'IBrowserConfig',
    'ICommandOptions', 
    'IScriptOptions',
    'SandboxStatus',
    'get_config',
    'init_logger',
    'get_logger',
    'BrowserService',
    'SandboxService',
]


# Default export equivalent
default = {
    'GraspServer': GraspServer,
}
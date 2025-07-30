"""Browser service for managing Chromium browser with CDP access.

This module provides the BrowserService class that manages Chromium browser
instances using the Grasp sandbox environment and exposes CDP endpoints.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any, Union

import aiohttp
from ..utils.logger import get_logger
from .sandbox import SandboxService, CommandEventEmitter
from ..models import IBrowserConfig, ISandboxConfig, ICommandOptions


class CDPConnection:
    """CDP connection information."""
    
    def __init__(
        self,
        ws_url: str,
        http_url: str,
        port: int,
        pid: Optional[int] = None
    ):
        self.ws_url = ws_url
        self.http_url = http_url
        self.port = port
        self.pid = pid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'wsUrl': self.ws_url,
            'httpUrl': self.http_url,
            'port': self.port,
            'pid': self.pid
        }


class BrowserService:
    """Browser service for managing Chromium browser with CDP access.
    
    Uses Grasp sandbox to run browser and expose CDP endpoint.
    """
    
    def __init__(
        self,
        sandbox_config: ISandboxConfig,
        browser_config: Optional[IBrowserConfig] = None
    ):
        """Initialize BrowserService.
        
        Args:
            sandbox_config: Sandbox configuration
            browser_config: Browser configuration (optional)
        """
        self.sandbox_service = SandboxService(sandbox_config)
        
        # Set default browser config
        default_config: IBrowserConfig = {
            'cdpPort': 9222,
            'headless': True,
            'launchTimeout': 30000,
            'args': [],
            'envs': {}
        }
        
        if browser_config:
            default_config.update(browser_config)
        
        self.config = default_config
        self.logger = self._get_default_logger()
        self.cdp_connection: Optional[CDPConnection] = None
        self.browser_process: Optional[CommandEventEmitter] = None
        self._health_check_task: Optional[asyncio.Task] = None
    
    def _get_default_logger(self):
        """Gets or creates a default logger instance."""
        try:
            return get_logger().child('BrowserService')
        except Exception:
            # If logger is not initialized, create a default one
            from ..utils.logger import Logger
            default_logger = Logger({
                'level': 'debug' if self.config.get('debug', False) else 'info',
                'console': True,
            })
            return default_logger.child('BrowserService')

    async def initialize(self) -> None:
        """Initialize the Grasp sandbox.
        
        Returns:
            Promise that resolves when sandbox is ready
        """
        self.logger.info('Initializing Browser service')
        await self.sandbox_service.create_sandbox()
        self.logger.info('Grasp sandbox initialized successfully')
    
    async def launch_browser(
        self,
        browser_type: str = 'chromium'
    ) -> CDPConnection:
        """Launch Chromium browser with CDP server.
        
        Args:
            browser_type: Browser type ('chromium' or 'chrome-stable')
            
        Returns:
            CDP connection information
            
        Raises:
            RuntimeError: If browser launch fails
        """
        if not self.sandbox_service:
            raise RuntimeError('Grasp service not initialized. Call initialize() first.')
        
        try:
            self.logger.info(
                f'Launching Chromium browser with CDP (port: {self.config["cdpPort"]}, headless: {self.config["headless"]})'
            )
            
            # Check if adblock is enabled and adjust browser type
            if (
                self.config['envs'].get('ADBLOCK') == 'true' and 
                browser_type == 'chromium'
            ):
                self.logger.warn(
                    '⚠️ Adblock is enabled. Should use chrome-stable instead.'
                )
                browser_type = 'chrome-stable'
            
            # Read the Playwright script
            script_path = Path(__file__).parent.parent / 'sandbox' / f'{browser_type}.mjs'
            
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    playwright_script = f.read()
            except FileNotFoundError:
                raise RuntimeError(f'Browser script not found: {script_path}')
            
            # Prepare environment variables
            envs = {
                'CDP_PORT': str(self.config['cdpPort']),
                'BROWSER_ARGS': json.dumps(self.config['args']),
                'LAUNCH_TIMEOUT': str(self.config['launchTimeout']),
                'SANDBOX_TIMEOUT': str(self.sandbox_service.timeout),
                'HEADLESS': str(self.config['headless']).lower(),
                'NODE_ENV': 'production',
                'SANDBOX_ID': self.sandbox_service.id,
                'WORKSPACE': self.sandbox_service.workspace,
                'BS_SOURCE_TOKEN': 'Qth8JGboEKVersqr1PSsUFMW',
                'BS_INGESTING_HOST': 's1363065.eu-nbg-2.betterstackdata.com',
                'SENTRY_DSN': 'https://21fa729ceb72d7f0adef06b4f786c067@o4509574910509056.ingest.us.sentry.io/4509574913720320',
                **self.config['envs']
            }
            
            # Prepare script options
            from ..models import IScriptOptions
            script_options: IScriptOptions = {
                'type': 'esm',
                'background': True,
                'nohup': not self.sandbox_service.is_debug,
                'timeoutMs': 0,
                'envs': envs,
                'preCommand': '' if self.config['headless'] else 'xvfb-run -a -s "-screen 0 1280x1024x24" '
            }
            
            # Run the Playwright script in background
            self.browser_process = await self.sandbox_service.run_script(
                playwright_script,
                script_options
            )
            
            # Set up event listeners for browser process
            self._setup_browser_process_listeners()
            
            # Wait for browser to start and CDP to be available
            result = await self._wait_for_cdp_ready()
            
            # Create CDP connection info
            self.cdp_connection = result
            
            self.logger.info(
                f'Chromium browser launched successfully (cdpPort: {self.config["cdpPort"]}, wsUrl: {self.cdp_connection.ws_url})'
            )
            
            # Start health check if not in debug mode
            if not self.sandbox_service.is_debug:
                self._health_check_task = asyncio.create_task(
                    self._start_health_check()
                )
            
            return self.cdp_connection
            
        except Exception as error:
            self.logger.error(f'Failed to launch Chromium browser: {str(error)}')
            raise RuntimeError(f'Failed to launch browser: {str(error)}') from error
    
    def _setup_browser_process_listeners(self) -> None:
        """Set up event listeners for browser process."""
        if not self.browser_process:
            return
        
        def on_stdout(data: str) -> None:
            self.logger.info(f'Browser stdout: {data}')
        
        def on_stderr(data: str) -> None:
            self.logger.info(f'Browser stderr: {data}')
        
        def on_exit(exit_code: int) -> None:
            self.logger.info(f'Browser process exited (exitCode: {exit_code})')
            self.cdp_connection = None
            self.browser_process = None
            asyncio.create_task(self.sandbox_service.destroy())
        
        def on_error(error: Exception) -> None:
            self.logger.error(f'Browser process error: {error}')
        
        # Only set up listeners if browser_process has the 'on' method
        if hasattr(self.browser_process, 'on'):
            self.browser_process.on('stdout', on_stdout)
            self.browser_process.on('stderr', on_stderr)
            self.browser_process.on('exit', on_exit)
            self.browser_process.on('error', on_error)
    
    async def _wait_for_cdp_ready(self) -> CDPConnection:
        """Wait for CDP server to be ready.
        
        Returns:
            CDP connection information
            
        Raises:
            RuntimeError: If CDP server fails to become ready within timeout
        """
        delay_ms = 200
        max_attempts = self.config['launchTimeout'] // delay_ms
        
        for attempt in range(1, max_attempts + 1):
            try:
                self.logger.debug(
                    f'Checking CDP availability (attempt {attempt}/{max_attempts})'
                )
                
                # Check if CDP endpoint is responding
                options: ICommandOptions = {
                    'timeout': 0,
                    'inBackground': False
                }
                result = await self.sandbox_service.run_command(
                    f'curl -s http://localhost:{self.config["cdpPort"]}/json/version',
                    options,
                    True,
                )
                
                if (
                    getattr(result, 'exit_code', None) == 0 and 
                    'Browser' in getattr(result, 'stdout', '')
                ):
                    stdout_content = getattr(result, 'stdout', '')
                    metadata = json.loads(stdout_content)
                    host = self.sandbox_service.get_sandbox_host(
                        self.config['cdpPort'] + 1
                    )
                    
                    # Update URLs for external access
                    ws_url = metadata['webSocketDebuggerUrl'].replace(
                        'ws://', 'wss://'
                    ).replace(
                        f'localhost:{self.config["cdpPort"]}', host
                    )
                    
                    http_url = f'https://{host}'
                    
                    connection = CDPConnection(
                        ws_url=ws_url,
                        http_url=http_url,
                        port=self.config['cdpPort']
                    )
                    
                    self.logger.info(f'CDP server is ready (metadata: {metadata})')
                    return connection
                    
            except Exception as error:
                self.logger.debug(
                    f'CDP check failed (attempt {attempt}): {error}'
                )
            
            if attempt < max_attempts:
                await asyncio.sleep(delay_ms / 1000)
        
        raise RuntimeError('CDP server failed to become ready within timeout')
    
    async def _start_health_check(self) -> None:
        """Start health check for browser process."""
        while self.cdp_connection:
            try:
                await asyncio.sleep(5)
                
                if not self.cdp_connection:
                    break
                
                async with aiohttp.ClientSession() as session:
                    async with session.head(
                        f'{self.cdp_connection.http_url}/json/version'
                    ) as response:
                        if response.status != 200:
                            self.logger.info('Browser process exited')
                            await self.sandbox_service.destroy()
                            break
                            
            except Exception:
                self.logger.info('Browser process exited')
                await self.sandbox_service.destroy()
                break
    
    def get_cdp_connection(self) -> Optional[CDPConnection]:
        """Get current CDP connection information.
        
        Returns:
            CDP connection info or None if not connected
        """
        return self.cdp_connection
    
    def is_browser_running(self) -> bool:
        """Check if browser is running.
        
        Returns:
            True if browser process is active
        """
        return self.browser_process is not None and self.cdp_connection is not None
    
    async def stop_browser(self) -> None:
        """Stop the browser and cleanup resources.
        
        Returns:
            Promise that resolves when cleanup is complete
        """
        if not self.browser_process:
            self.logger.info('No browser process to stop')
            return
        
        try:
            self.logger.info('Stopping Chromium browser')
            
            # Cancel health check task
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
                self._health_check_task = None
            
            # Kill the browser process
            if hasattr(self.browser_process, 'kill'):
                await self.browser_process.kill()
            
            self.browser_process = None
            self.cdp_connection = None
            
            self.logger.info('Chromium browser stopped successfully')
            
        except Exception as error:
            self.logger.error(f'Error stopping browser: {error}')
            raise
    
    async def cleanup(self) -> None:
        """Cleanup all resources including Grasp sandbox.
        
        Returns:
            Promise that resolves when cleanup is complete
        """
        self.logger.info('Cleaning up Browser service')
        
        # Stop browser first
        if self.is_browser_running():
            await self.stop_browser()
        
        # Cleanup Grasp sandbox
        await self.sandbox_service.destroy()
        
        self.logger.info('Browser service cleanup completed')
    
    @property
    def id(self) -> Optional[str]:
        """Get sandbox ID.
        
        Returns:
            Sandbox ID
        """
        return self.sandbox_service.id
    
    def get_sandbox(self) -> SandboxService:
        """Get the underlying Grasp service instance.
        
        Returns:
            Grasp service instance
        """
        return self.sandbox_service
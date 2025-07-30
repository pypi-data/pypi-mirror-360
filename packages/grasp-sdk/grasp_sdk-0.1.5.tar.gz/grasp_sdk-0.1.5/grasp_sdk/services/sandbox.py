#!/usr/bin/env python3
"""
Sandbox service for managing E2B sandbox lifecycle and operations.

This module provides Python implementation of the sandbox service,
equivalent to the TypeScript version in src/services/sandbox.service.ts
"""

import asyncio
import os
import tempfile
import time
from typing import Dict, Any, Optional, Union, List, Callable
from pathlib import Path
from e2b import AsyncSandbox

# Type definitions for E2B SDK
from typing import Any as CommandHandle, Any as CommandResult

from ..models import ISandboxConfig, SandboxStatus, IScriptOptions, ICommandOptions
from ..utils.logger import Logger, get_logger
from ..utils.config import get_config
from ..utils.auth import verify


class CommandEventEmitter:
    """
    Extended event emitter for background command execution.
    Emits 'stdout', 'stderr', and 'exit' events.
    """
    
    def __init__(self, handle: Optional[Any] = None):
        self.handle = handle
        self._callbacks: Dict[str, List[Callable]] = {
            'stdout': [],
            'stderr': [],
            'exit': [],
            'error': []
        }
    
    def set_handle(self, handle: Any) -> None:
        """Set the command handle (used internally)."""
        self.handle = handle
    
    def on(self, event: str, callback: Callable) -> None:
        """Register event listener."""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    def emit(self, event: Any, *args) -> None:
        """Emit event to all registered listeners."""
        # print(f'🚀 emit ${event}')
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(*args)
                except Exception as e:
                    # Ignore callback errors to prevent breaking the emitter
                    pass
    
    async def wait(self) -> Any:
        """Wait for command to complete."""
        while not self.handle:
            await asyncio.sleep(0.1)
        return await self.handle.wait()
    
    async def kill(self) -> None:
        """Kill the running command."""
        if not self.handle:
            raise RuntimeError('Command handle not set')
        await self.handle.kill()
    
    def get_handle(self) -> Optional[Any]:
        """Get the original command handle."""
        return self.handle


class SandboxService:
    """
    E2B Sandbox service for managing sandbox lifecycle and operations.
    """
    
    def __init__(self, config: ISandboxConfig):
        self.config = config
        self.sandbox: Optional[Any] = None
        self.status: SandboxStatus = SandboxStatus.STOPPED
        self.logger = self._get_default_logger()
        
        # Default working directory
        self.DEFAULT_WORKING_DIRECTORY = '/home/user'
    
    def _get_default_logger(self) -> Logger:
        """Gets or creates a default logger instance."""
        try:
            return get_logger().child('SandboxService')
        except Exception:
            # If logger is not initialized, create a default one
            from ..utils.logger import Logger
            default_logger = Logger({
                'level': 'debug' if self.config.get('debug', False) else 'info',
                'console': True,
            })
            return default_logger.child('SandboxService')
    
    @property
    def id(self) -> Optional[str]:
        """Get sandbox ID."""
        return self.sandbox.sandbox_id if self.sandbox else None
    
    @property
    def workspace(self) -> str:
        """Get workspace ID from API key."""
        return self.config['key'][3:19]
    
    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return bool(self.config.get('debug', False))
    
    @property
    def timeout(self) -> int:
        """Get timeout value."""
        return self.config['timeout']
    
    async def create_sandbox(self) -> None:
        """
        Creates and starts a new sandbox.
        
        Raises:
            RuntimeError: If sandbox creation fails
        """

        try:
            self.status = SandboxStatus.CREATING
            
            # Verify authentication
            res = await verify(self.config)
            if not res['success']:
                raise RuntimeError('Authorization failed.')
            
            api_key = res['data']['token']
            
            # Create sandbox
            self.logger.info('Creating Grasp sandbox', {
                'templateId': self.config['templateId'],
            })
            # Use Sandbox constructor directly (e2b SDK 1.5.3+)
            self.sandbox = await AsyncSandbox.create(
                template=self.config['templateId'],
                api_key=api_key,
                timeout=self.config['timeout'] // 1000  # Convert ms to seconds
            )

            self.status = SandboxStatus.RUNNING
            self.logger.info('Grasp sandbox created successfully', {
                'sandboxId': getattr(self.sandbox, 'sandbox_id', 'unknown'),
            })
            
        except Exception as error:
            self.status = SandboxStatus.ERROR
            self.logger.error('Failed to create Grasp sandbox', str(error))
            raise RuntimeError(f'Failed to create sandbox: {error}')
    
    async def run_command(
        self,
        command: str,
        options: Optional[ICommandOptions] = None,
        quiet: bool = False
    ) -> Union[Any, CommandEventEmitter, None]:
        """
        Runs a command in the sandbox.
        
        Args:
            command: Command to execute
            options: Execution options
            quiet: Suppress error logging
            
        Returns:
            CommandResult for synchronous execution,
            CommandEventEmitter for background execution,
            or None for nohup execution
            
        Raises:
            RuntimeError: If sandbox is not running or command fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        if options is None:
            options = {}
        
        cwd = options.get('cwd', self.DEFAULT_WORKING_DIRECTORY)
        timeout_ms = options.get('timeout', self.config['timeout'])
        use_nohup = options.get('nohup', False)
        in_background = options.get('inBackground', False)
        envs = options.get('envs', {})

        # print(f'command: {command}')
        # print(f'🚀 options {options}')
        
        try:
            self.logger.debug('Running command in sandbox', {
                'command': command,
                'cwd': cwd,
                'timeout': timeout_ms,
                'nohup': use_nohup,
                'background': in_background
            })
            
            if not in_background:
                # Foreground execution
                final_command = command
                if use_nohup:
                    # Create log directory
                    await self.sandbox.commands.run('mkdir -p ~/logs/grasp')
                    
                    # Generate log file name using sandbox id
                    log_file = f'~/logs/grasp/log-{self.id}.log'
                    final_command = f'nohup {command} > {log_file} 2>&1 &'
                
                if hasattr(self.sandbox, 'commands'):
                    result = await self.sandbox.commands.run(
                        final_command,
                        cwd=cwd,
                        timeout=timeout_ms,
                        envs=envs,
                        background=in_background,
                    )
                else:
                    raise RuntimeError('Sandbox commands interface not available')
                
                if hasattr(result, 'error') and result.error:
                    self.logger.error(result.stderr)
                
                return None if use_nohup else result
            
            else:
                # Background execution
                if use_nohup:
                    # Create log directory
                    await self.sandbox.commands.run('mkdir -p ~/logs/grasp')
                    
                    # Generate log file name using sandbox id
                    log_file = f'~/logs/grasp/log-{self.id}.log'
                    nohup_command = f'nohup {command} > {log_file} 2>&1 &'
                    # print(f"💬 {nohup_command}")
                    await self.sandbox.commands.run(
                        nohup_command,
                        cwd=cwd,
                        timeout=timeout_ms // 1000,
                        envs=envs,
                        background=in_background,
                    )
                    return None

                # Create CommandEventEmitter for background execution
                event_emitter = CommandEventEmitter()
                
                # Schedule background execution
                async def _execute_background():
                    try:
                        if self.sandbox and hasattr(self.sandbox, 'commands'):
                            commands_attr = getattr(self.sandbox, 'commands', None)
                            if not commands_attr:
                                raise RuntimeError("Sandbox commands not available")
                            handle = await commands_attr.run(
                                command,
                                cwd=cwd,
                                timeout=timeout_ms // 1000,
                                background=True,
                                envs=envs,
                                on_stdout=lambda data: (
                                    self.logger.debug('Command stdout', {'data': data}),
                                    event_emitter.emit('stdout', data)
                                )[1],
                                on_stderr=lambda data: (
                                    self.logger.debug('Command stderr', {'data': data}),
                                    event_emitter.emit('stderr', data)
                                )[1]
                            )
                        
                            event_emitter.set_handle(handle)
                        else:
                            raise RuntimeError("Sandbox or commands not available")
                        
                        # Wait for command completion (for non-nohup commands)
                        if not use_nohup:
                            try:
                                # print(f"⏳ {command}")
                                result = await handle.wait()
                                # print(f"✅ {command} 执行完毕")
                                # event_emitter.emit('stdout', '🎉 ok')
                                event_emitter.emit('exit', result.exit_code)
                            except Exception as error:
                                event_emitter.emit('error', error)
                    
                    except Exception as error:
                        event_emitter.emit('error', error)
                
                # Start background execution
                asyncio.create_task(_execute_background())
                return event_emitter
        
        except Exception as error:
            if not quiet:
                self.logger.error('Command execution failed', str(error))
            
            # Return error result as dict
            return {
                'exit_code': 1,
                'stdout': '',
                'stderr': str(error)
            }
    
    async def run_script(
        self,
        code: str,
        options: Optional[IScriptOptions] = None
    ) -> Union[Any, CommandEventEmitter]:
        """
        Runs JavaScript code in the sandbox.
        
        Args:
            code: JavaScript code to execute
            options: Script execution options
            
        Returns:
            CommandResult for synchronous execution,
            CommandEventEmitter for background execution
            
        Raises:
            RuntimeError: If sandbox is not running or script execution fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        if options is None:
            options = {'type': 'cjs'}
        
        try:
            # Generate temporary file name in working directory
            timestamp = int(time.time() * 1000)
            extension = 'mjs' if options['type'] == 'esm' else 'js'
            working_dir = options.get('cwd', self.DEFAULT_WORKING_DIRECTORY)
            script_path = f'{working_dir}/script_{timestamp}.{extension}'
            
            self.logger.debug('Running JavaScript code in sandbox', {
                'type': options['type'],
                'scriptPath': script_path,
                'codeLength': len(code),
            })
            
            # Write code to temporary file
            await self.sandbox.files.write(script_path, code)
            
            # Choose execution command based on type
            pre_command = options.get('preCommand', '')
            command = f'{pre_command}node {script_path}'
            
            # Set environment variables
            envs = options.get('envs', {})
            envs['PLAYWRIGHT_BROWSERS_PATH'] = '0'

            # Prepare command options
            cmd_options: Optional[Any] = {
                'cwd': options.get('cwd'),
                'timeout': options.get('timeoutMs'),
                'inBackground': options.get('background', False),
                'nohup': options.get('nohup', False),
                'envs': envs,
            }
            
            # Execute the script
            result = await self.run_command(command, cmd_options)
            
            # Cleanup temporary file (if not background execution)
            if not options.get('background', False):
                try:
                    await self.run_command(f'rm -f {script_path}')
                except Exception as cleanup_error:
                    self.logger.warn('Failed to cleanup script file', {
                        'scriptPath': script_path,
                        'error': cleanup_error,
                    })
            
            return result
        
        except Exception as error:
            self.logger.error('Script execution failed', str(error))
            raise RuntimeError(f'Failed to execute script: {error}')
    
    def _is_binary_file(self, file_path: str) -> bool:
        """
        Check if a file is binary based on its extension.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file is binary, false otherwise
        """
        binary_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico',
            '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
            '.exe', '.dll', '.so', '.dylib',
            '.bin', '.dat', '.db', '.sqlite'
        }
        
        ext = Path(file_path).suffix.lower()
        return ext in binary_extensions
    
    async def copy_file_from_sandbox(self, remote_path: str, local_path: str) -> None:
        """
        Copy file from sandbox to local filesystem.
        
        Args:
            remote_path: File path in sandbox
            local_path: Local destination path
            
        Raises:
            RuntimeError: If sandbox is not running or copy fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        try:
            self.logger.debug('Copying file from sandbox', {
                'remotePath': remote_path,
                'localPath': local_path,
            })
            
            # Check if file is binary
            is_binary = self._is_binary_file(remote_path)
            
            if is_binary:
                # For binary files, read as bytes
                file_content = await self.sandbox.files.read(remote_path, format='bytes')
                with open(local_path, 'wb') as f:
                    f.write(file_content)
            else:
                # For text files, read as string
                file_content = await self.sandbox.files.read(remote_path, format='text')
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            
            self.logger.info(f'File copied from sandbox: {remote_path} -> {local_path}')
        
        except Exception as error:
            self.logger.error(f'Failed to copy file: {error}')
            raise
    
    async def upload_file_to_sandbox(self, local_path: str, remote_path: str) -> None:
        """
        Uploads a file to the sandbox.
        
        Args:
            local_path: Local file path
            remote_path: Destination path in sandbox
            
        Raises:
            RuntimeError: If sandbox is not running or upload fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        try:
            self.logger.debug('Uploading file to sandbox', {
                'localPath': local_path,
                'remotePath': remote_path,
            })
            
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            await self.sandbox.files.write(remote_path, file_content)
            
            self.logger.debug('File uploaded successfully', {
                'localPath': local_path,
                'remotePath': remote_path,
            })
        
        except Exception as error:
            self.logger.error('Failed to upload file to sandbox', str(error))
            raise RuntimeError(f'Failed to upload file: {error}')
    
    async def list_files(self, path: str) -> List[str]:
        """
        Lists files in a sandbox directory.
        
        Args:
            path: Directory path in sandbox
            
        Returns:
            List of filenames
            
        Raises:
            RuntimeError: If sandbox is not running or listing fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        try:
            self.logger.debug('Listing files in sandbox', {'path': path})
            
            result = await self.run_command(f'ls -la "{path}"')
            
            if hasattr(result, 'exit_code') and getattr(result, 'exit_code', 0) != 0:
                raise RuntimeError(f'Failed to list files: {getattr(result, "stderr", "")}')
            
            # Parse ls output to extract filenames
            stdout = getattr(result, 'stdout', '') if result else ''
            if stdout:
                lines = stdout.split('\n')
                files = []
                
                for line in lines[1:]:  # Skip first line (total)
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 9:  # Valid ls -la output
                            filename = parts[-1]
                            if filename not in ('.', '..'):
                                files.append(filename)
                
                return files
            
            return []
        
        except Exception as error:
            self.logger.error('Failed to list files', str(error))
            raise RuntimeError(f'Failed to list files: {error}')
    
    def get_status(self) -> SandboxStatus:
        """Gets the current sandbox status."""
        return self.status
    
    def get_sandbox_id(self) -> Optional[str]:
        """Gets sandbox ID if available."""
        return getattr(self.sandbox, 'sandbox_id', None) if self.sandbox else None
    
    def get_sandbox_host(self, port: int) -> Optional[str]:
        """
        Gets the external host address for a specific port.
        
        Args:
            port: Port number to get host for
            
        Returns:
            External host address or None if sandbox not available
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            self.logger.warn('Cannot get sandbox host: sandbox not running')
            return None
        
        try:
            host = self.sandbox.get_host(port)
            self.logger.debug('Got sandbox host for port', {'port': port, 'host': host})
            return host
        except Exception as error:
            self.logger.error('Failed to get sandbox host', {'port': port, 'error': error})
            return None
    
    async def destroy(self) -> None:
        """
        Destroys the sandbox and cleans up resources.
        
        Raises:
            RuntimeError: If sandbox destruction fails
        """
        if self.sandbox:
            try:
                self.logger.info('Destroying Grasp sandbox', {
                    'sandboxId': getattr(self.sandbox, 'sandbox_id', 'unknown'),
                })
                
                await self.sandbox.kill()
                self.sandbox = None
                self.status = SandboxStatus.STOPPED
                
                self.logger.info('Grasp sandbox destroyed successfully')
            
            except Exception as error:
                self.logger.error('Failed to destroy sandbox', str(error))
                raise RuntimeError(f'Failed to destroy sandbox: {error}')
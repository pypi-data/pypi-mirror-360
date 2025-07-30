# Grasp SDK - Python Implementation

[![PyPI version](https://badge.fury.io/py/grasp-sdk.svg)](https://badge.fury.io/py/grasp-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

🐍 Python implementation of Grasp SDK for E2B platform providing secure command execution and browser automation in isolated cloud environments.

**Current Version: 0.1.4** - [View on PyPI](https://pypi.org/project/grasp-sdk/0.1.4/)

## 🚀 Features

- **Secure Execution**: Run commands and scripts in isolated E2B sandboxes
- **Browser Automation**: Control Chromium browsers with Playwright integration
- **Async/Await Support**: Full async/await support for modern Python development
- **Type Safety**: Complete type hints with Pydantic models
- **WebSocket Communication**: Real-time communication with sandbox environments
- **Multi-language Support**: Compatible with Node.js/TypeScript version

## 📦 Installation

```bash
# Install from PyPI
pip install grasp_sdk

# Install from source
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## 🔧 Quick Start

### Using GraspServer Context Manager (Recommended)

```python
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv

from grasp_sdk import GraspServer
from grasp_sdk.models import IBrowserConfig, ISandboxConfig

# 加载环境变量
load_dotenv("../.env.grasp")

async def main():
    """主函数：演示 Grasp SDK 的基本用法"""
    
    # 检查是否有 API key
    api_key = os.getenv('GRASP_KEY')
    if not api_key:
        print("⚠️ 警告：未设置 GRASP_KEY 环境变量")
        print("请设置 GRASP_KEY 环境变量或在 .env 文件中配置")
        print("示例：export GRASP_KEY=your_api_key_here")
        return

    print("🚀 正在启动浏览器...")

    async with GraspServer({
            # 'key': api_key,
            # 'type': 'chrome-stable',
            # 'headless': False,
            # 'adblock': True,
            # 'debug': True,
            'timeout': 3600000,  # 容器最长运行1小时（最大值可以为一天 86400000）
        }) as connection:
    
        try:
            print(f"连接信息: {connection}")
            print(f"WebSocket URL: {connection['ws_url']}")
            print(f"HTTP URL: {connection['http_url']}")
            
            # 使用 Playwright 连接到 CDP
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(
                    connection['ws_url'],
                    timeout=150000
                )
                
                # 创建第一个页面并访问网站
                page1 = await browser.new_page()
                await page1.goto('https://getgrasp.ai/', wait_until='domcontentloaded')
                await page1.screenshot(path='grasp-ai.png')
                await page1.close()
                
                # 获取或创建上下文
                contexts = browser.contexts
                context = contexts[0] if contexts else await browser.new_context()
                
                # 创建第二个页面
                page2 = await context.new_page()
                
                # 将 HTML 字符串渲染到页面中
                await page2.set_content('<h1>Hello Grasp</h1>', wait_until='networkidle')
                
                # 截图演示
                await page2.screenshot(path='hello-world.png', full_page=True)
                
                # 清理资源
                await page2.close()
                await context.close()
                await browser.close()
                
            print('✅ 任务完成。')
            
        except Exception as e:
            print(f"❌ 执行过程中出现错误: {str(e)}")
            raise
        
        finally:
            # 注意：使用 GraspServer 上下文管理器时，资源会自动清理
            print("程序结束，资源将自动清理")

if __name__ == '__main__':
    asyncio.run(main())
```

## 🏗️ Architecture

The Python implementation mirrors the Node.js/TypeScript version:

```
py-src/
├── __init__.py              # Main package exports
├── grasp_server.py          # Main GraspServer class
├── services/                # Core services
│   ├── __init__.py
│   ├── sandbox_service.py   # E2B sandbox management
│   └── browser_service.py   # Browser automation
├── types/                   # Type definitions
│   └── __init__.py
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── logger.py           # Logging utilities
│   └── auth.py             # Authentication
├── cli/                     # Command line interface
│   ├── __init__.py
│   └── main.py
└── tests/                   # Test suite
    └── ...
```

## 🔑 Environment Variables

```bash
# Required
E2B_API_KEY=your_e2b_api_key_here

# Optional
GRASP_LOG_LEVEL=info
GRASP_TIMEOUT=30000
GRASP_TEMPLATE=python
```

## 🧪 Development

### Quick Setup

```bash
# Install development dependencies automatically
python install_dev_deps.py

# Or manually install
pip install -e ".[dev]"
```

### Running Tests

```bash
# Simple tests (no pytest required)
python test_connect_simple.py

# Full test suite (requires pytest)
pytest tests/

# Run specific test file
pytest tests/test_connect.py -v
```

### Code Quality

```bash
# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8 .
```

### Examples

```bash
# Run Connect usage examples
python example_connect.py
```

## 📚 API Reference

### GraspServer (Recommended)

Async context manager for automatic sandbox resource management and browser automation.

```python
class GraspServer:
    def __init__(self, options: Optional[Dict[str, Any]] = None)
    async def __aenter__(self) -> Dict[str, Any]  # Returns connection info
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None
```

**Usage:**
```python
async with GraspServer(options) as connection:
    # connection contains: {'id', 'ws_url', 'http_url'}
    # Automatic cleanup on exit
```

**Options:**
- `key`: Your Grasp API key (loaded from environment if not provided)
- `type`: Browser type ('chromium' or 'chrome-stable')
- `headless`: Run in headless mode (default: True)
- `adblock`: Enable adblock (default: False)
- `debug`: Enable debug mode (default: False)
- `timeout`: Container maximum runtime in milliseconds (default: 30000, max: 86400000)

### GraspServer

Main class for interacting with E2B sandboxes and browser automation.

```python
class GraspServer:
    def __init__(self, sandbox_config: Optional[Dict[str, Any]] = None)
    async def create_browser_task(self, browser_type: str = 'chromium', config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
    async def cleanup(self) -> None
    def get_status(self) -> Optional[SandboxStatus]
    def get_sandbox_id(self) -> Optional[str]
    @property
    def sandbox(self) -> Optional[SandboxService]
```

## 🤝 Compatibility

This Python implementation provides the same API surface as the Node.js/TypeScript version, ensuring:

- **Feature Parity**: All features available in both implementations
- **API Consistency**: Same method names and behavior
- **Type Safety**: Equivalent type definitions using TypedDict and Pydantic
- **Error Handling**: Consistent error types and messages

## 📄 License

MIT License - see the [LICENSE](../LICENSE) file for details.

## 📋 Release History

### v0.1.4 (2025-01-27)
- Version synchronization update
- Package metadata improvements
- Documentation updates

### v0.1.0 (2025-01-27)
- Initial release
- Core functionality implementation
- Complete API compatibility with Node.js version

## 🔗 Related

- [Node.js/TypeScript Implementation](../src/)
- [E2B Platform](https://e2b.dev/)
- [Playwright Python](https://playwright.dev/python/)
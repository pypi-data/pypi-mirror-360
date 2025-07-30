#!/usr/bin/env python3
"""
Grasp SDK Python 使用示例

这个示例展示了如何使用 grasp_sdk 启动浏览器、连接 CDP、执行基本操作并截图。
"""

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
                
                # 等待一段时间（可选）
                # await asyncio.sleep(10)
                
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
                
                # 等待特定元素可见（可选）
                # await page2.wait_for_selector('#my-element')
                
                # 截图演示
                await page2.screenshot(path='hello-world.png', full_page=True)
                
                # 清理资源
                await page2.close()
                await context.close()
                await browser.close()
                
            # print('⏳ 等待10秒...')
            # await asyncio.sleep(10)
            print('✅ 任务完成。')
            
        except Exception as e:
            print(f"❌ 执行过程中出现错误: {str(e)}")
            raise
        
        finally:
            # 注意：使用 launch_browser 函数时，资源会在程序退出时自动清理
            # 如果需要手动清理，可以使用 GraspServer 类的实例方法
            print("程序结束，资源将自动清理")


if __name__ == '__main__':
    # 运行主函数
    asyncio.run(main())
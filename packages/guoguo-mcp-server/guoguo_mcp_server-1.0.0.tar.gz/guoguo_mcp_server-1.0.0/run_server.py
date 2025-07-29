#!/usr/bin/env python3
"""
寄件服务MCP Server启动脚本
"""

import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from guoguo_mcp import main

if __name__ == "__main__":
    print("🚀 启动寄件服务MCP Server...")
    print("📋 提供以下工具:")
    print("  - query_address_book: 地址簿查询")
    print("  - create_shipping_order: 创建寄件订单")
    print("  - list_shipping_orders: 查询订单列表")
    print("  - get_order_detail: 查询订单详情")
    print("\n等待客户端连接...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1) 
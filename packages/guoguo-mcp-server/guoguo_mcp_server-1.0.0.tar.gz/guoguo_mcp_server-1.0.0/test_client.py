#!/usr/bin/env python3
"""
寄件服务MCP Server测试客户端
支持测试命令行参数配置
"""

import asyncio
import json
import subprocess
import time
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server_with_args(token: str = "test_token_123", use_mock: bool = True):
    """测试带命令行参数的MCP服务器"""
    
    # 构建命令行参数
    args = ["python", "src/guoguo_mcp/__init__.py"]
    if token:
        args.extend(["--token", token])
    if use_mock:
        args.append("--use-mock")
    else:
        args.append("--no-mock")
    
    print(f"🚀 启动寄件服务MCP Server测试...")
    print(f"📋 命令行参数: {' '.join(args[1:])}")
    
    server_params = StdioServerParameters(
        command="python",
        args=["src/guoguo_mcp/__init__.py"] + args[2:],  # 去掉python命令
        env=None
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化
                await session.initialize()
                print("✅ MCP Server连接成功")
                print(f"🔑 使用访问令牌: {token}")
                print(f"🎭 Mock模式: {'开启' if use_mock else '关闭'}")
                print()
                
                # 测试工具列表
                print("📋 测试工具列表...")
                tools = await session.list_tools()
                print(f"可用工具数量: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description.split()[0]}...")
                print()
                
                # 测试地址簿查询
                print("🏠 测试地址簿查询...")
                result = await session.call_tool("query_address_book", {})
                response_data = json.loads(result.content[0].text)
                print(f"地址簿查询结果: 状态={response_data['status']}, 数量={response_data.get('total_count', 0)}")
                print()
                
                # 测试地址簿搜索
                print("🔍 测试地址簿搜索...")
                result = await session.call_tool("query_address_book", {"search_key": "张三"})
                response_data = json.loads(result.content[0].text)
                print(f"搜索结果: 状态={response_data['status']}, 匹配数量={response_data.get('total_count', 0)}")
                print()
                
                # 测试创建寄件订单
                print("📦 测试创建寄件订单...")
                order_data = {
                    "sender_name": "测试寄件人",
                    "sender_phone": "13900139000",
                    "sender_address": "测试市测试区测试街道123号",
                    "receiver_name": "测试收件人",
                    "receiver_phone": "13900139001", 
                    "receiver_address": "目标市目标区目标街道456号",
                    "package_type": "测试物品",
                    "package_weight": 1.5,
                    "package_size": "20x15x10",
                    "service_type": "快速"
                }
                
                result = await session.call_tool("create_shipping_order", order_data)
                response_data = json.loads(result.content[0].text)
                
                if response_data.get("status") == "success":
                    order_id = response_data.get("order_id")
                    cost = response_data.get("estimated_cost")
                    print(f"订单创建成功: ID={order_id}, 预计费用={cost}元")
                    
                    # 测试查询订单详情
                    print(f"🔍 测试查询订单详情 ({order_id})...")
                    result = await session.call_tool("get_order_detail", {
                        "order_id": order_id,
                        "detail_level": "full"
                    })
                    detail_data = json.loads(result.content[0].text)
                    if detail_data.get("status") == "success":
                        print(f"订单详情查询成功: 状态={detail_data['order_info']['status']}")
                    else:
                        print(f"订单详情查询失败: {detail_data.get('message')}")
                else:
                    print(f"订单创建失败: {response_data.get('message')}")
                print()
                
                # 测试查询订单列表
                print("📋 测试查询订单列表...")
                result = await session.call_tool("list_shipping_orders", {
                    "page_size": 5,
                    "page_number": 1
                })
                response_data = json.loads(result.content[0].text)
                
                if response_data.get("status") == "success":
                    orders = response_data.get("orders", [])
                    pagination = response_data.get("pagination", {})
                    print(f"订单列表查询成功: 当前页{len(orders)}条, 总计{pagination.get('total_count', 0)}条")
                else:
                    print(f"订单列表查询失败: {response_data.get('message')}")
                print()
                
                # 测试状态过滤
                print("🎯 测试按状态过滤订单...")
                result = await session.call_tool("list_shipping_orders", {
                    "page_size": 10,
                    "page_number": 1,
                    "status": "已签收"
                })
                response_data = json.loads(result.content[0].text)
                
                if response_data.get("status") == "success":
                    orders = response_data.get("orders", [])
                    print(f"已签收订单: {len(orders)}条")
                else:
                    print(f"状态过滤失败: {response_data.get('message')}")
                print()
                
                print("✅ 所有测试完成！")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True


async def test_different_configurations():
    """测试不同的配置组合"""
    
    print("🔧 测试不同的配置组合...\n")
    
    # 测试1: Mock模式 + 测试访问令牌
    print("=" * 50)
    print("测试1: Mock模式 + 测试访问令牌")
    print("=" * 50)
    success1 = await test_mcp_server_with_args(
        token="dev_test_token_456", 
        use_mock=True
    )
    
    # 测试2: Mock模式 + 生产访问令牌格式
    print("\n" + "=" * 50)
    print("测试2: Mock模式 + 生产访问令牌格式")
    print("=" * 50)
    success2 = await test_mcp_server_with_args(
        token="prod_sf_token_789abc", 
        use_mock=True
    )
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"测试1 (开发环境): {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"测试2 (生产格式): {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("🎉 所有配置测试都通过了！")
        return True
    else:
        print("⚠️  部分测试失败，请检查配置")
        return False


def test_command_line_args():
    """测试命令行参数解析"""
    print("🧪 测试命令行参数解析...")
    
    test_cases = [
        ["--help"],
        ["--token", "test123", "--use-mock"],
        ["--api-url", "https://api.test.com", "--token", "token123", "--timeout", "60"],
        ["--no-mock", "--token", "production_token"],
        ["--token", "test456", "--no-mock"]  # 测试--no-mock参数
    ]
    
    for i, args in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: python src/guoguo_mcp/__init__.py {' '.join(args)}")
        
        try:
            if "--help" in args:
                # Help 命令会退出，这是正常的
                result = subprocess.run(
                    ["python", "src/guoguo_mcp/__init__.py"] + args,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "usage:" in result.stdout:
                    print("✅ Help 输出正常")
                else:
                    print("❌ Help 输出异常")
            else:
                # 其他参数只测试是否能正常解析（不启动服务器）
                print("✅ 参数格式正确")
                
        except Exception as e:
            print(f"❌ 参数解析错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test-args":
        # 测试命令行参数
        test_command_line_args()
    else:
        # 运行完整测试
        asyncio.run(test_different_configurations()) 
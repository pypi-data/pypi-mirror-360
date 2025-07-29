#!/usr/bin/env python3
"""
寄件服务MCP Server
提供寄件订单管理、地址簿查询等功能，通过HTTP API对接远程服务
"""

import asyncio
import logging
import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

import httpx
from mcp.server.fastmcp import FastMCP


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# API配置
class APIConfig:
    """API配置类"""
    def __init__(self, 
                 base_url: Optional[str] = None,
                 token: Optional[str] = None,
                 timeout: Optional[int] = None,
                 use_mock: Optional[bool] = None):
        # 优先使用传入的参数，其次使用环境变量，最后使用默认值
        self.base_url = (
            base_url or 
            os.getenv("SHIPPING_API_BASE_URL") or 
            "https://pre-xg.cainiao.com/"
        )
        self.token = (
            token or 
            os.getenv("SHIPPING_API_TOKEN") or 
            "demo_token"
        )
        self.timeout = (
            timeout or 
            int(os.getenv("SHIPPING_API_TIMEOUT", "30"))
        )
        self.use_mock = (
            use_mock if use_mock is not None else
            os.getenv("SHIPPING_USE_MOCK", "false").lower() == "true"
        )
        
    @property
    def headers(self) -> Dict[str, str]:
        """获取HTTP请求头"""
        return {
            "token":f"{self.token}"
        }


# 解析命令行参数或MCP配置参数
def parse_config_from_args() -> APIConfig:
    """从命令行参数解析配置"""
    import argparse
    
    parser = argparse.ArgumentParser(description="寄件服务MCP Server")
    parser.add_argument("--api-url", 
                       help="API服务器URL (例如: https://api.sf-express.com)")
    parser.add_argument("--token", 
                       help="API访问令牌")
    parser.add_argument("--timeout", 
                       type=int, 
                       help="请求超时时间(秒)")
    parser.add_argument("--use-mock", 
                       action="store_true", 
                       help="使用模拟数据而不是真实API")
    parser.add_argument("--no-mock", 
                       action="store_true", 
                       help="禁用模拟数据，使用真实API")
    
    # 解析已知参数，忽略其他参数
    args, unknown = parser.parse_known_args()
    
    # 确定use_mock的值
    use_mock = None
    if args.use_mock:
        use_mock = True
    elif args.no_mock:
        use_mock = False
    
    return APIConfig(
        base_url=args.api_url,
        token=args.token,
        timeout=args.timeout,
        use_mock=use_mock
    )


# 初始化配置
config = parse_config_from_args()

# 创建FastMCP服务器
mcp = FastMCP(
    name="寄件服务MCP Server",
    version="2.0.0",
    description="提供寄件订单管理、地址簿查询等功能的MCP Server，通过HTTP API对接远程服务"
)


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING_PICKUP = "待取件"
    PICKED_UP = "已取件"
    IN_TRANSIT = "运输中"
    OUT_FOR_DELIVERY = "派送中"
    DELIVERED = "已签收"
    RETURNED = "已退回"
    CANCELLED = "已取消"
    EXCEPTION = "异常"


class ServiceType(Enum):
    """服务类型枚举"""
    STANDARD = "标准"
    EXPRESS = "快速"
    ECONOMY = "经济"


@dataclass
class Address:
    """地址信息"""
    name: str
    phone: str
    address: str
    is_default: bool = False


@dataclass
class ContactInfo:
    """联系人信息"""
    name: str
    phone: str
    address: str


@dataclass
class PackageInfo:
    """包裹信息"""
    type: str
    weight: float  # kg
    size: str  # 长x宽x高，单位cm


@dataclass
class ShippingOrder:
    """寄件订单"""
    order_id: str
    sender: ContactInfo
    receiver: ContactInfo
    package: PackageInfo
    service_type: ServiceType
    status: OrderStatus
    create_time: datetime
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    cost: Optional[float] = None


class HTTPClient:
    """HTTP客户端类"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.timeout),
            headers=config.headers
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """发送GET请求"""
        try:
            # 确保URL格式正确，避免双斜杠
            base_url = self.config.base_url.rstrip('/')
            endpoint = endpoint.lstrip('/')
            url = f"{base_url}/{endpoint}"
            logger.info(f"发送GET请求: {url}, 参数: {params}")
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"API响应成功: {response.status_code}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP状态错误: {e.response.status_code} - {e.response.text}")
            return {
                "status": "error",
                "error_code": "HTTP_ERROR",
                "message": f"HTTP错误 {e.response.status_code}: {e.response.text}"
            }
        except httpx.RequestError as e:
            logger.error(f"请求错误: {str(e)}")
            return {
                "status": "error",
                "error_code": "REQUEST_ERROR",
                "message": f"请求失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return {
                "status": "error",
                "error_code": "UNKNOWN_ERROR",
                "message": f"未知错误: {str(e)}"
            }
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送POST请求"""
        try:
            url = f"{self.config.base_url}{endpoint}"
            logger.info(f"发送POST请求: {url}, 数据: {data}")
            
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"API响应成功: {response.status_code}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP状态错误: {e.response.status_code} - {e.response.text}")
            return {
                "status": "error",
                "error_code": "HTTP_ERROR",
                "message": f"HTTP错误 {e.response.status_code}: {e.response.text}"
            }
        except httpx.RequestError as e:
            logger.error(f"请求错误: {str(e)}")
            return {
                "status": "error",
                "error_code": "REQUEST_ERROR",
                "message": f"请求失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return {
                "status": "error",
                "error_code": "UNKNOWN_ERROR",
                "message": f"未知错误: {str(e)}"
            }


# Mock数据（仅在开发环境使用）
def get_mock_address_book() -> List[Address]:
    """获取模拟地址簿数据"""
    return [
        Address(name="张三", phone="13800138002", address="北京市朝阳区中关村大街1号", is_default=True),
        Address(name="李四", phone="13800138001", address="上海市浦东新区陆家嘴环路1000号"),
        Address(name="王五", phone="13800138002", address="广州市天河区珠江新城花城大道85号"),
        Address(name="赵六", phone="13800138003", address="深圳市南山区深南大道10000号"),
    ]


def get_mock_orders() -> List[ShippingOrder]:
    """获取模拟订单数据"""
    return [
        ShippingOrder(
            order_id="SF2024001",
            sender=ContactInfo(name="张三", phone="1380013802", address="北京市朝阳区中关村大街1号"),
            receiver=ContactInfo(name="李四", phone="13800138001", address="上海市浦东新区陆家嘴环路1000号"),
            package=PackageInfo(type="文件", weight=0.5, size="30x20x5"),
            service_type=ServiceType.EXPRESS,
            status=OrderStatus.DELIVERED,
            create_time=datetime.now() - timedelta(days=2),
            estimated_delivery=datetime.now() - timedelta(days=1),
            actual_delivery=datetime.now() - timedelta(hours=6),
            cost=25.0
        ),
        ShippingOrder(
            order_id="SF2024002",
            sender=ContactInfo(name="王五", phone="13800138002", address="广州市天河区珠江新城花城大道85号"),
            receiver=ContactInfo(name="赵六", phone="13800138003", address="深圳市南山区深南大道10000号"),
            package=PackageInfo(type="电子产品", weight=1.2, size="25x15x10"),
            service_type=ServiceType.STANDARD,
            status=OrderStatus.IN_TRANSIT,
            create_time=datetime.now() - timedelta(days=1),
            estimated_delivery=datetime.now() + timedelta(hours=12),
            cost=15.0
        )
    ]


@mcp.tool()
async def query_address_book(search_key: Optional[str] = None) -> str:
    """
    查询用户的地址簿信息
    
    Args:
        search_key: 搜索关键词(可选)，可以搜索姓名、电话或地址
    
    Returns:
        包含地址列表的JSON字符串
    """
    try:
        if config.use_mock:
            # 使用模拟数据
            logger.info("使用模拟数据进行地址簿查询")
            address_book = get_mock_address_book()
            
            filtered_addresses = address_book
            if search_key:
                search_key = search_key.lower()
                filtered_addresses = [
                    addr for addr in address_book
                    if (search_key in addr.name.lower() or 
                        search_key in addr.phone or 
                        search_key in addr.address.lower())
                ]
            
            result = {
                "status": "success",
                "total_count": len(filtered_addresses),
                "addresses": [asdict(addr) for addr in filtered_addresses]
            }
            
        else:
            # 调用远程API
            async with HTTPClient(config) as client:
                params = {}
                if search_key:
                    params["search"] = search_key
                
                api_response = await client.get("/mcp/api/v1/address-book", params=params)
                
                # 添加调试信息
                logger.info(f"API原始响应: {json.dumps(api_response, ensure_ascii=False)}")
                
                # 解析API响应格式
                if api_response.get("success"):
                    data = api_response.get("data", {})
                    # 转换为统一格式
                    result = {
                        "status": "success",
                        "total_count": data.get("totalCount", 0),
                        "addresses": []
                    }
                    
                    # 转换地址格式
                    for addr in data.get("addresses", []):
                        result["addresses"].append({
                            "name": addr.get("name"),
                            "phone": addr.get("phone"),
                            "address": addr.get("address"),
                            "is_default": addr.get("default", False)
                        })
                else:
                    # API返回错误 - 处理两种错误格式
                    error_code = api_response.get("errorCode") or api_response.get("code", "API_ERROR")
                    error_message = api_response.get("errorMsg") or api_response.get("message", "API调用失败")
                    
                    result = {
                        "status": "error",
                        "error_code": error_code,
                        "message": error_message,
                        "total_count": 0,
                        "addresses": []
                    }
        
        logger.info(f"地址簿查询完成，返回{result.get('total_count', 0)}条记录")
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"地址簿查询失败: {e}")
        error_result = {
            "status": "error",
            "error_code": "QUERY_ERROR",
            "message": f"查询失败: {str(e)}",
            "addresses": []
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
async def create_shipping_order(
    sender_name: str,
    sender_phone: str,
    sender_address: str,
    receiver_name: str,
    receiver_phone: str,
    receiver_address: str,
    package_type: str,
    package_weight: float,
    package_size: str,
    service_type: str = "标准"
) -> str:
    """
    创建新的寄件订单
    
    Args:
        sender_name: 寄件人姓名
        sender_phone: 寄件人电话
        sender_address: 寄件人地址
        receiver_name: 收件人姓名
        receiver_phone: 收件人电话
        receiver_address: 收件人地址
        package_type: 物品类型
        package_weight: 重量(kg)
        package_size: 尺寸(长x宽x高,cm)
        service_type: 服务类型(标准/快速/经济)
    
    Returns:
        包含订单号和预计费用的JSON字符串
    """
    try:
        # 验证服务类型
        try:
            service_enum = ServiceType(service_type)
        except ValueError:
            return json.dumps({
                "status": "error",
                "error_code": "INVALID_SERVICE_TYPE",
                "message": f"无效的服务类型: {service_type}，支持的类型: 标准/快速/经济"
            }, ensure_ascii=False, indent=2)
        
        # 构造请求数据
        order_data = {
            "sender": {
                "name": sender_name,
                "phone": sender_phone,
                "address": sender_address
            },
            "receiver": {
                "name": receiver_name,
                "phone": receiver_phone,
                "address": receiver_address
            },
            "package": {
                "type": package_type,
                "weight": package_weight,
                "size": package_size
            },
            "service_type": service_type
        }
        
        if config.use_mock:
            # 使用模拟数据
            logger.info("使用模拟数据创建订单")
            
            # 模拟费用计算
            base_cost = 10.0
            weight_cost = package_weight * 5.0
            service_multiplier = {"标准": 1.0, "快速": 1.5, "经济": 0.8}[service_type]
            estimated_cost = (base_cost + weight_cost) * service_multiplier
            
            # 模拟配送时间计算
            delivery_hours = {"标准": 48, "快速": 24, "经济": 72}[service_type]
            estimated_delivery = datetime.now() + timedelta(hours=delivery_hours)
            
            # 生成订单号
            order_id = f"SF{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            result = {
                "status": "success",
                "order_id": order_id,
                "estimated_cost": round(estimated_cost, 2),
                "estimated_delivery": estimated_delivery.strftime("%Y-%m-%d %H:%M:%S"),
                "pickup_time": "24小时内安排取件",
                "tracking_number": order_id
            }
            
        else:
            # 调用远程API
            async with HTTPClient(config) as client:
                api_response = await client.post("/mcp/api/v1/orders", data=order_data)
                
                # 解析API响应格式
                if api_response.get("success"):
                    data = api_response.get("data", {})
                    # 转换为统一格式
                    result = {
                        "status": "success",
                        "order_id": data.get("orderId") or data.get("order_id"),
                        "estimated_cost": data.get("estimatedCost") or data.get("estimated_cost"),
                        "estimated_delivery": data.get("estimatedDelivery") or data.get("estimated_delivery"),
                        "pickup_time": data.get("pickupTime") or data.get("pickup_time", "24小时内安排取件"),
                        "tracking_number": data.get("trackingNumber") or data.get("tracking_number") or data.get("orderId") or data.get("order_id")
                    }
                else:
                    # API返回错误 - 处理两种错误格式
                    error_code = api_response.get("errorCode") or api_response.get("code", "API_ERROR")
                    error_message = api_response.get("errorMsg") or api_response.get("message", "API调用失败")
                    
                    result = {
                        "status": "error",
                        "error_code": error_code,
                        "message": error_message
                    }
        
        if result.get("status") == "success":
            logger.info(f"订单创建成功: {result.get('order_id')}")
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"创建订单失败: {e}")
        error_result = {
            "status": "error",
            "error_code": "CREATE_ORDER_ERROR",
            "message": f"创建订单失败: {str(e)}"
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
async def list_shipping_orders(
    page_size: int = 10,
    page_number: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    分页查询寄件订单列表
    
    Args:
        page_size: 每页数量
        page_number: 页码(从1开始)
        start_date: 开始日期(YYYY-MM-DD格式)
        end_date: 结束日期(YYYY-MM-DD格式)
        status: 订单状态过滤
    
    Returns:
        包含订单列表和分页信息的JSON字符串
    """
    try:
        if config.use_mock:
            # 使用模拟数据
            logger.info("使用模拟数据查询订单列表")
            orders = get_mock_orders()
            
            # 状态过滤
            if status:
                try:
                    status_enum = OrderStatus(status)
                    orders = [order for order in orders if order.status == status_enum]
                except ValueError:
                    pass
            
            # 日期过滤
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    orders = [order for order in orders if order.create_time >= start_dt]
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                    orders = [order for order in orders if order.create_time < end_dt]
                except ValueError:
                    pass
            
            # 分页
            total_count = len(orders)
            total_pages = (total_count + page_size - 1) // page_size
            start_idx = (page_number - 1) * page_size
            end_idx = start_idx + page_size
            page_orders = orders[start_idx:end_idx]
            
            # 转换为字典格式
            order_dicts = []
            for order in page_orders:
                order_dict = {
                    "order_id": order.order_id,
                    "sender": asdict(order.sender),
                    "receiver": asdict(order.receiver),
                    "package": asdict(order.package),
                    "service_type": order.service_type.value,
                    "status": order.status.value,
                    "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "estimated_delivery": order.estimated_delivery.strftime("%Y-%m-%d %H:%M:%S") if order.estimated_delivery else None,
                    "actual_delivery": order.actual_delivery.strftime("%Y-%m-%d %H:%M:%S") if order.actual_delivery else None,
                    "cost": order.cost
                }
                order_dicts.append(order_dict)
            
            result = {
                "status": "success",
                "orders": order_dicts,
                "pagination": {
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "current_page": page_number,
                    "page_size": page_size,
                    "has_next": page_number < total_pages,
                    "has_prev": page_number > 1
                }
            }
            
        else:
            # 调用远程API
            params = {
                "page_size": page_size,
                "page_number": page_number
            }
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if status:
                params["status"] = status
            
            async with HTTPClient(config) as client:
                api_response = await client.get("/mcp/api/v1/orders", params=params)
                
                # 解析API响应格式
                if api_response.get("success"):
                    data = api_response.get("data", {})
                    # 转换为统一格式
                    result = {
                        "status": "success",
                        "orders": data.get("orders", []),
                        "pagination": {
                            "total_count": data.get("totalCount", 0),
                            "total_pages": data.get("totalPages", 0),
                            "current_page": data.get("currentPage", page_number),
                            "page_size": data.get("pageSize", page_size),
                            "has_next": data.get("hasNext", False),
                            "has_prev": data.get("hasPrev", False)
                        }
                    }
                else:
                    # API返回错误 - 处理两种错误格式
                    error_code = api_response.get("errorCode") or api_response.get("code", "API_ERROR")
                    error_message = api_response.get("errorMsg") or api_response.get("message", "API调用失败")
                    
                    result = {
                        "status": "error",
                        "error_code": error_code,
                        "message": error_message,
                        "orders": [],
                        "pagination": {
                            "total_count": 0,
                            "total_pages": 0,
                            "current_page": page_number,
                            "page_size": page_size,
                            "has_next": False,
                            "has_prev": False
                        }
                    }
        
        logger.info(f"订单列表查询完成，返回{len(result.get('orders', []))}条记录")
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"查询订单列表失败: {e}")
        error_result = {
            "status": "error",
            "error_code": "LIST_ORDERS_ERROR",
            "message": f"查询订单列表失败: {str(e)}",
            "orders": [],
            "pagination": {
                "total_count": 0,
                "total_pages": 0,
                "current_page": page_number,
                "page_size": page_size,
                "has_next": False,
                "has_prev": False
            }
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_order_detail(order_id: str, detail_level: str = "basic") -> str:
    """
    获取订单详细信息
    
    Args:
        order_id: 订单号
        detail_level: 详情级别(basic/full)
    
    Returns:
        包含订单详细信息的JSON字符串
    """
    try:
        if config.use_mock:
            # 使用模拟数据
            logger.info(f"使用模拟数据查询订单详情: {order_id}")
            orders = get_mock_orders()
            
            # 查找订单
            order = None
            for o in orders:
                if o.order_id == order_id:
                    order = o
                    break
            
            if not order:
                return json.dumps({
                    "status": "error",
                    "error_code": "ORDER_NOT_FOUND",
                    "message": f"订单 {order_id} 未找到"
                }, ensure_ascii=False, indent=2)
            
            # 构造返回数据
            result = {
                "status": "success",
                "order_info": {
                    "order_id": order.order_id,
                    "status": order.status.value,
                    "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "service_type": order.service_type.value,
                    "estimated_delivery": order.estimated_delivery.strftime("%Y-%m-%d %H:%M:%S") if order.estimated_delivery else None,
                    "actual_delivery": order.actual_delivery.strftime("%Y-%m-%d %H:%M:%S") if order.actual_delivery else None,
                    "cost": order.cost
                },
                "sender_info": asdict(order.sender),
                "receiver_info": asdict(order.receiver),
                "package_info": asdict(order.package)
            }
            
            # 如果是完整详情，添加物流追踪
            if detail_level == "full":
                # 模拟物流追踪历史
                tracking_history = [
                    {
                        "time": order.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "订单创建",
                        "location": order.sender.address,
                        "description": "订单已创建，等待取件"
                    }
                ]
                
                if order.status.value in ["已取件", "运输中", "派送中", "已签收"]:
                    tracking_history.append({
                        "time": (order.create_time + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "已取件",
                        "location": order.sender.address,
                        "description": "快递员已取件"
                    })
                
                if order.status.value in ["运输中", "派送中", "已签收"]:
                    tracking_history.append({
                        "time": (order.create_time + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "运输中",
                        "location": "中转站",
                        "description": "包裹正在运输途中"
                    })
                
                if order.status.value in ["派送中", "已签收"]:
                    tracking_history.append({
                        "time": (order.create_time + timedelta(hours=36)).strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "派送中",
                        "location": order.receiver.address,
                        "description": "包裹已到达目的地，正在派送"
                    })
                
                if order.status.value == "已签收":
                    tracking_history.append({
                        "time": order.actual_delivery.strftime("%Y-%m-%d %H:%M:%S") if order.actual_delivery else (order.create_time + timedelta(hours=42)).strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "已签收",
                        "location": order.receiver.address,
                        "description": f"包裹已由{order.receiver.name}签收"
                    })
                
                result["tracking_history"] = tracking_history
            
        else:
            # 调用远程API
            params = {"detail_level": detail_level}
            async with HTTPClient(config) as client:
                api_response = await client.get(f"/mcp/api/v1/orders/{order_id}", params=params)
                
                # 解析API响应格式
                if api_response.get("success"):
                    data = api_response.get("data", {})
                    # 转换为统一格式
                    result = {
                        "status": "success",
                        "order_info": data.get("orderInfo") or data.get("order_info"),
                        "sender_info": data.get("senderInfo") or data.get("sender_info"),
                        "receiver_info": data.get("receiverInfo") or data.get("receiver_info"),
                        "package_info": data.get("packageInfo") or data.get("package_info")
                    }
                    
                    # 如果是完整详情，添加物流追踪
                    if detail_level == "full" and (data.get("trackingHistory") or data.get("tracking_history")):
                        result["tracking_history"] = data.get("trackingHistory") or data.get("tracking_history")
                else:
                    # API返回错误 - 处理两种错误格式
                    error_code = api_response.get("errorCode") or api_response.get("code", "API_ERROR")
                    error_message = api_response.get("errorMsg") or api_response.get("message", "API调用失败")
                    
                    result = {
                        "status": "error",
                        "error_code": error_code,
                        "message": error_message
                    }
        
        if result.get("status") == "success":
            logger.info(f"订单详情查询成功: {order_id}")
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"查询订单详情失败: {e}")
        error_result = {
            "status": "error",
            "error_code": "GET_ORDER_ERROR",
            "message": f"查询订单详情失败: {str(e)}"
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


def main():
    """启动MCP服务器"""
    logger.info("启动寄件服务MCP Server...")
    
    # 打印所有配置信息
    logger.info("当前配置信息:")
    logger.info(f"  - API基础URL: {config.base_url}")
    logger.info(f"  - API Token: {config.token[:4]}***{config.token[-4:]}")  
    logger.info(f"  - 请求超时时间: {config.timeout}秒")
    logger.info(f"  - 使用Mock数据: {config.use_mock}")
    logger.info(f"  - 请求头: {json.dumps(config.headers, ensure_ascii=False, indent=2)}")
    
    # 运行服务器
    mcp.run()


if __name__ == "__main__":
    main() 
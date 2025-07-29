# 寄件服务MCP Server 配置指南

本文档详细说明如何配置寄件服务MCP Server以对接不同的寄件服务提供商API。

## 🔧 配置方式

### 1. 命令行参数配置（推荐）

直接通过命令行参数传递配置：

```bash
python src/guoguo_mcp/__init__.py \
  --api-url "https://api.sf-express.com" \
  --token "your_access_token" \
  --timeout 30 \
  --no-mock
```

**参数说明：**
- `--api-url`: API服务器地址
- `--token`: API访问令牌
- `--timeout`: 请求超时时间（秒）
- `--use-mock`: 启用模拟模式（开发测试用）
- `--no-mock`: 禁用模拟模式，使用真实API

### 2. 环境变量配置

通过环境变量设置配置：

```bash
export SHIPPING_API_BASE_URL="https://api.sf-express.com"
export SHIPPING_API_TOKEN="your_access_token"
export SHIPPING_API_TIMEOUT="30"
export SHIPPING_USE_MOCK="false"

python src/guoguo_mcp/__init__.py
```

### 3. Claude Desktop配置

在Claude Desktop的配置文件中设置：

```json
{
  "mcpServers": {
    "guoguo-shipping": {
      "command": "python",
      "args": [
        "/path/to/guoguo_mcp/src/guoguo_mcp/__init__.py",
        "--api-url", "https://api.sf-express.com",
        "--token", "sf_prod_token_12345",
        "--timeout", "30",
        "--no-mock"
      ],
      "env": {
        "PATH": "/path/to/venv/bin:/usr/bin:/bin"
      }
    }
  }
}
```

## 🌍 不同环境配置示例

### 开发环境（Mock模式）

```bash
# 使用模拟数据，无需真实API
python src/guoguo_mcp/__init__.py --use-mock
```

### 测试环境

```bash
# 使用测试API
python src/guoguo_mcp/__init__.py \
  --api-url "https://test-api.sf-express.com" \
  --token "test_token_abcd1234" \
  --no-mock
```

### 生产环境

```bash
# 使用生产API
python src/guoguo_mcp/__init__.py \
  --api-url "https://api.sf-express.com" \
  --token "prod_token_xyz789" \
  --timeout 60 \
  --no-mock
```

## 🚚 支持的寄件服务提供商

### 顺丰速运

```bash
python src/guoguo_mcp/__init__.py \
  --api-url "https://api.sf-express.com" \
  --token "sf_your_access_token" \
  --no-mock
```

### 圆通速递

```bash
python src/guoguo_mcp/__init__.py \
  --api-url "https://api.yto.net.cn" \
  --token "yto_your_access_token" \
  --no-mock
```

### 中通快递

```bash
python src/guoguo_mcp/__init__.py \
  --api-url "https://api.zto.com" \
  --token "zto_your_access_token" \
  --no-mock
```

### 申通快递

```bash
python src/guoguo_mcp/__init__.py \
  --api-url "https://api.sto.cn" \
  --token "sto_your_access_token" \
  --no-mock
```

## 📋 配置优先级

配置的优先级顺序（从高到低）：

1. **命令行参数** - 最高优先级
2. **环境变量** - 中等优先级  
3. **默认值** - 最低优先级

## 🔐 API访问令牌管理

### 安全建议

1. **不要在代码中硬编码访问令牌**
2. **使用环境变量或命令行参数传递**
3. **为不同环境使用不同的访问令牌**
4. **定期轮换访问令牌**

### 令牌格式示例

```bash
# 开发环境
dev_sf_token_20240101_abc123

# 测试环境  
test_sf_token_20240101_def456

# 生产环境
prod_sf_token_20240101_xyz789
```

## 🐛 故障排除

### 常见问题

#### 1. API访问令牌错误
```
错误: HTTP错误 401: Unauthorized
解决: 检查访问令牌是否正确，是否有访问权限
```

#### 2. 网络连接超时
```
错误: 请求失败: Read timeout
解决: 增加超时时间 --timeout 60
```

#### 3. API地址错误
```
错误: 请求失败: Name or service not known
解决: 检查API地址是否正确
```

### 调试模式

启用详细日志输出：

```bash
export PYTHONPATH=/path/to/guoguo_mcp
python -m logging --level DEBUG src/guoguo_mcp/__init__.py --use-mock
```

## 📖 API接口规范

### 地址簿查询 API

**端点**: `GET /api/v1/address-book`

**参数**:
- `search`: 搜索关键词（可选）

**响应**:
```json
{
  "status": "success",
  "total_count": 4,
  "addresses": [...]
}
```

### 创建订单 API

**端点**: `POST /api/v1/orders`

**请求体**:
```json
{
  "sender": {
    "name": "寄件人姓名",
    "phone": "13800138000",
    "address": "寄件人地址"
  },
  "receiver": {
    "name": "收件人姓名", 
    "phone": "13900139000",
    "address": "收件人地址"
  },
  "package": {
    "type": "物品类型",
    "weight": 1.5,
    "size": "20x15x10"
  },
  "service_type": "快速"
}
```

### 查询订单列表 API

**端点**: `GET /api/v1/orders`

**参数**:
- `page_size`: 每页数量
- `page_number`: 页码
- `start_date`: 开始日期
- `end_date`: 结束日期  
- `status`: 订单状态

### 查询订单详情 API

**端点**: `GET /api/v1/orders/{order_id}`

**参数**:
- `detail_level`: 详情级别（basic/full）

## 📞 技术支持

如果在配置过程中遇到问题，请：

1. 检查配置参数是否正确
2. 验证API密钥是否有效
3. 确认网络连接正常
4. 查看错误日志获取详细信息

更多技术支持，请参考README.md或提交Issue。 
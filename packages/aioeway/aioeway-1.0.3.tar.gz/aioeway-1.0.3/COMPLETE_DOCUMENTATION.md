# AIOEway 完整文档

一个基于异步编程的Python库，用于与设备进行MQTT通信，支持设备信息和运行数据的实时监控。

## 目录

1. [功能特性](#功能特性)
2. [安装依赖](#安装依赖)
3. [快速开始](#快速开始)
4. [新配置方式](#新配置方式)
5. [GET主题订阅功能](#get主题订阅功能)
6. [QoS功能说明](#qos功能说明)
7. [MQTT主题格式](#mqtt主题格式)
8. [API文档](#api文档)
9. [数据结构](#数据结构)
10. [高级用法](#高级用法)
11. [真实设备测试指南](#真实设备测试指南)
12. [故障排除](#故障排除)

---

## 功能特性

- 🔌 支持MQTT 3.1.1协议
- ⚡ 完全异步实现，高性能
- 📊 设备信息监控（每10分钟上报一次）
- 📈 设备运行数据监控（每分钟上报一次）
- 🔄 自动重连机制
- 📝 详细的日志记录
- 🎯 多设备同时监控
- 🛡️ 协程安全设计
- 🔧 异步上下文管理器支持
- 🔐 支持TLS加密连接
- 📡 支持QoS=1消息质量保证
- 🎯 支持GET主题订阅

## 安装依赖

```bash
pip install -r requirements.txt
```

或者直接安装：

```bash
pip install aiomqtt
```

## 快速开始

### 基本使用

```python
import asyncio
from device_mqtt_client import DeviceMQTTClient, DeviceInfo, DeviceData
from typing import List

async def on_device_info(info: DeviceInfo):
    print(f"设备信息更新: WiFi={info.wifi_ssid}, IP={info.ip}")

async def on_device_data(data_list: List[DeviceData]):
    for data in data_list:
        print(f"设备{data.sort}: 功率={data.gen_power}W, 温度={data.temperature}℃")

async def main():
    # 创建MQTT客户端（新配置方式）
    client = DeviceMQTTClient(
        device_model="INV001",        # 设备机型码
        device_sn="SN123456789",     # 设备SN
        username="testuser",         # 用户名
        password="processed_password",  # 已处理的密码
        broker_host="localhost",     # MQTT服务器地址
        broker_port=8883,            # MQTT服务器端口（TLS端口）
        keepalive=60,                # 心跳间隔
        use_tls=True                 # 使用TLS加密
    )
    
    # 使用异步上下文管理器
    async with client:
        # 开始监控
        await client.start_monitoring(
            device_id="INV001",
            device_sn="SN123456789",
            info_callback=on_device_info,
            data_callback=on_device_data
        )
        
        # 保持运行
        await asyncio.sleep(60)

# 运行异步程序
asyncio.run(main())
```

---

## 新配置方式

### 概述

AIOEway库已更新为新的配置方式，支持更安全和标准化的MQTT客户端配置。新的配置方式要求用户提供设备机型码、设备SN、用户名、已处理的密码等参数，并自动生成符合规范的客户端ID。

### 新配置参数

#### 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `device_model` | str | 设备机型码，用于标识设备型号 |
| `device_sn` | str | 设备序列号，设备的唯一标识符 |
| `username` | str | MQTT用户名，用于服务器认证 |
| `password` | str | 已处理的密码，直接用于MQTT认证 |
| `broker_host` | str | MQTT服务器地址（IP或域名） |

#### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `broker_port` | int | 1883 | MQTT服务器端口 |
| `keepalive` | int | 60 | 心跳间隔（秒） |
| `use_tls` | bool | True | 是否使用TLS加密连接 |

### 自动生成的配置

#### 客户端ID格式
```
client_id = "{device_model}/{device_sn}"
```

### 配置示例

#### 本地测试配置
```python
local_config = {
    "device_model": "INV001",
    "device_sn": "SN123456789",
    "username": "testuser",
    "password": "processed_password_123",  # 已处理的密码
    "broker_host": "localhost",
    "broker_port": 1883,
    "use_tls": False
}

client = DeviceMQTTClient(**local_config)
```

#### 生产环境配置
```python
production_config = {
    "device_model": "INV002",
    "device_sn": "SN987654321",
    "username": "produser",
    "password": "processed_prod_password",  # 已处理的密码
    "broker_host": "mqtt.example.com",
    "broker_port": 8883,
    "use_tls": True
}

client = DeviceMQTTClient(**production_config)
```

#### 云服务配置示例

**阿里云IoT**
```python
aliyun_config = {
    "device_model": "INV003",
    "device_sn": "ALY123456789",
    "username": "aliyun_device_user",
    "password": "processed_aliyun_password",  # 已处理的密码
    "broker_host": "iot-as-mqtt.cn-shanghai.aliyuncs.com",
    "broker_port": 443,
    "use_tls": True
}
```

**腾讯云IoT**
```python
tencent_config = {
    "device_model": "INV004",
    "device_sn": "TX123456789",
    "username": "tencent_device_user",
    "password": "processed_tencent_password",  # 已处理的密码
    "broker_host": "iotcloud-mqtt.gz.tencentdevices.com",
    "broker_port": 8883,
    "use_tls": True
}
```

### TLS配置说明

#### 启用TLS
当 `use_tls=True` 时，客户端将使用SSL/TLS加密连接：
- 自动创建SSL上下文
- 使用默认的证书验证
- 适用于生产环境

#### 禁用TLS
当 `use_tls=False` 时，客户端将使用明文连接：
- 不进行加密
- 适用于本地测试环境
- 不推荐在生产环境使用

---

## GET主题订阅功能

### 概述

AIOEway库现在支持订阅GET主题，用于接收设备信息和数据的获取响应。新增的GET主题格式为：

- `{device_id}/{device_sn}/info/get` - 设备信息获取响应
- `{device_id}/{device_sn}/data/get` - 设备数据获取响应

### 新增功能

#### 新增订阅方法

**`subscribe_device_info_get()`**
```python
async def subscribe_device_info_get(self, device_id: str, device_sn: str, 
                                  callback: Callable[[DeviceInfo], Awaitable[None]]):
    """异步订阅设备信息获取主题"""
```

**`subscribe_device_data_get()`**
```python
async def subscribe_device_data_get(self, device_id: str, device_sn: str, 
                                  callback: Callable[[List[DeviceData]], Awaitable[None]]):
    """异步订阅设备数据获取主题"""
```

#### 增强的监控功能

`start_monitoring()` 方法现在支持GET主题回调：

```python
async def start_monitoring(self, device_id: str, device_sn: str,
                         info_callback: Optional[Callable[[DeviceInfo], Awaitable[None]]] = None,
                         data_callback: Optional[Callable[[List[DeviceData]], Awaitable[None]]] = None,
                         info_get_callback: Optional[Callable[[DeviceInfo], Awaitable[None]]] = None,
                         data_get_callback: Optional[Callable[[List[DeviceData]], Awaitable[None]]] = None,
                         data_interval: int = 60):
```

### GET主题使用示例

#### 基本用法

```python
import asyncio
from device_mqtt_client import DeviceMQTTClient, DeviceInfo, DeviceData
from typing import List

async def on_device_info_get(device_info: DeviceInfo):
    print(f"[INFO GET] 设备: {device_info.device_id}/{device_info.device_sn}")
    print(f"[INFO GET] 状态: {device_info.device_status}")

async def on_device_data_get(device_data_list: List[DeviceData]):
    print(f"[DATA GET] 收到 {len(device_data_list)} 条数据")
    for data in device_data_list:
        print(f"[DATA GET] {data.data_type}: {data.data_value} {data.unit}")

async def main():
    client = DeviceMQTTClient(
        device_model="INV001",
        device_sn="SN123456789",
        username="test_user",
        password="processed_password",
        broker_host="localhost",
        broker_port=8883,
        use_tls=True
    )
    
    try:
        if await client.connect():
            # 订阅GET主题
            await client.subscribe_device_info_get(
                "INV001", "SN123456789", on_device_info_get
            )
            await client.subscribe_device_data_get(
                "INV001", "SN123456789", on_device_data_get
            )
            
            # 等待消息
            await asyncio.sleep(60)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 使用增强的监控功能

```python
async def comprehensive_monitoring():
    client = DeviceMQTTClient(
        device_model="INV001",
        device_sn="SN123456789",
        username="test_user",
        password="processed_password",
        broker_host="localhost",
        broker_port=8883,
        use_tls=True
    )
    
    # 定义所有回调函数
    async def on_info_post(device_info: DeviceInfo):
        print(f"[POST] 设备信息: {device_info.device_status}")
    
    async def on_data_post(device_data_list: List[DeviceData]):
        print(f"[POST] 设备数据: {len(device_data_list)} 条")
    
    async def on_info_get(device_info: DeviceInfo):
        print(f"[GET] 设备信息响应: {device_info.device_status}")
    
    async def on_data_get(device_data_list: List[DeviceData]):
        print(f"[GET] 设备数据响应: {len(device_data_list)} 条")
    
    try:
        if await client.connect():
            # 开始全面监控（包括POST和GET主题）
            await client.start_monitoring(
                device_id="INV001",
                device_sn="SN123456789",
                info_callback=on_info_post,
                data_callback=on_data_post,
                info_get_callback=on_info_get,
                data_get_callback=on_data_get
            )
            
            # 持续监控
            await asyncio.sleep(300)  # 5分钟
    finally:
        await client.disconnect()
```

### 主题对比

| 主题类型 | 主题格式 | 用途 | 回调参数 |
|---------|---------|------|----------|
| POST | `{device_id}/{device_sn}/info/post` | 设备主动推送信息 | `DeviceInfo` |
| POST | `{device_id}/{device_sn}/data/post` | 设备主动推送数据 | `List[DeviceData]` |
| GET | `{device_id}/{device_sn}/info/get` | 设备信息获取响应 | `DeviceInfo` |
| GET | `{device_id}/{device_sn}/data/get` | 设备数据获取响应 | `List[DeviceData]` |

---

## QoS功能说明

### 概述

AIOEway库现在支持MQTT订阅时设置QoS（Quality of Service）级别。所有订阅操作默认使用**QoS=1**，确保消息至少被传递一次。

### QoS级别说明

#### QoS 0 - 最多一次传递
- 消息发送后不确认
- 可能丢失消息
- 性能最高，适用于可容忍消息丢失的场景

#### QoS 1 - 至少一次传递（当前使用）
- 消息发送后需要确认
- 保证消息至少被传递一次
- 可能重复接收消息
- 平衡了可靠性和性能

#### QoS 2 - 恰好一次传递
- 最高可靠性，保证消息恰好被传递一次
- 性能开销最大
- 适用于关键业务场景

### 当前实现

#### 默认QoS设置

所有MQTT订阅操作都使用**QoS=1**：

```python
# 所有订阅方法都使用QoS=1
await self.client.subscribe(topic, qos=1)
```

#### 支持的订阅方法

1. **subscribe_device_info()** - 订阅设备信息（POST）
2. **subscribe_device_data()** - 订阅设备数据（POST）
3. **subscribe_device_info_get()** - 订阅设备信息（GET）
4. **subscribe_device_data_get()** - 订阅设备数据（GET）
5. **start_monitoring()** - 统一监控（包含所有上述订阅）

#### 主题格式

所有主题都使用QoS=1进行订阅：

- `{device_id}/{device_sn}/info/post` (QoS=1)
- `{device_id}/{device_sn}/data/post` (QoS=1)
- `{device_id}/{device_sn}/info/get` (QoS=1)
- `{device_id}/{device_sn}/data/get` (QoS=1)

### 日志输出

启用QoS=1后，订阅日志会包含QoS信息：

```
2025-06-23 14:35:07,123 - device_mqtt_client - INFO - 已订阅设备信息主题: INV001/SN123456789/info/post (QoS=1)
2025-06-23 14:35:07,124 - device_mqtt_client - INFO - 已订阅设备数据主题: INV001/SN123456789/data/post (QoS=1)
2025-06-23 14:35:07,125 - device_mqtt_client - INFO - 已订阅设备信息获取主题: INV001/SN123456789/info/get (QoS=1)
2025-06-23 14:35:07,126 - device_mqtt_client - INFO - 已订阅设备数据获取主题: INV001/SN123456789/data/get (QoS=1)
```

### 性能考虑

#### QoS=1的优势

1. **可靠性**: 保证消息至少被传递一次
2. **适中开销**: 比QoS=0稍高，但比QoS=2低得多
3. **适用性**: 适合大多数IoT应用场景

#### 潜在影响

1. **网络流量**: 略微增加（确认消息）
2. **内存使用**: 略微增加（消息缓存）
3. **延迟**: 可能略微增加（等待确认）

### 向后兼容性

- ✅ **完全向后兼容**
- ✅ **不需要修改现有代码**
- ✅ **自动应用QoS=1**
- ✅ **保持所有现有功能**

---

## MQTT主题格式

### 设备信息主题
- **主题**: `{ID}/{SN}/info/post`
- **频率**: 按需上报
- **数据格式**:
```json
{
  "netFirmVer": 1.0,
  "appFirmVer": 1.0,
  "wifiSsid": "HJDZ-EW-WIFI",
  "ip": "192.168.1.100",
  "wifiIsNormal": 0,
  "isLock": 1,
  "board": [
    {
      "name": "net",
      "chip": "esp32",
      "hdVer": 1.0
    },
    {
      "name": "app",
      "chip": "esp32",
      "hdVer": 1.0
    }
  ]
}
```

### 设备运行数据主题
- **主题**: `{ID}/{SN}/data/post`
- **频率**: 每分钟上报一次
- **数据格式**:
```json
[
  {
    "sort": 1,
    "inputVoltage": 220.2,
    "InputCurrent": 10.2,
    "gridVoltage": 220.2,
    "gridFreq": 50.0,
    "genPower": 20.2,
    "genPowerToDay": 10,
    "genPowerTotal": 10,
    "temperature": 26.5,
    "errCode": 0,
    "duration": 0
  }
]
```

### GET主题消息格式

#### 设备信息GET响应消息示例
```json
{
    "device_id": "INV001",
    "device_sn": "SN123456789",
    "device_model": "INV001",
    "firmware_version": "1.0.0",
    "hardware_version": "1.0",
    "device_status": "online",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 设备数据GET响应消息示例
```json
[
    {
        "device_id": "INV001",
        "device_sn": "SN123456789",
        "data_type": "power",
        "data_value": "1500",
        "unit": "W",
        "timestamp": "2024-01-01T12:00:00Z"
    },
    {
        "device_id": "INV001",
        "device_sn": "SN123456789",
        "data_type": "temperature",
        "data_value": "45.5",
        "unit": "°C",
        "timestamp": "2024-01-01T12:00:00Z"
    }
]
```

---

## API文档

### DeviceMQTTClient类

#### 初始化
```python
DeviceMQTTClient(
    device_model: str,           # 设备机型码
    device_sn: str,             # 设备序列号
    username: str,              # MQTT用户名
    password: str,              # 已处理的密码
    broker_host: str,           # MQTT服务器地址
    broker_port: int = 1883,    # MQTT服务器端口
    keepalive: int = 60,        # 心跳间隔
    use_tls: bool = True        # 是否使用TLS
)
```

#### 主要方法

- `connect() -> bool`: 连接到MQTT代理
- `disconnect()`: 断开连接
- `start_monitoring()`: 开始监控设备
- `stop_monitoring()`: 停止监控设备
- `subscribe_device_info()`: 订阅设备信息（POST）
- `subscribe_device_data()`: 订阅设备数据（POST）
- `subscribe_device_info_get()`: 订阅设备信息（GET）
- `subscribe_device_data_get()`: 订阅设备数据（GET）
- `get_monitored_devices()`: 获取监控设备列表
- `is_device_monitored()`: 检查设备监控状态

---

## 数据结构

### DeviceInfo
设备信息数据结构，包含：
- `net_firm_ver`: 网络模块固件版本
- `app_firm_ver`: 主控模块固件版本
- `wifi_ssid`: WiFi名称
- `ip`: IP地址
- `wifi_is_normal`: WiFi状态（0=正常，1=异常）
- `is_lock`: 锁定状态（0=锁定，1=未锁定）
- `board`: 板卡信息列表

### DeviceData
设备运行数据结构，包含：
- `sort`: 序号
- `input_voltage`: 输入电压(V)
- `input_current`: 输入电流(A)
- `grid_voltage`: 电网电压(V)
- `grid_freq`: 电网频率(Hz)
- `gen_power`: 发电功率(W)
- `gen_power_today`: 今日发电量(Wh)
- `gen_power_total`: 总发电量(kWh)
- `temperature`: 温度(℃)
- `err_code`: 错误码
- `duration`: 工作时长(s)

---

## 高级用法

### 多设备监控

```python
async def multi_device_example():
    client = DeviceMQTTClient(
        device_model="INV001",
        device_sn="SN123456789",
        username="testuser",
        password="processed_password",  # 已处理的密码
        broker_host="localhost",
        broker_port=1883,
        use_tls=False
    )
    
    async with client:
        # 监控多个设备
        device_list = [
            ("device_001", "SN001"),
            ("device_002", "SN002"),
            ("device_003", "SN003")
        ]
        
        for device_id, device_sn in device_list:
            await client.subscribe_device_data(device_id, device_sn, on_device_data)
            await client.subscribe_device_info(device_id, device_sn, on_device_info)
            print(f"已订阅设备 {device_id}/{device_sn}")
        
        # 保持监控
        await asyncio.sleep(300)
```

---

## 真实设备测试指南

### 📋 测试脚本说明

#### 1. `test_real_device.py` - 完整功能测试
- 🔧 交互式配置MQTT连接参数
- 📊 详细的数据验证和分析
- 📈 完整的统计信息和历史记录
- ⚠️ 数据异常检测和警告

#### 2. `quick_device_test.py` - 快速测试
- ⚡ 预设常用MQTT配置
- 🎯 简化的数据显示
- 📱 支持命令行和交互模式
- 🚀 快速验证连接和数据接收

### 🚀 快速开始

#### 方式一：快速测试（推荐新手）

```bash
# 交互模式
python3 quick_device_test.py

# 命令行模式
python3 quick_device_test.py "本地测试" "your_device_id" "your_device_sn" 60
```

#### 方式二：完整测试（推荐深度测试）

```bash
python3 test_real_device.py
```

### 📡 MQTT代理设置

#### 本地测试环境

**使用Docker（推荐）**
```bash
# 启动Mosquitto MQTT代理
docker run -it -p 1883:1883 -p 9001:9001 eclipse-mosquitto
```

**使用Homebrew（macOS）**
```bash
# 安装
brew install mosquitto

# 启动
mosquitto -p 1883 -v
```

**使用apt（Ubuntu/Debian）**
```bash
# 安装
sudo apt update
sudo apt install mosquitto mosquitto-clients

# 启动
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

#### 云端MQTT服务

**阿里云IoT平台**
- 地址：`iot-as-mqtt.cn-shanghai.aliyuncs.com`
- 端口：1883
- 需要设备证书认证

**腾讯云IoT平台**
- 地址：`iotcloud-mqtt.gz.tencentdevices.com`
- 端口：1883
- 需要设备密钥认证

**免费公共测试服务器**
- 地址：`test.mosquitto.org`
- 端口：1883（无认证）/ 8883（SSL）
- ⚠️ 仅用于测试，不要发送敏感数据

### 🔧 设备配置

#### 获取设备信息

1. **设备ID（Device ID）**
   - 通常是设备的唯一标识符
   - 格式示例：`device001`, `INV_001`, `solar_panel_01`

2. **设备SN（Serial Number）**
   - 设备序列号
   - 格式示例：`SN12345678`, `ABC123DEF456`

### 📊 数据验证

#### 设备信息验证
- ✅ WiFi连接状态
- ✅ IP地址格式
- ✅ 固件版本号
- ✅ 设备锁定状态

#### 设备数据验证
- ⚡ **电压范围**：180-250V（输入），200-250V（电网）
- 📈 **频率范围**：49-51Hz
- 🌡️ **温度范围**：-10°C到80°C
- 💡 **功率检查**：非负值
- ❌ **错误码**：0为正常

### 🔍 测试场景

#### 1. 连接测试
```bash
# 测试MQTT连接是否正常
python3 quick_device_test.py "本地测试" "test_device" "test_sn" 10
```

#### 2. 数据接收测试
```bash
# 长时间监控数据接收
python3 test_real_device.py
# 输入真实设备ID和SN，运行60秒
```

#### 3. 数据准确性测试
```bash
# 对比设备实际状态和接收到的数据
python3 test_real_device.py
# 检查温度、功率、电压等参数是否与实际一致
```

#### 4. 异常情况测试
- 🔌 断开网络连接
- 🔄 重启MQTT代理
- ⚠️ 发送异常数据

### 📈 测试结果分析

#### 正常情况指标
- 📡 **连接成功率**：100%
- 📊 **数据接收频率**：按设备配置（通常1分钟/次）
- 🔍 **数据完整性**：所有字段都有值
- ✅ **数据合理性**：通过验证检查

#### 异常情况处理
- ❌ **连接失败**：检查MQTT代理地址和端口
- 📭 **无数据接收**：检查设备ID/SN和主题格式
- ⚠️ **数据异常**：查看验证警告信息
- 🔄 **连接中断**：观察自动重连机制

---

## 故障排除

### 常见问题

#### 1. 连接失败
```
❌ 连接失败: [Errno 61] Connection refused
```
**解决方案：**
- 检查MQTT代理是否运行
- 确认地址和端口正确
- 验证网络连接

#### 2. 认证失败
```
❌ 连接失败: Connection Refused: not authorised
```
**解决方案：**
- 检查用户名和密码
- 确认设备权限配置
- 验证密钥和加密算法

#### 3. 无数据接收
```
📊 设备数据: 0次
```
**解决方案：**
- 确认设备ID和SN正确
- 检查设备是否在线并发送数据
- 验证MQTT主题格式
- 检查QoS设置

#### 4. 数据格式错误
```
❌ 处理消息时出错: KeyError
```
**解决方案：**
- 检查设备发送的JSON格式
- 确认字段名称匹配
- 验证数据类型

#### 5. TLS连接问题
```
❌ SSL错误: certificate verify failed
```
**解决方案：**
- 检查证书配置
- 确认服务器支持TLS
- 验证端口号（通常8883用于TLS）

### QoS相关问题

**Q: 为什么选择QoS=1而不是QoS=0或QoS=2？**

A: QoS=1提供了可靠性和性能的最佳平衡：
- 比QoS=0更可靠（不会丢失消息）
- 比QoS=2更高效（更少的网络开销）
- 适合IoT设备监控场景

**Q: 如何验证QoS设置是否生效？**

A: 查看订阅日志，应该包含"(QoS=1)"标记：
```
已订阅设备信息主题: INV001/SN123456789/info/post (QoS=1)
```

### 调试技巧

#### 1. 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. 使用MQTT客户端工具
```bash
# 订阅主题测试
mosquitto_sub -h localhost -t "device_001/SN123456/+/+" -v

# 发布测试消息
mosquitto_pub -h localhost -t "device_001/SN123456/info/post" -m '{"test": "data"}'
```

#### 3. 网络连接测试
```bash
# 测试MQTT端口连通性
telnet localhost 1883

# 测试TLS端口连通性
openssl s_client -connect localhost:8883
```

### 测试文件说明

#### 可用的测试脚本

1. **`test_qos_unit.py`** - QoS单元测试
   ```bash
   python3 test_qos_unit.py
   ```

2. **`test_qos.py`** - QoS集成测试
   ```bash
   python3 test_qos.py
   ```

3. **`test_get_topics.py`** - GET主题测试
   ```bash
   python3 test_get_topics.py
   ```

4. **`test_new_config.py`** - 新配置测试
   ```bash
   python3 test_new_config.py
   ```

5. **`config_new_example.py`** - 配置示例
   ```bash
   python3 config_new_example.py
   ```

6. **`example.py`** - 完整使用示例
   ```bash
   python3 example.py
   ```

### 性能优化建议

1. **连接池管理**
   - 复用MQTT连接
   - 避免频繁连接/断开

2. **消息处理优化**
   - 使用异步处理
   - 避免阻塞操作

3. **内存管理**
   - 及时清理回调函数
   - 监控内存使用情况

4. **网络优化**
   - 合理设置keepalive间隔
   - 使用合适的QoS级别

---

## 更新日志

### v1.3.0 (2025-06-23)
- ✅ 新增QoS=1支持
- ✅ 更新所有订阅方法
- ✅ 增强日志输出
- ✅ 添加QoS单元测试

### v1.2.0 (2025-06-23)
- ✅ 新增GET主题订阅功能
- ✅ 增强start_monitoring方法
- ✅ 添加GET主题测试
- ✅ 完善消息处理逻辑

### v1.1.0 (2025-06-23)
- ✅ 实现新配置方式
- ✅ 支持TLS加密连接
- ✅ 自动生成客户端ID和加密密码
- ✅ 添加配置示例和测试

### v1.0.0 (初始版本)
- ✅ 基础MQTT通信功能
- ✅ 设备信息和数据监控
- ✅ 异步编程支持
- ✅ 多设备监控

---

## 快速命令参考

```bash
# 安装依赖
pip install -r requirements.txt

# 运行基本示例
python3 example.py

# 运行QoS测试
python3 test_qos_unit.py

# 运行GET主题测试
python3 test_get_topics.py

# 运行新配置测试
python3 test_new_config.py

# 查看配置示例
python3 config_new_example.py

# 快速设备测试
python3 quick_device_test.py

# 完整设备测试
python3 test_real_device.py
```

---

**注意**: 本文档整合了AIOEway库的所有功能说明，包括新配置方式、GET主题订阅、QoS功能和测试指南。所有功能都向后兼容，无需修改现有代码即可享受新特性。
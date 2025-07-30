# AIOEway - 异步MQTT设备交互库

一个基于Python异步编程的MQTT设备通信库，用于与IoT设备进行高效的双向通信。

## 特性

- 🚀 **异步编程**: 基于asyncio，支持高并发设备连接
- 🔒 **安全连接**: 支持TLS/SSL加密连接
- 📊 **数据结构化**: 内置设备信息和运行数据的结构化处理
- 🔄 **双向通信**: 支持设备信息查询和实时数据监控
- 📝 **完整日志**: 详细的连接和通信日志记录
- 🛠️ **易于使用**: 简洁的API设计，快速上手

## 安装

```bash
pip install aioeway
```

## 快速开始

### 基本使用

```python
import asyncio
from device_mqtt_client import DeviceMQTTClient

async def on_device_info(device_info):
    print(f"设备信息: {device_info}")

async def on_device_data(device_data_list):
    for data in device_data_list:
        print(f"设备数据: 功率={data.gen_power}W, 温度={data.temperature}°C")

async def main():
    # 创建客户端
    client = DeviceMQTTClient(
        device_model="MODEL001",
        device_sn="SN123456",
        username="your_username",
        password="your_password",
        broker_host="mqtt.example.com",
        broker_port=1883,
        use_tls=True
    )
    
    try:
        # 连接到MQTT代理
        if await client.connect():
            print("连接成功！")
            
            # 开始监控设备
            await client.start_monitoring(
                device_id="productCode",
                device_sn="deviceNum",
                info_callback=on_device_info,
                data_callback=on_device_data
            )
            
            # 保持连接
            await asyncio.sleep(60)
            
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 同步请求设备信息

```python
async def get_device_info():
    client = DeviceMQTTClient(...)
    
    if await client.connect():
        # 同步获取设备信息
        device_info = await client.request_device_info_and_wait(
            device_id="productCode",
            device_sn="deviceNum",
            timeout=10.0
        )
        
        if device_info:
            print(f"设备IP: {device_info.ip}")
            print(f"WiFi: {device_info.wifi_ssid}")
            print(f"固件版本: {device_info.app_firm_ver}")
        
        await client.disconnect()
```

## 数据结构

### 设备信息 (DeviceInfo)

```python
@dataclass
class DeviceInfo:
    net_firm_ver: float      # 网络模块固件版本
    app_firm_ver: float      # 主控模块固件版本
    wifi_ssid: str           # WiFi名称
    ip: str                  # IP地址
    wifi_is_normal: int      # WiFi是否可用（0：是 1：否）
    is_lock: int             # 是否锁定（0：是 1：否）
    board: List[Dict]        # 板卡信息
```

### 设备运行数据 (DeviceData)

```python
@dataclass
class DeviceData:
    sort: int                # 序号
    input_voltage: float     # 输入电压(V)
    input_current: float     # 输入电流(A)
    grid_voltage: float      # 电网电压(V)
    grid_freq: float         # 电网频率(Hz)
    gen_power: float         # 发电功率(W)
    gen_power_today: int     # 今日发电量(Wh)
    gen_power_total: int     # 总发电量(kWh)
    temperature: float       # 温度(℃)
    err_code: int            # 错误码
    duration: int            # 工作时长（s）
```

## MQTT主题格式

- **设备信息推送**: `{device_id}/{device_sn}/info/post`
- **设备数据推送**: `{device_id}/{device_sn}/data/post`
- **设备信息获取**: `{device_id}/{device_sn}/info/get`
- **设备数据获取**: `{device_id}/{device_sn}/data/get`
- **信息请求**: `{device_id}/{device_sn}/info/request`
- **数据请求**: `{device_id}/{device_sn}/data/request`

## API 参考

### DeviceMQTTClient

#### 初始化参数

- `device_model`: 设备机型码
- `device_sn`: 设备序列号
- `username`: MQTT用户名
- `password`: MQTT密码
- `broker_host`: MQTT代理服务器地址
- `broker_port`: MQTT代理服务器端口（默认1883）
- `keepalive`: 心跳间隔秒数（默认60）
- `use_tls`: 是否使用TLS加密（默认True）

#### 主要方法

- `connect()`: 连接到MQTT代理
- `disconnect()`: 断开连接
- `subscribe_device_info()`: 订阅设备信息
- `subscribe_device_data()`: 订阅设备数据
- `request_device_info_and_wait()`: 同步请求设备信息
- `request_device_data_and_wait()`: 同步请求设备数据
- `start_monitoring()`: 开始监控设备
- `stop_monitoring()`: 停止监控设备

## 要求

- Python 3.7+
- aiomqtt >= 2.0.0

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持异步MQTT通信
- 支持TLS加密连接
- 完整的设备信息和数据结构
- 同步和异步API支持

### v1.0.1
- 修改包格式错误

### v1.0.2
- 断线重连
- 防止多个监听任务冲突

### v1.0.3
- 修复aiomqtt 2.0+版本兼容性问题
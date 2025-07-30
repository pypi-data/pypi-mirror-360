#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOEway 完整示例集合
整合了所有配置方式、使用场景和功能演示的完整示例
"""

import asyncio
import logging
from device_mqtt_client import DeviceMQTTClient, DeviceInfo, DeviceData
from typing import List

# =============================================================================
# 配置部分
# =============================================================================

# 日志配置
LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "filename": "aioeway_examples.log",  # 日志文件（可选）
}

# MQTT代理配置
MQTT_CONFIG = {
    "broker_host": "localhost",  # MQTT代理地址
    "broker_port": 1883,         # MQTT代理端口
    "username": None,            # 用户名（可选）
    "password": None,            # 密码（可选）
    "client_id": "aioeway_examples",  # 客户端ID
    "keepalive": 60,             # 心跳间隔（秒）
    "clean_session": True,       # 清理会话
}

# 设备配置
DEVICE_CONFIG = {
    "device_ids": ["device_001", "device_002", "device_003"],  # 设备ID列表
    "monitor_all_info": True,    # 监控所有设备信息
    "data_interval": 60,         # 数据监控间隔（秒）
    "info_interval": 600,        # 信息监控间隔（秒）
}

# 告警配置
ALERT_CONFIG = {
    "temperature_threshold": 80.0,     # 温度告警阈值（℃）
    "power_threshold": 1000.0,         # 功率告警阈值（W）
    "voltage_min": 200.0,              # 最小电压（V）
    "voltage_max": 240.0,              # 最大电压（V）
    "humidity_max": 90.0,              # 最大湿度（%）
    "enable_email_alert": False,       # 启用邮件告警
    "enable_webhook_alert": False,     # 启用Webhook告警
    "alert_cooldown": 300,             # 告警冷却时间（秒）
}

# =============================================================================
# 新配置方式示例
# =============================================================================

# 示例1：本地测试配置（无TLS）
LOCAL_CONFIG = {
    "device_model": "INV001",           # 设备机型码
    "device_sn": "SN123456789",         # 设备SN
    "username": "testuser",             # 用户名
    "password": "processed_password_123",  # 已处理的密码
    "broker_host": "localhost",         # MQTT服务器地址
    "broker_port": 1883,                # MQTT服务器端口（标准端口）
    "keepalive": 60,                    # 心跳间隔（秒）
    "use_tls": False                    # 不使用TLS加密
}

# 示例2：生产环境配置（使用TLS）
PRODUCTION_CONFIG = {
    "device_model": "INV002",           # 设备机型码
    "device_sn": "SN987654321",         # 设备SN
    "username": "production_user",      # 用户名
    "password": "processed_prod_password",  # 已处理的密码
    "broker_host": "mqtt.example.com",  # MQTT服务器地址
    "broker_port": 8883,                # MQTT服务器端口（TLS端口）
    "keepalive": 120,                   # 心跳间隔（秒）
    "use_tls": True                     # 使用TLS加密
}

# 示例3：阿里云IoT配置
ALIYUN_IOT_CONFIG = {
    "device_model": "INV003",                           # 设备机型码
    "device_sn": "ALY123456789",                       # 设备SN
    "username": "aliyun_device_user",                  # 用户名
    "password": "processed_aliyun_password",           # 已处理的密码
    "broker_host": "iot-as-mqtt.cn-shanghai.aliyuncs.com",  # 阿里云IoT MQTT地址
    "broker_port": 443,                                # 阿里云IoT端口
    "keepalive": 300,                                  # 心跳间隔（秒）
    "use_tls": True                                    # 使用TLS加密
}

# 示例4：腾讯云IoT配置
TENCENT_IOT_CONFIG = {
    "device_model": "INV004",                          # 设备机型码
    "device_sn": "TX123456789",                        # 设备SN
    "username": "tencent_device_user",                 # 用户名
    "password": "processed_tencent_password",          # 已处理的密码
    "broker_host": "iotcloud-mqtt.gz.tencentdevices.com",  # 腾讯云IoT MQTT地址
    "broker_port": 8883,                               # 腾讯云IoT端口
    "keepalive": 240,                                  # 心跳间隔（秒）
    "use_tls": True                                    # 使用TLS加密
}

# 示例5：AWS IoT配置
AWS_IOT_CONFIG = {
    "device_model": "INV005",                          # 设备机型码
    "device_sn": "AWS123456789",                       # 设备SN
    "username": "aws_device_user",                     # 用户名
    "password": "processed_aws_password",              # 已处理的密码
    "broker_host": "your-endpoint.iot.us-east-1.amazonaws.com",  # AWS IoT端点
    "broker_port": 8883,                               # AWS IoT端口
    "keepalive": 300,                                  # 心跳间隔（秒）
    "use_tls": True                                    # 使用TLS加密
}

# =============================================================================
# 工具函数
# =============================================================================

def get_config_by_environment(env: str = "local"):
    """根据环境获取配置"""
    configs = {
        "local": LOCAL_CONFIG,
        "production": PRODUCTION_CONFIG,
        "aliyun": ALIYUN_IOT_CONFIG,
        "tencent": TENCENT_IOT_CONFIG,
        "aws": AWS_IOT_CONFIG
    }
    
    return configs.get(env, LOCAL_CONFIG)

def create_custom_config(device_model: str, device_sn: str, username: str,
                        password: str, broker_host: str,
                        broker_port: int = 8883, keepalive: int = 60,
                        use_tls: bool = True):
    """创建自定义配置"""
    return {
        "device_model": device_model,
        "device_sn": device_sn,
        "username": username,
        "password": password,
        "broker_host": broker_host,
        "broker_port": broker_port,
        "keepalive": keepalive,
        "use_tls": use_tls
    }

def create_configured_client(config: dict = None):
    """创建配置好的异步MQTT客户端"""
    if config is None:
        config = LOCAL_CONFIG
    
    # 配置日志
    logging.basicConfig(**LOGGING_CONFIG)
    
    # 创建客户端
    if "device_model" in config:
        # 新配置方式
        client = DeviceMQTTClient(**config)
    else:
        # 传统配置方式
        client = DeviceMQTTClient(
            broker_host=config.get("broker_host", "localhost"),
            broker_port=config.get("broker_port", 1883),
            username=config.get("username"),
            password=config.get("password"),
            client_id=config.get("client_id", "aioeway_client")
        )
    
    return client

# =============================================================================
# 回调函数
# =============================================================================

async def validate_device_info(device_info: DeviceInfo):
    """异步验证设备信息"""
    if not device_info.device_id:
        print("[WARNING] 设备ID为空")
    
    if not device_info.device_name:
        print("[WARNING] 设备名称为空")

async def log_device_info(device_info: DeviceInfo):
    """异步记录设备信息"""
    print(f"[LOG] 记录设备信息: {device_info.device_id}")

async def log_device_data(device_data: DeviceData):
    """异步记录设备数据"""
    print(f"[LOG] 记录设备数据: {device_data.device_id}")

async def check_alerts(data: DeviceData):
    """异步检查告警条件"""
    alerts = []
    
    # 温度告警
    if hasattr(data, 'temperature') and data.temperature > ALERT_CONFIG["temperature_threshold"]:
        alerts.append(f"高温告警: {data.temperature}°C")
    
    # 功率告警
    if hasattr(data, 'power') and data.power > ALERT_CONFIG["power_threshold"]:
        alerts.append(f"高功率告警: {data.power}W")
    
    # 电压告警
    if hasattr(data, 'voltage') and (data.voltage < ALERT_CONFIG["voltage_min"] or 
        data.voltage > ALERT_CONFIG["voltage_max"]):
        alerts.append(f"电压异常: {data.voltage}V")
    
    # 湿度告警
    if hasattr(data, 'humidity') and data.humidity > ALERT_CONFIG["humidity_max"]:
        alerts.append(f"湿度过高: {data.humidity}%")
    
    # 异步处理告警
    for alert in alerts:
        print(f"[ALERT] 设备 {data.device_id}: {alert}")
        
        # 异步发送告警
        if ALERT_CONFIG["enable_email_alert"]:
            await send_email_alert(alert)
        
        if ALERT_CONFIG["enable_webhook_alert"]:
            await send_webhook_alert(alert)

async def send_email_alert(message: str):
    """异步发送邮件告警"""
    print(f"[EMAIL] 异步发送告警邮件: {message}")
    await asyncio.sleep(0.1)  # 模拟异步操作

async def send_webhook_alert(message: str):
    """异步发送Webhook告警"""
    print(f"[WEBHOOK] 异步发送Webhook告警: {message}")
    await asyncio.sleep(0.1)  # 模拟异步操作

# =============================================================================
# 基础示例
# =============================================================================

async def basic_example():
    """基本使用示例"""
    print("\n=== 1. 基本使用示例 ===")
    
    # 异步设备信息回调
    async def on_device_info(device_info: DeviceInfo):
        print(f"设备信息: 设备ID={device_info.device_id}, 状态={device_info.device_status}")
    
    # 异步设备数据回调
    async def on_device_data(device_data_list: List[DeviceData]):
        for data in device_data_list:
            print(f"设备数据: {data.data_type}={data.data_value} {data.unit}")
    
    try:
        # 使用异步上下文管理器
        async with DeviceMQTTClient(
            broker_host="localhost",
            broker_port=1883,
            client_id="basic_example_client"
        ) as client:
            
            # 开始监控（包含回调函数）
            await client.start_monitoring(
                device_id="DEV001",
                device_sn="SN123456",
                info_callback=on_device_info,
                data_callback=on_device_data
            )
            
            print("基础监控中... (5秒)")
            await asyncio.sleep(5)  # 运行5秒
            
    except Exception as e:
        print(f"基本示例错误: {e}")

async def multi_device_example():
    """多设备监控示例"""
    print("\n=== 2. 多设备监控示例 ===")
    
    # 设备信息回调
    async def on_device_info(device_info: DeviceInfo):
        print(f"[INFO] 设备: ID={device_info.device_id}, 状态={device_info.device_status}")
    
    # 设备数据回调
    async def on_device_data(device_data_list: List[DeviceData]):
        for data in device_data_list:
            print(f"[DATA] 设备: {data.data_type}={data.data_value} {data.unit}")
    
    try:
        async with DeviceMQTTClient(
            broker_host="localhost",
            broker_port=1883,
            client_id="multi_device_client"
        ) as client:
            
            # 监控多个设备
            devices = [
                ("device_001", "SN001"),
                ("device_002", "SN002"),
                ("device_003", "SN003")
            ]
            
            # 为每个设备启动监控
            for device_id, device_sn in devices:
                await client.start_monitoring(
                    device_id=device_id,
                    device_sn=device_sn,
                    info_callback=on_device_info,
                    data_callback=on_device_data
                )
                print(f"已开始监控设备 {device_id}/{device_sn}")
            
            print("多设备监控中... (5秒)")
            await asyncio.sleep(5)  # 运行5秒
            
    except Exception as e:
        print(f"多设备监控错误: {e}")

async def custom_processing_example():
    """自定义数据处理示例"""
    print("\n=== 3. 自定义数据处理示例 ===")
    
    # 自定义数据处理函数
    async def process_device_data(device_data_list: List[DeviceData]):
        for device_data in device_data_list:
            # 检查数据类型和值
            if device_data.data_type == "temperature" and float(device_data.data_value) > 60:
                print(f"⚠️ 高温告警: 设备 温度 {device_data.data_value}°C")
            
            # 功率监控
            if device_data.data_type == "power" and float(device_data.data_value) > 2000:
                print(f"⚡ 高功率: 设备 功率 {device_data.data_value}W")
            
            # 错误检查
            if device_data.data_type == "error_code" and int(device_data.data_value) != 0:
                print(f"❌ 设备错误: 设备 错误码 {device_data.data_value}")
    
    try:
        async with DeviceMQTTClient(
            broker_host="localhost",
            broker_port=1883,
            client_id="custom_processing_client"
        ) as client:
            
            # 开始监控并设置自定义处理回调
            await client.start_monitoring(
                device_id="device_001",
                device_sn="SN001",
                data_callback=process_device_data
            )
            
            print("自定义处理监控中... (5秒)")
            await asyncio.sleep(5)  # 运行5秒
            
    except Exception as e:
        print(f"自定义处理示例错误: {e}")

# =============================================================================
# 配置方式示例
# =============================================================================

async def example_with_traditional_config():
    """使用传统配置方式的示例"""
    print("\n=== 4. 传统配置方式示例 ===")
    
    # 使用传统的配置方式
    client = DeviceMQTTClient(
        broker_host="localhost",
        broker_port=1883,
        client_id="traditional_client"
    )
    
    # 定义回调函数
    async def on_device_info(device_info: DeviceInfo):
        print(f"收到设备信息: {device_info.device_id}")
        print(f"设备状态: {device_info.device_status}")
    
    async def on_device_data(device_data_list: List[DeviceData]):
        print(f"收到设备数据，共 {len(device_data_list)} 条")
        for data in device_data_list:
            print(f"  {data.data_type}: {data.data_value} {data.unit}")
    
    try:
        # 连接到MQTT代理
        if await client.connect():
            print("连接成功")
            
            # 开始监控设备
            await client.start_monitoring(
                device_id="DEV001",
                device_sn="SN123456",
                info_callback=on_device_info,
                data_callback=on_device_data
            )
            
            # 运行一段时间
            await asyncio.sleep(5)
            
        else:
            print("连接失败")
    
    except Exception as e:
        print(f"示例运行出错: {e}")
    
    finally:
        await client.disconnect()

async def example_with_new_config():
    """使用新配置方式的示例"""
    print("\n=== 5. 新配置方式示例 ===")
    
    # 使用新的配置方式
    client = DeviceMQTTClient(
        device_model="INV001",      # 设备机型码
        device_sn="SN123456789",   # 设备SN
        username="test_user",       # 用户名
        password="processed_password_123",  # 已处理的密码
        broker_host="localhost",    # MQTT服务器地址
        broker_port=8883,           # MQTT服务器端口
        keepalive=60,               # 心跳间隔
        use_tls=True                # 启用TLS
    )
    
    # 显示生成的配置信息
    print(f"生成的客户端ID: {client.client_id}")
    print(f"使用的密码: {client.password}")
    
    # 定义回调函数
    async def on_device_info(device_info: DeviceInfo):
        print(f"收到设备信息: {device_info.device_id}/{device_info.device_sn}")
        print(f"设备状态: {device_info.device_status}")
    
    async def on_device_data(device_data_list: List[DeviceData]):
        print(f"收到设备数据，共 {len(device_data_list)} 条")
        for data in device_data_list:
            print(f"  {data.data_type}: {data.data_value} {data.unit}")
    
    # 定义GET主题回调函数
    async def on_device_info_get(device_info: DeviceInfo):
        print(f"[GET] 收到设备信息获取响应: {device_info.device_id}/{device_info.device_sn}")
        print(f"[GET] 设备状态: {device_info.device_status}")
    
    async def on_device_data_get(device_data_list: List[DeviceData]):
        print(f"[GET] 收到设备数据获取响应，共 {len(device_data_list)} 条")
        for data in device_data_list:
            print(f"[GET]   {data.data_type}: {data.data_value} {data.unit}")
    
    try:
        # 连接到MQTT代理
        if await client.connect():
            print("连接成功")
            
            # 开始监控设备（包括GET主题）
            await client.start_monitoring(
                device_id="INV001",
                device_sn="SN123456789",
                info_callback=on_device_info,
                data_callback=on_device_data,
                info_get_callback=on_device_info_get,
                data_get_callback=on_device_data_get
            )
            
            # 运行一段时间
            await asyncio.sleep(5)
            
        else:
            print("连接失败")
    
    except Exception as e:
        print(f"示例运行出错: {e}")
    
    finally:
        await client.disconnect()

async def example_with_different_configs():
    """演示不同配置方式的示例"""
    print("\n=== 6. 不同配置方式示例 ===")
    
    # 配置1: 最小配置
    client1 = DeviceMQTTClient(
        broker_host="localhost"
    )
    
    # 配置2: 完整配置
    client2 = DeviceMQTTClient(
        device_model="INV002",
        device_sn="SN987654321",
        username="user2",
        password="processed_password2",
        broker_host="localhost",
        broker_port=8883,
        keepalive=120,
        use_tls=True
    )
    
    print(f"客户端1 ID: {client1.client_id}")
    print(f"客户端2 ID: {client2.client_id}")
    
    print("配置演示完成")

# =============================================================================
# GET主题示例
# =============================================================================

async def example_get_topics_only():
    """仅演示GET主题订阅功能"""
    print("\n=== 7. GET主题订阅示例 ===")
    
    client = DeviceMQTTClient(
        device_model="INV001",
        device_sn="SN123456789",
        username="test_user",
        password="processed_password",
        broker_host="localhost",
        broker_port=8883,
        keepalive=60,
        use_tls=True
    )
    
    # 定义GET主题回调函数
    async def on_device_info_get(device_info: DeviceInfo):
        print(f"[INFO GET] 设备: {device_info.device_id}/{device_info.device_sn}")
        print(f"[INFO GET] 型号: {device_info.device_model}")
        print(f"[INFO GET] 状态: {device_info.device_status}")
        print(f"[INFO GET] 固件版本: {device_info.firmware_version}")
    
    async def on_device_data_get(device_data_list: List[DeviceData]):
        print(f"[DATA GET] 收到 {len(device_data_list)} 条数据")
        for data in device_data_list:
            print(f"[DATA GET] {data.data_type}: {data.data_value} {data.unit}")
    
    try:
        if await client.connect():
            print("连接成功，订阅GET主题...")
            
            # 仅订阅GET主题
            await client.subscribe_device_info_get(
                "INV001", "SN123456789", on_device_info_get
            )
            await client.subscribe_device_data_get(
                "INV001", "SN123456789", on_device_data_get
            )
            
            print("等待GET主题消息... (5秒)")
            await asyncio.sleep(5)
            
        else:
            print("连接失败")
    
    except Exception as e:
        print(f"GET主题示例出错: {e}")
    
    finally:
        await client.disconnect()

# =============================================================================
# 高级示例
# =============================================================================

async def advanced_monitoring_example():
    """高级监控示例"""
    print("\n=== 8. 高级监控示例 ===")
    
    # 创建配置好的客户端
    client = create_configured_client(LOCAL_CONFIG)
    
    # 设置高级回调函数
    async def on_device_info(device_info: DeviceInfo):
        print(f"[INFO] 设备信息更新: {device_info.device_id}")
        print(f"  设备状态: {device_info.device_status}")
        print(f"  设备类型: {device_info.device_type}")
        
        # 数据验证
        await validate_device_info(device_info)
        
        # 异步数据日志
        await log_device_info(device_info)
    
    async def on_device_data(device_data_list: List[DeviceData]):
        for device_data in device_data_list:
            print(f"[DATA] 设备 {device_data.device_id}:")
            if hasattr(device_data, 'temperature'):
                print(f"  温度: {device_data.temperature}°C")
            if hasattr(device_data, 'power'):
                print(f"  功率: {device_data.power}W")
            if hasattr(device_data, 'voltage'):
                print(f"  电压: {device_data.voltage}V")
            
            # 异步告警检查
            await check_alerts(device_data)
            
            # 异步数据日志
            await log_device_data(device_data)
    
    try:
        if await client.connect():
            print("连接成功，开始高级监控...")
            
            # 开始监控
            await client.start_monitoring(
                device_id="INV001",
                device_sn="SN123456789",
                info_callback=on_device_info,
                data_callback=on_device_data
            )
            
            print("高级监控中... (5秒)")
            await asyncio.sleep(5)
            
        else:
            print("连接失败")
    
    except Exception as e:
        print(f"高级监控示例出错: {e}")
    
    finally:
        await client.disconnect()

async def cloud_config_examples():
    """云服务配置示例"""
    print("\n=== 9. 云服务配置示例 ===")
    
    configs = [
        ("阿里云IoT", ALIYUN_IOT_CONFIG),
        ("腾讯云IoT", TENCENT_IOT_CONFIG),
        ("AWS IoT", AWS_IOT_CONFIG)
    ]
    
    for name, config in configs:
        print(f"\n{name}配置:")
        print(f"  设备机型码: {config['device_model']}")
        print(f"  设备SN: {config['device_sn']}")
        print(f"  用户名: {config['username']}")
        print(f"  密码: {config['password']}")
        print(f"  服务器: {config['broker_host']}:{config['broker_port']}")
        print(f"  TLS: {'是' if config['use_tls'] else '否'}")
        
        # 生成client_id
        client_id = f"{config['device_model']}/{config['device_sn']}"
        
        print(f"  生成的客户端ID: {client_id}")

# =============================================================================
# 主函数
# =============================================================================

async def run_all_examples():
    """运行所有示例"""
    print("=== AIOEway 完整示例集合 ===")
    print("演示所有配置方式、使用场景和功能")
    
    # 基础示例
    await basic_example()
    await multi_device_example()
    await custom_processing_example()
    
    # 配置方式示例
    await example_with_traditional_config()
    await example_with_new_config()
    await example_with_different_configs()
    
    # GET主题示例
    await example_get_topics_only()
    
    # 高级示例
    await advanced_monitoring_example()
    
    # 云服务配置示例
    await cloud_config_examples()
    
    print("\n=== 所有示例运行完成 ===")

async def interactive_example_selector():
    """交互式示例选择器"""
    examples = {
        "1": ("基本使用示例", basic_example),
        "2": ("多设备监控示例", multi_device_example),
        "3": ("自定义数据处理示例", custom_processing_example),
        "4": ("传统配置方式示例", example_with_traditional_config),
        "5": ("新配置方式示例", example_with_new_config),
        "6": ("不同配置方式示例", example_with_different_configs),
        "7": ("GET主题订阅示例", example_get_topics_only),
        "8": ("高级监控示例", advanced_monitoring_example),
        "9": ("云服务配置示例", cloud_config_examples),
        "0": ("运行所有示例", run_all_examples)
    }
    
    print("\n=== AIOEway 示例选择器 ===")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    
    try:
        choice = input("\n请选择要运行的示例 (0-9): ").strip()
        if choice in examples:
            name, func = examples[choice]
            print(f"\n运行: {name}")
            await func()
        else:
            print("无效选择")
    except KeyboardInterrupt:
        print("\n用户取消")
    except Exception as e:
        print(f"运行示例时出错: {e}")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(**LOGGING_CONFIG)
    
    print("AIOEway 完整示例集合")
    print("选择运行模式:")
    print("1. 交互式选择")
    print("2. 运行所有示例")
    
    try:
        mode = input("请选择模式 (1/2): ").strip()
        if mode == "1":
            asyncio.run(interactive_example_selector())
        elif mode == "2":
            asyncio.run(run_all_examples())
        else:
            print("无效选择，运行所有示例")
            asyncio.run(run_all_examples())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
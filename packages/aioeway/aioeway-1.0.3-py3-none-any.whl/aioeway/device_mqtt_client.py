#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOEway - 异步MQTT设备交互库
用于通过MQTT协议与设备进行异步通信，支持设备信息查询和运行数据监控
"""

import json
import asyncio
import time
from typing import Dict, List, Callable, Optional, Awaitable
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    import aiomqtt
except ImportError:
    raise ImportError("请安装aiomqtt库: pip install aiomqtt")

# 设置日志
logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """设备信息数据结构"""
    net_firm_ver: float  # 网络模块固件版本
    app_firm_ver: float  # 主控模块固件版本
    wifi_ssid: str       # WiFi名称
    ip: str              # IP地址
    wifi_is_normal: int  # WiFi是否可用（0：是 1：否）
    is_lock: int         # 是否锁定（0：是 1：否）
    board: List[Dict]    # 板卡信息

    @classmethod
    def from_dict(cls, data: Dict) -> 'DeviceInfo':
        """从字典创建DeviceInfo对象"""
        return cls(
            net_firm_ver=data.get('netFirmVer', 0.0),
            app_firm_ver=data.get('appFirmVer', 0.0),
            wifi_ssid=data.get('wifiSsid', ''),
            ip=data.get('ip', ''),
            wifi_is_normal=data.get('wifiIsNormal', 1),
            is_lock=data.get('isLock', 1),
            board=data.get('board', [])
        )


@dataclass
class DeviceData:
    """设备运行数据结构"""
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

    @classmethod
    def from_dict(cls, data: Dict) -> 'DeviceData':
        """从字典创建DeviceData对象"""
        return cls(
            sort=data.get('sort', 0),
            input_voltage=data.get('inputVoltage', 0.0),
            input_current=data.get('InputCurrent', 0.0),
            grid_voltage=data.get('gridVoltage', 0.0),
            grid_freq=data.get('gridFreq', 0.0),
            gen_power=data.get('genPower', 0.0),
            gen_power_today=data.get('genPowerToDay', 0),
            gen_power_total=data.get('genPowerTotal', 0),
            temperature=data.get('temperature', 0.0),
            err_code=data.get('errCode', 0),
            duration=data.get('duration', 0)
        )


class DeviceMQTTClient:
    """异步设备MQTT客户端"""
    
    def __init__(self, device_model: str, device_sn: str, username: str, 
                 password: str, broker_host: str, 
                 broker_port: int = 1883, keepalive: int = 60, 
                 use_tls: bool = True):
        """
        初始化异步MQTT客户端
        
        Args:
            device_model: 设备机型码
            device_sn: 设备SN
            username: 用户名
            password: 已处理的密码
            broker_host: MQTT代理服务器地址
            broker_port: MQTT代理服务器端口，默认1883
            keepalive: 心跳间隔（秒）
            use_tls: 是否使用TLS加密连接
        """
        self.device_model = device_model
        self.device_sn = device_sn
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password  # 直接使用用户传入的已处理密码
        self.keepalive = keepalive
        self.use_tls = use_tls
        
        # 生成client_id: 机型码/SN
        self.client_id = f"{device_model}/{device_sn}"
        
        # MQTT客户端实例
        self.client: Optional[aiomqtt.Client] = None
        
        # 存储设备信息和数据的回调函数
        self.device_info_callbacks: Dict[str, Callable[[DeviceInfo], Awaitable[None]]] = {}
        self.device_data_callbacks: Dict[str, Callable[[List[DeviceData]], Awaitable[None]]] = {}
        
        # 连接状态
        self.is_connected = False
        
        # 监控任务
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.message_handler_task: Optional[asyncio.Task] = None
        
        # 停止事件
        self._stop_event = asyncio.Event()
    
    async def _resubscribe_all_topics(self):
        """重新订阅所有之前的主题"""
        if not self.client:
            return
            
        try:
            # 重新订阅设备信息主题
            for device_key in list(self.device_info_callbacks.keys()):
                if "_info_get" in device_key or "_data_get" in device_key:
                    continue  # 跳过临时的get主题
                    
                device_id, device_sn = device_key.split("_", 1)
                topic = f"{device_id}/{device_sn}/info/post"
                await self.client.subscribe(topic, qos=1)
                logger.debug(f"重新订阅信息主题: {topic}")
            
            # 重新订阅设备数据主题
            for device_key in list(self.device_data_callbacks.keys()):
                if "_info_get" in device_key or "_data_get" in device_key:
                    continue  # 跳过临时的get主题
                    
                device_id, device_sn = device_key.split("_", 1)
                topic = f"{device_id}/{device_sn}/data/post"
                await self.client.subscribe(topic, qos=1)
                logger.debug(f"重新订阅数据主题: {topic}")
                
            # 重新订阅get主题
            for device_key in list(self.device_info_callbacks.keys()):
                if "_info_get" in device_key:
                    base_key = device_key.replace("_info_get", "")
                    device_id, device_sn = base_key.split("_", 1)
                    topic = f"{device_id}/{device_sn}/info/get"
                    await self.client.subscribe(topic, qos=1)
                    logger.debug(f"重新订阅信息获取主题: {topic}")
            
            for device_key in list(self.device_data_callbacks.keys()):
                if "_data_get" in device_key:
                    base_key = device_key.replace("_data_get", "")
                    device_id, device_sn = base_key.split("_", 1)
                    topic = f"{device_id}/{device_sn}/data/get"
                    await self.client.subscribe(topic, qos=1)
                    logger.debug(f"重新订阅数据获取主题: {topic}")
                    
        except Exception as e:
            logger.error(f"重新订阅主题时出错: {e}")
    
    async def _handle_messages(self):
        """异步消息处理器，含断线重连"""
        while not self._stop_event.is_set():
            if not self.client:
                # 等待客户端初始化
                await asyncio.sleep(1)
                continue
        
            try:
                async for message in self.client.messages:
                    await self._process_message(message)

            except asyncio.CancelledError:
                logger.info("消息处理器已停止")
                break
            except Exception as e:
                logger.error(f"消息处理时出错，准备重连: {e}")
                self.is_connected = False
                # 尝试重新连接
                if await self.connect():
                    logger.info("重连成功")
                else:
                    await asyncio.sleep(5)  # 重连失败，等待后重试

    
    async def _process_message(self, message):
        """处理单个消息"""
        try:
            topic = str(message.topic)
            payload = json.loads(message.payload.decode('utf-8'))
            
            # 解析topic获取设备ID和SN
            topic_parts = topic.split('/')
            if len(topic_parts) >= 4:
                device_id = topic_parts[0]
                device_sn = topic_parts[1]
                message_type = topic_parts[2]
                action = topic_parts[3]
                
                device_key = f"{device_id}_{device_sn}"
                
                if message_type == "info" and action == "post":
                    # 处理设备信息
                    device_info = DeviceInfo.from_dict(payload)
                    if device_key in self.device_info_callbacks:
                        await self.device_info_callbacks[device_key](device_info)
                
                elif message_type == "info" and action == "get":
                    # 处理设备信息获取
                    device_info = DeviceInfo.from_dict(payload)
                    get_device_key = f"{device_key}_info_get"
                    if get_device_key in self.device_info_callbacks:
                        await self.device_info_callbacks[get_device_key](device_info)
                
                elif message_type == "data" and action == "post":
                    # 处理设备数据
                    if isinstance(payload, list):
                        device_data_list = [DeviceData.from_dict(data) for data in payload]
                        if device_key in self.device_data_callbacks:
                            await self.device_data_callbacks[device_key](device_data_list)
                
                elif message_type == "data" and action == "get":
                    # 处理设备数据获取
                    if isinstance(payload, list):
                        device_data_list = [DeviceData.from_dict(data) for data in payload]
                        get_device_key = f"{device_key}_data_get"
                        if get_device_key in self.device_data_callbacks:
                            await self.device_data_callbacks[get_device_key](device_data_list)
                    
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
    
    async def connect(self) -> bool:
        try:
            client_kwargs = {
                "hostname": self.broker_host,
                "port": self.broker_port,
                "keepalive": self.keepalive,
                "identifier": self.client_id,
                "username": self.username,
                "password": self.password,
            }
            if self.use_tls:
                import ssl
                ssl_context = ssl.create_default_context()
                client_kwargs["tls_context"] = ssl_context

            self.client = aiomqtt.Client(**client_kwargs)
            await self.client.__aenter__()

            self.is_connected = True
            # 重置停止事件
            self._stop_event.clear()
            logger.info(f"成功连接到MQTT代理: {self.broker_host}:{self.broker_port} {'(TLS)' if self.use_tls else '(无加密)'}")

            # 如果消息处理器已存在，取消并重新创建，保证单实例运行
            if self.message_handler_task and not self.message_handler_task.done():
                self.message_handler_task.cancel()
                try:
                    await self.message_handler_task
                except asyncio.CancelledError:
                    pass

            self.message_handler_task = asyncio.create_task(self._handle_messages())
            
            # 重新订阅所有之前的主题
            await self._resubscribe_all_topics()

            return True
        except Exception as e:
            logger.error(f"连接失败: {e}")
            self.is_connected = False
            self.client = None  # 确保清理客户端实例
            return False

    
    async def disconnect(self):
        """异步断开连接"""
        try:
            # 设置停止事件
            self._stop_event.set()
            
            # 停止所有监控任务
            for device_key in list(self.monitoring_tasks.keys()):
                await self.stop_monitoring(device_key)
            
            # 停止消息处理器
            if self.message_handler_task and not self.message_handler_task.done():
                self.message_handler_task.cancel()
                try:
                    await self.message_handler_task
                except asyncio.CancelledError:
                    pass
            
            # 断开MQTT连接
            if self.client:
                await self.client.__aexit__(None, None, None)
                self.client = None
            
            self.is_connected = False
            logger.info("已断开MQTT连接")
            
        except Exception as e:
            logger.error(f"断开连接时出错: {e}")
    
    async def subscribe_device_info(self, device_id: str, device_sn: str, 
                                  callback: Callable[[DeviceInfo], Awaitable[None]]):
        """异步订阅设备信息"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到MQTT代理")
        
        topic = f"{device_id}/{device_sn}/info/post"
        device_key = f"{device_id}_{device_sn}"
        
        self.device_info_callbacks[device_key] = callback
        await self.client.subscribe(topic, qos=1)
        logger.info(f"已订阅设备信息主题: {topic} (QoS=1)")
    
    async def subscribe_device_data(self, device_id: str, device_sn: str, 
                                  callback: Callable[[List[DeviceData]], Awaitable[None]]):
        """异步订阅设备运行数据"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到MQTT代理")
        
        topic = f"{device_id}/{device_sn}/data/post"
        device_key = f"{device_id}_{device_sn}"
        
        self.device_data_callbacks[device_key] = callback
        await self.client.subscribe(topic, qos=1)
        logger.info(f"已订阅设备数据主题: {topic} (QoS=1)")
    
    async def subscribe_device_info_get(self, device_id: str, device_sn: str, 
                                      callback: Callable[[DeviceInfo], Awaitable[None]]):
        """异步订阅设备信息获取主题"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到MQTT代理")
        
        topic = f"{device_id}/{device_sn}/info/get"
        device_key = f"{device_id}_{device_sn}_info_get"
        
        self.device_info_callbacks[device_key] = callback
        await self.client.subscribe(topic, qos=1)
        logger.info(f"已订阅设备信息获取主题: {topic} (QoS=1)")
    
    async def subscribe_device_data_get(self, device_id: str, device_sn: str, 
                                      callback: Callable[[List[DeviceData]], Awaitable[None]]):
        """异步订阅设备数据获取主题"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到MQTT代理")
        
        topic = f"{device_id}/{device_sn}/data/get"
        device_key = f"{device_id}_{device_sn}_data_get"
        
        self.device_data_callbacks[device_key] = callback
        await self.client.subscribe(topic, qos=1)
        logger.info(f"已订阅设备数据获取主题: {topic} (QoS=1)")
    
    async def request_device_info(self, device_id: str, device_sn: str, request_id: str = None):
        """发送设备信息获取请求"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到MQTT代理")
        
        # 生成请求ID（如果未提供）
        if request_id is None:
            request_id = f"info_req_{int(time.time() * 1000)}"
        
        # 构建请求主题和负载
        request_topic = f"{device_id}/{device_sn}/info/request"
        request_payload = {
            "action": "get_info",
            "request_id": request_id,
            "timestamp": int(time.time())
        }
        
        # 发送请求
        await self.client.publish(
            request_topic, 
            json.dumps(request_payload), 
            qos=1
        )
        
        logger.info(f"已发送设备信息请求: {request_topic} (请求ID: {request_id})")
        return request_id
    
    async def request_device_data(self, device_id: str, device_sn: str, request_id: str = None):
        """发送设备数据获取请求"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到MQTT代理")
        
        # 生成请求ID（如果未提供）
        if request_id is None:
            request_id = f"data_req_{int(time.time() * 1000)}"
        
        # 构建请求主题和负载
        request_topic = f"{device_id}/{device_sn}/data/request"
        request_payload = {
            "action": "get_data",
            "request_id": request_id,
            "timestamp": int(time.time())
        }
        
        # 发送请求
        await self.client.publish(
            request_topic, 
            json.dumps(request_payload), 
            qos=1
        )
        
        logger.info(f"已发送设备数据请求: {request_topic} (请求ID: {request_id})")
        return request_id
    
    async def request_device_info_and_wait(self, device_id: str, device_sn: str, 
                                         timeout: float = 10.0) -> Optional[DeviceInfo]:
        """发送设备信息请求并等待响应"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到MQTT代理")
        
        # 生成唯一的请求ID
        request_id = f"info_sync_{int(time.time() * 1000)}"
        response_received = asyncio.Event()
        received_info = None
        
        # 临时回调函数
        async def temp_callback(device_info: DeviceInfo):
            nonlocal received_info
            received_info = device_info
            response_received.set()
        
        # 订阅响应主题
        await self.subscribe_device_info_get(device_id, device_sn, temp_callback)
        
        try:
            # 发送请求
            await self.request_device_info(device_id, device_sn, request_id)
            
            # 等待响应
            try:
                await asyncio.wait_for(response_received.wait(), timeout=timeout)
                logger.info(f"收到设备信息响应 (请求ID: {request_id})")
                return received_info
            except asyncio.TimeoutError:
                logger.warning(f"设备信息请求超时 (请求ID: {request_id}, 超时: {timeout}秒)")
                return None
                
        finally:
            # 清理临时回调
            device_key = f"{device_id}_{device_sn}_info_get"
            if device_key in self.device_info_callbacks:
                del self.device_info_callbacks[device_key]
    
    async def request_device_data_and_wait(self, device_id: str, device_sn: str, 
                                         timeout: float = 10.0) -> Optional[List[DeviceData]]:
        """发送设备数据请求并等待响应"""
        if not self.is_connected or not self.client:
            raise ConnectionError("未连接到MQTT代理")
        
        # 生成唯一的请求ID
        request_id = f"data_sync_{int(time.time() * 1000)}"
        response_received = asyncio.Event()
        received_data = None
        
        # 临时回调函数
        async def temp_callback(device_data_list: List[DeviceData]):
            nonlocal received_data
            received_data = device_data_list
            response_received.set()
        
        # 订阅响应主题
        await self.subscribe_device_data_get(device_id, device_sn, temp_callback)
        
        try:
            # 发送请求
            await self.request_device_data(device_id, device_sn, request_id)
            
            # 等待响应
            try:
                await asyncio.wait_for(response_received.wait(), timeout=timeout)
                logger.info(f"收到设备数据响应 (请求ID: {request_id})")
                return received_data
            except asyncio.TimeoutError:
                logger.warning(f"设备数据请求超时 (请求ID: {request_id}, 超时: {timeout}秒)")
                return None
                
        finally:
            # 清理临时回调
            device_key = f"{device_id}_{device_sn}_data_get"
            if device_key in self.device_data_callbacks:
                del self.device_data_callbacks[device_key]
    
    async def start_monitoring(self, device_id: str, device_sn: str,
                             info_callback: Optional[Callable[[DeviceInfo], Awaitable[None]]] = None,
                             data_callback: Optional[Callable[[List[DeviceData]], Awaitable[None]]] = None,
                             info_get_callback: Optional[Callable[[DeviceInfo], Awaitable[None]]] = None,
                             data_get_callback: Optional[Callable[[List[DeviceData]], Awaitable[None]]] = None,
                             data_interval: int = 60):
        """异步开始监控设备（包括信息和数据）"""
        device_key = f"{device_id}_{device_sn}"
        
        # 如果已经在监控，先停止
        if device_key in self.monitoring_tasks:
            await self.stop_monitoring(device_key)
        
        # 订阅主题
        if info_callback:
            await self.subscribe_device_info(device_id, device_sn, info_callback)
        
        if data_callback:
            await self.subscribe_device_data(device_id, device_sn, data_callback)
        
        if info_get_callback:
            await self.subscribe_device_info_get(device_id, device_sn, info_get_callback)
        
        if data_get_callback:
            await self.subscribe_device_data_get(device_id, device_sn, data_get_callback)
        
        # 创建监控任务
        async def monitoring_loop():
            try:
                while not self._stop_event.is_set():
                    # 这里可以添加定期检查逻辑
                    # 由于数据是通过MQTT推送的，这里主要用于保持监控状态
                    await asyncio.sleep(data_interval)
            except asyncio.CancelledError:
                logger.info(f"设备 {device_key} 监控任务已停止")
        
        task = asyncio.create_task(monitoring_loop())
        self.monitoring_tasks[device_key] = task
        
        logger.info(f"开始监控设备 {device_id}/{device_sn}")
    
    async def stop_monitoring(self, device_key: str):
        """异步停止监控指定设备"""
        # 停止监控任务
        if device_key in self.monitoring_tasks:
            task = self.monitoring_tasks[device_key]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del self.monitoring_tasks[device_key]
        
        # 移除回调函数
        if device_key in self.device_info_callbacks:
            del self.device_info_callbacks[device_key]
        
        if device_key in self.device_data_callbacks:
            del self.device_data_callbacks[device_key]
        
        # 移除get主题的回调函数
        info_get_key = f"{device_key}_info_get"
        if info_get_key in self.device_info_callbacks:
            del self.device_info_callbacks[info_get_key]
        
        data_get_key = f"{device_key}_data_get"
        if data_get_key in self.device_data_callbacks:
            del self.device_data_callbacks[data_get_key]
        
        logger.info(f"停止监控设备: {device_key}")
    
    def get_monitored_devices(self) -> List[str]:
        """获取当前监控的设备列表"""
        return list(self.monitoring_tasks.keys())
    
    def is_device_monitored(self, device_id: str, device_sn: str) -> bool:
        """检查设备是否正在被监控"""
        device_key = f"{device_id}_{device_sn}"
        return device_key in self.monitoring_tasks
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()
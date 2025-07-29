import threading
import json
from typing import Callable, Dict, List, Optional
import nacos
import socket
import signal
import sys
import os
import yaml
import time
import atexit
import traceback
import random
from concurrent.futures import ThreadPoolExecutor

from sycommon.config.Config import SingletonMeta
from sycommon.logging.kafka_log import SYLogger


class NacosService(metaclass=SingletonMeta):
    def __init__(self, config):
        if config:
            self.config = config
            self.nacos_config = config['Nacos']
            self.service_name = config['Name']
            self.host = config['Host']
            self.port = config['Port']
            self.version = os.getenv('VERSION')
            self.registered = False
            self._client_initialized = False  # 客户端初始化状态
            self._shutdown_event = threading.Event()
            self._executor = ThreadPoolExecutor(max_workers=5)

            # 配置参数
            self.max_retries = self.nacos_config.get('maxRetries', 5)
            self.retry_delay = self.nacos_config.get('retryDelay', 1)
            self.retry_backoff = self.nacos_config.get('retryBackoff', 1.5)
            self.max_retry_delay = self.nacos_config.get('maxRetryDelay', 30)
            self.heartbeat_interval = self.nacos_config.get(
                'heartbeatInterval', 5)
            self.register_retry_interval = self.nacos_config.get(
                'registerRetryInterval', 5)  # 注册重试间隔

            # 长期重试配置
            self.long_term_retry_delay = self.nacos_config.get(
                'longTermRetryDelay', 30)
            self.max_long_term_retries = self.nacos_config.get(
                'maxLongTermRetries', -1)  # -1表示无限重试

            # 注册验证配置
            self.registration_verify_count = self.nacos_config.get(
                'registrationVerifyCount', 3)  # 验证次数
            self.registration_verify_interval = self.nacos_config.get(
                'registrationVerifyInterval', 1)  # 验证间隔

            self.real_ip = self.get_service_ip(self.host)
            self._long_term_retry_count = 0  # 长期重试计数器

            # 初始化客户端（仅在首次调用时执行）
            self._initialize_client()

            # 启动时清理残留实例
            self._cleanup_stale_instance()

            self.share_configs = self.read_configs()

            # 配置监听器
            self._config_listeners = {}
            self._config_cache = {}

            # 心跳相关
            self._last_heartbeat_time = 0
            self._heartbeat_fail_count = 0
            self._heartbeat_thread = None

            # 启动配置监视线程
            self._watch_thread = threading.Thread(
                target=self._watch_configs, daemon=True)
            self._watch_thread.start()

            # 启动心跳线程（在初始化完成后立即启动）
            self.start_heartbeat()

    def _initialize_client(self):
        """初始化Nacos客户端（仅首次调用时执行）"""
        if self._client_initialized:
            return True

        for attempt in range(self.max_retries):
            try:
                register_ip = self.nacos_config['registerIp']
                namespace_id = self.nacos_config['namespaceId']
                self.nacos_client = nacos.NacosClient(
                    server_addresses=register_ip,
                    namespace=namespace_id
                )
                SYLogger.info("nacos:客户端初始化成功")
                self._client_initialized = True
                return True
            except Exception as e:
                delay = min(self.retry_delay * (self.retry_backoff ** attempt),
                            self.max_retry_delay)
                SYLogger.error(
                    f"nacos:客户端初始化失败 (尝试 {attempt+1}/{self.max_retries}): {e}")
                time.sleep(delay)

        SYLogger.warning("nacos:无法连接到 Nacos 服务器，已达到最大重试次数")
        return False

    def _cleanup_stale_instance(self):
        """清理可能存在的残留实例"""
        if not self._client_initialized:
            return

        try:
            self.nacos_client.remove_naming_instance(
                service_name=self.service_name,
                ip=self.real_ip,
                port=int(self.port),
                cluster_name="DEFAULT"
            )
            SYLogger.warning(
                f"nacos:清理残留实例: {self.real_ip}:{self.port}")
        except Exception as e:
            SYLogger.error(f"nacos:清理残留实例异常: {e}")

    def ensure_client_connected(self, retry_once=False):
        """确保Nacos客户端已连接，返回连接状态"""
        # 使用线程锁保护客户端初始化状态
        with threading.Lock():
            if self._client_initialized:
                return True

            SYLogger.warning("nacos:客户端未初始化，尝试连接...")

            # 记录尝试次数，避免无限循环
            attempt = 0
            max_attempts = 2 if retry_once else self.max_retries

            while attempt < max_attempts:
                try:
                    register_ip = self.nacos_config['registerIp']
                    namespace_id = self.nacos_config['namespaceId']

                    # 创建新的Nacos客户端实例
                    self.nacos_client = nacos.NacosClient(
                        server_addresses=register_ip,
                        namespace=namespace_id
                    )

                    # 验证客户端是否真正可用
                    connection_valid = self._verify_client_connection()

                    if connection_valid:
                        self._client_initialized = True
                        SYLogger.info("nacos:客户端初始化成功")

                        # 客户端重新连接后，检查服务注册状态
                        self.registered = self.check_service_registered()
                        return True
                    else:
                        raise ConnectionError("nacos:客户端初始化后无法验证连接")

                except Exception as e:
                    attempt += 1
                    delay = min(self.retry_delay * (self.retry_backoff ** (attempt - 1)),
                                self.max_retry_delay)

                    SYLogger.error(
                        f"nacos:客户端初始化失败 (尝试 {attempt}/{max_attempts}): {e}")
                    time.sleep(delay)

            SYLogger.error("nacos:无法连接到 Nacos 服务器，已达到最大重试次数")
            return False

    def _verify_client_connection(self):
        """验证客户端是否真正连接成功"""
        try:
            # 使用当前服务的命名实例查询来验证连接
            namespace_id = self.nacos_config['namespaceId']
            self.nacos_client.list_naming_instance(
                service_name=self.service_name,
                cluster_name="DEFAULT",
                namespace_id=namespace_id,
                group_name="DEFAULT_GROUP",
                healthy_only=True
            )
            return True
        except Exception as e:
            SYLogger.warning(f"nacos:客户端连接验证失败: {e}")
            return False

    def check_service_registered(self):
        """检查服务是否已注册（基于实例列表）"""
        if not self.ensure_client_connected():
            return False

        try:
            namespace_id = self.nacos_config['namespaceId']
            instances = self.nacos_client.list_naming_instance(
                self.service_name, "DEFAULT", namespace_id, "DEFAULT_GROUP", True)

            # 检查是否存在包含当前IP和端口的实例
            for instance in instances.get('hosts', []):
                if (instance.get('ip') == self.real_ip and
                        instance.get('port') == int(self.port)):
                    SYLogger.info(
                        f"nacos:找到已注册实例: {self.real_ip}:{self.port}")
                    return True

            SYLogger.warning(f"nacos:未找到注册实例: {self.real_ip}:{self.port}")
            return False
        except Exception as e:
            SYLogger.error(f"nacos:检查服务注册状态失败: {e}")
            return False

    def verify_registration(self):
        """多次验证服务是否成功注册"""
        success_count = 0
        SYLogger.info(
            f"nacos:开始验证服务注册状态，共验证 {self.registration_verify_count} 次")

        for i in range(self.registration_verify_count):
            if self.check_service_registered():
                success_count += 1
            else:
                SYLogger.warning(f"nacos:第 {i+1} 次验证未找到注册实例")

            if i < self.registration_verify_count - 1:
                time.sleep(self.registration_verify_interval)

        if success_count >= self.registration_verify_count / 2:
            SYLogger.info(
                f"nacos:服务注册验证成功，{success_count}/{self.registration_verify_count} 次验证通过")
            return True
        else:
            SYLogger.error(
                f"nacos:服务注册验证失败，仅 {success_count}/{self.registration_verify_count} 次验证通过")
            return False

    def register_with_retry(self):
        """带重试机制的服务注册（基于实例列表检查）"""
        retry_count = 0
        last_error = None

        # 重置注册状态，确保重新检查
        self.registered = False

        while not self.registered and (self.max_long_term_retries < 0 or retry_count < self.max_long_term_retries):
            try:
                # 尝试注册服务
                register_success = self.register(force=True)

                if not register_success:
                    raise RuntimeError("nacos:服务注册请求失败")

                # 注册请求发送成功后，等待一小段时间让Nacos服务器处理
                SYLogger.info(
                    f"nacos:服务注册请求已发送，等待 {self.registration_verify_interval} 秒后验证")
                time.sleep(self.registration_verify_interval)

                # 多次验证服务是否真正注册成功
                registered = self.verify_registration()
                self.registered = registered  # <-- 确保设置注册状态

                if self.registered:
                    # 注册成功后，更新客户端状态
                    self._client_initialized = True

                    # 注册成功后，通知心跳线程立即发送心跳
                    self._shutdown_event.set()
                    self._shutdown_event.clear()

                    # 注册成功后，更新监控线程的状态
                    self._long_term_retry_count = 0

                    SYLogger.info(f"nacos:服务注册成功并通过验证: {self.service_name}")
                    return True
                else:
                    raise RuntimeError("nacos:服务注册验证失败")

            except Exception as e:
                last_error = str(e)
                retry_count += 1
                delay = min(self.register_retry_interval * (self.retry_backoff ** (retry_count - 1)),
                            self.max_retry_delay)

                SYLogger.warning(
                    f"nacos:服务注册尝试 {retry_count} 失败: {last_error}，{delay}秒后重试")
                time.sleep(delay)

        if last_error:
            SYLogger.error(f"nacos:服务注册失败，最终错误: {last_error}")
        else:
            SYLogger.error(f"nacos:服务注册失败，已达到最大重试次数: {self.service_name}")

        return False

    def register(self, force=False):
        """注册服务到Nacos"""
        # 使用线程锁保护注册状态
        with threading.Lock():
            if self.registered and not force and self.check_service_registered():
                return True

            if self.registered and not force:
                self.registered = False
                SYLogger.warning("nacos:本地状态显示已注册，但Nacos中未找到服务实例，准备重新注册")

            metadata = {"ignore-metrics": "true"}
            if self.version:
                metadata["version"] = self.version

            for attempt in range(self.max_retries):
                if not self.ensure_client_connected():
                    return False

                try:
                    # 注册服务
                    self.nacos_client.add_naming_instance(
                        service_name=self.service_name,
                        ip=self.real_ip,
                        port=int(self.port),
                        metadata=metadata,
                        cluster_name="DEFAULT",
                        healthy=True,
                        ephemeral=True,
                        heartbeat_interval=self.heartbeat_interval
                    )
                    SYLogger.info(
                        f"nacos:服务 {self.service_name} 注册请求已发送: {self.real_ip}:{self.port}")

                    # 注册退出时的清理函数
                    if not hasattr(self, '_atexit_registered') or not self._atexit_registered:
                        atexit.register(self.deregister_service)
                        self._atexit_registered = True

                    return True
                except Exception as e:
                    if "signal only works in main thread" in str(e):
                        return True
                    elif attempt < self.max_retries - 1:
                        SYLogger.warning(
                            f"nacos:服务注册失败 (尝试 {attempt+1}/{self.max_retries}): {e}")
                        time.sleep(self.retry_delay)
                    else:
                        SYLogger.error(f"nacos:服务注册失败，已达到最大重试次数: {e}")
                        return False

    @staticmethod
    def setup_nacos(config: dict):
        """创建并初始化Nacos管理器"""
        instance = NacosService(config)

        # 使用增强的注册重试逻辑
        if not instance.register_with_retry():
            # 在抛出异常前，尝试注销服务以清理状态
            try:
                instance.deregister_service()
            except Exception as e:
                SYLogger.error(f"nacos:服务注册失败后，注销服务时发生错误: {e}")

            raise RuntimeError("nacos:服务注册失败，应用启动终止")

        # 服务注册成功后再注册信号处理
        signal.signal(signal.SIGTERM, instance.handle_signal)
        signal.signal(signal.SIGINT, instance.handle_signal)

        # 启动连接监控线程
        threading.Thread(target=instance.monitor_connection,
                         daemon=True).start()

        return instance

    def start_heartbeat(self):
        """启动心跳线程"""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return

        self._heartbeat_thread = threading.Thread(
            target=self._send_heartbeat_loop,
            name="NacosHeartbeatThread",
            daemon=True
        )
        self._heartbeat_thread.start()
        SYLogger.info("nacos:心跳线程已启动")

    def _send_heartbeat_loop(self):
        """心跳发送循环 - 独立线程，不依赖外部锁"""
        SYLogger.info("nacos:心跳线程开始运行")
        consecutive_failures = 0  # 连续失败次数计数器
        last_successful_heartbeat = time.time()  # 上次成功心跳时间
        thread_start_time = time.time()  # 线程启动时间
        heartbeat_counter = 0  # 心跳计数器

        # 初始化为当前时间，以便尽快发送第一次心跳
        next_heartbeat_time = time.time()

        while not self._shutdown_event.is_set():
            try:
                current_time = time.time()
                SYLogger.info(
                    f"nacos:心跳线程检查状态，registered={self.registered}, 上次成功心跳: {last_successful_heartbeat}, 运行时间: {current_time-thread_start_time:.2f}s, 心跳计数: {heartbeat_counter}")

                # 检查是否到了发送心跳的时间
                if current_time >= next_heartbeat_time:
                    # 复制注册状态，减少锁的持有时间
                    is_registered = self.registered

                    if is_registered:
                        # 双重检查，确保服务确实注册
                        if not self.check_service_registered():
                            SYLogger.warning(
                                "nacos:服务状态显示已注册，但Nacos中未找到实例")
                            self.registered = False
                            continue

                        SYLogger.info("nacos:准备发送心跳...")
                        success = self.send_heartbeat()
                        if success:
                            heartbeat_counter += 1
                            consecutive_failures = 0
                            last_successful_heartbeat = current_time
                            # 更新下一次计划发送时间
                            next_heartbeat_time = current_time + self.heartbeat_interval
                            SYLogger.info(
                                f"nacos:心跳发送成功({heartbeat_counter})，下次发送时间: {next_heartbeat_time}")
                        else:
                            consecutive_failures += 1
                            # 失败时减少下次发送间隔，加快恢复
                            next_heartbeat_time = current_time + min(
                                self.heartbeat_interval,
                                self.long_term_retry_delay *
                                (self.retry_backoff **
                                 (consecutive_failures - 1))
                            )
                            SYLogger.warning(
                                f"nacos:心跳发送失败，将减少下次发送间隔为 {next_heartbeat_time - current_time:.2f} 秒")
                    else:
                        SYLogger.warning("nacos:服务未注册，跳过心跳发送")
                        # 服务未注册时，尝试重新注册
                        if current_time - next_heartbeat_time > self.register_retry_interval:
                            SYLogger.info("nacos:服务未注册，尝试重新注册")
                            self.register_with_retry()
                            next_heartbeat_time = current_time + self.heartbeat_interval
                        else:
                            # 缩短检查间隔
                            next_heartbeat_time = current_time + \
                                min(self.heartbeat_interval, 5)

                # 检查线程运行时间，防止线程挂起 - 统一为1小时重置
                if current_time - thread_start_time > 3600:
                    SYLogger.info("nacos:心跳线程已运行1小时，重置内部状态")
                    thread_start_time = current_time
                    heartbeat_counter = 0

                # 检查是否长时间没有成功心跳
                if current_time - last_successful_heartbeat > self.heartbeat_interval * 3:
                    SYLogger.warning(
                        f"nacos:已超过3个心跳周期({self.heartbeat_interval*3}秒)没有成功发送心跳，尝试重新注册")
                    self.register_with_retry()
                    last_successful_heartbeat = current_time

                # 计算休眠时间，避免过度循环
                sleep_time = next_heartbeat_time - current_time
                if sleep_time > 0:
                    SYLogger.info(f"nacos:心跳线程休眠 {sleep_time:.2f} 秒")
                    self._shutdown_event.wait(sleep_time)
                else:
                    # 如果已经晚了，立即执行下一次循环
                    self._shutdown_event.wait(0.1)

            except Exception as e:
                SYLogger.error(f"nacos:心跳线程异常: {str(e)}")
                traceback.print_exc()
                # 发生异常时，增加下次发送间隔
                next_heartbeat_time = time.time() + 5
                self._shutdown_event.wait(1)

        SYLogger.info("nacos:心跳线程已停止")

    def send_heartbeat(self):
        """发送心跳到Nacos"""
        if not self.ensure_client_connected():
            return False

        try:
            # 发送心跳
            result = self.nacos_client.send_heartbeat(
                service_name=self.service_name,
                ip=self.real_ip,
                port=int(self.port),
                cluster_name="DEFAULT",
                weight=1.0,
                metadata={"version": self.version} if self.version else None
            )

            # 处理返回结果
            if result and isinstance(result, dict) and result.get('lightBeatEnabled', False):
                SYLogger.info(
                    f"nacos:心跳发送成功，Nacos返回: {result}")
                return True
            else:
                SYLogger.warning(
                    f"nacos:心跳发送失败，Nacos返回: {result}")
                return False

        except Exception as e:
            SYLogger.error(f"nacos:发送心跳时发生异常: {e}")
            return False

    def reconnect_nacos_client(self):
        """重新连接Nacos客户端"""
        SYLogger.warning("nacos:尝试重新连接Nacos客户端")
        self._client_initialized = False
        return self.ensure_client_connected()

    def monitor_connection(self):
        """监控Nacos连接状态，定期检查并在需要时重连"""
        check_interval = self.nacos_config.get('checkInterval', 10)
        thread_start_time = time.time()  # 线程启动时间
        check_counter = 0  # 检查计数器

        while not self._shutdown_event.is_set():
            try:
                current_time = time.time()
                SYLogger.info(
                    f"nacos:连接监控线程运行中，运行时间: {current_time-thread_start_time:.2f}s, 检查计数: {check_counter}")

                # 检查客户端连接状态
                if not self.ensure_client_connected():
                    SYLogger.warning("nacos:检测到Nacos客户端连接丢失，尝试重新初始化")
                    self._initialize_client()  # 尝试重新初始化客户端

                # 检查服务注册状态
                current_registered = self.check_service_registered()

                # 更新注册状态并在状态变更时通知心跳线程
                if current_registered != self.registered:
                    if current_registered:
                        self.registered = True
                        SYLogger.info(f"nacos:服务实例已重新注册")
                    else:
                        self.registered = False
                        SYLogger.warning(f"nacos:服务实例未注册，尝试重新注册")
                        # 不在锁内调用可能耗时的操作
                        self._executor.submit(self.register_with_retry)

                # 额外检查：即使状态未变，也定期验证服务是否真的可用
                if random.random() < 0.2:  # 20%的概率执行深度检查
                    self.verify_registration()

                # 每小时重置一次内部状态
                if current_time - thread_start_time > 3600:
                    SYLogger.info("nacos:连接监控线程已运行1小时，重置内部状态")
                    thread_start_time = current_time
                    check_counter = 0

                check_counter += 1
                # 休眠指定时间
                self._shutdown_event.wait(check_interval)
            except Exception as e:
                SYLogger.error(f"nacos:连接监控异常: {e}")
                time.sleep(self.retry_delay)

    def get_service_ip(self, config_ip):
        """获取服务实际IP地址"""
        if config_ip in ['127.0.0.1', '0.0.0.0']:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(('8.8.8.8', 80))
                    return s.getsockname()[0]
            except Exception:
                return '127.0.0.1'
        return config_ip

    def deregister_service(self):
        """从Nacos注销服务"""
        if not self.registered or not self._client_initialized:
            return

        SYLogger.info("nacos:正在注销服务...")
        try:
            self.nacos_client.remove_naming_instance(
                service_name=self.service_name,
                ip=self.real_ip,
                port=int(self.port),
                cluster_name="DEFAULT"
            )
            self.registered = False
            SYLogger.info(f"nacos:服务 {self.service_name} 已注销")
        except Exception as e:
            SYLogger.error(f"nacos:注销服务时发生错误: {e}")
        finally:
            self._shutdown_event.set()
            self._executor.shutdown()

    def handle_signal(self, signum, frame):
        """处理退出信号"""
        SYLogger.info(f"nacos:收到信号 {signum}，正在关闭服务...")
        self.deregister_service()
        sys.exit(0)

    def read_configs(self) -> dict:
        """读取共享配置"""
        configs = {}
        shared_configs = self.nacos_config.get('sharedConfigs', [])

        for config in shared_configs:
            data_id = config['dataId']
            group = config['group']

            for attempt in range(self.max_retries):
                try:
                    # 检查客户端连接
                    if not self.ensure_client_connected():
                        self.reconnect_nacos_client()

                    # 获取配置
                    content = self.nacos_client.get_config(data_id, group)

                    try:
                        configs[data_id] = json.loads(content)
                    except json.JSONDecodeError:
                        try:
                            configs[data_id] = yaml.safe_load(content)
                        except yaml.YAMLError:
                            SYLogger.error(f"nacos:无法解析 {data_id} 的内容")
                    break
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        SYLogger.warning(
                            f"nacos:读取配置 {data_id} 失败 (尝试 {attempt+1}/{self.max_retries}): {e}")
                        time.sleep(self.retry_delay)
                    else:
                        SYLogger.error(
                            f"nacos:读取配置 {data_id} 失败，已达到最大重试次数: {e}")

        return configs

    def add_config_listener(self, data_id: str, callback: Callable[[str], None]):
        """添加配置变更监听器"""
        self._config_listeners[data_id] = callback
        # 初始获取一次配置
        if config := self.get_config(data_id):
            callback(config)

    def get_config(self, data_id: str, group: str = "DEFAULT_GROUP") -> Optional[str]:
        """获取配置内容"""
        if not self.ensure_client_connected():
            return None

        try:
            return self.nacos_client.get_config(data_id, group=group)
        except Exception as e:
            SYLogger.error(f"nacos:获取配置 {data_id} 失败: {str(e)}")
            return None

    def _watch_configs(self):
        """配置监听线程"""
        while not self._shutdown_event.is_set():
            try:
                for data_id, callback in list(self._config_listeners.items()):
                    new_config = self.get_config(data_id)
                    if new_config and new_config != self._config_cache.get(data_id):
                        self._executor.submit(callback, new_config)
                        self._config_cache[data_id] = new_config
            except Exception as e:
                SYLogger.error(f"nacos:配置监视线程异常: {str(e)}")
            self._shutdown_event.wait(5)  # 每5秒检查一次

    def discover_services(self, service_name: str, group: str = "DEFAULT_GROUP", version: str = None) -> List[Dict]:
        """发现服务实例列表 (与Java格式兼容)"""
        if not self.ensure_client_connected():
            return []

        return self.get_service_instances(service_name, group, version)

    def get_service_instances(self, service_name: str, group: str = "DEFAULT_GROUP", version: str = None) -> List[Dict]:
        try:
            namespace_id = self.nacos_config['namespaceId']
            instances = self.nacos_client.list_naming_instance(
                service_name, "DEFAULT", namespace_id, group, True)
            if not instances or 'hosts' not in instances:
                return []
            return instances.get('hosts', [])
        except Exception as e:
            SYLogger.error(f"nacos:服务发现失败: {service_name}: {str(e)}")
            return []

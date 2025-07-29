import os
import configparser
from pathlib import Path


class ConfigManager:
    _instance = None
    CONFIG_DIR = Path.home() / "Bin/Config"
    CONFIG_FILE = CONFIG_DIR / "cordy.ini"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance

    def _init_config(self):
        """初始化配置管理"""
        self._ensure_config_exists()
        self.config = configparser.ConfigParser()
        self.config.read(self.CONFIG_FILE)

    def _ensure_config_exists(self):
        """确保配置文件和目录存在"""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if not self.CONFIG_FILE.exists():
            self._create_default_config()

    def _create_default_config(self):
        """创建默认配置文件"""
        import pkg_resources
        try:
            # 从包中读取默认配置
            default_config = pkg_resources.resource_string('CordyMotion', 'config/cordy.ini')
            with open(self.CONFIG_FILE, 'wb') as f:
                f.write(default_config)
        except Exception as e:
            # 回退方案：手动创建默认配置
            default_config = (
                "[network]\n"
                "ip = 127.0.0.1\n"
                "port = 8899\n"
            )
            with open(self.CONFIG_FILE, 'w') as f:
                f.write(default_config)

    @property
    def ip(self):
        """获取IP配置"""
        return self.config.get('network', 'ip', fallback='127.0.0.1')

    @property
    def port(self):
        """获取端口配置"""
        return int(self.config.get('network', 'port', fallback=8080))

    def reload(self):
        """重新加载配置文件"""
        self.config.read(self.CONFIG_FILE)


# 创建全局配置管理器实例
config = ConfigManager()

# 暴露给模块的接口
ip = config.ip
port = config.port


class IRU:
    """IRU命名空间，包含方法fixture_load(), fixture_unload(), power_on_dut(), power_off_dut(), fixture_iru_pos()

        示例:
            >>> from CordyMotion import IRU
            >>> IRU.fixture_load()
    """

    @staticmethod
    def fixture_load():
        """执行fixture_load操作

        功能描述:
            - 功能:在上料位装载DUT后，治具气缸夹紧
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = IRU.fixture_load()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 300000)
            caller.send_command("fixtureload")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_unload():
        """执行fixture_unload操作

        功能描述:
            - 功能:在上料位，治具气缸松开，取下DUT
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = IRU.fixture_unload()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 300000)
            caller.send_command("fixtureunload")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def power_on_dut():
        """执行power_on_dut操作

        功能描述:
            - 功能:给上料位的DUT供电
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = IRU.power_on_dut()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 300000)
            caller.send_command("powerondut")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def power_off_dut():
        """执行power_off_dut操作

        功能描述:
            - 功能:给上料位的DUT断电
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = IRU.power_off_dut()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 300000)
            caller.send_command("poweroffdut")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_iru_pos():
        """执行fixture_iru_pos操作

        功能描述:
            - 功能:在上料位装载DUT并通电后，按机台左右两侧的启动按钮，将上料位的DUT转到IRU测试位进行入测试
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = IRU.fixture_iru_pos()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 300000)
            caller.send_command("fixtureirupos")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True



class SimpleIQ:
    """IRU命名空间，包含方法fixture_load(), fixture_unload(), power_on_dut()
    , power_off_dut(), fixture_led_on(), fixture_led_off(), fixture_lcd_on()
    , fixture_lcd_off(), fixture_wf_pos(), fixture_sfr_pos()

        示例:
            >>> from CordyMotion import SimpleIQ
            >>> SimpleIQ.fixture_load()
    """
    @staticmethod
    def power_on_dut(slot=None):
        """执行power_on_dut操作

        功能描述:
            - 功能:给上料位的DUT供电
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.power_on_dut()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 300000)
            caller.send_command("powerondut")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def power_off_dut(slot=None):
        """执行power_off_dut操作

        功能描述:
            - 功能:给上料位的DUT断电
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.power_off_dut()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 100000)
            caller.send_command("poweroffdut")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_led_on():
        """执行fixture_led_on操作

        功能描述:
            - 功能:点亮LED
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.fixture_led_on()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 100000)
            caller.send_command("fixtureledon")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_led_off():
        """执行power_off_dut操作

        功能描述:
            - 功能:关闭LED
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.fixture_led_off()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 100000)
            caller.send_command("fixtureledoff")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_lcd_on():
        """执行fixture_lcd_on操作

        功能描述:
            - 功能:点亮LCD屏幕
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.fixture_lcd_on()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 100000)
            caller.send_command("fixturelcdon")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_lcd_off():
        """执行fixture_lcd_off操作

        功能描述:
            - 功能:关闭LCD屏幕
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.fixture_lcd_off()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 100000)
            caller.send_command("fixturelcdoff")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_wf_pos():
        """执行fixture_wf_pos操作

        功能描述:
            - 功能:DUT进入white field测试工位
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.fixture_wf_pos()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 300000)
            caller.send_command("fixturewfpos")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_sfr_pos():
        """执行fixture_sfr_pos操作

        功能描述:
            - 功能:DUT进入sfr测试工位
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.fixture_sfr_pos()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 300000)
            caller.send_command("fixturesfrpos")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_load_pos():
        """执行fixture_load_pos操作

        功能描述:
            - 功能:DUT进入sfr测试工位
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.fixture_load_pos()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 500000)
            caller.send_command("fixtureloadpos")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_load():
        """执行fixture_load操作

        功能描述:
            - 功能:在上料位装载DUT后，治具气缸夹紧
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.fixture_load()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 100000)
            caller.send_command("fixtureload")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True

    @staticmethod
    def fixture_unload():
        """执行fixture_unload操作

        功能描述:
            - 功能:在上料位，治具气缸松开，取下DUT
            - 返回True结果

        参数:
            无

        返回:
            bool: 操作是否成功

        示例:
            >>> result = SimpleIQ.fixture_unload()
            >>> print(result)
            True

        异常:
            ImportError: 当cordymotioncaller包未安装时抛出
        """
        try:
            from CordyMotion.CordyMotionCaller import MotionCaller
            caller = MotionCaller(ip, port, 100000)
            caller.send_command("fixtureunload")
        except ImportError:
            raise ImportError("motion package is required but not found")
        return True
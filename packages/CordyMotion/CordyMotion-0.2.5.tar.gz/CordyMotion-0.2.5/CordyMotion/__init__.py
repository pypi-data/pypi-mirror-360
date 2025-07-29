"""CordyMotion 包

提供以下命名空间接口:
- IRU.fixture_load(): 执行操作:在上料位装载DUT后，治具气缸夹紧
- IRU.fixture_unload(): 执行操作:在上料位，治具气缸松开，取下DUT
- IRU.power_on_dut(): 执行操作:给上料位的DUT供电
- IRU.power_off_dut(): 执行操作:给上料位的DUT断电
- IRU.fixture_iru_pos(): 执行操作:在上料位装载DUT并通电后，按机台左右两侧的启动按钮，将上料位的DUT转到IRU测试位进行入测试

- Simple.fixture_load(): 执行操作:在上料位装载DUT后，治具气缸夹紧
- Simple.fixture_unload(): 执行操作:在上料位，治具气缸松开，取下DUT
- Simple.power_on_dut(): 执行操作:给上料位的DUT供电
- Simple.power_off_dut(): 执行操作:给上料位的DUT断电
- Simple.fixture_led_on(): 执行操作:点亮LED
- Simple.fixture_led_off(): 执行操作:关闭LED
- Simple.fixture_lcd_on(): 执行操作:点亮LCD屏幕
- Simple.fixture_lcd_off(): 执行操作:关闭LCD屏幕
- Simple.fixture_wf_pos(): 执行操作:DUT进入white field测试工位
- Simple.fixture_sfr_pos(): 执行操作:DUT进入sfr测试工位

安装依赖:
包需要cordymotioncaller.whl作为依赖，会自动安装

版本: 0.1.0

示例:
    >>> from CordyMotion import IRU, SimpleIQ
    >>> help(IRU.fixture_load)  # 查看fixture_load使用帮助
    >>> IRU.fixture_load()
    >>> SimpleIQ.fixture_load()
"""

from .CordyMotion import IRU, SimpleIQ, ConfigManager

__all__ = ['IRU', 'SimpleIQ', 'ConfigManager']
__version__ = '0.1.0'
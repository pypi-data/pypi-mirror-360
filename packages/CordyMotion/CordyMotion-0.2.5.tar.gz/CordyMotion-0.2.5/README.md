.
# CordyMotion
CordyMotion 是基于珠海市科迪电子科技有限公司平台的设备驱动运控程序客户端cordymotioncaller的一层封装。主要是用于IRU以及SimpleIQ等测试设备调用的API。
目前CordyMotion只支持Linux(Ubuntu22.04)版本。

---
## 主要特点
* CordyMotion 安装后，会将配置文件cordy.ini 安装在Ubuntu当前用户目录下的Bin/Config下（例如：~/Bin/Config/cordy.ini)
* cordy.ini配置文件中包含Serer端 IP 和 port. (需要正确配置Server端的IP 和 Port, 否则CordyMotion无法正确工作。)

---

## pip 安装
CordyMotion 已经发布到 Pypi 官网，通过 pip 指令可以安装。
注意：需要提前在 Ubuntu22.04 操作系统上安装python(版本3.10)
```
pip install CordyMotion
```

验证CordyMotion 是否安装成功
```
>>> from CordyMotion import IRU
>>> help(IRU)

```
输出如下内容:
```
|  IRU命名空间，包含方法fixture_load(), fixture_unload(), power_on_dut(), power_off_dut(), fixture_iru_pos()
 |  
 |  示例:
 |      >>> from CordyMotion import IRU
 |      >>> IRU.fixture_load()
 |  
 ...
```
表示安装成功

## 帮助说明

* 使用者可以通过 help() 来查询 CordyMotion 的帮助说明。目前支持对整个whl包、包中指定类、类中指定的方法的使用说明。

### 查看 class 说明
```
from CordyMotion import IRU, SimpleIQ

help(IRU) 
help(SimpleIQ)
```

### 查看 function 说明
```
from CordyMotion import IRU, SimpleIQ
help(IRU.fixture_load)
help(SimpleIQ.fixture_unload)
```
### 查看 Package 说明
```
import CordyMotion
help(CordyMotion)
```

### Version History
| version | Desc                                     |
|---------|------------------------------------------|
| 0.2.3   | add SimpleIQ.fixture_load_pos(), 治具回到上料位 |
| 0.2.4   | extend the timeout value to 300 seconds  |



### issue
* CordyMotion 通过TCP与 Server端连接，执行运控操作时，当前版本首先会尝试与Server连接，当超时3次都无法连接成功时，CordyMotion会退出连接。此时需要检查连接状态：
1. Server 端是否成功启动
2. 检查Server端的IP地址和监听端口
3. 检查CordyMotion的配置文件 cordy.ini 中配置的Server IP 和 Port是否正确。






# 庐山派 CanMV-K230 项目

本项目展示了如何在庐山派 CanMV-K230 上运行 YOLO 模型，并通过 MQTT 发布检测结果。

## 前提条件

在开始之前，请确保你已经完成以下准备工作：

- 安装 Python 3.x
- 配置虚拟环境
- 安装必要的工具：`ampy`, `mpremote`, `screen`

## 安装步骤

### 配置虚拟环境

```shell
cd project # 假设这是项目目录
python3.9 -m venv venv
source venv/bin/activate
```

### 安装工具

```bash
pip install adafruit-ampy
pip install mpremote
sudo apt-get install screen  # 对于 Debian/Ubuntu 系统
brew install screen          # 对于 macOS 系统
```

### 配置连接庐山派 CanMV-K230

**Mac**

通过 USB 线将庐山派 CanMV-K230 连接到电脑，并找到设备的挂载位置：

```shell
# lsusb
...
Bus 001 Device 009: ID 1209:abd1 1209 CanMV  Serial: 001000000
...
```

发现`ID 1209:abd1 1209 CanMV  Serial: 001000000`，可以使用`lsusb -v`查看详细信息，但是有`001000000`就够了，使用下面的命令查看挂载位置：

```shell
ls /dev/tty* | grep '001000000'
```

**ubuntu**
```bash

~$ lsusb
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 002: ID 1209:abd1 InterBiometrics
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
~$ ls /dev/ttyA*
/dev/ttyACM0

```

将结果添加当前目录下的 `.ampy` 文件中：

```plaintext
AMPY_PORT=/dev/tty.usbmodem0010000001 #/dev/ttyACM0
AMPY_BAUD=115200
AMPY_DELAY=0.5
```

## 配置

修改配置文件

### 上传文件到庐山派 CanMV-K230

使用 `ampy` 工具上传文件：

```bash
ampy put boot.py /sdcard/boot.py
ampy put main.py /sdcard/main.py
ampy put src /sdcard/src
```

### 使用 mpremote 安装依赖

**Mac**
```bash
mpremote connect /dev/tty.usbmodem0010000001 mip install --target /sdcard/libs ntptime
mpremote connect /dev/tty.usbmodem0010000001 mip install --target /sdcard/libs umqtt.simple
```

**windows**
```bash
mpremote connect COM12 mip install --target /sdcard/libs ntptime
mpremote connect COM12 mip install --target /sdcard/libs umqtt.simple
```

**ubuntu**
```bash
mpremote connect /dev/ttyACM0 mip install --target /sdcard/libs ntptime
mpremote connect /dev/ttyACM0 mip install --target /sdcard/libs umqtt.simple
```

**最终结果**

![image](https://github.com/user-attachments/assets/ebdb30fe-3d0a-445b-9cc9-23184bce1108)


## 使用说明

### 运行项目

确保所有文件已上传到庐山派 CanMV-K230，然后运行主程序：

```bash
ampy run main.py
```

### 查看日志

使用 `screen` 工具连接到庐山派 CanMV-K230 并查看日志输出：

```bash
screen -S K230 /dev/cu.usbmodem0010000001 115200
```

要退出 `screen` 会话，可以按 `Ctrl+A`，然后按 `K`，最后按 `Y` 确认退出。

## 常用命令

**上传文件**：

```bash
ampy put <文件名>
```

**下载文件**：

```bash
ampy get <文件名> > <本地文件名>
```

**列出文件**：

```bash
ampy ls [目标路径]
```

**删除文件**：

```bash
ampy rm <文件名>
```

**运行脚本**：

```bash
ampy run <脚本名>
```

**安装 mip 包**：

```bash
mpremote connect /dev/tty.usbmodem0010000001 mip install <包名> --target="/sdcard/libs"
```

**连接 REPL**：

```bash
screen -S K230 /dev/cu.usbmodem0010000001 115200
```

## 总结

通过以上步骤，你可以在命令行中方便地连接庐山派 CanMV-K230，实现文件的上传、下载，安装第三方包以及查看日志等操作。希望本文对你有所帮助。

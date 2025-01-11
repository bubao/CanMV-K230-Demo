# 使用命令行连接庐山派 CanMV-K230

本文将介绍如何在命令行连接庐山派 CanMV-K230，并实现上传、下载、使用 mip 安装第三方包以及使用 screen 连接查看日志等操作。

<!--more-->

## 前提条件

在开始之前，请确保你已经完成以下准备工作：

**安装 Python 3.x**：

你可以从 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python 3.x。

配置 venv 环境：

```shell
cd project # 假设这是项目目录
python3.9 -m venv venv
source venv/bin/activate
```

安装`ampy`,`mpremote`,`screen`

```bash
pip install adafruit-ampy
pip install mpremote
sudo apt-get install screen  # 对于 Debian/Ubuntu 系统
brew install screen          # 对于 macOS 系统
```

`ampy`,`mpremote`,`screen`的功能：

- ampy 用于上传下载的命令行工具
- screen 是一个终端多路复用器，可以让你在一个终端窗口中运行多个会话。
- mpremote 是一个用于与 MicroPython 设备交互的命令行工具，主要是用来安装`mip`

## 配置连接庐山派 CanMV-K230

首先，通过 USB 线将庐山派 CanMV-K230 连接到电脑。

```shell
# lsusb
Bus 001 Device 002: ID 2109:0822 VIA Labs, Inc. USB3.1 Hub
Bus 001 Device 004: ID 05e3:0626 Genesys Logic, Inc. USB3.1 Hub
Bus 001 Device 006: ID 0b95:1790 ASIX Electronics Corporation AX88179A  Serial: 000000000066F0
Bus 001 Device 007: ID 05e3:0749 Genesys Logic, Inc. USB3.0 Card Reader  Serial: 000000001536
Bus 001 Device 001: ID 2109:2822 VIA Labs, Inc. USB2.0 Hub
Bus 001 Device 009: ID 1209:abd1 1209 CanMV  Serial: 001000000
Bus 001 Device 005: ID 048d:5212 Integrated Technology Express, Inc. ITE BillBoard
Bus 001 Device 003: ID 05e3:0610 Genesys Logic, Inc. USB2.1 Hub
Bus 001 Device 008: ID 2109:8822 VIA Labs, Inc. USB Billboard Device  Serial: 0000000000000001
Bus 000 Device 000: ID 2109:0822 VIA Labs, Inc. USB 3.1 Bus
Bus 000 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
```

发现`ID 1209:abd1 1209 CanMV  Serial: 001000000`，可以使用`lsusb -v`查看详细信息，但是有`001000000`就够了，使用下面的命令查看挂载位置：

```shell
# ls /dev/tty* | grep '001000000'
/dev/tty.usbmodem0010000001
```

`/dev/tty.usbmodem0010000001`在后面连接 CanMV-K230 会用到。

## 上传文件到庐山派 CanMV-K230

使用 ampy 工具可以方便地将文件上传到庐山派 CanMV-K230。首先安装 ampy：

```bash
pip install adafruit-ampy
```

为了方便使用，建议在项目文件夹下创建`.ampy`文件，并加入以下内容：

```txt
AMPY_PORT=/dev/tty.usbmodem0010000001
AMPY_BAUD=115200
AMPY_DELAY=0.5
```

然后使用以下命令将文件上传到板子上：

```bash
ampy put <文件名> [目标路径]
```

同样地，可以使用 ampy 工具从板子上下载文件：

```bash
ampy get <文件名> > <本地文件名>
```

## 添加依赖

立创庐山派固件缺少 `ntptime`和`umqtt.simple`，需要使用`mpremote`手动安装：

```bash
mpremote connect /dev/tty.usbmodem0010000001 mip install ntptime
mpremote connect /dev/tty.usbmodem0010000001 mip install umqtt.simple
```

在 REPL 中，输入以下命令安装 mip：

```python
import libs.mip as mip
mip.install("<包名>")
```

## 使用 screen 查看日志

可以使用 screen 工具连接到庐山派 CanMV-K230 并查看日志输出：

```bash
screen -S K230 /dev/cu.usbmodem0010000001 115200
```

要退出 screen 会话，可以按`Ctrl+A`，然后按`K`，最后按`Y`确认退出。

> 每次进入都会 soft reset，可以按`Ctrl+D`手动 soft reset，如果正在运行，也可以用`Ctrl+C`终止运行。

## 常用命令

以下是一些常用的命令，帮助你更好地使用庐山派 CanMV-K230：

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
mpremote connect /dev/tty.usbmodem0010000001 mip --target="/sdcard/libs" install mip
```

**连接 REPL**：

```bash
screen -S K230 /dev/cu.usbmodem0010000001 115200
```

## 总结

通过以上步骤，你可以在命令行中方便地连接庐山派 CanMV-K230，实现文件的上传、下载，安装第三方包以及查看日志等操作。希望本文对你有所帮助。

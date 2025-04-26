# helldivers2AutoStratagems

[![GitHub license](https://img.shields.io/github/license/GDNDZZK/helldivers2AutoStratagems.svg)](https://github.com/GDNDZZK/helldivers2AutoStratagems/blob/master/LICENSE) ![Python版本](https://img.shields.io/badge/python-3.10%2B-yellow) ![GitHub issues](https://img.shields.io/github/issues/GDNDZZK/helldivers2AutoStratagems.svg) ![GitHub all releases](https://img.shields.io/github/downloads/GDNDZZK/helldivers2AutoStratagems/total.svg) ![GitHub forks](https://img.shields.io/github/forks/GDNDZZK/helldivers2AutoStratagems.svg?style=flat)
 ![GitHub stars](https://img.shields.io/github/stars/GDNDZZK/helldivers2AutoStratagems.svg?style=flat)


绝地潜兵2一键搓球!基于视觉识别一键自动更新战略配备指令,附带Web UI,可以使用快捷键或网页搓球.

[演示视频(使用快捷键呼叫战备)](https://www.acfun.cn/v/ac47131715) [演示视频(使用Web UI呼叫战备)](https://www.acfun.cn/v/ac47189365)

## 注意

- 暂不支持弧形UI
- 暂不支持HDR(你可以手动设置`COLORS`参数临时支持,但这种方法麻烦且不通用.如果你有办法获取HDR截图并正确转换到SDR,欢迎修改`imageProcessing.capture_screenshot`函数并提交PR)
- 建议在游戏中使用 `按住`打开战略配备面板
- 本软件使用[GPL-3.0](https://github.com/GDNDZZK/helldivers2AutoStratagems/blob/master/LICENSE)开源,请民主的使用
- 有任何问题欢迎提issues,欢迎提PR参与开发

## 运行方法

#### 1.使用Releases版本

1. 下载并解压7z压缩包
2. 运行程序:

   ```
   helldivers2AutoStratagems.exe
   ```
3. 运行后会出现托盘图标,右键点击 `exit`退出

#### 2.从源代码构建

1. 克隆或下载此仓库到本地
2. 确保你的Python版本在3.10及以上
3. 安装必要的Python库：

   ```shell
   pip install -r requirements.txt
   ```
4. 运行程序：

   ```
   app.py
   ```
5. 运行后会出现托盘图标,右键点击 `exit`退出

## 使用GUI自定义设置

#### 如何打开设置面板

* 启动程序时会自动打开设置面板,如果你不希望这样可以取消勾选 `允许设置面板随程序开启`.
* 右键托盘图标,点击 `settings`
* 使用快捷键(默认 `<ctrl>+<=>`)

#### 识别区域设置

1. 点击 `交互式更改`会出现区域选择框
2. 按住并拖动区域选择框右下角区域(`完成`按钮附近)改变大小
3. 按住并拖动区域选择框的其它区域移动
4. 点击 `截图测试`可以看到识别区域是否正确

#### WebUI设置

1. 左侧输入框代表监听地址,默认`all`监听所有地址(ipv4和ipv6),你可以设置为`0.0.0.0`仅监听ipv4地址,`::`仅监听ipv6地址,`127.0.0.1`仅监听本机
2. 右侧输入框代表端口,默认`80`,如果有冲突可以设置为其它端口
3. 如果你已经启动了WebUI,需要重新打开才能生效

#### 按键设置

1. 点击`配置键盘快捷键`,打开快捷键设置面板
2. 点击对应按键的按钮(例如`识别按键`、`打开设置`等)会弹出按键输入框
3. 按下按键会显示,松开后会记录
4. `战略配备键位`(包括`上`,`下`,`左`,`右`,`战备面板`)只允许设置一个按键,这些按键用于输出

## 识别战备

1. 按下快捷键(默认`<ctrl> + <->`)开始识别
2. 两声提示音表示更新完成,如果你开启了Web UI,更新会自动同步
3. 听到长提示音表示识别错误,建议找光线较暗的地方重新识别

## 使用快捷键呼叫战备

#### 标准模式

1. 默认使用`<ctrl>+<1>`,`<ctrl>+<2>`...`<ctrl>+<9>`,`<ctrl>+<0>`呼叫战备面板中第1-10个战备
2. 标准模式不会实时更新战备,因此战备有变动要重新识别才能同步

#### 干扰器优化模式
1. 每次使用战备都会重新识别,不会输出中间文件
2. 此模式不会实时更新设置,因此修改设置可能要重新启动软件才能生效
3. 由于每次使用战备都会重新识别,所以还是会比识别完成后的标准模式慢,但会比先识别后使用的标准模式快
4. 默认使用`<ctrl>+<f1>`...`<ctrl>+<f10>`呼叫战备面板中第1-10个战备
5. 实测效果其实一般,只有一定的概率能在指令改变前召唤出来,并且有可能因为指令变化召唤出其它战备.所以其实并不推荐用这个,遇到干扰器还是建议老老实实手搓

## 使用网页呼叫战备(Web UI)

1. 右键托盘图标,点击`start webui`开启Web UI
2. 如果你缺少网络基础知识,请使用搜索引擎搜索`查询电脑的局域网ip`,确保你想用来显示网页的设备和你的电脑连接了相同`局域网`
3. 在浏览器中访问`http://你电脑的ip:端口号`打开网页,如果端口号是80可以不用输入(http默认端口)
4. 一些示例(注意这只是示例,请填写你电脑实际的地址和你设置的端口号):`http://192.168.1.2:2333`(ipv4局域网地址,使用2333端口),`http://192.168.1.2`(使用默认80端口),`http://[fe80::a1b2:c3d4:e5f6:789a]:5555`(ipv6局域网地址,使用5555端口),`http://[fe80::a1b2:c3d4:e5f6:789a]`(ipv6局域网地址,使用默认80端口)
5. 注意部分浏览器可能会强制将`http`替换为`https`导致无法使用,如有这种情况请自行解决
6. 网页支持横屏和竖屏,支持PC和移动端,支持鼠标和触屏
7. 打开网页后识别出新的战备会自动添加到网页上,鼠标悬停或触屏长按网页上的战备框右上角会出现删除按钮,点击可以移除网页中单个战备
8. 点击即可自动打开战备面板呼叫对应战备
9. 刷新网页移除网页中的所有战备
10. 设计时并未考虑同时打开多个网页的情况,如果你这样做可能会遇到非预期异常现象

## 部分文件和目录的说明与配置

#### temp/

1. 此目录仅在更新过战略配备指令后才会出现
2. 识别后的原始结果会存入 `./temp/arrow_original.txt`,可用于评估识别效果
3. 如果 `./temp/arrow.txt`存在,使用`标准呼叫战备按键`会自动读取该文件中的战略配备指令,你可以手动修改此文件改变`标准呼叫战备按键`触发的指令(重新识别后该文件会被覆盖,因此不推荐这样做)

#### defaultArrow.txt

1. 这里可以设置战略配备指令默认值,当某个战备因为冷却等原因无法识别时会使用此文件下定义的指令(如果存在)
2. 如果 `./temp/arrow.txt`不存在,按下`标准呼叫战备按键`后会读取该文件
3. `defaultArrow.txt`、`./temp/arrow.txt`、`./temp/arrow_original.txt`中第N行对应第N个战备

#### config.ini

1. 如果文件不存在,将会使用默认值自动创建
2. 所有设置会被保存在这里
3. `THRESHOLD`和 `COLORS`通常不建议自行修改,假如你使用了滤镜等改变画面颜色导致识别失败,可以尝试修改这两项参数.过滤效果可以查看 `./temp/screenshot_binary.bmp`
4. `COLORS`代表二值化保留的颜色,`THRESHOLD`代表阈值
5. 设置`COLORS`参数你可以获取不同战备边框和战备箭头的颜色16进制RGB代码,多种颜色使用`,`分隔

#### arrow/

1. 此目录存放图像匹配模板,通常不建议修改
2. 此目录下任何修改需要重启软件后生效
3. 当你发现某个战备指令方向识别错误时可以尝试去 `./temp/split_images/{num}/`下找到该箭头图片,将箭头方向改为向上后放入 `./arrow`下,也许能改善识别效果
4. 过多的模板图片会降低识别速度,还可能降低识别效果

## TODO

* [X] 获取截图
* [X] 统一大小
* [X] 二值化
* [X] 获取指令区域
* [X] 指令识别
* [X] 快捷键
* [X] 默认值
* [X] 指令输入
* [X] 托盘图标
* [X] 提示音频
* [X] 使用config.ini调参
* [X] 可设置的按键触发速度
* [X] 带鱼屏导致缩放后战备面板过小 #2
* [X] 虚线边框的战备无法识别 #3
* [X] 干扰器优化模式(每次按下战备先识别后触发,不等待输出临时文件提高识别速度)
* [X] 可设置的按键(小键盘问题 #3)
* [ ] UI弧度修正(感觉好麻烦,摸了)
* [ ] HDR自动适配
* [ ] 预设战备字典
* [X] 实时显示状态可交互的网页(咕咕咕咕)
* [ ] Linux X11适配(Wayland存在诸多问题无法解决,暂时放弃.蔚蓝得毁掉一切😭)

## settingGUI TODO

* [X] 完善按键输入识别，支持区分左右modifies
* [X] 添加打开战备面板(ACTIVATION)按键设置项
* [X] 添加webui设置项
* [ ] 添加二值化设置项
* [ ] 让按键输入识别在Wayland下工作（X11情况未知，需要测试）
* [ ] 修复wayland下resizePanel无法获取窗口位置的问题（大概差不多可能是修不了，蔚蓝得毁掉一切😭）

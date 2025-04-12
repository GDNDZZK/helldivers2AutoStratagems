# helldivers2AutoStratagems

[![GitHub license](https://img.shields.io/github/license/GDNDZZK/helldivers2AutoStratagems.svg)](https://github.com/GDNDZZK/helldivers2AutoStratagems/blob/master/LICENSE) ![Python版本](https://img.shields.io/badge/python-3.10%2B-yellow)

绝地潜兵2一键搓球!基于视觉识别一键自动更新战略配备指令.

[演示视频](https://www.bilibili.com/video/BV1kjZSYtEwM)

## 注意

- 暂不支持弧形UI,暂时无法调节战备命令按键,请将战备命令按键设置为上下左右方向键(也许会更新)
- 默认激活键为 `ctrl`,请将激活键设置为和打开战略配备面板相同按键
- 建议在游戏中使用 `按住`打开战略配备面板
- 本软件使用[GPL-3.0](https://github.com/GDNDZZK/helldivers2AutoStratagems/blob/master/LICENSE)开源,请民主的使用
- 有任何问题欢迎提issues,欢迎提PR参与开发

## 使用方法

#### 1.使用Releases版本

1. 下载并解压7z压缩包
2. 运行程序:

   ```
   helldivers2AutoStratagems.exe
   ```
3. 运行后会出现托盘图标,右键托盘图标退出
4. 打开战略配备面板使用 `ctrl`+`0`更新战略配备指令
5. 听到提示音后可以放心关闭战略配备面板等待识别
6. 两声提示音表示更新完成,按下 `ctrl`+`1~9`自动搓球
7. 听到长提示音表示识别错误,建议找光线较暗的地方重新识别

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
5. 运行后会出现托盘图标,右键托盘图标退出
6. 打开战略配备面板使用 `ctrl`+`0`更新战略配备指令
7. 听到提示音后可以关闭战略配备面板
8. 两声提示音表示更新完成,按下 `ctrl`+`1~9`自动搓球
9. 听到长提示音表示识别错误,建议找光线较暗的地方重新识别

## 一些说明与自定义配置

#### temp/

1. 此目录仅在更新过战略配备指令后才会出现
2. 识别后的原始结果会存入 `./temp/arrow_original.txt`,可用于评估识别效果
3. 如果 `./temp/arrow.txt`存在,按下 `ctrl`+`1~9`后会自动读取该文件中的战略配备指令,你可以手动修改此文件改变战略配备指令

#### defaultArrow.txt

1. 这里可以设置战略配备指令默认值,当某个战备因为冷却等原因无法识别时会使用此文件下定义的指令(如果存在)
2. 如果 `./temp/arrow.txt`不存在,按下 `ctrl`+`1~9`后会读取该文件
3. `defaultArrow.txt`、`./temp/arrow.txt`、`./temp/arrow_original.txt`中第N行对应第N个战备

#### config.ini

1. `ACTIVATION`可以修改 `ctrl`为其它按键
2. 强烈建议你首次更新战略配备指令后检查 `./temp/screenshot_cropped.png`是否完整显示战略配备面板,如果不能完整显示,请修改 `LEFT`、`TOP`、`RIGHT`、`BOTTOM`调整识别区域
3. `THRESHOLD`和 `COLORS`通常不建议自行修改,假如你使用了滤镜等改变画面颜色导致识别失败,可以尝试修改这两项参数.过滤效果可以查看 `./temp/screenshot_binary.bmp`

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
* [ ] 干扰器优化模式(每次按下战备先识别后触发,不等待输出临时文件提高识别速度)
* [ ] 可设置的战备指令按键(小键盘问题 #3)
* [ ] UI弧度修正(感觉好麻烦,摸了)
* [ ] 实时显示状态可交互的网页(咕咕咕咕)
* [ ] 自动搓游戏机(我不知道有啥意义)
* [X] 自定义设置单按键激活(其实 `ACTIVATION=`后面空的就行)

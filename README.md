# DumbDrawPhD - 笨比博士会画图 🎨🐱


## 这是什么？🤔

喵呜~这是一个专门为**实验室里的笨比博士**设计的**拖拽式科研绘图工具**！(｡･ω･｡)ﾉ♡

再也不用担心被老板骂"图都不会画"啦！只要把数据文件拖进来，用**人话**告诉本喵你想画什么，AI就会帮你生成代码并运行~

## 为什么需要这个？😼

因为本喵发现：
- 90%的博士都**不会写代码**
- 99%的博士都觉得**画图很痛苦**
- 100%的博士都**不想学**但**必须画**

## 功能特点 🎯

- 🖱️ **拖拽上传**：直接把数据文件拖进来就好啦~（也可以点击“导入”按钮）
- 🗣️ **人话交互**："帮我画个柱状图，要蓝色的！背景要五彩斑斓渐变黑" 这样说就行！
- 🤖 **AI生成代码**：自动生成Python绘图代码并给你图
- 😺 **猫娘陪伴**：画图时还有本喵给你加油打气！

## 快速开始 🚀

1. **拖**：把你的数据文件(.csv/.xlsx/.txt,甚至是tif格式的图片也可以喵)拖到窗口里
2. **说**：告诉DumbDrawPhD你想画什么
   - "画个折线图，X是时间，Y是温度"
   - "做个箱线图，要粉色的！"
   - "给我的数据做个PCA，前三个主成分"
3. **等**：让AI生成代码并自动运行
4. **保存**：右键保存图片，Ctrl+C复制代码

## 示例对话 💬

用户："这是一个成绩单，里面有StudentID，Gender，Score这三列。你帮我画个图，统计一下全班的成绩分布，以及给个分析图看看男生女生直接成绩有无显著差异。把差异的星号*画在图上"

DumbDrawPhD："喵~明白啦！(≧▽≦) 正在用seaborn生成彩虹柱状图，已经添加误差线咯~"

## 系统要求 ⚙️

- 操作系统：Windows/macOS/Linux
- 内存：≥8GB (毕竟不能用太卡的电脑)
- Python 3.8+ (打包的exe里已经内置啦，不用自己装)

## 免责声明 ⚠️

本喵不保证：
- 能治好你老板的暴躁症
- 能让你发的论文不被拒
- 能让你准时毕业

但保证：
- 画图过程会很开心！(◕‿◕✿)

---

🐾 **Happy Dumb Drawing!** 🐾

*"就算是最笨的博士，也有权利画出漂亮的图表！" —— DumbDrawPhD开发喵*


## 开发
打包成exe或其它二进制文件时候，务必使用隐式导入，将一些必要的包加进去，不然可执行文件里运行代码的时候会找不到包。例如以下：
```commandline
pyinstaller -w DumbDrawPhD.py \
    --hidden-import PySide6 \
    --hidden-import requests \
    --hidden-import matplotlib \
    --hidden-import seaborn \
    --hidden-import pandas \
    --hidden-import openpyxl \
    --hidden-import PIL \
    --hidden-import Bio \
    --hidden-import numpy \
    --hidden-import rasterio \
    --hidden-import sklearn \
    --hidden-import skimage \
    --hidden-import scipy \
    --hidden-import cv2 \
    --hidden-import openai
```
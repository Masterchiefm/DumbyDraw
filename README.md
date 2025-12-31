# DumbyDraw - 笨比博士会画图 🎨🐱


## 这是什么？🤔

喵呜~这是一个专门为**实验室里的笨比博士**设计的**拖拽式科研绘图工具**！(｡･ω･｡)ﾉ♡

再也不用担心被老板骂"图都不会画"啦！只要把数据文件拖进来，用**人话**告诉本喵你想画什么，AI就会帮你生成代码并运行~

## 示例

### 1. 给我处理测序数据
<img width="1193" height="956" alt="image" src="https://github.com/user-attachments/assets/27906c40-6ca1-40ae-8a62-6d27b644f0b0" />


### 2. 给我画信号热图
<img width="1445" height="927" alt="image" src="https://github.com/user-attachments/assets/caac80af-6ac0-471a-adae-e94a13537017" />


### 3. 给我把南极站标出来
<img width="1742" height="923" alt="image" src="https://github.com/user-attachments/assets/a37a76c4-f2fe-463e-99e7-e0c85dd9043b" />


### 4. 随便画点什么
   <img width="1117" height="900" alt="image" src="https://github.com/user-attachments/assets/402de58c-cd33-4767-92ab-2dd85def5828" />



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
### 安装
1. 最简单的方法是直接从[release](https://github.com/Masterchiefm/DumbyDraw/releases/latest)中下载啦，但是只有win/Linux版本的


2. 或者从源码运行
理论上win，Linux，mac都可用
首先在电脑安装python和pip。然后终端里运行以下即可：
```commandline
# 国内用这个链接
pip install git+https://gitee.com/MasterChiefm/DumbyDraw.git
```
```commandline
# 网络好的话用这个链接
pip install git+https://github.com/Masterchiefm/DumbyDraw.git
```

注意，Ubuntu还需要安装以下依赖：
```
sudo apt update && sudo apt install libxcb-cursor0
```

搞定这些后，以后要运行就直接这样：
```commandline
DumbyDraw
```
这样就能运行啦！

### 使用
首先设置AI的API，AI可不是免费的哦！可以用deepseek,chatgpt等api，你有哪个用哪个。（本喵用的是deepseek-V3.2，思考模型表现挺不错的）
如果没有，这是我在SiliconFlow的邀请链接，你自己注册一个就行，送十几块钱的API费用呢。
https://cloud.siliconflow.cn/i/Su2ao83G

邀请码是Su2ao83G

然后打开程序，在程序底部输入AI的base_url，model，api密钥就行了。
例如我的就是``https://api.siliconflow.cn/v1``,``deepseek-ai/DeepSeek-V3``和``sk-xxxxxxxxxxxxxxxxxxxxxx``
你照样填就好了

实际使用：
1. **拖**：把你的数据文件(.csv/.xlsx/.txt,甚至是tif格式的图片也可以喵)拖到窗口里
2. **说**：告诉DumbyDraw你想画什么
   - "画个折线图，X是时间，Y是温度"
   - "做个箱线图，要粉色的！"
   - "给我的数据做个PCA，前三个主成分"
3. **等**：让AI生成代码并自动运行
4. **保存**：右键保存图片，Ctrl+C复制代码

## 示例对话 💬
```
用户："这是一个成绩单，里面有StudentID，Gender，Score这三列。你帮我画个图，统计一下全班的成绩分布，以及给个分析图看看男生女生直接成绩有无显著差异。把差异的星号*画在图上"

DumbyDraw："喵~明白啦！(≧▽≦) 正在用seaborn生成彩虹柱状图，已经添加误差线咯~"
```

或者
```
用户：“这是我的双端测序数据，帮我merge一下，然后找到ATCG和GATC序列之间的碱基，并翻译成氨基酸。给我统计一下提取到的各种序列的分布，给我画出前20条的丰度直方图”
```

或者
```
用户：“给我在北极上标出这些点，坐标是114,514”
```

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

*"就算是最笨的博士，也有权利画出漂亮的图表！" —— DumbyDraw开发喵*


## 打包分发
打包成exe或其它二进制文件时候，不要使用pyinstaller等工具，否则运行生成代码的时候会缺一堆包。

建议使用conda pack将整个环境打包。

installer里是windows内的打包工具。

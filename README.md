# TbReview
<!--这是个TheBrain的可视化复盘小工具，就是把每天修改过的特定类型的节点，归集到「回顾」节点下面，复盘结束后，将复盘的的内容整理成卡片，发送至Anki或者flome。-->

**取名：TbReview**

## 一、开发的过程:

- 今年加入了张玉新老师的TheBrain交流群，学习了很多思考的方法，就想着能让复盘更自动化的点，就开始着手做个简单的自动化程序。
- 最开始是做了一个将创建或修改的特定类型（我的是「洞见卡片」和「原则」两个类型）节点定时自动连接到固定节点（我的是「回顾」节点）。
- 后来在群友的期待下，我开始做的更可配置化，后来越做越来劲，慢慢组成了现在的样子，因为时间平时没有太多时间，自己也没有系统学过写代码，有些bug卡了很久，时间拖得有点久。
- 开发测试了很多版本，也将不清楚了，姑且现在的版本当作v1.0吧。

## 二、效果展示和操作介绍

### （一）效果展示

1. 图1: 主界面![截屏2024-09-11 12.11.41](/Users/nijianhai/Downloads/截屏2024-09-11 12.11.41.png)

2. 图2: 参数设置1![截屏2024-09-11 12.12.10](/Users/nijianhai/Downloads/截屏2024-09-11 12.12.10.png)
3. 图3: 参数设置2![截屏2024-09-11 12.12.25](/Users/nijianhai/Downloads/截屏2024-09-11 12.12.25.png)
4. 图4: 是否有新的思考的参数设置![截屏2024-09-11 12.12.47](/Users/nijianhai/Downloads/截屏2024-09-11 12.12.47.png)
5. 图5: 制卡方式的参数设置![截屏2024-09-11 12.13.04](/Users/nijianhai/Downloads/截屏2024-09-11 12.13.04.png)
6. 图6: 运行效果![截屏2024-09-11 12.13.36](/Users/nijianhai/Downloads/截屏2024-09-11 12.13.36.png)
7. 图7: 交互界面1![截屏2024-09-11 12.53.28](/Users/nijianhai/Downloads/截屏2024-09-11 12.53.28.png)
8. 图8: 交互界面2

<img src="/Users/nijianhai/Downloads/截屏2024-09-11 12.53.39.png" alt="截屏2024-09-11 12.53.39" style="zoom:30%;" /><img src="/Users/nijianhai/Downloads/截屏2024-09-11 12.54.06.png" alt="截屏2024-09-11 12.54.06" style="zoom:30%;" /><img src="/Users/nijianhai/Downloads/截屏2024-09-11 12.54.22.png" alt="截屏2024-09-11 12.54.22" style="zoom:30%;" />

### （二）操作介绍

#### 1. 复盘的逻辑

1. 「回顾」节点：要有一个用来回顾的节点，用来将需要定期复盘的thought连接到「回顾」节点。注意：**「回顾」节点的种类不能是类型**，否则会将所有修改记录的节点内容都制作成卡片，**建议使用便签种类**。
2. 「问题卡片」类型节点：要有一个用来表示问题的类型节点，**用来做卡片的正面或标题**。这个节点仅用来对卡片内容进行归类，可以是问题，可以直指某个事物，名称可以自拟。
3. 若干个用来区分TB节点且想制成卡片的类型节点：我的是「洞见卡片」和「原则」两个类型，支持自定义，将平时自己创建或修改的经过思考后的要作为自己洞见的thought归类到这两个类型中，**用来做卡片的内容或者背面**。我对卡片的内容进行了特定的处理，已经**支持TB的「.1.1.1、.1.1、.1.2、.1、.2」的排序**，按照符合TB的规则进行排序后，去除这些数字符号。在anki中会进行相应的有序列表、无序列表和缩进显示
4. 「精进域」节点：即对某一个领域不断精进的意思 (群友羿智的方法)。「问题卡片」类型的节点一定会有一个「精进域」的类型的父节点，**用来做卡片的标签或者牌组**，方便对卡片进行归类。「精进域」类型节点的父节点也可以是「精进域」类型节点，会递归查询所有关联的「精进域」类型节点，进行路径排序，变成标签或者牌组的路径。
5. 时间周期：thought连接或断开「回顾」节点时，「回顾」节点都会产生修改记录。
   - 连接「回顾」节点：**复盘结束时必须要将thought节点与「回顾」节点断开连接**，建议是复盘完一个thought，就将其与「回顾」节点断开连接。我预设的是，启动TbReview程序，点击运行后，上次复盘结束（即「回顾」节点最近一次修改时间）到“点击运行”之间，有创建或修改记录的「洞见卡片」和「原则」两个类型的节点会自动连接到「回顾」节点。可以自定义排除操作类型，我排除了「102'已删除'、301'忘记'」2中操作类型的记录。操作类型详见《操作类型字典.md》
   - 制卡：连接「回顾」节点之后，到TB中进行一次复盘，可能会对「洞见卡片」和「原则」类型的节点进行修改，**修改后断开与「回顾」节点的连接**，然后回到TbReview程序，点击“创建卡片”，将自动对改成修改的节点制作成记忆卡片，并发送至Anki或flomo。这样能够保证发送的卡片内容是最新的
   - 已连接到「回顾」节点的thought，没及时复盘并断开连接，不会进行制卡，直到完成复盘断开连接。
   - **回顾时，当日事当日毕**
6. 如何避免发送至flomo/Anki的卡片标签或牌组紊乱？
   - 「里程碑」类型节点下级的「问题卡片」要父连接到「精进域」类型的节点
   - 「问题卡片」下级不要再设「问题卡片」
   - 一个「问题卡片」只能对应一个「精进域」
   - 「洞见卡片」下级还可以有「洞见卡片」



#### 2. 设置

1. 参数设置

   - 启动后会进入主界面 (图1)，在主界面的左小角点击"⚙︎"，会出现参数设置界面 (图2)。

   - 参数设置界面分了两个分页：「参数设置」和「TB_rul设置」。参数设置用来设置API和Brain ID、thought ID、类型ID等，以及思考情况和制卡方式；TB_rul设置用来设置「回顾」节点的本地路径。

2. 是否有新的思考

   - 思考情况分为"New Ths"和"No Ths" (图4)
     - "New Ths"表示两次复盘之间「洞见卡片」和「原则」两个类型的节点**有**新的创建或修改记录。
     - 和"No Ths"表示两次复盘之间「洞见卡片」和「原则」两个类型的节点**没有**新的创建或修改记录。

3. 制卡方式有["Anki卡片", "flomo卡片", "不制卡"]

   - "Anki卡片"表示制作Anki类型的卡片，并发送至Anki。
   - "flomo卡片"表示制作flomo类型的卡片，并发送至flomo。
   - "不制卡"表示不进行卡片制作。

#### 3. 操作交互

- 启动TbReview程序后，首先看到主界面 (图1)，中间有个醒目的‘立即回顾“的按钮，点击后，会根据设置的内容进行不同类型的运行。
- 思考情况选择"New Ths"时，会先将有创建或修改记录的「洞见卡片」和「原则」两个类型的节点会连接到「回顾」节点。连接结束后，会弹出窗口 (图7)，根据卡片方式的选择会有不同的操作界面 (图8)。
- 点击「To TheBrain」会跳转到TB的「回顾」节点，在TB操作完毕后，回到TbReview程序，再点击”创建卡片“，会关闭弹窗，然后进行相应的制卡。在制卡方式为"不制卡"时，点击「To TheBrain」跳转到TB「回顾」节点同时，会关闭弹窗。
- 进行自动化处理时，所有按钮会变会，防止误操作。

## 三 、代码和功能的情况说明

### （一）文件结构说明

#### 1. 先展示一下整个文件的结构：

<!--/TbReview
├── 代码运行模式
│   ├── anki_sync_mac.sh
│   ├── anki_sync_win.bat
│   ├── anki.py
│   ├── config_mr.txt
│   ├── config.py
│   ├── flomo.py
│   ├── fupan.py
│   ├── TB_rul.txt
│   ├── gui_app_card.py
│   ├── gui_app.py
│   ├── review_time.txt
│   ├── TbReview_win.bat
│   ├── TbReview.app
├── Mac_App
│   ├── 01 pyinstaller打包
│   │   ├── build
│   │   ├── dist
│   │   │   ├── TbReview
│   │   │   ├── TbReview.app
│   │   ├── anki_sync_mac.sh
│   │   ├── anki_sync_win.bat
│   │   ├── anki.py
│   │   ├── app.icns
│   │   ├── config_mr.txt
│   │   ├── config.py
│   │   ├── flomo.py
│   │   ├── fupan.py
│   │   ├── gui_app_card.py
│   │   ├── gui_app.py
│   │   ├── gui_app.spec
│   │   ├── pyinstaller打包命令.txt
│   │   ├── requirements.txt
│   │   ├── review_time.txt
│   │   ├── setup.py
│   │   ├── TB_rul.txt
│   │   ├── TbReview.spec
│   ├── 02 cx_Freeze打包
│   │   ├── build
│   │   │   ├── exe.macosx-14.0-arm64-3.12
│   │   │   ├── TbReviewTool.app
│   │   ├── anki_sync_mac.sh
│   │   ├── anki_sync_win.bat
│   │   ├── anki.py
│   │   ├── app.icns
│   │   ├── build_log.txt
│   │   ├── config_mr.txt
│   │   ├── config.py
│   │   ├── flomo.py
│   │   ├── fupan.py
│   │   ├── gui_app_card.py
│   │   ├── gui_app.py
│   │   ├── requirements.txt
│   │   ├── review_time.txt
│   │   ├── setup.py
│   │   ├── TB_rul.txt
│   ├── 开箱即用（由于未知原因会闪退一次，会重新启动）
│       ├── TbReview.app
├── 操作类型字典.md
├── README.md-->

#### 2. 「代码运行模式」部分，指通过终端运行的方式

- 这部分可以满足个性化，可以进行云端自动化
- 使用的时候要将「代码运行模式」整个文件夹复制过去

- 提供几种运行的方式
  1. 终端运行gui_app.py
  2. **【推荐方式】**Automator制作的app，通过Automator修改一下里面的路径就可以点击即用了。如果有兴趣，可以**创建自定义 URL Scheme 来实现使用特定 URL 启动应用程序**。我自定义了URL Scheme，直接在TB创建图钉，添加url，复盘结束后点击即可运行程序，**体验相当丝滑**
  3. 提供了Windows的脚本运行方式，点击TbReview_win.bat即可。相应的要在gui_app.py中将anki_sync_mac.sh改成anki_sync_win.bat

#### 3. 「Mac_App」部分，指Mac系统的app可以点击即用

- 用了pyinstaller和 cx_Freeze两种打包方式
- pyinstaller打包了出现了一个小bug，就是点击app会先闪退一次，但是会重新启动。我估摸这应该是启动是加载什么东西失败了，一直找不到问题原因。不介意的，在「开箱即用」文件夹里
- cx_Freeze的打包方式很奇怪（**未知bug待解决**），打包的要么闪退，要么点击按钮没效果，但是进入「/Contents/MacOS」文件夹，点击数据文件是完全正常运行的
- 我把两种打包方式附带的微调后的文档也上传了，有兴趣的小伙伴可以试试，**找出解决方案也请告诉我一下**
- 另外，py2app的打包方式是我最开始试的，一直没成功过
- Windows的因为自己没有环境，就没打包，有兴趣的可以自己打包一下

### （二）功能说明

每个文件的功能逐个进行讲解

#### 「/代码运行模式」

1. fupan.py功能：将上次复盘结束时到运行该代码时之间的有修改记录的特定类型节点连接到「回顾」节点。
2. anki.py功能：将运行完fupan.py后到运行该代码之间的所有与「回顾」节点断开连接的特定类型节点制作成卡片发送至Anki中。
   - 卡片的逻辑：
     - 卡片正面：「洞见卡片」和「原则」两个类型的节点一定会有一个「问题卡片」类型的父节点，创建或修改的「洞见卡片」和「原则」两个类型的节点的父节点为卡片正面
     - 卡片背面：卡片正面即某个「问题卡片」类型的节点，会根据改节点查找其所有洞见卡片」和「原则」两个类型节点的内容（仅name）。
     - 牌组：「问题卡片」类型的节点一定会有一个「精进域」的类型的父节点。该父节点为牌组，牌组的路径是起始「精进域」类型节点，往上逐级查找父节点，排除不是「精进域」类型的
     - 每次创建卡片会将同一牌组下的相同卡片删除，保证卡片的内容是最新的

3. flomo.py功能：将运行完fupan.py后到运行该代码之间的所有与「回顾」节点断开连接的特定类型节点制作成卡片发送至flomo中。

   - 逻辑和anki的类似，牌组变成标签，卡片正面为第一句话，卡片背面是后续的内容，格式调整为markdown

   - 不过flomo的API不够友好，不支持所有格式输入，所以必须手动去flomo上按几下删除换行符和回车键。这个问题和flomo团队沟通过，目前没有优化计划。不过也好，强迫自己再去复盘一次

4. anki_sync_mac.sh和anki_sync_win.bat的功能一样，分别适用Mac和Windows。用来将anki卡片自动进行同步
5. config.py是参数配置文件，上面说的所有节点类型都可以进行自定义配置，以符合你们自己的习惯
6. config_mr.txt是参数配置的默认文件
7. TB_rul.txt是「回顾」节点的本地路径，方便可视化界面直接跳转到TB
8. gui_app.py功能，这是可视化的代码，用来调用上面的代码，具体功能在**<u>操作介绍</u>**中已经讲了，就不重复了。对界面不满意的可以在这个代码中进行优化
9. 其他说明：fupan.py代码，运行结束后获取现在时间，转化格式后写入review_time.txt。anki.py代码，读取review_time.txt的时间，作为起始时间。这样就避免当日没复盘结束的节点，被反复建卡，而且没复盘过，卡片也不精准

## 讲在最后

这个代码断断续续写了大概50来天，速度不快，主要自己对代码就懂点皮毛，我的「回顾」逻辑不一定适用其他人，写这个代码一是为自用，二是能够抛砖引玉，希望有更多的TB小工具出现，丰富大家的使用方式。

代码还有很多不完善的地方，特别是独立的App，希望有比较懂代码的大佬能够帮忙完善。

最后期待更多人的交流！

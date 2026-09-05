# paper-code-mapper

<p align="center">
  <strong>Paper Code Evidence Reader</strong><br/>
  Code-first research paper × GitHub repository walkthrough with evidence
</p>

`paper-code-mapper` 是一个面向科研论文与对应 GitHub 仓库的 ChatGPT Skill。

它不是从论文章节出发去“找几段对应代码”，而是先沿着**真实代码执行路径**阅读仓库，再恢复论文作者的**完整论证主线**，最后用**真实 PDF 原文截图、翻译、公式与实验**把两条路线连接起来。

> **一句话：给它论文 PDF + GitHub 仓库，它会生成一个可以离线打开的交互式 HTML Reader，帮助你真正读懂“代码怎么做、论文为什么这样做、证据到底支持到哪里”。**

---

# 1. 真实效果

下面不是设计稿，而是 `paper-code-mapper` 对 **AlphaSteer** 进行实际分析后生成的 Reader 截图。

## 1.1 代码逐条解析主界面

![Real AlphaSteer code reader](docs/images/real-code-reader-overview.jpg)

真实 Reader 中可以同时看到：

- 顶部：`阅读语言` 与 `原文 / 译文语言`
- 模式切换：`代码逐条解析` / `作者论证主线`
- 阅读工具：`按执行顺序读` / `阅读说明`
- 论文工具：`原文全页` / `截图译文目录`
- 左侧：真实 `代码文件 / 函数` 导航与搜索
- 中间：研究语境、源码、逐语句解释、执行后的状态变化
- 右侧：`变量释义` / `小例子` / `原文与译文`

## 1.2 代码旁边直接核对论文原文

![Real AlphaSteer paper evidence](docs/images/real-paper-evidence.jpg)

在真实 Reader 中，不需要离开代码页面去翻 PDF。右侧可以直接显示：

- 当前代码对应的 PDF 页码
- 原始 PDF 截图
- 当前 selected region
- 忠实中文翻译
- 原文 transcript
- 公式与段落上下文

这意味着你可以一边看：

```text
hidden_states[layer_idx][:, -1, :]
```

一边核对论文到底有没有说“最后一个 token”、作者如何定义 activation，以及代码实现是否与论文一致。

> 截图来自 AlphaSteer 的真实静态源码分析 Reader。它展示的是代码 / 论文证据审计结果，不代表已经运行或复现 AlphaSteer 的 GPU 实验。

---

# 2. 30 秒上手

## Step 1 — 准备两个输入

你通常只需要：

```text
① 论文 PDF
② 对应的 GitHub repository URL
```

例如：

```text
Use the attached AlphaSteer paper and
https://github.com/AlphaLab-USTC/AlphaSteer

Walk through the official execution path code first.
Explain the actual code statement by statement for a beginner,
trace tensor/state changes and effective configuration values,
then connect each implementation step to the paper's complete argument,
equations, experiments, limitations and original PDF evidence.

Build a Chinese/English offline HTML reader with real PDF screenshots
and faithful translations.
```

如果你只关心一个函数，也可以直接指定：

```text
Focus only on EmbeddingExtractor.extract_embeddings.
Explain which token position is actually used,
how hidden_states are indexed,
what the tensor shapes are,
and how this corresponds to the paper.
```

## Step 2 — 获得 HTML Reader

项目级解析完成后会得到类似：

```text
paper_code_reader.html
```

它是**自包含离线 HTML**。

```text
下载 HTML
   ↓
双击打开
   ↓
Chrome / Edge / Safari
   ↓
开始阅读
```

普通读者不需要：

- 启动 Flask / FastAPI
- 安装 Node.js
- 启动 Web Server
- 下载论文模型 checkpoint
- 跑 GPU 实验

HTML 是“阅读与证据审计界面”，不是论文模型本身。

---

# 3. 产品说明书：HTML 每个区域怎么用

下面以真实 AlphaSteer Reader 为例。

## 3.1 顶部双语言选择器

Reader 顶部有两个独立选择器：

```text
阅读语言              原文 / 译文语言
简体中文 ▼            简体中文 ▼
```

### `阅读语言`

控制整个教学层：

- 页面 UI
- 代码解释
- 变量释义
- 小例子
- Research context
- 作者论证主线

例如切换为 English 后，不只是按钮变成英文，**代码解释本身也会变成英文**。

### `原文 / 译文语言`

只控制论文证据区域旁边显示的文本：

```text
简体中文  → selected PDF region 的忠实翻译
English   → original-language transcript
```

不会修改：

- 源代码
- 变量名
- 公式
- 数值
- PDF 原图

---

## 3.2 `代码逐条解析`：真正从代码开始读

默认主模式是：

```text
代码逐条解析
```

这不是论文目录，而是一条真实代码阅读路线。

### 左侧：`代码文件 / 函数`

真实界面中的左栏会列出当前分析路径，例如 AlphaSteer：

```text
scripts/alphasteer.sh
    └── shell entrypoint

src/utils/embedding_utils.py
    └── EmbeddingExtractor.extract_embeddings

src/utils/steering_utils.py
    ├── null_space_projection_l
    └── cal_tilde_delta_with_regularization_l

src/utils/const.py
    └── AlphaSteer_STEERING_LAYERS

src/AlphaSteerModel/AlphaLlama.py
    └── ...
```

你可以：

- 点击文件 / 函数进入对应阅读单元
- 搜索文件名
- 搜索函数名
- 搜索变量名
- 顺着推荐 execution route 阅读

> 文件出现在 Reader 中，不代表它一定被 `main()` 调用。Skill 会区分主路径、辅助脚本、独立评估入口和工程工具。

---

## 3.3 `按执行顺序读`：不知道从哪开始时点这里

如果仓库较大，推荐先点顶部：

```text
按执行顺序读
```

它回答的是：

> “如果我要理解这个方法真正怎么运行，我应该按照什么顺序读？”

典型顺序是：

```text
launcher / shell
      ↓
configuration
      ↓
entrypoint
      ↓
data preparation
      ↓
core function / class
      ↓
tensor / state transformation
      ↓
model intervention
      ↓
generation / evaluation
```

对于 AlphaSteer，Reader 会把 activation extraction、null-space、steering matrix、runtime forward 等串成连续路径，而不是按论文 Section 1、2、3 排列。

---

## 3.4 中央 `研究语境`：先知道这段代码为什么重要

选择一个代码单元后，中间顶部会显示：

```text
这段代码在研究逻辑中的位置
```

它不是在重复论文摘要，而是在回答：

```text
这段代码解决哪个研究问题？
       ↓
它实现论文哪一步设计？
       ↓
它和前后代码是什么关系？
       ↓
有没有直接论文对应？
```

如果只是工程代码，也会明确标记没有直接 research claim，而不是强行对应某个公式。

---

## 3.5 Source statement + 代码解释

核心区域把**真实源码**和**逐语句解释**并列展示。

例如：

```python
embeddings = extractor.extract_embeddings(
    prompts=prompts,
    batch_size=args.batch_size,
    layers=layers,
)
```

Reader 不会只解释成：

```text
“调用 extract_embeddings 提取 embeddings”
```

而会继续解释：

```text
prompts 是什么
batch_size 从哪里来
layers 的有效值是什么
        ↓
函数内部真正读取什么 token 位置
        ↓
输出 tensor shape 是什么
        ↓
结果交给谁
```

每个重要 statement 尽量回答四件事：

| 项目 | Reader 回答什么 |
| --- | --- |
| `Source` | 真实源码是什么 |
| `Meaning` | Python / tensor 操作是什么意思 |
| `Why here` | 为什么当前计算流程需要这一步 |
| `Result` | 执行后变量、shape、state 或控制流发生什么变化 |

---

## 3.6 右侧 `变量释义`

点击：

```text
变量释义
```

可以快速查看当前代码单元里的关键变量。

AlphaSteer 示例：

```text
prompts
从选定数据列读取的 Python 字符串。

layers
要提取的层索引。

outputs.hidden_states
Transformer 各层 hidden-state 张量组成的集合。

H
按样本为第一维保存的激活张量。
```

这个区域适合零基础或第一次阅读陌生仓库时使用。

---

## 3.7 `小例子`：用 before / after 理解 tensor

当代码涉及：

- slicing
- reshape
- transpose
- matrix multiplication
- broadcast
- token shift
- mask

可以切到：

```text
小例子
```

例如：

```text
Before hidden state:
[B, T, D] = [2, 17, 4096]

[:, -1, :]

After:
[B, D] = [2, 4096]
```

这样不是只告诉你“取最后一个 token”，而是让你看到操作前后到底变了什么。

---

# 4. `原文与译文`：代码旁边直接审计论文证据

在右侧切换：

```text
原文与译文
```

就会出现第二张真实截图中的界面。

你会看到：

```text
论文页码
   ↓
原始 PDF selected region
   ↓
中文忠实翻译 / English transcript
```

例如 AlphaSteer Reader 中会显示：

```text
PDF 第 5 页
可学习 activation steering 与两项目标
```

并直接展示论文原图和公式。

### 为什么要保留真实 PDF 像素？

因为下面四件事不是一回事：

```text
Original PDF pixels
        ≠
Translation
        ≠
Author-argument interpretation
        ≠
Code explanation
```

Reader 会把它们分开，避免把模型自己的解释伪装成论文原文。

---

# 5. `原文全页` 与 `截图译文目录`

## `原文全页`

如果 selected region 太窄，可以点：

```text
原文全页
```

用于检查：

- 前后文限定条件
- 双栏论文上下文
- 公式前面的符号定义
- 图表附近的 caption / note

## `截图译文目录`

点击：

```text
截图译文目录
```

可以按 PDF 页码浏览 Reader 收录的所有证据区域，而不必逐个代码 block 查找。

适合：

- 快速浏览论文重点
- 检查所有 selected regions
- 集中阅读中文翻译
- 回到对应 code / argument

> 这里的翻译只对应 Reader 选择的 PDF region，并不代表整页或整篇论文已经全文翻译。

---

# 6. `作者论证主线`：回答“为什么这样做”

代码回答：

```text
HOW — 这个方法到底怎么实现？
```

点击顶部：

```text
作者论证主线
```

则切换到：

```text
WHY — 作者为什么提出这个设计？
```

这条路线和函数调用顺序是独立的。

典型结构：

```text
Problem / Observation
        ↓
Diagnosis / Hypothesis
        ↓
Method Design
        ↓
Experiment / Ablation
        ↓
Supported Conclusion
        ↓
Limitations / Missing Evidence
```

每个 argument node 会重点回答：

- 当前在解决什么问题
- 作者实际声称了什么
- 为什么这一点会引出下一步设计
- 哪段论文、公式、图表或实验支持它
- 当前证据**不能**证明什么
- 哪些真实代码实现 / 配置 / 测量了这个 claim

因此 Reader 不会因为“指标变好了”就自动写成“论文机制已被证明”。

---

# 7. Code ↔ Paper 双向阅读

推荐不要只沿一条路线读到底，而是来回跳转：

```text
代码逐条解析
      ↓
看懂真实 implementation
      ↓
研究语境
      ↓
作者论证主线
      ↓
论文原始证据
      ↓
回到对应代码
```

这也是 `paper-code-mapper` 和普通 paper-to-code 搜索工具最大的区别。

它保留两条独立路线：

```text
Code execution order
≠
Paper argument order
```

然后建立双向链接。

---

# 8. correspondence status 怎么读

Skill 不会笼统地写：

```text
“这段代码对应论文 Eq. 7”
```

而是给出更精确的状态：

| Status | 含义 |
| --- | --- |
| `Exact match` | 当前代码与论文描述直接一致 |
| `Equivalent implementation` | 写法 / tensor orientation 不同，但计算含义等价 |
| `Partial match` | 代码只覆盖论文描述的一部分 |
| `Runtime override` | 实际运行值覆盖默认配置或论文常用值 |
| `Implementation extension` | released code 比论文公开描述多做了一步 |
| `Potential mismatch` | 论文与代码存在值得进一步核对的不一致 |
| `No direct paper counterpart` | 工程代码，没有直接 research claim |
| `Unresolved` | 当前证据不足，不强行下结论 |

看到 `Potential mismatch` 或 `Unresolved` 时，建议打开 `原文与译文` / `原文全页` 再核对源码。

---

# 9. 推荐的 10 分钟阅读路线

第一次打开 Reader，可以这样用：

```text
01  选择阅读语言
      ↓
02  按执行顺序读
      ↓
03  从左侧进入第一个入口文件
      ↓
04  看研究语境
      ↓
05  Source + 逐语句代码解释
      ↓
06  变量释义 / 小例子
      ↓
07  切换作者论证主线
      ↓
08  打开原文与译文核对论文
      ↓
09  特别检查 Runtime override / Potential mismatch
      ↓
10  最后看 Limitations / Missing evidence
```

如果你的目标是：

> **“这篇论文的代码到底怎么跑？”**

优先看：

```text
按执行顺序读 + 代码逐条解析
```

如果你的目标是：

> **“released code 真的实现了论文说的东西吗？”**

优先看：

```text
作者论证主线
+ 原文与译文
+ correspondence status
```

---

# 10. AlphaSteer 示例

同一个 Reader 会保留两条路线。

### Code execution route

```text
scripts/alphasteer.sh
      ↓
activation extraction
      ↓
last-position hidden states
      ↓
benign null-space projector
      ↓
malicious regression
      ↓
steering matrix
      ↓
Llama runtime intervention
      ↓
generation
```

### Author argument route

```text
fixed refusal steering creates a safety–utility tradeoff
      ↓
steering should depend on model state
      ↓
benign behavior should lie in a protected null space
      ↓
malicious activations should be mapped toward refusal behavior
      ↓
apply the learned transformation at selected layers
      ↓
evaluate safety and utility
      ↓
state tested-scale limitations
```

两者会双向连接，但不会混成一条目录。

---

# 11. 作为 ChatGPT Skill 使用

核心入口：

```text
SKILL.md
```

UI metadata：

```text
agents/openai.yaml
```

仓库结构：

```text
paper-code-mapper/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
├── references/
├── assets/
├── docs/
│   └── images/
└── tests/
```

Skill name：

```text
paper-code-mapper
```

Display name：

```text
Paper Code Evidence Reader
```

---

# 12. 自己构建 Reader

> 对普通使用者来说，不需要手工执行下面这些命令。通常由 Skill 完成分析和构建。这里主要面向开发 / 二次开发。

## 12.1 渲染真实 PDF 区域

```bash
python scripts/render_sources.py \
  --pdf paper.pdf \
  --regions regions.json \
  --output-dir source_images
```

需要：

```text
PyMuPDF
Pillow
```

## 12.2 合并分析、截图与翻译

```bash
python scripts/merge_sources.py \
  --analysis analysis.json \
  --sources source_images/source_layer.json \
  --translations translations.json \
  --output analysis_bilingual.json
```

## 12.3 构建 HTML

```bash
python scripts/build_reader.py \
  --input analysis_bilingual.json \
  --output reader.html \
  --source-pdf paper.pdf \
  --report validation.json
```

如果有本地源码树，可以额外验证 verbatim source ranges：

```bash
python scripts/build_reader.py \
  --input analysis_bilingual.json \
  --repo-root /path/to/repository \
  --output reader.html \
  --source-pdf paper.pdf \
  --report validation.json
```

---

# 13. 使用边界

本 Skill 默认优先进行**静态源码检查**。

不会为了生成 Reader 自动：

- 安装未知科研仓库依赖
- 下载大型 checkpoint
- 启动 GPU 实验
- 执行未知 launcher
- 声称复现论文结果

需要特别区分：

```text
Correct implementation ≠ Reproduced result

Better metric ≠ Proven mechanism

Function definition ≠ Function execution

Call edge ≠ Argument edge
```

如果只做了静态源码检查，Reader 会明确写“static source inspection”。

---

# 14. 适合谁

适合：

- 第一次阅读陌生科研仓库
- 论文 + GitHub 精读
- 复现前代码审计
- AI / LLM / CV / NLP 方法代码学习
- activation / hidden state / attention / loss / token 计算追踪
- 检查 paper implementation 与 released code 是否一致
- 给零基础或跨方向研究者制作交互式科研阅读材料

不适合把它当成：

- 自动跑通任意论文的 reproduction framework
- 普通论文摘要器
- 根据函数名猜公式的 mapper
- 自动证明论文机制正确的工具

---

## Status

当前重点支持：

- Code-first statement-level reading
- Full author-argument track
- Bidirectional paper-code mapping
- Real PDF evidence regions
- Faithful translation / source transcript
- Simplified Chinese + English reading locales
- Offline self-contained HTML Reader
- Source / schema / language validation

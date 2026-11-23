---
name: olah-style-work-notes
description: Faithfully transform authorized, sanitized meeting transcripts, spoken work notes and weekly summaries into traceable Olah-inspired visual HTML articles with original SVG, topic/time indexing, privacy gates and browser QA.
---

# Olah-style Work Notes · 工作会议可视化整理 Skill

使命：**听懂工作发生了什么、达成了什么、什么尚未确认，再让复杂的协作关系变得可见。**

参考 xm-journal 的文档结构和 Olah-style-posts 渐进解释法。本 Skill 不是“套漂亮 HTML”的提示词，而是一套含隐私、语义拆解、来源、叙事、可视化、测试、发布的强制生产流程。

## 适用输入

- 今天 / 本周工作口述；会议录音经用户提供的转写；会议纪要片段；项目讨论摘要。
- 用户可提供日期、地点、角色、项目主题、希望强调的问题和脱敏后的可发布内容。
- 没有输入不虚构工作会议。不自动访问企业协作平台或识别用户未提供的录音。

## 输出契约

在得到明确公开授权后：
1. notes/daily、notes/meetings 或 notes/weekly 目录下的一份**脱敏、可公开** Markdown 原稿。
2. posts/YYYY/MM/YYYY-MM-DD-slug/index.html（一个 h1，独立可读）。
3. posts/.../assets/*.svg（仅在确实帮助解释时生成原创图）。
4. posts/.../evidence.json（声明与来源、未经确认的信息、发布许可）。
5. 自动生成日期 × 主题 × 类型首页，并通过结构与浏览器检查。

未取得明确授权时：**只在当前对话或用户指定的私有空间内提供待审阅草稿，不触碰公开仓库。**

## 7 道 Gate

### Gate 0 — 保密与授权

先阅读 AGENTS.md、docs/privacy.md。默认 private。识别客户/个人信息、内部链接、金额、专利、密钥及安全细节；未公开内容不进入本仓库。录音文字的“可处理”不等于“可上传”。

### Gate 1 — 口述事实地图

按 references/input-processing.md 分类为 事实 / 提议 / 观点 / 分歧 / 明确决定 / 行动 / 未确认，并标记时间轴和说话人不确定性。记录“是谁明确说的”与“我们推断”的区分；保留必要上下文但避免逐字铺排。不得发明参会人、数字和期限。

### Gate 2 — 信息架构

会议：议题 → 已知背景 → 决策条件 → 备选方案与不同意见 → 已确定结论 → 下一步。
每日：日内事件 → 重要工作主线 → 阻力或转折 → 下一步。
每周：多个来源的关系 → 关键进展 → 持续障碍 → 后续重点（不虚构完成度）。

一条记录有一个可解释主线、2–5 个有信息量的章节；跨日内容可以链接，不复制多份全文。

### Gate 3 — 视觉故事板

优先画：输入到输出流程、利益相关方/依赖关系、问题树、决策分支、系统机制、明确日期的时间线或风险分层。先写出“此图帮助读者回答什么问题”，再绘制 SVG。没有量化证据就**不绘制量化曲线或进度百分比**。参考 references/visualization.md。

### Gate 4 — HTML 制作

使用 assets/templates/article.html 作为可审计起点（默认 private/unreviewed），按具体内容替换所有占位与图解，不得直接发布模板占位图；详见 docs/publishing.md。

用语义 HTML、段落分层、文章目录和图注；原创 SVG 必须 viewBox/title/desc；桌面、移动端和打印都可读；JS 只做有意义交互，脱离 JS 仍须可读；本地资源、无需第三方网络。每个文章可拥有独立配色/结构，但共享可访问性规范。

### Gate 5 — 证据与纠错

参考 references/provenance.md。建立 evidence.json，列出 claim ids、来源记录与性质。用户口述的事实用“据该次转写”，编辑综合用“归纳”；外部信息需要独立核实并附链接。分歧仍分歧，建议仍建议，计划仍计划；无法核实标记待确认。

### Gate 6 — 构建和 QA

~~~bash
python -m unittest discover -s tests -v
python scripts/build_site.py
python scripts/validate_site.py
python scripts/browser_qa.py
~~~

验证全部文章及首页；浏览器不可用须明确 NOT VERIFIED；在合并前检查每个文件的隐私风险。

### Gate 7 — 经许可发布

用户明确同意**具体脱敏版本**公开后，才提交。CI 通过后才合并，Pages 成功后才声明上线。新增内容不需要手工修改首页计数。没有批准不写入 Git，即使仅在 PR 分支也不行。

## HTML metadata contract

~~~html
<meta name="notes:title" content="标题">
<meta name="notes:date" content="2026-11-24">
<meta name="notes:summary" content="可公开的摘要">
<meta name="notes:kind" content="meeting">
<meta name="notes:topics" content="engineering,collaboration">
<meta name="notes:tags" content="架构,决策">
<meta name="notes:source" content="notes/meetings/2026/11/2026-11-24-topic.md">
<meta name="notes:visibility" content="public">
<meta name="notes:release" content="approved">
~~~

路径使用 posts/YYYY/MM/YYYY-MM-DD-slug/index.html；evidence.json 需要 release.approved=true / audience=public。所有文本以适合公开的脱敏内容为前提。

## 技术与风格边界

拒绝把长录音压成没有依据的任务看板、制造似是而非的指标、用汇报套话掩盖争议，或在用户未许可的情况下推送公开 GitHub。借鉴渐进解释而非复制上游受保护图文。

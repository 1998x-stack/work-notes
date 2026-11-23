# 体系结构：从工作输入到可视化知识档案

## 借鉴与差异

延续 xm-journal 的 AGENTS / Skill / Markdown 原稿 / posts / evidence / 静态首页 / tests / Pages 组织方式，但在工作场景加入多条目/日、主题 taxonomy、类型过滤、行动归属边界及明确的公开发布门禁。

## 数据流

~~~text
用户主动提供录音转写/工作描述
  → 本地或会话内保密分级（默认 private）
  → ASR 纠错与语义切片（不猜测说话人）
  → 来源与声明分层（事实/提议/决定/疑问/行动）
  → Markdown 记录、保留审阅状态
  → 授权公开的脱敏版本（写入 notes/）
  → 文章脚本与独有 SVG + evidence.json（写入 posts/）
  → Python build_site 发现文章、解析 notes:* 元数据
  → 发布门禁（release.approved、source、安全结构）
  → 生成首页、逐月索引、主题筛选数据
  → 单测 / 静态验证 / 浏览器 QA
  → GitHub Pages
~~~

## 目录语义

- notes/daily/YYYY/MM/YYYY-MM-DD.md：每日多事件归纳。
- notes/meetings/YYYY/MM/YYYY-MM-DD-slug.md：单个会议记录；与原始录音分离。
- notes/weekly/YYYY/YYYY-Www.md：跨日工作线索，明确日期跨度。
- posts/YYYY/MM/YYYY-MM-DD-slug/index.html：供公开阅读的独立 HTML 页面，每份记录独立视觉结构。
- posts/.../evidence.json：来源、statement id、公开审阅标记，及已知不确定性。
- site/index.html：静态模板；关键内容 JS 关闭仍可阅读。
- _site：构建产物，不纳入版本管理。

## 发布门禁

脚本要求 notes:visibility=public、notes:release=approved；证据文件 release.approved=true / audience=public 且 source 指向仓库中存在的脱敏 Markdown 原稿。机器门禁只能验证约定，**不能证明用户确实授权**，必须由 Agent 在 Git 写入前独立核实。

## 构建特点

不需要数据库、后端、Google Analytics、CDN、密钥或外部 API。按月分组构建，客户端同时支持全文关键字、年-月、日期范围、类型、主题组合过滤；URL query string 可复现筛选；原 HTML 卡片可被无 JS 浏览器阅读。

## 非目标

不会自动录音或接入企业微信、飞书、邮箱、Calendar；不会监控员工活动；不会把内部资料保存在此公共仓库；不会在无授权情况下生成周报公开发布。

## 后续扩展

若需要真正的内部会议知识库，应使用私有仓库或企业私有存储 + SSO/RBAC + 审批与审计日志，将公开站点作为单独脱敏发布通道，而不是给公开 GitHub Pages 叠加前端密码框。

# 发布一篇新的工作视觉笔记

## 0. 从非公开环境开始

首先读取 AGENTS.md、docs/privacy.md 和 Skill。会议音频/完整转写仅在用户授权的私有环境进行处理，不应在公开 GitHub PR、Issue、Discussion 或提交记录里出现。

## 1. 语义与事实核验

- 明确日期/时区、是否真实会议、公开范围。
- 形成 facts、proposals、decisions、disagreements、open_questions、actions、synthesis 列表。
- 对说话人、截止日期、数量和项目名等 ASR 易错点做核实，不能瞎补。
- 按用户要求整理成**待审阅** Markdown；在公开授权之前**不提交**至此仓库。

## 2. 取得明确公开许可

用户需要确认最终脱敏版本可以公开，并核对图中可能暴露的内部关系。若用户只说“帮忙做成网页”，仍不可假定允许公开。记录实际许可事实，不自行生成假许可。

## 3. 根据模板构建

- 复制 skills/olah-style-work-notes/assets/templates/article.html 的结构。
- 脱敏 Markdown 存入 notes/meetings/YYYY/MM/YYYY-MM-DD-slug.md，或对应 daily / weekly 目录。
- 正式 HTML 存入 posts/YYYY/MM/YYYY-MM-DD-slug/index.html。
- 替换所有 __PLACEHOLDER__，并校验 html 转义、图语义及页面样式；文章路径一定带日期前缀，可同日多篇。
- 原创 SVG 存入该篇 posts/.../assets/；使用相对链接；viewBox、title、desc、figcaption 完整。
- 在 HTML head 写 notes:* 元数据。kind 使用 data/taxonomy.json 中 meeting/daily/weekly/project 之一；topics 使用 1—3 个受控 slug。
- 在 posts/.../evidence.json 记录 source.id、source.path、claims、release 信息，与 Markdown source 精确对应。
- 仅用户实际批准后才把 notes:visibility 改为 public、notes:release 改为 approved，并写入 release.approved=true / audience=public / approval_record。批准不足时仍保持 private/unreviewed，**且不提交真实内容**。

## 4. 质量门禁

~~~bash
python -m unittest discover -s tests -v
python scripts/build_site.py
python scripts/validate_site.py
python scripts/browser_qa.py
~~~

- 本地检查能发现来源缺失、未经批准标记、分类错误、无效日期、资源断链等。
- CI 不替代人工脱敏审阅；敏感内容只要已被 push 就可能永久泄露。
- PR green 以后才考虑合并；完成 Pages deploy 后才报告已上线。

## 5. 支持今天与本周

今天：记录实际日期，多个会议各占一篇；日记可写总览并关联相关会议。

本周：以 week YYYY-Www、period_start/end 标明覆盖范围，不把每条会议内容硬拷贝到周报；选择跨日依赖、已解决问题与仍需核实的动作，并给出可追溯来源。

## 6. 示例与真实数据边界

site/demo.html 是合成设计演示，examples/synthetic-meeting.md 也完全虚构。两者不自动进入公开笔记计数。不要复制其中的“会议结论”冒充真实事实。

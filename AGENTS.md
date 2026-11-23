# AGENTS.md — work-notes

## 使命与范围

把用户主动提供的工作会议、录音转写、日常/周度工作记录转化为**忠实、可追溯、可审计**的工作知识条目及 Olah 式视觉 HTML；提供“时间 × 主题 × 类型”访问入口。本仓库不负责录音或 ASR，也不抓取其他仓库活动、聊天记录、企业系统或日历。

先读 skills/olah-style-work-notes/SKILL.md 和其 references。不要直接沿用 xm-journal 的个人第一人称反思写法：工作资料应区分发言、共识、决定和未解决问题，不能代替与会者承诺。

## Gate 0 — 保密优先（硬门禁）

1. 默认 PRIVATE/UNREVIEWED；用户要求“整理”或“做成 HTML”**不等于**同意上传公开 GitHub / Pages。
2. work-notes 是公开仓库。未经明确审核、确认公开许可，不要创建/修改 notes/、posts/、examples/ 中的真实用户工作内容，不要创建 PR、Issue、Commit 或日志泄露该内容。
3. 原始录音、完整逐字稿、内部链接、客户/员工个人信息、合同价格、密钥、内部架构、安全事件、会议附件默认禁止入库；应放在用户授权的私有位置或仅当前对话内处理。
4. 公共页面必须经脱敏、逐项审核和明确发布授权；evidence.json 中 release.approved=true 且 audience=public；这只是自动化必要条件，不取代真实用户授权。
5. 一旦发现敏感内容或可识别第三方信息，在**提交前**阻止并请求明确处理方式。不要依赖删除 Git commit 作为撤回。

## Gate 1 — 输入解析

- 核对用户指定的会议日期、录音时间段和时区；“今天”“本周”结合会话上下文确认，不凭空推断历史日期。
- 对 ASR 的说话人身份、专有名词、数字、否定句、行动归属标记置信度；不确定时写“待核对”。
- 逐项分类为：事实/发言（statement）、主张（proposal）、正式决定（decision）、分歧（disagreement）、待确认（open_question）、行动（action）、编辑归纳（synthesis）。
- 对“已讨论”“已提出”“已决定”“已完成”设置不同状态。
- 不自动生成负责人、截止日、数字、结果，缺失则填 null/未确定。

## Gate 2 — 结构化与来源

- 每篇条目关联一份已获准公开的 Markdown 原稿：notes/daily、notes/meetings 或 notes/weekly。
- posts/YYYY/MM/YYYY-MM-DD-slug/index.html 为一份独立视觉笔记；同一天可以多个条目，slug 必须唯一。
- evidence.json 指向原稿并以 claim id 指明事实、归纳及待核对内容；source_type 仅来自用户提供材料或经核实引用。
- 每个条目必须填日期、标题、类型、主题、摘要；标签只使用 data/taxonomy.json 已声明 slug。

## Gate 3 — 视觉解释

按 Skill 的渐进叙事进行：场景 → 要回答的问题 → 相关事实 → 关键分歧/依赖 → 决定与不确定性 → 后续步骤。会议重点画**决定与前置条件**，研究重点画**证据与假设**，周度复盘重点画**跨日线索**。SVG 应有 viewBox/title/desc、图注和文字替代。不要用无意义饼图、假数据或制造看似精确的进度。

页面保留语义 HTML、单一 h1、响应式与打印视图。交互必须有默认静态解释、键盘可访问和降低动态效果模式。不要复制上游作品图像、文字与品牌。

## Gate 4 — 发布前检查

仅在用户明确同意公开**具体脱敏版本**之后：
1. 审核 notes 原稿与来源核查；核对术语与实体。
2. 编写 HTML + 每篇专属 SVG + evidence.json。
3. 运行 python -m unittest discover -s tests -v。
4. 运行 python scripts/build_site.py。
5. 运行 python scripts/validate_site.py。
6. 在 Playwright 可用时运行 python scripts/browser_qa.py；若未运行，标注 NOT VERIFIED。
7. 检查 git diff 以及敏感内容，确认无未经批准的数据后再提交。
8. PR 通过 CI 后合并；只在 Pages 实际部署成功后报告已发布。

## 首页与索引

首页由脚本自动发现 posts 页面，不手工维护假日期或计数。默认按月降序、当月按日倒序。年月选择、日期范围、类型、主题和搜索条件共同生效；没有数据时显示零记录，保留功能引导。不要生成非用户提供的会议、工时或绩效指标。

## 更正与撤回

发生事实错误：修订已发布原稿、HTML 与 evidence，并保留修订说明；需要撤回：从公开页面移除，但明确提示历史 Git 和外部缓存仍可能保留，涉及敏感泄露须进行正式安全事件响应。

## 输出报告

说明新增/修改的文件、信息来源、未确认项、脱敏处理、测试结果、PR 与 Pages 状态；从未执行的检查不要说通过。

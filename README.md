# work-notes · 工作知识与会议可视化档案

**把工作口述、会议转写和阶段思考，整理为有证据、有结构、可回看的视觉笔记。**

[项目首页（Pages 启用并部署后访问）](https://1998x-stack.github.io/work-notes/) · [核心 Skill](skills/olah-style-work-notes/SKILL.md) · [Agent 规则](AGENTS.md)

work-notes 参考 [xm-journal](https://github.com/1998x-stack/xm-journal) 的“原稿 → Olah 式渐进解释 → 独立 HTML/SVG → 自动索引”组织方式，但专门服务工作会议、录音转写、日常工作笔记及周度归纳。**公开仓库不等于内部知识库：默认不发布任何新材料。**

## 产品目标

- **双轴首页**：按日期（年、月、日期范围）和主题（产品、工程、协作、运营、研究、管理）检索，会议、日记、周复盘按类型过滤。
- **一个来源，一份可审计原稿**：把口述中事实、观点、决定、行动、待确认项分离，保留可追溯的说话内容与不确定性。
- **一份记录，一篇视觉 HTML**：使用原创 SVG 呈现会议决策路径、依赖关系、风险分歧、时间线及行动闭环；不把所有会议塞进同一固定模板。
- **审核后公开**：没有明确公开授权和脱敏检查的笔记，只能留在非公开工作区，不能进入 GitHub 仓库或 Pages。
- **可复现构建**：文章索引从 posts 目录自动发现，不手工维护日期列表，不抓取外部账号活动。

## 输入与产出

你可以直接提供今天/本周的会议转写、录音摘要或自然口述，并说明日期及是否允许公开。语音识别不由本仓库负责；先通过你选择的 ASR 得到转写文本。

~~~text
录音 / 转写 / 会议纪要
       ↓  先做保密与发布分级（默认 PRIVATE）
语义分段、说话人不确定性、时间轴、观点和证据
       ↓
事实 / 争议 / 决策 / 待确认 / 行动项（负责人、截止日未知则留空）
       ↓
审核过的 Markdown 原稿（notes/）
       ↓  仅在获得明确公开授权后
Olah 风格 HTML + SVG + evidence.json（posts/）
       ↓
日期 × 主题 × 类型索引（自动生成）
       ↓
测试、检查、GitHub Pages
~~~

**特别说明：** 原始录音、逐字转写、内部会议附件、客户名单、内部网址及凭据不能直接放在此公开仓库。本项目的 notes/ 仅保存获准公开的整理稿。

## 项目结构

~~~text
work-notes/
├── AGENTS.md                                  # Agent 行为规范
├── README.md
├── data/taxonomy.json                         # 主题与类型字典
├── notes/
│   ├── daily/YYYY/MM/YYYY-MM-DD.md            # 获准公开的每日稿
│   ├── meetings/YYYY/MM/YYYY-MM-DD-slug.md    # 获准公开的会议稿
│   ├── weekly/YYYY/YYYY-Www.md                # 获准公开的周度稿
│   └── templates/                            # 三类 Markdown 模板
├── posts/YYYY/MM/YYYY-MM-DD-slug/
│   ├── index.html                             # 单篇视觉文章
│   ├── evidence.json                          # 引用与审批记录
│   └── assets/*.svg                           # 独立可视化图解
├── site/                                       # 首页模板 / CSS / JS / 示例页
├── skills/olah-style-work-notes/              # 核心内容生产 Skill
├── scripts/build_site.py                      # 自动索引与生成 _site
├── scripts/validate_site.py                   # 内容校验与发布门禁
├── scripts/browser_qa.py                      # Chromium 视图与交互验证
├── tests/                                      # 标准库单元测试
├── examples/                                   # 全为合成的非真实会议示例
└── .github/workflows/pages.yml                # CI 与 Pages 部署
~~~

## 使用示例

在 ChatGPT 中发送：

> 请按 work-notes 仓库的 AGENTS.md 和 skills/olah-style-work-notes/SKILL.md 整理以下 2026-11-24 的会议转写。先输出事实、决定、待确认、行动项以及隐私风险。尚未授权公开，不要写入公开 GitHub 仓库。

审核内容后，**另行明确授权**哪些部分适合公开，才执行 HTML 生成与提交。不要将“让我整理会议”和“允许公开会议”视为同一件事。

## 本地构建和验收

Python 3.11+；构建、静态验证和单测不需要第三方 Python 包。

~~~bash
python -m unittest discover -s tests -v
python scripts/build_site.py
python scripts/validate_site.py

# 可选的真实浏览器 QA
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/browser_qa.py

cd _site && python -m http.server 8000
~~~

站点入口 http://localhost:8000 。仓库尚无获准公开的真实笔记时，首页显示诚实的零数据引导，不伪造会议或成果。可以在首页查看标注为“合成演示”的视觉文章示例。

## 发布

PR 只执行测试与构建；合并 main 后由 Pages workflow 发布。首次使用须在仓库 Settings → Pages 中把 Source 配置为 GitHub Actions。部署成功以 GitHub Actions / Pages 实际运行结果为准。

## 内容和安全边界

- **默认不公开**。保密、内部或含第三方敏感信息的记录应进入有访问控制的私有系统，不应出现在本仓库任何提交历史中。
- 不补造参会人、承诺、期限、投票结果、分歧或会议结论。AI 归纳需标为编辑性综合。
- 不把讨论中的建议自动升级成已决定事项，不把“希望”“可能”变成完成事实。
- 不外呼 ASR 或 LLM 服务处理录音；本仓库只接收主动提供并审核的内容，不设无人值守采集。
- 本项目是知识归档与可视化，不是员工工作时长或绩效监控系统。

## 参考

[xm-journal](https://github.com/1998x-stack/xm-journal) 的组织方式及 [Olah-style-posts](https://github.com/1998x-stack/Olah-style-posts) 的渐进解释原则；本站所有文字、图解、样式与实现为重新设计。

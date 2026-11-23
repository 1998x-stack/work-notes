# 保密、资料治理与发布审核

此仓库和 Pages 均可能对公众可见。任何加入 Git 历史的资料，即使之后删除，也可能仍保留于镜像、Fork、索引与缓存。网页“隐藏”不等于访问控制。

## 分类

| 级别 | 示例 | 允许提交公开 work-notes? |
| --- | --- | --- |
| PRIVATE（默认） | 完整录音、未经审阅转写、内部会议、客户资料 | 绝不 |
| REVIEW（整理中） | 未经核对的纪要、未达成共识的推断 | 绝不 |
| PUBLIC-APPROVED | 用户明确批准的脱敏版本 | 可，检查后 |

## 审阅清单

- 明确哪一份脱敏版本可公开；别把“帮我整理”当作“发布”。
- 删除或替代个人姓名、电话、邮箱、员工号、客户名称、合同与报价、内部域名和访问令牌。
- 对安全架构、商业计划、法律事项、未披露绩效等内容先做更严格的人工审阅。
- 不保留原始转写/音频 URL 或敏感原文摘要片段在 PR、Issue、commit message、CI 日志、Git LFS 中。
- 不确定是会议决定还是个人提议，一律标记待确认。
- 检查 SVG 内的文字和 source evidence：隐私风险不只存在正文。
- 删除公开内容前应说明历史不可完全擦除，必要时升级安全处理。

## evidence.json 约定

~~~json
{
  "schema_version": 1,
  "source": {"id": "public-sanitized-note-id", "type": "user-reviewed-summary", "path": "notes/meetings/YYYY/MM/YYYY-MM-DD-topic.md"},
  "release": {"approved": true, "audience": "public", "approval_record": "由用户在发布时明确批准的脱敏版本"},
  "claims": [{"id": "C1", "kind": "user-statement", "source_id": "public-sanitized-note-id", "confidence": "confirmed"}]
}
~~~

approval_record 只是审批记录说明；模型不得自行填写虚假审批。实际授权需在提交前进行核验。

## 如何安全使用

新录音先在对话/被授权私有环境中生成待审核摘要，保持公开 repo 无变化。只有用户明确批准*特定*可公开文本之后，才创建 notes/、posts/ 文件及 PR。

对于长期内部归档，请使用 private repo 与有访问权限的存储；不要将 GitHub Pages 误用为内部保密系统。

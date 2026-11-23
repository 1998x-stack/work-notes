# 来源与审批模型

## Claim-level traceability

每条重要内容带 claim_id，可选 source_marker 指向用户原文片段的非敏感编号。kind 建议取 user-statement / editorial-synthesis / externally-verified / open-question。confidence 使用 confirmed / uncertain / inferred；推断不得误写为用户原话。

## 区分事实层级

- 与会者提出方案 ≠ 会议同意方案。
- 暂定计划 ≠ 已经完成的工作。
- 转写出现名称 ≠ 已可靠确定说话人身份。
- 两份来源不同 ≠ 允许 AI 自动判断哪份一定正确。

## 可公开证据 JSON

~~~json
{
  "schema_version": 1,
  "source": {"id": "public-note-1", "type": "user-reviewed-summary", "path": "notes/meetings/2026/11/2026-11-24-example.md"},
  "release": {"approved": true, "audience": "public", "approval_record": "用户对当前脱敏版本的明确授权"},
  "claims": [
    {"id": "C1", "kind": "user-statement", "source_id": "public-note-1", "confidence": "confirmed"}
  ]
}
~~~

审批记录只能按实际授权填写，不能凭生成流程自动赋值。公开证据不应包含原始私有转写，也不应引用不可访问的内部系统链接。

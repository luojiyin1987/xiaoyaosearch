# 飞书文档插件

识别从飞书导出的 Markdown 文档并提取元数据信息。

---

## 功能特点

- **零配置**：自动识别飞书导出格式，无需配置文件
- **性能优化**：仅解析文件末尾500字符，对扫描性能影响<1%
- **容错友好**：解析失败不影响文件索引
- **原文跳转**：搜索结果可跳转到飞书原文

---

## 使用方法

### 1. 从飞书导出文档

1. 打开飞书文档
2. 点击右上角 **"..."** 菜单
3. 选择 **"导出为 Markdown"**

### 2. 放置到本地目录

将导出的 Markdown 文件放置到扫描目录（如 `D:/Documents/feishu_docs/`）

### 3. 构建索引

```bash
# API 调用
POST /api/index/create
{
  "folder_path": "D:/Documents/feishu_docs",
  "recursive": true
}
```

### 4. 搜索验证

```bash
# API 调用
POST /api/search
{
  "query": "搜索关键词"
}
```

搜索结果将显示 **"飞书"** 来源标识（紫色），并支持点击跳转到原文。

---

## 支持的格式

飞书导出的 Markdown 文档末尾包含以下元数据：

```markdown
---
> 更新: 2026-03-30 02:52:46
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/MZKMwqpljiod1ak38Cscnr8hnkh>
---
```

---

## 常见问题

### Q: 飞书元数据解析失败怎么办？

A: 解析失败不影响文件索引，只是 `source_type` 为 `"filesystem"`（本地文件）。检查导出格式是否完整。

### Q: 支持哪些飞书文档类型？

A: 支持所有能导出为 Markdown 的飞书文档类型（Wiki、常规文档等）。

### Q: 原文链接会过期吗？

A: 如果您有飞书文档的访问权限，原文链接长期有效。权限变更可能导致链接失效。

### Q: 可以批量导出飞书文档吗？

A: 飞书支持批量导出，导出后的文件放到同一目录即可被识别。

---

## 技术实现

### 元数据解析

```python
# 仅读取文件末尾 500 字符
content_tail = content[-500:]

# 正则表达式匹配
pattern = r'>\s*来源类型:\s*feishu\s*>?\s*原文:\s*<(https://[^\s>]+)>'
```

### 性能指标

| 指标 | 目标值 |
|-----|-------|
| 单文件解析时间 | < 1ms |
| 扫描性能影响 | < 1% |

---

## 版本信息

- **版本**: 1.0.0
- **作者**: XiaoyaoSearch Team
- **更新日期**: 2026-03-31

---

## 相关文档

- [PRD文档](../../../../docs/特性开发/plugins+feishu/plugins+feishu-01-prd.md)
- [技术方案](../../../../docs/特性开发/plugins+feishu/plugins+feishu-03-技术方案.md)
- [实施步骤](../../../../docs/特性开发/plugins+feishu/plugins+feishu-实施方案.md)

# 钉钉文档插件

识别钉钉导出工具生成的 `.xyddjson` 元数据文件并提取文档信息。

## 使用方法

### 1. 安装钉钉导出工具

1. 安装钉钉导出浏览器插件
2. 登录钉钉账号

### 2. 导出钉钉文档

1. 打开钉钉文档
2. 点击导出按钮
3. 选择导出格式（.docx、.pdf等）
4. 导出工具自动生成 `.xyddjson` 元数据文件

### 3. 放置到本地目录

将导出的文件放置到扫描目录（如 `D:/Documents/dingding_docs/`）

### 4. 构建索引

```bash
POST /api/index/create
{
  "folder_path": "D:/Documents/dingding_docs",
  "recursive": true
}
```

### 5. 搜索验证

```bash
POST /api/search
{
  "query": "搜索关键词"
}
```

---

## .xyddjson 格式

钉钉导出工具会自动生成同名元数据文件：

**文件示例**：
- `项目报告.docx` (导出文件)
- `项目报告.docx.xyddjson` (元数据文件)

**元数据格式**：
```json
{
  "version": "1.0.0",
  "source": "dingtalk-docs",
  "exportTool": "xiaoyaosearch-dingding-export",
  "exportToolVersion": "1.0.0",
  "exportTime": "2026-04-08T15:30:00.000Z",
  "file": {
    "fileName": "项目报告.docx",
    "originalName": "项目报告",
    "dentryUuid": "A1B2C3D4E5F6G7H8",
    "dentryKey": "key_abc123",
    "docKey": "doc_xyz789",
    "url": "https://alidocs.dingtalk.com/i/nodes/A1B2C3D4E5F6G7H8",
    "fileSize": 24576,
    "extension": "adoc",
    "exportFormat": ".docx",
    "contentType": "alidoc"
  }
}
```

**字段说明**：

| 字段路径 | 类型 | 必填 | 说明 | 示例值 |
|---------|------|------|------|--------|
| `version` | string | 是 | 元数据格式版本 | `"1.0.0"` |
| `source` | string | 是 | 数据来源标识 | `"dingtalk-docs"` |
| `exportTime` | string | 是 | 导出时间（ISO 8601） | `"2026-04-08T15:30:00.000Z"` |
| `file.fileName` | string | 是 | 导出后的文件名 | `"项目报告.docx"` |
| `file.originalName` | string | 是 | 钉钉文档原始名称 | `"项目报告"` |
| `file.dentryUuid` | string | 是 | 钉钉文档唯一ID | `"A1B2C3D4E5F6G7H8"` |
| `file.url` | string | 是 | 钉钉文档访问地址 | `"https://alidocs.dingtalk.com/i/nodes/..."` |

---

## 特性

- ✅ **零配置**：自动识别 `.xyddjson` 元数据文件
- ✅ **性能优化**：独立元数据文件，解析速度快
- ✅ **容错友好**：解析失败不影响文件索引
- ✅ **原文跳转**：搜索结果可跳转到钉钉原文
- ✅ **可扩展**：`.xyddjson` 格式可用于其他平台

---

## 目录结构示例

```
D:\我的文档\钉钉导出\
├── 工作文档\
│   ├── 项目文档\
│   │   ├── 需求文档.docx
│   │   ├── 需求文档.docx.xyddjson      ← 元数据文件
│   │   ├── 技术方案.docx
│   │   └── 技术方案.docx.xyddjson      ← 元数据文件
│   └── 会议纪要\
│       ├── 周会记录.docx
│       ├── 周会记录.docx.xyddjson
│       ├── 产品讨论.pdf
│       └── 产品讨论.pdf.xyddjson
└── 市场文档\
    ├── 竞品分析.pdf
    └── 竞品分析.pdf.xyddjson
```

---

## 与飞书方案对比

| 对比项 | 飞书 | 钉钉 | 钉钉优势 |
|-------|------|------|----------|
| 元数据位置 | 文件内容末尾 | 独立JSON文件 | 结构化、易维护 |
| 解析方式 | 正则表达式 | JSON解析 | 更可靠、更快速 |
| 解析性能 | ~1ms | <1ms | 更快 |
| 可扩展性 | 仅限飞书 | 可用于其他平台 | 通用性强 |

---

## 常见问题

**Q: 可以删除 .xyddjson 文件吗？**

A: 可以删除，但删除后文档将无法被识别为钉钉数据源，会被当作普通本地文件处理。

---

**Q: 元数据解析失败怎么办？**

A: 解析失败不影响文件索引，只是 source_type 为 "filesystem"。检查 `.xyddjson` 文件是否存在且格式正确。

---

**Q: 原文链接会过期吗？**

A: 如果您有钉钉文档的访问权限，原文链接长期有效。权限变更可能导致链接失效。

---

**Q: .xyddjson 文件会占用多少存储空间？**

A: 每个 `.xyddjson` 文件约 1KB，对存储空间影响很小（约 5% 增加）。

---

**Q: 为什么选择独立的元数据文件而不是嵌入文件内容？**

A: 独立元数据文件有以下优势：
1. 结构化JSON格式，解析更可靠
2. 无需读取文件内容，性能更好
3. 元数据与文件分离，易于维护
4. 可扩展到其他平台，通用性强

---

**Q: 如何升级元数据格式？**

A: 元数据文件包含 `version` 字段，未来升级时会支持多版本格式兼容，旧格式仍可正常使用。

---

## 技术细节

**解析流程**：
```
1. 构造元数据文件路径：file_path + '.xyddjson'
2. 检查文件是否存在
3. 读取并解析 JSON 内容
4. 验证 source 字段是否为 'dingtalk-docs'
5. 提取关键字段：url, dentryUuid, exportTime
6. 返回标准化的数据源信息
```

**性能指标**：
- 解析速度：< 1ms/文件
- 文件大小：约 1KB/元数据文件
- 内存占用：极低（小文件JSON解析）

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-04-08 | 初始版本 |

---

**插件版本**: v1.0.0
**创建时间**: 2026-04-08
**维护者**: XiaoyaoSearch Team

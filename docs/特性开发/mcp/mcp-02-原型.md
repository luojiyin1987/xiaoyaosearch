# 原型设计：MCP 服务器支持

> **文档类型**：原型设计文档
> **特性名称**：MCP 服务器支持
> **设计状态**：已完成
> **创建时间**：2026-03-11
> **最后更新**：2026-03-11
> **关联文档**：[MCP PRD](./mcp-01-prd.md)

---

## 📋 设计说明

> **重要提示**：MCP 服务器是纯后端特性，用户界面为 **Claude Desktop**（第三方应用），本原型主要描述配置方式和用户使用体验。

本原型文档不同于传统UI原型，不涉及具体的界面设计和交互规范，而是聚焦在：
1. **Claude Desktop 配置方式**
2. **用户使用场景描述**
3. **配置向导和文档**

---

## 1. 用户配置界面

### 1.1 Claude Desktop 配置文件

**配置文件路径**：
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**配置内容**：

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "disabled": false
    }
  }
}
```

### 1.2 配置参数说明

| 参数 | 类型 | 必填 | 说明 | 示例值 |
|------|------|------|------|--------|
| `url` | string | 是 | MCP SSE 端点地址 | `http://127.0.0.1:8000/mcp` |
| `disabled` | boolean | 否 | 是否禁用此服务器 | `false` |
| `timeout` | number | 否 | 连接超时时间（毫秒） | `30000` |
| `retries` | number | 否 | 重连次数 | `3` |

### 1.3 高级配置选项

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "timeout": 30000,
      "retries": 3,
      "env": {
        "MCP_DEFAULT_LIMIT": "20",
        "MCP_DEFAULT_THRESHOLD": "0.7"
      }
    }
  }
}
```

---

## 2. 用户使用场景

### 场景1：首次配置

**步骤流程**：

```
用户启动小遥搜索后端
  ↓
确认后端正常运行（http://127.0.0.1:8000）
  ↓
打开 Claude Desktop 配置文件
  ↓
添加小遥搜索 MCP 服务器配置
  ↓
保存配置文件
  ↓
重启 Claude Desktop
  ↓
在 Claude 对话中测试搜索功能
```

**配置向导**：

1. **启动后端服务**
   ```bash
   cd backend
   python main.py
   ```

2. **验证服务状态**
   - 访问：http://127.0.0.1:8000/docs
   - 确认 API 文档正常显示

3. **编辑 Claude Desktop 配置**
   - 打开配置文件（路径见上文）
   - 添加小遥搜索配置
   - 保存文件

4. **重启 Claude Desktop**
   - 完全退出 Claude Desktop
   - 重新启动应用

5. **验证连接**
   - 在 Claude Desktop 中输入："帮我搜索关于机器学习的文档"
   - 观察是否调用小遥搜索工具

### 场景2：日常使用

**对话示例**：

```
用户：我在之前的工作文档中有关于异步编程的内容吗？

Claude：让我帮你搜索一下...
[调用小遥搜索 MCP 工具：semantic_search]
  参数：{"query": "异步编程", "limit": 10}

Claude：找到了！你的项目中有以下关于异步编程的文档：

1. asyncio最佳实践.pdf
   - 相关度：92%
   - 路径：D:\Documents\asyncio-guide.pdf

2. Python异步编程笔记.md
   - 相关度：87%
   - 路径：D:\Notes\python-async.md

需要我帮你打开某个文档或总结具体内容吗？
```

### 场景3：图片搜索

**对话示例**：

```
用户：[上传一张架构图截图]
      我记得之前保存过类似的架构图，能帮我找找吗？

Claude：让我用这张图片搜索一下...
[调用小遥搜索 MCP 工具：image_search]
  参数：{"image_data": "base64...", "limit": 5}

Claude：找到了相似的图片！

1. 微服务架构设计图.png
   - 相似度：89%
   - 路径：D:\Documents\architecture.png

2. 系统架构草图.drawio
   - 相似度：76%
   - 路径：D:\Projects\system-architecture.drawio

需要我帮你打开查看吗？
```

### 场景4：语音搜索

**对话示例**：

```
用户：[按住麦克风按钮，说出查询内容]
      "帮我找一下关于机器学习算法优化的文档"

Claude：收到语音查询，正在识别...
[调用小遥搜索 MCP 工具：voice_search]
  参数：{
    "audio_data": "base64...",
    "search_type": "semantic",
    "limit": 10
  }

Claude：我识别到你的查询是"机器学习算法优化"，正在搜索...

找到了以下相关文档：

1. 深度学习优化技巧.pdf
   - 相关度：94%
   - 路径：D:\Documents\dl-optimization.pdf

2. 机器学习算法调优指南.md
   - 相关度：89%
   - 路径：D:\Notes\ml-algorithm-tuning.md

3. 模型性能优化最佳实践.docx
   - 相关度：85%
   - 路径：D:\Work\model-optimization.docx

需要我帮你打开某个文档或总结具体内容吗？
```

---

## 3. Claude Desktop 中的工具显示

### 3.1 工具列表

Claude Desktop 会显示可用的 MCP 工具：

```
小遥搜索 (xiaoyao-search)
├── semantic_search      语义搜索（基于 BGE-M3）
├── fulltext_search      全文搜索（基于 Whoosh）
├── voice_search         语音搜索（基于 FasterWhisper）
├── image_search         图像搜索（基于 CN-CLIP）
└── hybrid_search        混合搜索（语义+全文）
```

### 3.2 工具描述

**semantic_search**
```
描述：基于BGE-M3模型的语义搜索，支持自然语言查询理解。
适合用自然语言描述的查询，如"关于机器学习算法优化的方法"。

参数：
  - query: string (必填) - 搜索查询词（1-500字符）
  - limit: integer (可选) - 返回结果数量（1-100，默认20）
  - threshold: number (可选) - 相似度阈值（0.0-1.0，默认0.7）
  - file_types: array (可选) - 文件类型过滤
```

**fulltext_search**
```
描述：基于Whoosh的全文搜索，支持精确关键词匹配和中文分词。
适合查找特定术语、代码片段或精确短语。

参数：
  - query: string (必填) - 搜索查询词（1-500字符）
  - limit: integer (可选) - 返回结果数量（1-100，默认20）
  - file_types: array (可选) - 文件类型过滤
```

**voice_search**
```
描述：基于FasterWhisper模型的语音搜索，支持语音输入转文本后进行搜索。
适合通过语音快速搜索，无需手动输入文字。

参数：
  - audio_data: string (必填) - Base64 编码的音频数据（支持 WAV、MP3、M4A 格式）
  - search_type: string (可选) - 搜索类型（semantic/fulltext/hybrid，默认 semantic）
  - limit: integer (可选) - 返回结果数量（1-100，默认20）
  - threshold: number (可选) - 相似度阈值（0.0-1.0，默认0.7）
  - file_types: array (可选) - 文件类型过滤

说明：
  - 音频时长建议不超过30秒
  - 支持中英文语音识别
  - 自动将识别结果转换为搜索查询
```

**image_search**
```
描述：基于CN-CLIP模型的图像搜索，支持图片上传查找相似内容。
可以通过图片查找相似的图片或包含相关内容的文档。

参数：
  - image_data: string (必填) - Base64 编码的图片数据
  - limit: integer (可选) - 返回结果数量（1-100，默认20）
  - threshold: number (可选) - 相似度阈值（0.0-1.0，默认0.7）
```

**hybrid_search**
```
描述：结合语义搜索和全文搜索的混合搜索，提供最佳的搜索结果。
综合向量相似度和文本匹配度进行排序。

参数：
  - query: string (必填) - 搜索查询词（1-500字符）
  - limit: integer (可选) - 返回结果数量（1-100，默认20）
  - threshold: number (可选) - 相似度阈值（0.0-1.0，默认0.7）
  - file_types: array (可选) - 文件类型过滤
```

---

## 4. 配置文档设计

### 4.1 快速开始指南

```markdown
# 小遥搜索 MCP 快速开始

## 步骤1：启动后端服务

```bash
cd backend
python main.py
```

看到以下日志表示启动成功：
```
✅ 小遥搜索服务启动完成
📖 API文档: http://127.0.0.1:8000/docs
✅ MCP 服务器初始化完成
```

## 步骤2：配置 Claude Desktop

1. 打开配置文件：
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. 添加以下配置：
   ```json
   {
     "mcpServers": {
       "xiaoyao-search": {
         "url": "http://127.0.0.1:8000/mcp"
       }
     }
   }
   ```

3. 保存文件并重启 Claude Desktop

## 步骤3：测试连接

在 Claude Desktop 中输入：
```
帮我搜索关于人工智能的文档
```

如果 Claude 自动调用搜索工具，说明配置成功！
```

### 4.2 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| Claude Desktop 无法连接 | 后端服务未启动 | 启动后端服务：`python backend/main.py` |
| 搜索工具未显示 | 配置文件格式错误 | 检查 JSON 格式是否正确 |
| 搜索无结果 | 索引未构建 | 在小遥搜索中构建索引 |
| 连接超时 | 端口被占用 | 检查 8000 端口是否被占用 |

---

## 5. 用户反馈收集

### 5.1 配置反馈

**配置难度评分**：
- 1分 - 非常困难，需要技术背景
- 2分 - 有些困难，但可以完成
- 3分 - 一般，需要按照文档操作
- 4分 - 比较简单，文档清晰
- 5分 - 非常简单，无需文档

### 5.2 使用体验反馈

**功能满意度**：
- [ ] 搜索准确性
- [ ] 响应速度
- [ ] 结果展示
- [ ] 配置便捷性
- [ ] 文档完整性

---

## 6. 后续优化方向

### 6.1 配置优化

- [ ] 提供配置工具自动生成配置文件
- [ ] 支持配置验证和测试
- [ ] 添加配置向导UI

### 6.2 功能扩展

- [ ] 支持更多搜索工具（如资源访问、提示词模板）
- [ ] 支持自定义搜索参数
- [ ] 添加搜索历史记录

### 6.3 文档优化

- [ ] 提供视频教程
- [ ] 添加更多使用示例
- [ ] 多语言文档支持

---

## 7. 设计检查清单

### 7.1 配置文档
- [ ] 快速开始指南
- [ ] 详细配置说明
- [ ] 故障排查指南
- [ ] FAQ 文档

### 7.2 用户体验
- [ ] 配置流程简单清晰
- [ ] 错误提示友好明确
- [ ] 使用示例丰富实用
- [ ] 文档易于理解

### 7.3 技术实现
- [ ] 配置验证机制
- [ ] 错误处理完善
- [ ] 日志记录详细
- [ ] 调试工具完备

---

**文档结束**

> **实施状态**：⏸️ 规划中
> **设计类型**：配置导向 + 用户体验描述
> **UI平台**：Claude Desktop（第三方应用）
> **更新记录**：
> - v1.0 (2026-03-11): 初始版本，描述配置方式和使用场景

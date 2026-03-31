# 插件化架构与语雀数据源 - 接口文档增量

> **特性状态**：已完成
> **创建时间**：2026-02-22
> **最后更新**：2026-02-22 (v1.3 - 插件提供元数据)
> **关联文档**：[技术方案](./plugins+yuque-03-技术方案.md) | [任务清单](./plugins+yuque-04-开发任务清单.md)

---

## 目录

1. [接口变更概述](#1-接口变更概述)
2. [搜索API扩展](#2-搜索api扩展)
3. [插件配置方式](#3-插件配置方式)
4. [数据模型变更](#4-数据模型变更)

---

## 1. 接口变更概述

### 变更统计

| API模块 | 新增接口 | 修改接口 | 删除接口 |
|---------|---------|---------|---------|
| 搜索服务 | 0 | 1 | 0 |
| **合计** | **0** | **1** | **0** |

### 变更摘要

- **修改**: 搜索API响应增加数据源信息字段（source_type、source_url、source_name）

**插件管理方式说明**：
- 插件无需通过API管理
- 插件放到`data/plugins/`目录自动加载
- 配置通过`config.yaml`文件完成
- 系统启动时自动同步数据源

---

## 2. 搜索API扩展

### 2.1 修改搜索响应

**原接口**：`POST /api/search`

**变更点**：响应数据增加以下字段

| 字段 | 类型 | 说明 |
|------|------|------|
| source_type | string | 数据源类型（filesystem/yuque/feishu等），由插件提供 |
| source_url | string | 原文访问链接（可选），由插件从文件内容提取 |

**响应示例**

```json
{
  "success": true,
  "data": {
    "total": 2,
    "results": [
      {
        "id": "file_001",
        "filename": "产品需求文档.md",
        "path": "/docs/产品需求文档.md",
        "file_type": "markdown",
        "content_preview": "这是一个产品需求文档...",
        "score": 0.95,
        "source_type": "filesystem",
        "source_url": null
      },
      {
        "id": "yuque_001",
        "filename": "API设计规范",
        "path": "https://www.yuque.com/docs/api-design",
        "file_type": "markdown",
        "content_preview": "本文档描述API设计规范...",
        "score": 0.92,
        "source_type": "yuque",
        "source_url": "https://www.yuque.com/docs/api-design"
      }
    ]
  }
}
```

---

## 3. 插件配置方式

### 3.1 插件目录结构

```
data/plugins/
├── datasource/           # 数据源插件目录
│   ├── yuque/           # 语雀知识库插件
│   │   ├── plugin.py    # 插件实现代码
│   │   ├── config.yaml  # 插件配置文件
│   │   └── data/        # 下载的数据目录
│   │       └── downloaded/
│   └── feishu/          # 飞书文档插件（未来）
│       ├── plugin.py
│       ├── config.yaml
│       └── data/
└── ai_model/            # AI模型插件目录（架构预留）
```

### 3.2 配置文件格式

**语雀插件配置示例** (`data/plugins/datasource/yuque/config.yaml`)

```yaml
# 插件基本信息
plugin:
  id: yuque
  name: 语雀知识库
  version: "1.0.0"
  type: datasource
  enabled: true

# 知识库配置列表（支持多个知识库）
repos:
  # 知识库 1：产品文档
  - name: "产品文档"
    url: "https://www.yuque.com/your-org/product-docs"
    download_dir: "./data/product-docs"
    token: ""  # 可选，私有知识库需要
    cookie_key: "_yuque_session"  # 可选，企业部署
    ignore_images: false
    incremental: true

  # 知识库 2：技术文档
  - name: "技术文档"
    url: "https://www.yuque.com/your-org/tech-docs"
    download_dir: "./data/tech-docs"
    token: ""
    ignore_images: false
    incremental: true
```

### 3.3 配置项说明

**插件基本信息**

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plugin.id | string | 是 | 插件唯一标识 |
| plugin.name | string | 是 | 插件显示名称 |
| plugin.version | string | 是 | 版本号（semver格式） |
| plugin.type | string | 是 | 插件类型（datasource/ai_model等） |
| plugin.enabled | boolean | 是 | 是否启用插件 |

**知识库配置（repos 列表项）**

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 是 | 知识库名称（用于标识） |
| url | string | 是 | 语雀知识库 URL |
| download_dir | string | 是 | 下载目录（相对于插件目录） |
| token | string | 否 | 语雀 Cookie（私有知识库需要） |
| cookie_key | string | 否 | 企业部署的 Cookie Key（默认 `_yuque_session`） |
| ignore_images | boolean | 否 | 是否忽略图片（默认 false） |
| incremental | boolean | 否 | 是否增量下载（默认 true） |

### 3.4 配置文件加载流程

```
系统启动
    ↓
扫描 data/plugins/ 目录
    ↓
发现插件目录（datasource/yuque/、datasource/feishu/等）
    ↓
读取每个插件的 config.yaml
    ↓
验证配置有效性（检查 plugin.enabled）
    ↓
加载插件模块（plugin.py）
    ↓
初始化插件实例（调用 initialize()）
    ↓
自动执行插件同步（调用 sync()）
    ↓
同步完成，等待索引构建
```

**关键说明**：
- 插件自动发现：放到 `data/plugins/datasource/` 下自动加载
- 启动时同步：应用启动时自动执行增量同步
- 无需 API：不需要通过 API 手动触发同步

---

## 4. 数据模型变更

### 4.1 搜索响应数据模型

```typescript
// 搜索结果项
interface SearchResultItem {
  id: string;                  // 文件唯一标识
  filename: string;            // 文件名
  path: string;                // 文件路径
  file_type: string;           // 文件类型
  content_preview: string;     // 内容预览
  score: number;               // 相似度评分

  // 新增字段（由插件提供）
  source_type: string;         // 数据源类型（filesystem/yuque/feishu）
  source_url?: string;         // 原文访问链接（可选）
}

// 搜索响应
interface SearchResponse {
  success: boolean;
  data: {
    total: number;
    results: SearchResultItem[];
  };
}
```

### 4.2 插件配置数据模型

```typescript
// 语雀插件配置（YAML格式对应）
interface YuquePluginConfig {
  plugin: {
    id: string;              // 插件ID
    name: string;            // 插件名称
    version: string;         // 版本号
    type: string;            // 插件类型
    enabled: boolean;        // 是否启用
  };
  repos: Array<{
    name: string;            // 知识库名称
    url: string;             // 知识库URL
    download_dir: string;    // 下载目录
    token?: string;          // 认证Token（可选）
    cookie_key?: string;     // Cookie Key（可选）
    ignore_images?: boolean; // 是否忽略图片（可选）
    incremental?: boolean;   // 是否增量下载（可选）
  }>;
}
```

---

## 5. 开发者指南

### 5.1 创建新插件

1. **创建插件目录**
   ```bash
   mkdir -p data/plugins/datasource/my_datasource
   ```

2. **编写插件代码** (`plugin.py`)
   ```python
   from app.plugins.interface.datasource import DataSourcePlugin
   from typing import Dict, Any

   class MyDataSourcePlugin(DataSourcePlugin):
       """我的数据源插件"""

       @classmethod
       def get_metadata(cls) -> Dict[str, Any]:
           return {
               "id": "my_datasource",
               "name": "我的数据源",
               "version": "1.0.0",
               "type": "datasource",
               "author": "Your Name",
               "description": "插件描述"
           }

       async def initialize(self, config: Dict[str, Any]) -> bool:
           """初始化插件"""
           # 准备工作：检测工具、创建目录等
           return True

       async def sync(self) -> bool:
           """同步数据到本地"""
           # 调用外部工具或API，下载数据到本地
           return True

       def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
           """获取文件的数据源信息（索引时调用）"""
           # 从文件内容提取原始URL等信息
           return {
               "source_type": "my_datasource",
               "source_url": self._extract_url(content)
           }

       async def cleanup(self):
           """清理资源"""
           pass
   ```

3. **创建配置文件** (`config.yaml`)
   ```yaml
   plugin:
     id: my_datasource
     name: 我的数据源
     version: "1.0.0"
     type: datasource
     enabled: true

   repos:
     - name: "示例知识库"
       url: "https://example.com/docs"
       download_dir: "./data/downloaded"
   ```

4. **重启服务**
   系统会自动发现并加载新插件

**关键方法说明**：
- `initialize()`: 插件初始化时调用，检测工具、准备目录
- `sync()`: 应用启动时自动调用，下载数据到本地
- `get_file_source_info()`: 索引时调用，提供数据源信息

### 5.2 禁用插件

将配置文件中的 `enabled` 设置为 `false`，或重命名插件目录：

```bash
# 方法1：修改配置文件
# data/plugins/datasource/yuque/config.yaml
# plugin.enabled: false

# 方法2：重命名目录
mv data/plugins/datasource/yuque data/plugins/datasource/yuque.disabled
```

---

## 6. 更新日志

### v1.3.0 (2026-02-22)
- **插件提供元数据** ✅ 规划中
  - source_type 和 source_url 由插件通过 `get_file_source_info()` 方法提供
  - 移除 source_name 字段，简化数据模型
  - 更新配置文件格式（yuque-dl CLI 方式）
  - 支持多个知识库配置
  - 启动时自动同步

### v1.2.0 (2026-02-22)
- **约定优于配置** ✅ 规划中
  - 移除所有插件管理API
  - 移除所有数据源管理API
  - 插件通过配置文件管理
  - 插件自动发现和加载

### v1.1.0 (2026-02-22)
- **简化插件安装方式** ✅ 规划中
  - 移除插件上传API
  - 插件安装改为文件复制方式
  - 系统自动发现和加载

### v1.0.0 (2026-02-22)
- **插件化架构** ✅ 规划中
  - 插件管理API（已废弃）
  - 数据源管理API（已废弃）
  - 搜索API扩展（保留）

---

**文档维护**: 开发者
**最后更新**: 2026-02-22 (v1.3 - 插件提供元数据)
**文档状态**: 已批准

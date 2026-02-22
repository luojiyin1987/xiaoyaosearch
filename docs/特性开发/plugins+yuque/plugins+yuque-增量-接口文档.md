# 插件化架构与语雀数据源 - 接口文档增量

> **特性状态**：规划中
> **创建时间**：2026-02-22
> **最后更新**：2026-02-22 (v1.2 - 约定优于配置)
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
| source_type | string | 数据源类型（filesystem/yuque/feishu等） |
| source_url | string | 原文访问链接（可选） |
| source_name | string | 数据源显示名称 |

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
        "source_url": null,
        "source_name": "本地文件"
      },
      {
        "id": "yuque_001",
        "filename": "API设计规范",
        "path": "https://www.yuque.com/docs/api-design",
        "file_type": "markdown",
        "content_preview": "本文档描述API设计规范...",
        "score": 0.92,
        "source_type": "yuque",
        "source_url": "https://www.yuque.com/docs/api-design",
        "source_name": "语雀知识库"
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
├── yuque/
│   ├── plugin.py           # 插件实现代码
│   ├── config.yaml         # 插件配置文件
│   └── requirements.txt    # 依赖列表（可选）
├── feishu/
│   ├── plugin.py
│   ├── config.yaml
│   └── requirements.txt
└── filesystem/
    ├── plugin.py
    └── config.yaml
```

### 3.2 配置文件格式

**语雀插件配置示例** (`data/plugins/yuque/config.yaml`)

```yaml
# 插件基本信息
plugin:
  id: yuque
  name: 语雀知识库
  version: "1.0.0"
  enabled: true

# 数据源配置
datasource:
  type: yuque
  api_token: "your_yuque_api_token_here"  # 语雀API Token
  repo_slug: "username/knowledge_base"    # 知识库路径
  base_url: "https://www.yuque.com/api/v2"

# 同步配置
sync:
  interval: 60          # 同步间隔（分钟），0表示手动同步
  batch_size: 50        # 每批处理文档数量
  timeout: 30           # 请求超时时间（秒）
```

### 3.3 配置项说明

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plugin.id | string | 是 | 插件唯一标识 |
| plugin.name | string | 是 | 插件显示名称 |
| plugin.version | string | 是 | 版本号（semver格式） |
| plugin.enabled | boolean | 是 | 是否启用插件 |
| datasource.type | string | 是 | 数据源类型 |
| datasource.api_token | string | 是 | API认证令牌 |
| datasource.repo_slug | string | 是 | 知识库路径 |
| sync.interval | integer | 否 | 同步间隔（分钟），默认60 |
| sync.batch_size | integer | 否 | 批处理大小，默认50 |
| sync.timeout | integer | 否 | 请求超时（秒），默认30 |

### 3.4 配置文件加载流程

```
系统启动
    ↓
扫描 data/plugins/ 目录
    ↓
发现插件目录（yuque/、feishu/等）
    ↓
读取每个插件的 config.yaml
    ↓
验证配置有效性
    ↓
加载插件模块（plugin.py）
    ↓
初始化插件实例
    ↓
启动后台同步任务
```

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

  // 新增字段
  source_type: string;         // 数据源类型
  source_url?: string;         // 原文访问链接（可选）
  source_name: string;         // 数据源显示名称
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
// 插件配置（YAML格式对应）
interface PluginConfig {
  plugin: {
    id: string;
    name: string;
    version: string;
    enabled: boolean;
  };
  datasource: {
    type: string;
    [key: string]: any;        // 数据源特定配置
  };
  sync?: {
    interval?: number;
    batch_size?: number;
    timeout?: number;
  };
}
```

---

## 5. 开发者指南

### 5.1 创建新插件

1. **创建插件目录**
   ```bash
   mkdir -p data/plugins/my_datasource
   ```

2. **编写插件代码** (`plugin.py`)
   ```python
   from app.plugins.interface import DataSourcePlugin

   class MyDataSourcePlugin(DataSourcePlugin):
       def get_metadata(self):
           return {
               "id": "my_datasource",
               "name": "我的数据源",
               "version": "1.0.0"
           }

       async def scan(self):
           # 实现数据扫描逻辑
           pass
   ```

3. **创建配置文件** (`config.yaml`)
   ```yaml
   plugin:
     id: my_datasource
     name: 我的数据源
     version: "1.0.0"
     enabled: true

   datasource:
     type: my_datasource
     # 添加数据源特定配置
   ```

4. **重启服务**
   系统会自动发现并加载新插件

### 5.2 禁用插件

将配置文件中的 `enabled` 设置为 `false`，或重命名插件目录：

```bash
# 方法1：修改配置文件
# data/plugins/yuque/config.yaml
# plugin.enabled: false

# 方法2：重命名目录
mv data/plugins/yuque data/plugins/yuque.disabled
```

---

## 6. 更新日志

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
**最后更新**: 2026-02-22 (v1.2 - 约定优于配置)
**文档状态**: 已批准

# 钉钉文档数据源 - 技术方案

> **文档类型**：技术方案
> **特性状态**：规划中
> **创建时间**：2026-04-08
> **最后更新**：2026-04-08 (v1.0 - 初始版本)

---

## 1. 方案概述

### 1.1 技术目标

为小遥搜索添加**钉钉文档数据源识别能力**，支持从钉钉导出工具自动生成的 `.xyddjson` 元数据文件中提取文档信息，实现数据源标识和原文链接跳转功能。

### 1.2 设计原则

- **极简设计**：仅实现元数据文件解析，无外部同步需求
- **零配置**：无需配置文件，自动识别元数据文件
- **向后兼容**：完全基于现有插件化架构
- **性能优先**：独立元数据文件，解析速度快于内容解析
- **容错友好**：元数据解析失败不影响文件索引
- **可扩展性**：`.xyddjson` 格式可扩展到其他平台

### 1.3 与语雀/飞书插件的差异

| 对比项 | 语雀插件 | 飞书插件 | 钉钉插件 |
|-------|---------|---------|---------|
| **数据获取方式** | yuque-dl CLI 下载 | 用户手动导出 | 下载工具自动生成 |
| **是否需要同步** | ✅ 需要外部同步 | ❌ 无需同步 | ❌ 无需同步 |
| **配置文件** | config.yaml（多知识库） | 无需配置 | 无需配置 |
| **元数据位置** | 下载目录结构 | 文件内容末尾 | 独立JSON文件 |
| **核心方法** | sync() + get_file_source_info() | 仅 get_file_source_info() | 仅 get_file_source_info() |
| **解析方式** | CLI集成 | 正则表达式 | JSON解析 |
| **实现复杂度** | 高（CLI集成） | 中等（正则匹配） | 低（JSON解析） |
| **解析性能** | 中等 | ~1ms | <1ms |
| **扩展性** | 仅语雀 | 仅飞书 | 通用格式 |

### 1.4 技术选型

| 技术/框架 | 用途 | 选择理由 | 替代方案 |
|----------|------|---------|---------|
| Python ABC | 插件接口定义 | 标准库，与语雀/飞书插件一致 | Protocol |
| JSON | 元数据解析 | 标准格式，Python内置支持 | YAML、TOML |
| Pathlib | 文件路径操作 | 面向对象，跨平台兼容 | os.path |
| 复用现有架构 | 插件加载器 | 无需修改核心代码 | - |

**与飞书技术对比**：

| 对比项 | 飞书 | 钉钉 | 钉钉优势 |
|-------|------|------|----------|
| 元数据格式 | Markdown块 + 正则 | JSON | 结构化、易解析 |
| 解析复杂度 | 中等（需正则匹配） | 低（标准JSON） | 更可靠 |
| 错误处理 | 格式变化易失败 | 标准JSON，稳定 | 容错性强 |
| 性能 | 需读取文件内容 | 直接读取元数据文件 | 更快 |
| 扩展性 | 仅限飞书 | 可用于其他平台 | 通用性强 |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              API层                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  /api/search  │  /api/index/build                                       │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                        服务层 (Service Layer)                             │
├───────────────────────────────────────────────────────────────────────────┤
│  PluginLoader  │  DataSourceManager  │  IndexService  │  SearchService   │
└────────────┬──────────────────────────────────────────┬───────────────────┘
             │                                          │
┌────────────▼──────────────────────────────────────────▼───────────────────┐
│                        插件层 (Plugin Layer)                                │
├───────────────────────────────────────────────────────────────────────────┤
│  BasePlugin(interface) - 通用插件基类                                      │
│  └─ DataSourcePlugin(interface) - 核心方法: get_file_source_info()       │
│      ├─ YuqueDataSource (调用 yuque-dl CLI 下载)                         │
│      ├─ FeishuDataSource (解析本地飞书导出文档)                           │
│      └─ DingdingDataSource (解析 .xyddjson 元数据文件)                    │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                   本地文件系统 (用户放置导出的钉钉文档)                       │
├───────────────────────────────────────────────────────────────────────────┤
│  D:/Documents/dingding_docs/                                             │
│  ├── 需求文档.docx                                                       │
│  ├── 需求文档.docx.xyddjson  ← 元数据文件                                  │
│  ├── 技术方案.pdf                                                        │
│  └── 技术方案.pdf.xyddjson  ← 元数据文件                                  │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│              现有流程（完全复用，无需修改）                                  │
├───────────────────────────────────────────────────────────────────────────┤
│  FileSystemDataSource.scan() → 所有文件统一扫描                            │
│  └── 钉钉文档调用 DingdingDataSource.get_file_source_info()               │
│  IndexService → 统一索引构建 (Faiss + Whoosh)                              │
│  SearchService → 统一搜索服务                                              │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
用户使用钉钉导出工具导出文档
           │
           │ 自动生成 文件 + .xyddjson
           │
           ▼
    文件扫描服务
           │
           │ 检测同名 .xyddjson 文件
           ▼
    DingdingDataSource.get_file_source_info()
           │
           │ 读取并解析 JSON 元数据
           ▼
    提取 source_type=dingding, source_url, source_id
           │
           ▼
    存储到数据库 (source_type, source_url, source_id)
           │
           ▼
    构建索引 (Faiss + Whoosh)
           │
           ▼
    搜索结果显示钉钉标识 + 原文链接
```

### 2.3 插件目录结构

```
data/plugins/
├── datasource/              # 数据源插件目录
│   ├── yuque/              # 语雀知识库插件（已有）
│   │   ├── plugin.py
│   │   ├── config.yaml
│   │   └── data/
│   │
│   ├── feishu/             # 飞书文档插件（已有）
│   │   ├── plugin.py
│   │   └── README.md
│   │
│   └── dingding/           # 钉钉文档插件（新增）
│       ├── plugin.py       # 插件实现
│       └── README.md       # 使用说明
```

---

## 3. 核心模块设计

### 3.1 .xyddjson 格式规范

钉钉导出工具会为每个导出的文档生成一个同名元数据文件。

**文件结构示例**：

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

**字段说明表**：

| 字段路径 | 类型 | 必填 | 说明 | 示例值 |
|---------|------|------|------|--------|
| `version` | string | 是 | 元数据格式版本 | `"1.0.0"` |
| `source` | string | 是 | 数据来源标识 | `"dingtalk-docs"` |
| `exportTool` | string | 是 | 导出工具名称 | `"xiaoyaosearch-dingding-export"` |
| `exportToolVersion` | string | 是 | 导出工具版本 | `"1.0.0"` |
| `exportTime` | string | 是 | 导出时间（ISO 8601） | `"2026-04-08T15:30:00.000Z"` |
| `file.fileName` | string | 是 | 导出后的文件名 | `"项目报告.docx"` |
| `file.originalName` | string | 是 | 钉钉文档原始名称 | `"项目报告"` |
| `file.dentryUuid` | string | 是 | 钉钉文档唯一ID | `"A1B2C3D4E5F6G7H8"` |
| `file.url` | string | 是 | 钉钉文档访问地址 | `"https://alidocs.dingtalk.com/i/nodes/..."` |

**文件命名规则**：
- 格式：`{原文件名}.{扩展名}.xyddjson`
- 示例：
  - `项目报告.docx` → `项目报告.docx.xyddjson`
  - `需求文档.pdf` → `需求文档.pdf.xyddjson`

**目录结构示例**：
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

### 3.2 钉钉数据源插件实现

```python
# data/plugins/datasource/dingding/plugin.py
import json
from pathlib import Path
from typing import Dict, Any, Optional

from app.plugins.interface.datasource import DataSourcePlugin
from app.core.logging_config import logger


class DingdingDataSource(DataSourcePlugin):
    """
    钉钉文档数据源插件

    核心功能：
    1. 识别钉钉导出工具生成的元数据文件（.xyddjson）
    2. 提取元数据（dentryUuid、url、exportTime）
    3. 为索引服务提供数据源信息

    设计特点：
    - 无需配置文件（零配置）
    - 无需外部同步（下载工具自动生成）
    - 自动识别（同名元数据文件）
    - 标准JSON格式（可靠、高效、可扩展）
    """

    # 元数据文件扩展名
    METADATA_FILE_EXT = '.xyddjson'

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._plugin_dir: Path = None

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """返回插件元数据"""
        return {
            "id": "dingding",
            "name": "钉钉文档",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "识别钉钉导出工具生成的 .xyddjson 元数据文件",
            "datasource_type": "dingding",
            "dependencies": [],  # 无外部依赖
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        钉钉插件无需初始化配置，直接返回成功
        """
        try:
            self._config = config
            self._plugin_dir = Path(__file__).parent
            logger.info("钉钉数据源插件初始化成功")
            return True
        except Exception as e:
            logger.error(f"钉钉数据源插件初始化失败: {e}")
            return False

    async def sync(self) -> bool:
        """
        同步方法（钉钉无需同步）

        钉钉文档由下载工具自动生成元数据文件，无需外部同步逻辑
        """
        logger.info("钉钉文档由下载工具自动生成元数据文件，无需外部同步")
        return True

    def get_file_source_info(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """
        获取文件的数据源信息（核心方法）

        从钉钉导出的元数据文件（.xyddjson）中提取信息：
        - 来源类型: dingding
        - 原文链接: 钉钉文档 URL
        - 文档ID: dentryUuid

        Args:
            file_path: 文件路径
            content: 文件内容（钉钉插件不使用此参数）

        Returns:
            Dict[str, Any]: 包含以下键的字典:
                - source_type: "dingding" 或 None
                - source_url: 钉钉原文 URL 或 None
                - source_id: dentryUuid 或 None
                - export_time: 导出时间 或 None
                - original_name: 原始文件名 或 None
        """
        try:
            # 读取元数据文件
            metadata = self._read_metadata_file(file_path)

            if not metadata:
                return {"source_type": None, "source_url": None, "source_id": None}

            # 提取关键字段
            file_info = metadata.get("file", {})

            logger.debug(f"检测到钉钉文档: {file_path}")
            return {
                "source_type": "dingding",
                "source_url": file_info.get("url"),
                "source_id": file_info.get("dentryUuid"),
                "export_time": metadata.get("exportTime"),
                "original_name": file_info.get("originalName")
            }

        except Exception as e:
            logger.warning(f"解析钉钉元数据失败 {file_path}: {e}")
            return {"source_type": None, "source_url": None, "source_id": None}

    def _read_metadata_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        读取 .xyddjson 元数据文件

        Args:
            file_path: 原文件路径

        Returns:
            元数据字典，读取失败返回 None
        """
        # 构造元数据文件路径
        metadata_path = Path(str(file_path) + self.METADATA_FILE_EXT)

        # 检查文件是否存在
        if not metadata_path.exists():
            return None

        try:
            # 读取并解析 JSON
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # 验证元数据格式
            if metadata.get('source') != 'dingtalk-docs':
                logger.debug(f"元数据文件 source 字段不匹配: {metadata_path}")
                return None

            return metadata

        except json.JSONDecodeError as e:
            logger.warning(f"JSON 解析失败 {metadata_path}: {e}")
            return None
        except Exception as e:
            logger.warning(f"读取元数据文件失败 {metadata_path}: {e}")
            return None

    async def cleanup(self):
        """清理资源（无需清理）"""
        pass
```

### 3.3 元数据解析逻辑详解

#### 3.3.1 解析流程

```
1. 构造元数据文件路径：file_path + '.xyddjson'
2. 检查文件是否存在
3. 读取并解析 JSON 内容
4. 验证 source 字段是否为 'dingtalk-docs'
5. 提取关键字段：url, dentryUuid, exportTime
6. 返回标准化的数据源信息
```

#### 3.3.2 解析优化策略

| 优化策略 | 说明 | 性能提升 |
|---------|------|---------|
| 先检查文件存在 | 避免不必要的文件读取 | ~50% |
| 标准JSON解析 | 使用内置 json 库 | 高效稳定 |
| 异常捕获 | 解析失败不影响索引 | 稳定性 |
| 格式验证 | 检查 source 字段 | 准确性 |

#### 3.3.3 性能分析

| 操作 | 耗时 | 说明 |
|-----|------|------|
| 检查文件存在 | <0.01ms | Path.exists() |
| 读取JSON文件 | <0.5ms | 小文件（~1KB） |
| JSON解析 | <0.3ms | json.load() |
| 字段提取 | <0.01ms | 字典访问 |
| 总计 | <1ms/文件 | 对扫描性能影响<1% |

**与飞书性能对比**：

| 性能指标 | 飞书 | 钉钉 | 钉钉优势 |
|---------|------|------|----------|
| 解析速度 | ~1ms | <1ms | 更快 |
| 文件IO | 需读取文件内容 | 仅读取元数据文件 | 减少IO量 |
| 内存占用 | 中等（需缓存内容） | 低（JSON文件小） | 内存效率高 |
| CPU占用 | 正则匹配 | JSON解析 | 更稳定 |

---

## 4. 数据库集成

### 4.1 数据库字段

> **说明**：数据库表结构已在 plugins+yuque 特性中完成，本特性无需修改

**已有字段**：
```python
# backend/app/models/file.py
class FileModel(Base):
    # ... 其他字段 ...

    # 数据源相关字段（已存在）
    source_type = Column(String(50), default='filesystem', comment="数据源类型")
    source_url = Column(String(1000), nullable=True, comment="原始文档URL")
    source_id = Column(String(100), nullable=True, comment="文档唯一ID")
```

**新增存储内容**：
- `source_type = "dingding"`
- `source_url = "https://alidocs.dingtalk.com/i/nodes/..."`
- `source_id = "dentryUuid"`

### 4.2 索引服务集成

> **说明**：索引服务已在 plugins+yuque 特性中完成插件集成，本特性无需修改

**现有集成逻辑**：
```python
# backend/app/services/file_index_service.py（已有）

class FileIndexService:
    def __init__(self):
        self._plugin_loader = None  # 插件加载器引用

    def set_plugin_loader(self, plugin_loader):
        """设置插件加载器引用"""
        self._plugin_loader = plugin_loader

    async def _extract_source_info(self, file_path: str, content: str) -> dict:
        """提取数据源信息（调用插件方法）"""
        source_info = {"source_type": "filesystem", "source_url": None, "source_id": None}

        if not self._plugin_loader:
            return source_info

        # 遍历所有数据源插件
        datasource_plugins = self._plugin_loader.get_plugins_by_type("datasource")
        for plugin_id, plugin in datasource_plugins.items():
            try:
                plugin_info = plugin.get_file_source_info(file_path, content)
                if plugin_info.get("source_type"):
                    return plugin_info
            except Exception as e:
                logger.warning(f"插件 {plugin_id} 获取源信息失败: {e}")
                continue

        return source_info
```

---

## 5. 前端展示

### 5.1 搜索结果展示

> **说明**：前端已在 plugins+yuque 特性中完成数据源UI支持，本特性仅需增加钉钉标识

**已有实现** ([SearchResultCard.vue](frontend/src/renderer/src/components/SearchResultCard.vue))：

```vue
<!-- 数据源类型标识 -->
<span class="metadata-item source-type" :class="`source-${result.source_type || 'filesystem'}`">
  <component :is="getSourceIcon(result.source_type)" />
  {{ getSourceTypeLabel(result.source_type) }}
</span>

<!-- 原文链接 -->
<a v-if="result.source_url" :href="result.source_url" target="_blank" class="source-link">
  查看原文
</a>
```

**新增数据源类型映射**：
```typescript
const getSourceTypeLabel = (sourceType: string) => {
  const typeMap = {
    filesystem: '本地文件',
    yuque: '语雀',
    feishu: '飞书',
    dingding: '钉钉',  // ✅ 新增
    // ...
  }
  return typeMap[sourceType] || sourceType
}
```

**新增图标映射**：
```typescript
const getSourceIcon = (sourceType: string) => {
  const iconMap = {
    filesystem: FileOutlined,
    yuque: BookOutlined,
    feishu: CloudOutlined,
    dingding: DingdingOutlined,  // ✅ 新增（或使用钉钉Logo）
    // ...
  }
  return iconMap[sourceType] || FileOutlined
}
```

**新增样式定义**：
```css
.source-type.source-dingding {
  color: #0089FF;  /* 钉钉品牌色 */
  background: rgba(0, 137, 255, 0.1);
}
```

### 5.2 国际化配置

**新增翻译键**：

```json
{
  "searchResult": {
    "sourceDingding": {
      "zh-CN": "钉钉",
      "en-US": "DingTalk"
    }
  }
}
```

---

## 6. 插件配置与部署

### 6.1 插件文件清单

```
data/plugins/datasource/dingding/
├── plugin.py          # 插件实现
└── README.md          # 使用说明
```

### 6.2 部署步骤

1. **创建插件目录**：
```bash
mkdir -p data/plugins/datasource/dingding
```

2. **放置插件文件**：
- 将 `plugin.py` 放到插件目录
- 将 `README.md` 放到插件目录

3. **重启后端服务**：
```bash
# 后端服务会自动发现并加载插件
python backend/main.py
```

4. **验证插件加载**：
查看启动日志：
```
✅ 插件系统启动完成，已加载 3 个插件
  - yuque: 语雀知识库
  - feishu: 飞书文档
  - dingding: 钉钉文档
```

### 6.3 用户使用流程

**步骤1：安装钉钉导出工具**
1. 安装钉钉导出浏览器插件
2. 登录钉钉账号

**步骤2：导出钉钉文档**
1. 打开钉钉文档
2. 点击导出按钮
3. 选择导出格式（.docx、.pdf等）
4. 导出工具自动生成 `.xyddjson` 元数据文件

**步骤3：放置到本地目录**
```bash
# 将导出的文件放置到扫描目录
# 例如：D:/Documents/dingding_docs/
```

**步骤4：构建索引**
```bash
# 调用索引 API
POST /api/index/create
{
  "folder_path": "D:/Documents/dingding_docs",
  "recursive": true
}
```

**步骤5：搜索验证**
```bash
# 调用搜索 API
POST /api/search
{
  "query": "搜索关键词"
}

# 响应结果包含钉钉标识
{
  "results": [
    {
      "source_type": "dingding",
      "source_url": "https://alidocs.dingtalk.com/i/nodes/...",
      "source_id": "A1B2C3D4E5F6G7H8",
      "file_name": "项目报告.docx"
    }
  ]
}
```

---

## 7. 测试方案

### 7.1 单元测试

```python
# tests/plugins/test_dingding_plugin.py
import pytest
import json
from pathlib import Path
from app.plugins.datasource.dingding import DingdingDataSource


class TestDingdingDataSource:
    """钉钉数据源插件单元测试"""

    @pytest.fixture
    def plugin(self):
        return DingdingDataSource()

    @pytest.fixture
    def sample_metadata(self):
        """示例元数据"""
        return {
            "version": "1.0.0",
            "source": "dingtalk-docs",
            "exportTool": "xiaoyaosearch-dingding-export",
            "exportToolVersion": "1.0.0",
            "exportTime": "2026-04-08T15:30:00.000Z",
            "file": {
                "fileName": "项目报告.docx",
                "originalName": "项目报告",
                "dentryUuid": "A1B2C3D4E5F6G7H8",
                "url": "https://alidocs.dingtalk.com/i/nodes/A1B2C3D4E5F6G7H8"
            }
        }

    def test_get_metadata(self, plugin):
        """测试插件元数据"""
        metadata = plugin.get_metadata()
        assert metadata["id"] == "dingding"
        assert metadata["name"] == "钉钉文档"
        assert metadata["type"] == "datasource"

    def test_standard_metadata_parsing(self, plugin, sample_metadata, tmp_path):
        """测试标准元数据文件解析"""
        # 创建测试文件和元数据
        test_file = tmp_path / "项目报告.docx"
        test_file.touch()

        metadata_file = tmp_path / "项目报告.docx.xyddjson"
        metadata_file.write_text(json.dumps(sample_metadata, ensure_ascii=False))

        # 解析
        result = plugin.get_file_source_info(str(test_file), None)

        # 验证
        assert result["source_type"] == "dingding"
        assert result["source_url"] == "https://alidocs.dingtalk.com/i/nodes/A1B2C3D4E5F6G7H8"
        assert result["source_id"] == "A1B2C3D4E5F6G7H8"

    def test_metadata_file_not_exist(self, plugin, tmp_path):
        """测试元数据文件不存在"""
        test_file = tmp_path / "普通文件.docx"
        test_file.touch()

        result = plugin.get_file_source_info(str(test_file), None)

        assert result["source_type"] is None
        assert result["source_url"] is None

    def test_invalid_json_format(self, plugin, tmp_path):
        """测试损坏的JSON文件"""
        test_file = tmp_path / "项目报告.docx"
        test_file.touch()

        metadata_file = tmp_path / "项目报告.docx.xyddjson"
        metadata_file.write_text("{ invalid json }")

        result = plugin.get_file_source_info(str(test_file), None)

        # 解析失败应返回 None，不影响文件索引
        assert result["source_type"] is None

    def test_wrong_source_field(self, plugin, tmp_path, sample_metadata):
        """测试错误的 source 字段"""
        sample_metadata["source"] = "feishu"  # 错误的来源

        test_file = tmp_path / "项目报告.docx"
        test_file.touch()

        metadata_file = tmp_path / "项目报告.docx.xyddjson"
        metadata_file.write_text(json.dumps(sample_metadata, ensure_ascii=False))

        result = plugin.get_file_source_info(str(test_file), None)

        # source 字段不匹配，应返回 None
        assert result["source_type"] is None
```

### 7.2 集成测试

**测试用例1：端到端钉钉文档搜索**

```python
async def test_dingding_document_e2e():
    """测试钉钉文档端到端搜索"""
    import json

    # 1. 准备测试文件
    test_dir = Path("/test/dingding_docs")
    test_dir.mkdir(exist_ok=True)

    test_file = test_dir / "需求文档.docx"
    test_file.touch()

    metadata = {
        "version": "1.0.0",
        "source": "dingtalk-docs",
        "exportTime": "2026-04-08T15:30:00.000Z",
        "file": {
            "fileName": "需求文档.docx",
            "originalName": "需求文档",
            "dentryUuid": "TEST123",
            "url": "https://alidocs.dingtalk.com/i/nodes/TEST123"
        }
    }

    metadata_file = test_dir / "需求文档.docx.xyddjson"
    metadata_file.write_text(json.dumps(metadata, ensure_ascii=False))

    # 2. 构建索引
    index_service = get_file_index_service()
    await index_service.build_index(str(test_dir), recursive=True)

    # 3. 搜索验证
    search_service = get_search_service()
    results = await search_service.search("需求文档")

    # 4. 断言
    assert len(results) > 0
    assert results[0]["source_type"] == "dingding"
    assert results[0]["source_url"] == "https://alidocs.dingtalk.com/i/nodes/TEST123"
    assert results[0]["source_id"] == "TEST123"
```

**测试用例2：混合数据源搜索**

```python
async def test_mixed_datasource_search():
    """测试混合数据源搜索（本地+语雀+飞书+钉钉）"""
    # 准备四种类型的文件
    # 本地文件、语雀文档、飞书文档、钉钉文档

    # 搜索并验证结果包含四种数据源
    results = await search_service.search("关键词")

    source_types = {r["source_type"] for r in results}
    assert "filesystem" in source_types
    assert "yuque" in source_types
    assert "feishu" in source_types
    assert "dingding" in source_types
```

### 7.3 性能测试

**测试目标**：验证钉钉元数据解析对扫描性能的影响

```python
async def test_dingding_parsing_performance():
    """测试钉钉解析性能"""
    import time
    import json

    plugin = DingdingDataSource()

    # 创建测试元数据
    metadata = {
        "version": "1.0.0",
        "source": "dingtalk-docs",
        "exportTime": "2026-04-08T15:30:00.000Z",
        "file": {
            "fileName": "test.docx",
            "dentryUuid": "TEST123",
            "url": "https://alidocs.dingtalk.com/i/nodes/TEST123"
        }
    }

    # 创建临时文件
    test_file = Path("/test/test.docx")
    test_file.touch()

    metadata_file = Path("/test/test.docx.xyddjson")
    metadata_file.write_text(json.dumps(metadata))

    # 测试100次解析时间
    start = time.time()
    for _ in range(100):
        plugin.get_file_source_info(str(test_file), None)
    elapsed = time.time() - start

    # 清理
    test_file.unlink()
    metadata_file.unlink()

    # 断言：100次解析应小于100ms（单次<1ms）
    assert elapsed < 0.1, f"解析性能不达标: {elapsed}ms"
```

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-04-08 | 初始版本 |

---

## 9. 附录

### 9.1 .xyddjson 格式兼容性

| 版本 | 格式变化 | 支持状态 |
|------|---------|---------|
| v1.0 | 初始格式 | ✅ 支持 |
| v1.1 | 预留扩展字段 | 🚧 计划中 |

### 9.2 与飞书方案对比

| 对比项 | 飞书 | 钉钉 | 钉钉优势 |
|-------|------|------|----------|
| 元数据位置 | 文件内容末尾 | 独立JSON文件 | 结构化、易维护 |
| 元数据格式 | Markdown块 | JSON | 标准化、易解析 |
| 解析方式 | 正则表达式 | JSON解析 | 更可靠、更快速 |
| 文件读取 | 需读取文件内容 | 仅读取元数据文件 | 减少IO |
| 扩展性 | 仅限飞书 | 可用于其他平台 | 通用性强 |
| 性能 | ~1ms | <1ms | 更快 |
| 可靠性 | 依赖导出格式 | 标准JSON | 更稳定 |

### 9.3 常见问题

**Q1: .xyddjson 文件是什么？**
A: .xyddjson 是钉钉导出工具自动生成的元数据文件，采用JSON格式，包含文档的原始信息（URL、ID、导出时间等），用于小遥搜索识别文档来源。

**Q2: 可以删除 .xyddjson 文件吗？**
A: 可以删除，但删除后文档将无法被识别为钉钉数据源，会被当作普通本地文件处理。

**Q3: .xyddjson 格式可以用于其他平台吗？**
A: 可以。.xyddjson 格式设计时考虑了通用性，未来可以扩展到企业微信、飞书等其他平台。

**Q4: 元数据文件会占用多少存储空间？**
A: 每个 .xyddjson 文件约 1KB，对存储空间影响很小（约 5% 增加）。

**Q5: 为什么选择独立的元数据文件而不是嵌入文件内容？**
A: 独立元数据文件有以下优势：
1. 结构化JSON格式，解析更可靠
2. 无需读取文件内容，性能更好
3. 元数据与文件分离，易于维护
4. 可扩展到其他平台，通用性强

**Q6: 钉钉元数据解析失败怎么办？**
A: 解析失败不影响文件索引，只是 source_type 为 "filesystem"。检查 .xyddjson 文件是否存在且格式正确。

**Q7: 原文链接会过期吗？**
A: 如果您有钉钉文档的访问权限，原文链接长期有效。权限变更可能导致链接失效。

**Q8: 如何升级元数据格式？**
A: 元数据文件包含 `version` 字段，未来升级时会支持多版本格式兼容，旧格式仍可正常使用。

---

**文档版本**: v1.0
**创建时间**: 2026-04-08
**最后更新**: 2026-04-08 (v1.0 - 初始版本)
**维护者**: 开发者

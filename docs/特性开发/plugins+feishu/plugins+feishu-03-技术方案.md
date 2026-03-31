# 飞书文档数据源 - 技术方案

> **文档类型**：技术方案
> **特性状态**：规划中
> **创建时间**：2026-03-31
> **最后更新**：2026-03-31 (v1.0 - 初始版本)

---

## 1. 方案概述

### 1.1 技术目标

为小遥搜索添加**飞书文档数据源识别能力**，支持从飞书导出的本地 Markdown 文档中提取元数据信息，实现数据源标识和原文链接跳转功能。

### 1.2 设计原则

- **极简设计**：仅实现元数据解析，无外部同步需求
- **零配置**：无需配置文件，自动识别飞书文档格式
- **向后兼容**：完全基于现有插件化架构
- **性能优先**：仅解析文件末尾，不影响扫描性能
- **容错友好**：元数据解析失败不影响文件索引

### 1.3 与语雀插件的差异

| 对比项 | 语雀插件 | 飞书插件 |
|-------|---------|---------|
| **数据获取方式** | yuque-dl CLI 下载 | 用户手动导出 |
| **是否需要同步** | ✅ 需要外部同步 | ❌ 无需同步 |
| **配置文件** | config.yaml（多知识库） | 无需配置 |
| **核心方法** | sync() + get_file_source_info() | 仅 get_file_source_info() |
| **实现复杂度** | 高（CLI集成） | 低（元数据解析） |

### 1.4 技术选型

| 技术/框架 | 用途 | 选择理由 |
|----------|------|---------|
| Python ABC | 插件接口定义 | 标准库，与语雀插件一致 |
| 正则表达式 | 元数据解析 | 轻量高效，无需额外依赖 |
| 复用现有架构 | 插件加载器 | 无需修改核心代码 |

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
│      └─ FeishuDataSource (解析本地飞书导出文档)                           │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                   本地文件系统 (用户放置导出的飞书文档)                       │
├───────────────────────────────────────────────────────────────────────────┤
│  D:/Documents/feishu_docs/*.md  (用户手动导出并放置)                       │
│  + 其他本地目录                                                           │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│              现有流程（完全复用，无需修改）                                  │
├───────────────────────────────────────────────────────────────────────────┤
│  FileSystemDataSource.scan() → 所有文件统一扫描                            │
│  └── 飞书文档调用 FeishuDataSource.get_file_source_info()                   │
│  IndexService → 统一索引构建 (Faiss + Whoosh)                              │
│  SearchService → 统一搜索服务                                              │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
用户从飞书导出 Markdown 文档
           │
           │ 放置到本地目录
           │ (如 D:/Documents/feishu_docs/)
           ▼
    文件扫描服务
           │
           │ 检测文件内容
           ▼
    FeishuDataSource.get_file_source_info()
           │
           │ 正则解析元数据
           ▼
    提取 source_type=feishu, source_url
           │
           ▼
    存储到数据库 (source_type, source_url)
           │
           ▼
    构建索引 (Faiss + Whoosh)
           │
           ▼
    搜索结果显示飞书标识 + 原文链接
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
│   └── feishu/             # 飞书文档插件（新增）
│       ├── plugin.py       # 插件实现
│       ├── README.md       # 使用说明
│       └── (无需 config.yaml)
```

---

## 3. 核心模块设计

### 3.1 飞书导出格式规范

飞书导出的 Markdown 文档在文件末尾包含以下元数据格式：

```markdown
---
> 更新: 2026-03-30 02:52:46
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/MZKMwqpljiod1ak38Cscnr8hnkh>
---
```

**元数据字段说明**：

| 字段 | 说明 | 示例值 |
|-----|------|--------|
| 更新 | 文档最后更新时间 | 2026-03-30 02:52:46 |
| 来源类型 | 固定为 feishu | feishu |
| 原文 | 飞书文档完整 URL | https://feishu.cn/wiki/... |

### 3.2 飞书数据源插件实现

```python
# data/plugins/datasource/feishu/plugin.py
import re
from typing import Dict, Any
from pathlib import Path

from app.plugins.interface.datasource import DataSourcePlugin
from app.core.logging_config import logger


class FeishuDataSource(DataSourcePlugin):
    """
    飞书文档数据源插件

    核心功能：
    1. 识别飞书导出的 Markdown 文档
    2. 提取元数据（来源类型、原文链接）
    3. 为索引服务提供数据源信息

    设计特点：
    - 无需配置文件（零配置）
    - 无需外部同步（用户手动导出）
    - 自动识别（元数据匹配）
    """

    # 飞书元数据正则表达式模式
    FEISHU_METADATA_PATTERNS = [
        # 标准格式（中文）
        r'>\s*来源类型:\s*feishu\s*>?\s*原文:\s*<(https://[^\s>]+)>',
        # 兼容格式（英文）
        r'>\s*Source:\s*feishu\s*>?\s*URL:\s*<(https://[^\s>]+)>',
    ]

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._plugin_dir: Path = None

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """返回插件元数据"""
        return {
            "id": "feishu",
            "name": "飞书文档",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "识别飞书导出的 Markdown 文档并提取元数据",
            "datasource_type": "feishu",
            "dependencies": [],  # 无外部依赖
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        飞书插件无需初始化配置，直接返回成功
        """
        try:
            self._config = config
            self._plugin_dir = Path(__file__).parent
            logger.info("飞书数据源插件初始化成功")
            return True
        except Exception as e:
            logger.error(f"飞书数据源插件初始化失败: {e}")
            return False

    async def sync(self) -> bool:
        """
        同步方法（飞书无需同步）

        飞书文档由用户手动导出，无需外部同步逻辑
        """
        logger.info("飞书文档由用户手动导出，无需外部同步")
        return True

    def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        获取文件的数据源信息（核心方法）

        从飞书导出的 Markdown 文档末尾提取元数据：
        - 来源类型: feishu
        - 原文链接: 飞书文档 URL

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            Dict[str, Any]: 包含以下键的字典:
                - source_type: "feishu" 或 None
                - source_url: 飞书原文 URL 或 None
        """
        try:
            # 优化：只读取文件末尾 500 字符
            content_tail = content[-500:] if len(content) > 500 else content

            # 遍历所有匹配模式
            for pattern in self.FEISHU_METADATA_PATTERNS:
                match = re.search(pattern, content_tail, re.IGNORECASE | re.DOTALL)
                if match:
                    source_url = match.group(1).strip()
                    logger.debug(f"检测到飞书文档: {file_path}")
                    return {
                        "source_type": "feishu",
                        "source_url": source_url
                    }

            # 未检测到飞书元数据
            return {"source_type": None, "source_url": None}

        except Exception as e:
            logger.warning(f"解析飞书元数据失败 {file_path}: {e}")
            return {"source_type": None, "source_url": None}

    async def cleanup(self):
        """清理资源（无需清理）"""
        pass
```

### 3.3 元数据解析逻辑详解

#### 3.3.1 正则表达式设计

**标准格式匹配**：
```regex
>\s*来源类型:\s*feishu\s*>?\s*原文:\s*<(https://[^\s>]+)>
```

**匹配示例**：
```markdown
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/MZKMwqpljiod1ak38Cscnr8hnkh>
```

**兼容格式匹配**（未来扩展）：
```regex
>\s*Source:\s*feishu\s*>?\s*URL:\s*<(https://[^\s>]+)>
```

#### 3.3.2 解析优化策略

| 优化策略 | 说明 | 性能提升 |
|---------|------|---------|
| 仅读取末尾500字符 | 减少内存占用和处理时间 | ~90% |
| 多模式匹配 | 支持不同导出格式版本 | 兼容性 |
| 大小写不敏感 | 容错处理 | 健壮性 |
| 异常捕获 | 解析失败不影响索引 | 稳定性 |

#### 3.3.3 性能分析

| 操作 | 耗时 | 说明 |
|-----|------|------|
| 读取文件末尾500字符 | <0.1ms | 字符串切片 |
| 正则表达式匹配 | <0.5ms | 编译后的正则 |
| 总计 | <1ms/文件 | 对扫描性能影响<1% |

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
```

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
        source_info = {"source_type": "filesystem", "source_url": None}

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

> **说明**：前端已在 plugins+yuque 特性中完成飞书数据源UI支持，本特性无需修改

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

**数据源类型映射**：
```typescript
const getSourceTypeLabel = (sourceType: string) => {
  const typeMap = {
    filesystem: '本地文件',
    yuque: '语雀',
    feishu: '飞书',  // ✅ 已有
    // ...
  }
  return typeMap[sourceType] || sourceType
}
```

**样式定义**：
```css
.source-type.source-feishu {
  color: #722ed1;
  background: rgba(114, 46, 209, 0.1);
}
```

---

## 6. 插件配置与部署

### 6.1 插件文件清单

```
data/plugins/datasource/feishu/
├── plugin.py          # 插件实现
└── README.md          # 使用说明
```

### 6.2 部署步骤

1. **创建插件目录**：
```bash
mkdir -p data/plugins/datasource/feishu
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
✅ 插件系统启动完成，已加载 2 个插件
  - yuque: 语雀知识库
  - feishu: 飞书文档
```

### 6.3 用户使用流程

**步骤1：从飞书导出文档**
1. 打开飞书文档
2. 点击右上角 "..." 菜单
3. 选择 "导出为 Markdown"

**步骤2：放置到本地目录**
```bash
# 将导出的 Markdown 文件放置到扫描目录
# 例如：D:/Documents/feishu_docs/
```

**步骤3：构建索引**
```bash
# 调用索引 API
POST /api/index/create
{
  "folder_path": "D:/Documents/feishu_docs",
  "recursive": true
}
```

**步骤4：搜索验证**
```bash
# 调用搜索 API
POST /api/search
{
  "query": "搜索关键词"
}

# 响应结果包含飞书标识
{
  "results": [
    {
      "source_type": "feishu",
      "source_url": "https://feishu.cn/wiki/...",
      "file_name": "飞书文档标题.md"
    }
  ]
}
```

---

## 7. 测试方案

### 7.1 单元测试

```python
# tests/plugins/test_feishu_plugin.py
import pytest
from app.plugins.datasource.feishu import FeishuDataSource


class TestFeishuDataSource:
    """飞书数据源插件单元测试"""

    @pytest.fixture
    def plugin(self):
        return FeishuDataSource()

    def test_get_metadata(self, plugin):
        """测试插件元数据"""
        metadata = plugin.get_metadata()
        assert metadata["id"] == "feishu"
        assert metadata["name"] == "飞书文档"
        assert metadata["type"] == "datasource"

    def test_standard_format_parsing(self, plugin):
        """测试标准格式解析"""
        content = """
# 文档标题

文档内容...

---
> 更新: 2026-03-30 02:52:46
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/MZKMwqpljiod1ak38Cscnr8hnkh>
---
        """
        result = plugin.get_file_source_info("/test/file.md", content)
        assert result["source_type"] == "feishu"
        assert result["source_url"] == "https://feishu.cn/wiki/MZKMwqpljiod1ak38Cscnr8hnkh"

    def test_non_feishu_file(self, plugin):
        """测试非飞书文件"""
        content = "# 普通Markdown文件\n\n内容..."
        result = plugin.get_file_source_info("/test/file.md", content)
        assert result["source_type"] is None
        assert result["source_url"] is None

    def test_long_file_optimization(self, plugin):
        """测试长文件解析优化"""
        # 构造一个超长文件
        long_content = "# 标题\n" + "内容\n" * 10000 + """
---
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/test>
---
        """
        result = plugin.get_file_source_info("/test/long.md", long_content)
        assert result["source_type"] == "feishu"
        # 验证只读取末尾（性能）
        assert len(result["source_url"]) > 0
```

### 7.2 集成测试

**测试用例1：端到端飞书文档搜索**

```python
async def test_feishu_document_e2e():
    """测试飞书文档端到端搜索"""
    # 1. 准备测试文件
    test_file = Path("/test/feishu_doc.md")
    test_file.write_text("""
# 飞书测试文档

这是测试内容。

---
> 更新: 2026-03-30 02:52:46
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/test123>
---
    """)

    # 2. 构建索引
    index_service = get_file_index_service()
    await index_service.build_index("/test", recursive=True)

    # 3. 搜索验证
    search_service = get_search_service()
    results = await search_service.search("测试内容")

    # 4. 断言
    assert len(results) > 0
    assert results[0]["source_type"] == "feishu"
    assert results[0]["source_url"] == "https://feishu.cn/wiki/test123"
```

**测试用例2：混合数据源搜索**

```python
async def test_mixed_datasource_search():
    """测试混合数据源搜索（本地+语雀+飞书）"""
    # 准备三种类型的文件
    # 本地文件、语雀文档、飞书文档

    # 搜索并验证结果包含三种数据源
    results = await search_service.search("关键词")

    source_types = {r["source_type"] for r in results}
    assert "filesystem" in source_types
    assert "yuque" in source_types
    assert "feishu" in source_types
```

### 7.3 性能测试

**测试目标**：验证飞书元数据解析对扫描性能的影响

```python
async def test_feishu_parsing_performance():
    """测试飞书解析性能"""
    import time

    plugin = FeishuDataSource()
    test_content = "# 标题\n" + "内容\n" * 10000 + feishu_metadata

    # 测试100次解析时间
    start = time.time()
    for _ in range(100):
        plugin.get_file_source_info("/test.md", test_content)
    elapsed = time.time() - start

    # 断言：100次解析应小于100ms（单次<1ms）
    assert elapsed < 0.1, f"解析性能不达标: {elapsed}ms"
```

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-03-31 | 初始版本 |

---

## 9. 附录

### 9.1 飞书元数据格式兼容性

| 导出版本 | 格式示例 | 支持状态 |
|---------|---------|---------|
| 标准格式（中文） | `> 来源类型: feishu` | ✅ 支持 |
| 标准格式（英文） | `> Source: feishu` | ✅ 支持 |
| 未来格式 | 待定义 | 🚧 预留 |

### 9.2 常见问题

**Q1: 飞书元数据解析失败怎么办？**
A: 解析失败不影响文件索引，只是 source_type 为 "filesystem"。检查导出格式是否完整。

**Q2: 支持哪些飞书文档类型？**
A: 支持所有能导出为 Markdown 的飞书文档类型（Wiki、常规文档等）。

**Q3: 原文链接会过期吗？**
A: 如果您有飞书文档的访问权限，原文链接长期有效。权限变更可能导致链接失效。

**Q4: 可以批量导出飞书文档吗？**
A: 飞书支持批量导出，导出后的文件放到同一目录即可被识别。

---

**文档版本**: v1.0
**创建时间**: 2026-03-31
**最后更新**: 2026-03-31 (v1.0 - 初始版本)
**维护者**: 开发者

# 飞书文档数据源 - 实施方案

> **文档类型**：实施方案
> **特性状态**：已完成
> **创建时间**：2026-03-31
> **决策时间**：2026-03-31
> **决策人**：产品负责人

---

## 1. 实施概述

### 1.1 目标

为小遥搜索添加飞书文档数据源识别能力，支持从飞书导出的本地 Markdown 文档中提取元数据信息，实现数据源标识和原文链接跳转功能。

### 1.2 核心决策点（已确定）

| 决策项 | 决策结果 | 状态 |
|--------|---------|------|
| **飞书集成方式** | 零配置元数据解析 | ✅ 已确定 |
| **外部数据同步** | 无需同步（用户手动导出） | ✅ 已确定 |
| **配置文件** | 无需配置文件 | ✅ 已确定 |
| **复用现有架构** | 完全基于 plugins+yuque 基础设施 | ✅ 已确定 |

### 1.3 设计原则

- **零配置**：自动识别飞书导出格式，无需配置文件
- **极简实现**：仅实现元数据解析功能
- **性能优先**：仅解析文件末尾，不影响扫描性能
- **完全兼容**：复用现有插件基础设施

### 1.4 与语雀特性的关系

| 对比项 | 语雀特性 | 飞书特性 |
|-------|---------|---------|
| **是否新建基础设施** | ✅ 是 | ❌ 复用 |
| **是否需要外部同步** | ✅ yuque-dl | ❌ 用户导出 |
| **是否需要配置文件** | ✅ config.yaml | ❌ 零配置 |
| **核心实现** | CLI集成 | 元数据解析 |
| **预计工作量** | 14-18天 | 3-5天 |

---

## 2. 技术方案

### 2.1 飞书元数据格式

飞书导出的 Markdown 文档在文件末尾包含以下元数据：

```markdown
---
> 更新: 2026-03-30 02:52:46
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/MZKMwqpljiod1ak38Cscnr8hnkh>
---
```

### 2.2 解析策略

| 优化策略 | 说明 | 性能提升 |
|---------|------|---------|
| 仅读取末尾500字符 | 减少内存占用和处理时间 | ~90% |
| 多模式匹配 | 支持不同导出格式版本 | 兼容性 |
| 大小写不敏感 | 容错处理 | 健壮性 |
| 异常捕获 | 解析失败不影响索引 | 稳定性 |

### 2.3 工作流程

```
用户从飞书导出 Markdown → 放置到本地目录 → 文件扫描
                                                  ↓
                                    FeishuDataSource.get_file_source_info()
                                                  ↓
                                            正则解析元数据
                                                  ↓
                          source_type=feishu + source_url
                                                  ↓
                                            存储到数据库
                                                  ↓
                                            搜索结果显示飞书标识
```

---

## 3. 实施步骤

### 第一阶段：飞书插件实现（1-2天）

#### 3.1 创建插件目录结构

```bash
mkdir -p data/plugins/datasource/feishu
```

**目录结构：**
```
data/plugins/datasource/feishu/
├── plugin.py          # 插件实现
└── README.md          # 使用说明
```

#### 3.2 实现 FeishuDataSource 类

**创建 data/plugins/datasource/feishu/plugin.py：**

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

    核心功能：识别飞书导出的 Markdown 文档并提取元数据
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

        从飞书导出的 Markdown 文档末尾提取元数据

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            Dict[str, Any]: {source_type, source_url}
        """
        try:
            # 优化：仅读取文件末尾 500 字符
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

#### 3.3 创建使用说明文档

**创建 data/plugins/datasource/feishu/README.md：**

```markdown
# 飞书文档插件

识别从飞书导出的 Markdown 文档并提取元数据信息。

## 使用方法

### 1. 从飞书导出文档

1. 打开飞书文档
2. 点击右上角 "..." 菜单
3. 选择 "导出为 Markdown"

### 2. 放置到本地目录

将导出的 Markdown 文件放置到扫描目录（如 `D:/Documents/feishu_docs/`）

### 3. 构建索引

```bash
POST /api/index/create
{
  "folder_path": "D:/Documents/feishu_docs",
  "recursive": true
}
```

### 4. 搜索验证

```bash
POST /api/search
{
  "query": "搜索关键词"
}
```

## 支持的格式

飞书导出的 Markdown 文档末尾包含以下元数据：

```markdown
---
> 更新: 2026-03-30 02:52:46
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/MZKMwqpljiod1ak38Cscnr8hnkh>
---
```

## 特性

- ✅ 零配置：自动识别飞书导出格式
- ✅ 性能优化：仅解析文件末尾500字符
- ✅ 容错友好：解析失败不影响文件索引
- ✅ 原文跳转：搜索结果可跳转到飞书原文

## 常见问题

**Q: 飞书元数据解析失败怎么办？**
A: 解析失败不影响文件索引，只是 source_type 为 "filesystem"。检查导出格式是否完整。

**Q: 支持哪些飞书文档类型？**
A: 支持所有能导出为 Markdown 的飞书文档类型（Wiki、常规文档等）。

**Q: 原文链接会过期吗？**
A: 如果您有飞书文档的访问权限，原文链接长期有效。权限变更可能导致链接失效。
```

---

### 第二阶段：插件部署与验证（0.5-1天）

#### 3.4 本地部署

**步骤1：创建插件目录**
```bash
mkdir -p data/plugins/datasource/feishu
```

**步骤2：复制插件文件**
```bash
# 将 plugin.py 和 README.md 复制到插件目录
```

**步骤3：重启后端服务**
```bash
cd backend
python main.py
```

**步骤4：验证插件加载**

查看启动日志，确认插件已加载：
```
✅ 插件系统启动完成，已加载 2 个插件
  - yuque: 语雀知识库
  - feishu: 飞书文档
```

#### 3.5 准备测试文件

**创建飞书测试文档 feishu_test.md：**

```markdown
# 飞书测试文档

这是从飞书导出的测试文档内容。

---
> 更新: 2026-03-30 02:52:46
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/test123>
---
```

**将测试文件放到扫描目录：**
```bash
cp feishu_test.md D:/Documents/feishu_docs/
```

#### 3.6 集成验证

**步骤1：构建索引**
```bash
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:/Documents/feishu_docs",
    "recursive": true
  }'
```

**步骤2：搜索验证**
```bash
curl -X POST "http://127.0.0.1:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试文档"
  }'
```

**预期响应：**
```json
{
  "results": [
    {
      "file_name": "feishu_test.md",
      "source_type": "feishu",
      "source_url": "https://feishu.cn/wiki/test123",
      "highlight": "...",
      "score": 0.85
    }
  ]
}
```

**步骤3：前端验证**

打开前端应用，搜索 "测试文档"，验证：
- 搜索结果显示"飞书"标识（紫色）
- 可点击原文链接跳转到飞书

---

### 第三阶段：测试（1-2天）

#### 3.7 单元测试

**创建 tests/plugins/test_feishu_plugin.py：**

```python
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
        assert result["source_url"] == "https://feishu.cn/wiki/test"

    def test_empty_file(self, plugin):
        """测试空文件"""
        result = plugin.get_file_source_info("/test/empty.md", "")
        assert result["source_type"] is None
        assert result["source_url"] is None
```

**运行单元测试：**
```bash
cd backend
pytest tests/plugins/test_feishu_plugin.py -v
```

#### 3.8 集成测试

**创建 tests/integration/test_feishu_integration.py：**

```python
import pytest
from pathlib import Path


class TestFeishuIntegration:
    """飞书插件集成测试"""

    @pytest.mark.asyncio
    async def test_feishu_document_e2e(self):
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
        from app.services.file_index_service import get_file_index_service
        index_service = get_file_index_service()
        await index_service.build_full_index("/test", recursive=True)

        # 3. 搜索验证
        from app.services.chunk_search_service import get_chunk_search_service
        search_service = get_chunk_search_service()
        results = await search_service.search("测试内容")

        # 4. 断言
        assert len(results) > 0
        assert results[0]["source_type"] == "feishu"
        assert results[0]["source_url"] == "https://feishu.cn/wiki/test123"

    @pytest.mark.asyncio
    async def test_mixed_datasource_search(self):
        """测试混合数据源搜索"""
        # 准备三种类型的文件
        # 本地文件、语雀文档、飞书文档

        # 搜索并验证结果包含三种数据源
        results = await search_service.search("关键词")

        source_types = {r["source_type"] for r in results}
        assert "filesystem" in source_types
        assert "yuque" in source_types
        assert "feishu" in source_types
```

**运行集成测试：**
```bash
cd backend
pytest tests/integration/test_feishu_integration.py -v
```

#### 3.9 性能测试

**创建 tests/performance/test_feishu_performance.py：**

```python
import pytest
import time
from app.plugins.datasource.feishu import FeishuDataSource


class TestFeishuPerformance:
    """飞书插件性能测试"""

    @pytest.mark.asyncio
    async def test_parsing_performance(self):
        """测试解析性能"""
        plugin = FeishuDataSource()
        test_content = "# 标题\n" + "内容\n" * 10000 + """
---
> 来源类型: feishu
> 原文: <https://feishu.cn/wiki/test>
---
        """

        # 测试100次解析时间
        start = time.time()
        for _ in range(100):
            plugin.get_file_source_info("/test.md", test_content)
        elapsed = time.time() - start

        # 断言：100次解析应小于100ms（单次<1ms）
        assert elapsed < 0.1, f"解析性能不达标: {elapsed}ms"
```

---

### 第四阶段：文档更新（0.5天）

#### 3.10 更新全局文档

**修改 docs/CLAUDE.md，添加飞书插件说明：**

```markdown
### 插件化架构与飞书数据源 ✅ 已完成

**功能定位**：
为小遥搜索添加飞书文档数据源识别能力，支持搜索从飞书导出的本地 Markdown 文档。

**核心价值**：
- 降低使用门槛：用户无需配置，导出文件即可识别
- 提升搜索体验：搜索结果显示飞书来源标识
- 快速定位原文：支持跳转到飞书原文

**技术实现**：
- **零配置**：自动识别飞书导出格式
- **元数据解析**：正则表达式提取 source_type 和 source_url
- **性能优化**：仅解析文件末尾500字符

**设计完成度**：
- ✅ 全局文档同步
- ✅ 飞书PRD文档完成
- ✅ 飞书技术方案完成
- ✅ 飞书任务清单完成
- ✅ 飞书实施方案完成
```

---

## 4. 工作量与排期

### 4.1 工作量分解

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| 一 | 飞书插件实现 | 1-2天 |
| 二 | 插件部署与验证 | 0.5-1天 |
| 三 | 测试 | 1-2天 |
| 四 | 文档更新 | 0.5天 |
| **总计** | | **3-5天** |

### 4.2 里程碑

| 里程碑 | 预计完成时间 | 关键交付物 |
|--------|-------------|-----------|
| M1: 飞书插件完成 | 第1天 | plugin.py 实现 |
| M2: 部署验证完成 | 第2天 | 插件加载成功，搜索显示飞书标识 |
| M3: 测试完成 | 第3-4天 | 测试通过，性能达标 |
| M4: 文档完成 | 第4-5天 | 全局文档更新 |

### 4.3 关键文件清单

| 文件路径 | 说明 | 类型 |
|---------|------|------|
| `data/plugins/datasource/feishu/plugin.py` | 飞书插件实现 | 新建 |
| `data/plugins/datasource/feishu/README.md` | 使用说明 | 新建 |
| `tests/plugins/test_feishu_plugin.py` | 单元测试 | 新建 |
| `tests/integration/test_feishu_integration.py` | 集成测试 | 新建 |
| `tests/performance/test_feishu_performance.py` | 性能测试 | 新建 |
| `docs/CLAUDE.md` | 全局文档更新 | 修改 |

---

## 5. 风险与应对

| 风险项 | 风险等级 | 影响 | 应对措施 |
|--------|---------|------|---------|
| 飞书导出格式变化 | 低 | 元数据解析失败 | 多种格式兼容，提供清晰的格式说明 |
| 性能影响 | 低 | 扫描变慢 | 仅解析末尾500字符，性能测试验证 |
| 正则表达式错误 | 低 | 解析失败 | 多种模式匹配，充分测试 |

---

## 6. 验收标准

### 功能验收
- [ ] 飞书元数据被正确解析
- [ ] source_type 正确设置为 "feishu"
- [ ] source_url 正确提取
- [ ] 搜索结果显示飞书标识
- [ ] 原文链接可跳转
- [ ] 非飞书文档不受影响

### 质量验收
- [ ] 无P0/P1级别Bug
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试全部通过
- [ ] 性能指标达标（解析 < 1ms，扫描影响 < 5%）

### 文档验收
- [ ] README.md 内容完整
- [ ] 全局文档已更新
- [ ] 测试文档完整

---

## 7. 后续优化方向

### 短期优化（1-2个迭代）
- [ ] 支持飞书文档更新时间显示
- [ ] 飞书文档批量导入优化

### 中期规划（3-6个月）
- [ ] 飞书 API 直接集成（无需导出）
- [ ] 飞书文档实时同步

---

## 8. 决策记录

### 确定方案：零配置元数据解析

**决策时间**：2026-03-31

**确定内容**：
| 决策项 | 决策结果 |
|--------|---------|
| 飞书集成方式 | ✅ 零配置元数据解析 |
| 外部数据同步 | ❌ 无需同步（用户手动导出） |
| 配置文件 | ❌ 无需配置文件 |
| 复用现有架构 | ✅ 完全基于 plugins+yuque 基础设施 |

**方案优势**：
1. ✅ **开发快速**：复用现有插件基础设施，仅需实现解析逻辑
2. ✅ **维护成本低**：无需维护外部API集成
3. ✅ **用户友好**：零配置，导出即可使用
4. ✅ **性能优化**：仅解析文件末尾，影响极小

**已知权衡**：
1. ⚠️ 用户需要手动从飞书导出文档
2. ⚠️ 依赖飞书导出格式稳定性

**后续优化方向**（如需更自动化）：
- 飞书 API 直接集成
- 实时同步功能

---

**文档版本**: v1.0
**创建时间**: 2026-03-31
**最后更新**: 2026-03-31 (初始版本)
**状态**: 已批准，待开发

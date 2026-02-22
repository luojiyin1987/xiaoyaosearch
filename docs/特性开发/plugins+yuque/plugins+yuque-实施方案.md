# 插件化架构与语雀数据源 - 实施方案

> **文档类型**：实施方案
> **特性状态**：待实施
> **创建时间**：2026-02-22
> **最后更新**：2026-02-22 (v2.1 - yuque-dl CLI集成)
> **实施周期**：4周（2026-02-24 ~ 2026-03-21）

---

## 文档信息

| 项目 | 内容 |
|------|------|
| **项目名称** | 插件化架构与语雀数据源 |
| **文档版本** | v2.1 |
| **创建日期** | 2026-02-22 |
| **最后更新** | 2026-02-22 (v2.1 - yuque-dl CLI集成) |
| **项目周期** | 2026-02-24 ~ 2026-03-21（共4周/19个工作日） |
| **开发人员** | 开发者（单人） |

---

## 目录

1. [项目概述](#1-项目概述)
2. [实施准备](#2-实施准备)
3. [分阶段实施计划](#3-分阶段实施计划)
4. [代码实现指南](#4-代码实现指南)
5. [测试验证方案](#5-测试验证方案)
6. [部署上线方案](#6-部署上线方案)
7. [风险应对预案](#7-风险应对预案)
8. [验收标准](#8-验收标准)

---

## 1. 项目概述

### 1.1 项目背景

小遥搜索当前支持本地文件系统的搜索功能，为了扩展数据源支持，需要建立通用插件化架构。首个实现的数据源插件是语雀知识库，采用开源工具 **yuque-dl** 进行集成。

### 1.2 项目目标

| 目标 | 描述 | 优先级 |
|------|------|--------|
| **建立插件架构** | 实现通用插件系统，支持多种数据源扩展 | P0 |
| **语雀数据源** | 支持语雀知识库文档搜索 | P0 |
| **向后兼容** | 保持现有本地文件搜索功能 | P0 |
| **架构预留** | 为 AI 模型插件等预留接口 | P1 |

### 1.3 核心设计原则

```
约定优于配置 + CLI工具集成

┌─────────────────────────────────────────────────────────────┐
│                        设计原则                              │
├─────────────────────────────────────────────────────────────┤
│  1. 插件放置即安装（复制到 data/plugins/ 目录）               │
│  2. 配置文件管理（config.yaml，无需 API）                     │
│  3. 自动发现加载（系统启动时扫描）                            │
│  4. 类型隔离（不同插件类型独立目录）                          │
│  5. CLI 集成（语雀采用 yuque-dl 工具）                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.4 技术选型

| 技术/框架 | 用途 | 理由 |
|----------|------|------|
| Python ABC | 插件接口定义 | 标准库，类型安全 |
| importlib | 插件动态加载 | Python标准库，无额外依赖 |
| PyYAML | 配置文件解析 | 人类可读，易于编辑 |
| asyncio subprocess | CLI工具调用 | 异步进程管理 |
| yuque-dl | 语雀数据获取 | 成熟开源工具，避免维护API |

### 1.5 里程碑

| 里程碑 | 时间 | 交付物 |
|--------|------|--------|
| M1 | Week1 (02/28) | 插件基础设施完成 |
| M2 | Week2 (03/07) | 语雀插件完成 |
| M3 | Week3 (03/14) | 索引集成完成 |
| M4 | Week4 (03/21) | 测试与文档完成 |

---

## 2. 实施准备

### 2.1 环境准备

#### 开发环境检查

```bash
# Python 版本检查
python --version  # 需要 3.10+

# Node.js 版本检查（yuque-dl 依赖）
node --version   # 需要 18.4+
npm --version

# 安装 yuque-dl
npm install -g yuque-dl
# 或使用 npx（无需全局安装）
npx yuque-dl --version

# 验证 yuque-dl 安装
yuque-dl --help
# 或
npx yuque-dl --help
```

#### 项目目录结构准备

```bash
# 确保以下目录存在
backend/app/plugins/          # 新建：插件框架目录
backend/app/plugins/interface/  # 新建：接口定义目录
data/plugins/                 # 新建：插件目录
data/plugins/datasource/      # 新建：数据源插件目录
data/plugins/datasource/yuque/  # 新建：语雀插件目录
data/plugins/datasource/filesystem/  # 新建：本地文件插件目录
```

### 2.2 依赖安装

```bash
# 后端依赖
cd backend
pip install pyyaml

# 测试依赖
pip install pytest pytest-asyncio pytest-mock
```

### 2.3 数据库准备

```sql
-- 检查当前数据库结构
sqlite3 backend/data/xiaoyaosearch.db

-- 查看 files 表结构
.schema files

-- 备份数据库
cp backend/data/xiaoyaosearch.db backend/data/xiaoyaosearch.db.backup
```

### 2.4 配置文件模板准备

创建配置文件模板：

```yaml
# backend/app/plugins/config_template.yaml
plugin:
  id: example
  name: 示例插件
  version: "1.0.0"
  type: datasource
  enabled: true

datasource:
  type: example
  # 数据源特定配置
```

---

## 3. 分阶段实施计划

### 阶段一：插件基础设施（Week1：02/24-02/28）

#### 3.1.1 任务分解

| 任务 | 文件 | 工作量 | 依赖 |
|------|------|--------|------|
| 创建 BasePlugin 基类 | `app/plugins/base.py` | 2h | - |
| 定义 PluginType 枚举 | `app/plugins/base.py` | 1h | - |
| 创建 DataSourcePlugin 接口 | `app/plugins/interface/datasource.py` | 2h | BasePlugin |
| 创建 AIModelPlugin 接口 | `app/plugins/interface/ai_model.py` | 1.5h | BasePlugin |
| 实现 ConfigParser | `app/plugins/config_parser.py` | 3h | - |
| 实现 PluginLoader | `app/plugins/loader.py` | 4h | ConfigParser |
| 修改 main.py | `app/main.py` | 2h | PluginLoader |

#### 3.1.2 实施步骤

**Day 1-2：核心接口定义**

```python
# 1. 创建 base.py
# backend/app/plugins/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class PluginType(Enum):
    DATASOURCE = "datasource"
    AI_MODEL = "ai_model"
    # ... 其他类型

class BasePlugin(ABC):
    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]: pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool: pass

    @abstractmethod
    async def cleanup(self): pass
```

```python
# 2. 创建 datasource.py 接口
# backend/app/plugins/interface/datasource.py
from app.plugins.base import BasePlugin
from typing import AsyncIterator, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DataSourceItem:
    id: str
    title: str
    content: str
    source_type: str
    url: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

class DataSourcePlugin(BasePlugin):
    @abstractmethod
    async def scan(self, **kwargs) -> AsyncIterator[DataSourceItem]: pass

    @abstractmethod
    async def get_content(self, item_id: str) -> Optional[str]: pass
```

**Day 3-4：加载器与解析器**

```python
# 3. 实现 ConfigParser
# backend/app/plugins/config_parser.py
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigParser:
    @staticmethod
    def parse(config_path: Path) -> Optional[Dict[str, Any]]:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @staticmethod
    def validate(config: Dict[str, Any]) -> tuple[bool, list]:
        errors = []
        # 验证 plugin 段
        # 验证 type 字段
        # ...
        return len(errors) == 0, errors
```

```python
# 4. 实现 PluginLoader
# backend/app/plugins/loader.py
import importlib.util
import sys
from pathlib import Path
from typing import Dict
from app.plugins.base import BasePlugin, PluginType

class PluginLoader:
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self._loaded_plugins: Dict[str, BasePlugin] = {}

    async def discover_and_load_all(self) -> Dict[str, BasePlugin]:
        # 扫描 datasource/ 目录
        # 加载插件
        # 返回插件实例
        pass
```

**Day 5：启动集成**

```python
# 5. 修改 main.py
# backend/app/main.py
from contextlib import asynccontextmanager
from app.plugins.loader import PluginLoader
from pathlib import Path

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时加载插件
    plugin_dir = Path("data/plugins")
    plugin_loader = PluginLoader(plugin_dir)
    loaded_plugins = await plugin_loader.discover_and_load_all()
    logger.info(f"已加载 {len(loaded_plugins)} 个插件")

    yield

    # 关闭时清理
    await plugin_loader.cleanup_all()

app = FastAPI(lifespan=lifespan)
```

#### 3.1.3 验收标准

- [ ] BasePlugin 类定义完整
- [ ] PluginType 包含 DATASOURCE 和 AI_MODEL
- [ ] DataSourcePlugin 接口定义完整
- [ ] ConfigParser 能正确解析 YAML
- [ ] PluginLoader 能自动发现并加载插件
- [ ] 启动时插件自动加载

---

### 阶段二：语雀数据源插件（Week2：03/03-03/07）

#### 3.2.1 任务分解

| 任务 | 文件 | 工作量 | 依赖 |
|------|------|--------|------|
| yuque-dl 工具检测 | `yuque/plugin.py` | 2h | - |
| CLI 调用实现 | `yuque/plugin.py` | 4h | 工具检测 |
| Front Matter 解析 | `yuque/plugin.py` | 3h | - |
| 配置文件创建 | `yuque/config.yaml` | 1h | - |
| README 编写 | `yuque/README.md` | 1.5h | - |

#### 3.2.2 实施步骤

**Day 1-2：工具检测与插件框架**

```python
# 1. 创建语雀插件
# data/plugins/datasource/yuque/plugin.py
import asyncio
from pathlib import Path
from typing import Dict, Any, AsyncIterator
from app.plugins.interface.datasource import DataSourcePlugin, DataSourceItem

class YuqueDataSource(DataSourcePlugin):
    def __init__(self):
        self._yuque_dl_path = None
        self._download_dir = None

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "yuque",
            "name": "语雀知识库",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "基于 yuque-dl 的语雀知识库文档搜索"
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        # 1. 检测 yuque-dl 工具
        self._yuque_dl_path = await self._find_yuque_dl()
        if not self._yuque_dl_path:
            logger.error("未找到 yuque-dl，请安装: npm install -g yuque-dl")
            return False

        # 2. 设置下载目录
        self._download_dir = Path(config.get("download_dir", "./data/downloaded"))
        self._download_dir.mkdir(parents=True, exist_ok=True)

        return True

    async def _find_yuque_dl(self) -> str:
        # 1. 检查 npx
        if await self._check_command("npx yuque-dl --version"):
            return "npx yuque-dl"
        # 2. 检查全局安装
        if await self._check_command("yuque-dl --version"):
            return "yuque-dl"
        return None

    async def _check_command(self, cmd: str) -> bool:
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return proc.returncode == 0
        except:
            return False
```

**Day 3：CLI 调用实现**

```python
# 2. 实现 CLI 调用
async def scan(self, **kwargs) -> AsyncIterator[DataSourceItem]:
    # 1. 调用 yuque-dl 下载
    await self._download_repo()

    # 2. 扫描下载的文件
    async for item in self._scan_downloaded_files():
        yield item

async def _download_repo(self):
    cmd = self._build_command()
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        logger.error(f"yuque-dl 失败: {stderr.decode()}")

def _build_command(self) -> list:
    cmd = [self._yuque_dl_path]
    cmd.append(self._config["repo_url"])
    cmd.extend(["-d", str(self._download_dir)])

    if self._config.get("token"):
        cmd.extend(["-t", self._config["token"]])

    if self._config.get("incremental", True):
        cmd.append("--incremental")

    return cmd
```

**Day 4：Front Matter 解析**

```python
# 3. 实现元数据提取
import re
import yaml

async def _scan_downloaded_files(self):
    for root, dirs, files in os.walk(self._download_dir):
        for file in files:
            if not file.endswith(".md"):
                continue

            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取 Front Matter
            metadata = self._extract_front_matter(content)
            content = self._remove_front_matter(content)

            yield DataSourceItem(
                id=f"yuque:{file}",
                title=metadata.get("title", file),
                content=content,
                source_type="yuque",
                url=metadata.get("url", ""),
                metadata=metadata
            )

def _extract_front_matter(self, content: str) -> Dict:
    metadata = {}
    pattern = r'^---\n(.*?)\n---'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        try:
            metadata = yaml.safe_load(match.group(1)) or {}
        except:
            pass

    # 提取页脚 URL
    url_pattern = r'<!--原链接：(.*?)-->'
    url_match = re.search(url_pattern, content)
    if url_match:
        metadata["url"] = url_match.group(1).strip()

    return metadata

def _remove_front_matter(self, content: str) -> str:
    pattern = r'^---\n.*?\n---\n'
    return re.sub(pattern, '', content, count=1, flags=re.DOTALL).strip()
```

**Day 5：配置与文档**

```yaml
# 4. 创建配置文件
# data/plugins/datasource/yuque/config.yaml
plugin:
  id: yuque
  name: 语雀知识库
  version: "1.0.0"
  type: datasource
  enabled: true

yuque_dl:
  repo_url: "https://www.yuque.com/your-org/repo"
  download_dir: "./data/downloaded"
  token: ""  # 可选：访问私有知识库需要
  cookie_key: "_yuque_session"
  ignore_images: false
  incremental: true
```

```markdown
# 5. 创建 README.md
# data/plugins/datasource/yuque/README.md
# 语雀知识库插件

基于 [yuque-dl](https://github.com/gxr404/yuque-dl) 的语雀知识库数据源插件。

## 安装依赖

### 1. 安装 Node.js

确保系统已安装 Node.js 18.4 或更高版本

### 2. 安装 yuque-dl

\`\`\`bash
npm install -g yuque-dl
\`\`\`

或使用 npx：

\`\`\`bash
npx yuque-dl --version
\`\`\`

## 配置说明

编辑 \`config.yaml\` 文件：

\`\`\`yaml
yuque_dl:
  repo_url: "https://www.yuque.com/your-org/repo"
  token: ""  # 访问私有知识库需要
\`\`\`

## 获取 Cookie

1. 登录语雀
2. 打开浏览器 DevTools（F12）
3. 进入 Application -> Cookies -> https://www.yuque.com
4. 找到 \`_yuque_session\`，复制其值
```

#### 3.2.3 验收标准

- [ ] yuque-dl 工具检测正常（npx + 全局安装）
- [ ] CLI 调用成功下载知识库
- [ ] Front Matter 元数据提取正确
- [ ] 配置文件格式正确
- [ ] README 文档完整

---

### 阶段三：索引集成（Week3：03/10-03/14）

#### 3.3.1 任务分解

| 任务 | 文件 | 工作量 | 依赖 |
|------|------|--------|------|
| 本地文件插件迁移 | `filesystem/plugin.py` | 5h | DataSourcePlugin |
| 索引服务扩展 | `services/unified_index_service.py` | 3h | PluginLoader |
| 搜索响应扩展 | `api/search.py` | 2h | 索引服务 |

#### 3.3.2 实施步骤

**Day 1-2：本地文件插件迁移**

```python
# 1. 创建本地文件插件
# data/plugins/datasource/filesystem/plugin.py
import os
from pathlib import Path
from typing import Dict, Any, AsyncIterator
from app.plugins.interface.datasource import DataSourcePlugin, DataSourceItem

class FileSystemDataSource(DataSourcePlugin):
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "filesystem",
            "name": "本地文件",
            "version": "1.0.0",
            "type": "datasource"
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        self.scan_dirs = config.get("scan_dirs", [])
        return len(self.scan_dirs) > 0

    async def scan(self, **kwargs) -> AsyncIterator[DataSourceItem]:
        for scan_dir in self.scan_dirs:
            for root, dirs, files in os.walk(scan_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 读取文件并生成 DataSourceItem
                    yield self._process_file(file_path)

    def _process_file(self, file_path: str) -> DataSourceItem:
        # 文件处理逻辑
        pass
```

**Day 3：索引服务扩展**

```python
# 2. 扩展索引服务
# backend/app/services/unified_index_service.py
from app.plugins.loader import PluginLoader

class UnifiedIndexService:
    def __init__(self, plugin_loader: PluginLoader):
        self.plugin_loader = plugin_loader

    async def build_index(self):
        """构建多数据源索引"""
        datasource_plugins = self.plugin_loader.get_plugins_by_type("datasource")

        for plugin_id, plugin in datasource_plugins.items():
            logger.info(f"开始扫描数据源: {plugin_id}")

            async for item in plugin.scan():
                # 索引数据项
                await self._index_item(item, plugin_id)

            logger.info(f"完成扫描数据源: {plugin_id}")

    async def _index_item(self, item: DataSourceItem, source_id: str):
        """索引单个数据项"""
        # 1. 生成向量嵌入
        embedding = await self.embedding_service.embed_text(item.content)

        # 2. 存入数据库
        await self.db.insert_file(
            file_id=item.id,
            filename=item.title,
            content=item.content,
            source_type=item.source_type,
            source_url=item.url
        )

        # 3. 添加到向量索引
        await self.vector_index.add(item.id, embedding)
```

**Day 4-5：搜索响应扩展**

```python
# 3. 扩展搜索响应
# backend/app/api/search.py
@router.post("/search")
async def search(request: SearchRequest):
    # 1. 向量搜索
    results = await vector_service.search(query, top_k=20)

    # 2. 增强响应，添加数据源信息
    enriched_results = []
    for result in results:
        file_record = await db.get_file(result["id"])

        enriched = {
            **result,
            "source_type": file_record.get("source_type", "filesystem"),
            "source_url": file_record.get("source_url", ""),
            "source_name": _get_source_name(file_record.get("source_type"))
        }

        enriched_results.append(enriched)

    return {"results": enriched_results}

def _get_source_name(source_type: str) -> str:
    names = {
        "filesystem": "本地文件",
        "yuque": "语雀知识库",
        "feishu": "飞书文档"
    }
    return names.get(source_type, source_type)
```

#### 3.3.3 验收标准

- [ ] 本地文件插件正常工作
- [ ] 索引服务支持多数据源
- [ ] 搜索结果包含数据源信息
- [ ] 向后兼容现有功能

---

### 阶段四：数据库迁移与测试（Week4：03/17-03/21）

#### 3.4.1 任务分解

| 任务 | 文件 | 工作量 | 依赖 |
|------|------|--------|------|
| 数据库迁移脚本 | `alembic/versions/xxx.py` | 2h | - |
| 单元测试 | `tests/plugins/` | 6h | 插件实现 |
| 集成测试 | `tests/integration/` | 5h | 全部实现 |
| 文档完善 | 各文档 | 3h | - |

#### 3.4.2 实施步骤

**Day 1：数据库迁移**

```sql
-- 1. 创建迁移脚本
-- alembic/versions/002_add_plugin_source_fields.py
def upgrade():
    op.add_column('files', sa.Column('source_type', sa.String(), nullable=True))
    op.add_column('files', sa.Column('source_url', sa.String(), nullable=True))

    # 更新现有数据
    op.execute("UPDATE files SET source_type = 'filesystem' WHERE source_type IS NULL")

    # 创建索引
    op.create_index('idx_files_source_type', 'files', ['source_type'])

def downgrade():
    op.drop_index('idx_files_source_type', 'files')
    op.drop_column('files', 'source_url')
    op.drop_column('files', 'source_type')
```

```bash
# 2. 执行迁移
cd backend
alembic upgrade head

# 3. 验证迁移
sqlite3 data/xiaoyaosearch.db "SELECT source_type, COUNT(*) FROM files GROUP BY source_type;"
```

**Day 2-3：单元测试**

```python
# tests/plugins/test_config_parser.py
import pytest
from app.plugins.config_parser import ConfigParser
from pathlib import Path

def test_parse_valid_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
plugin:
  id: test
  name: 测试
  version: "1.0.0"
  type: datasource
  enabled: true
""")

    config = ConfigParser.parse(config_file)
    assert config is not None
    assert config["plugin"]["id"] == "test"

def test_validate_missing_type():
    config = {"plugin": {"id": "test"}}
    valid, errors = ConfigParser.validate(config)
    assert not valid
    assert "type" in str(errors)
```

```python
# tests/plugins/test_loader.py
import pytest
from app.plugins.loader import PluginLoader
from pathlib import Path

@pytest.mark.asyncio
async def test_discover_plugins(tmp_path):
    # 创建测试插件目录
    plugin_dir = tmp_path / "plugins" / "datasource" / "test"
    plugin_dir.mkdir(parents=True)

    (plugin_dir / "plugin.py").write_text("""
from app.plugins.interface.datasource import DataSourcePlugin

class TestPlugin(DataSourcePlugin):
    @classmethod
    def get_metadata(cls):
        return {"id": "test", "type": "datasource"}

    async def initialize(self, config):
        return True

    async def scan(self, **kwargs):
        return
    async def get_content(self, item_id):
        return None
    async def cleanup(self):
        pass
""")

    (plugin_dir / "config.yaml").write_text("""
plugin:
  id: test
  type: datasource
  enabled: true
""")

    loader = PluginLoader(tmp_path / "plugins")
    plugins = await loader.discover_and_load_all()

    assert "test" in plugins
```

**Day 4：集成测试**

```python
# tests/integration/test_yuque_plugin.py
import pytest
from unittest.mock import AsyncMock, patch
from app.plugins.loader import PluginLoader

@pytest.mark.asyncio
async def test_yuque_plugin_download():
    # Mock subprocess
    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"", b""))
        mock_subprocess.return_value = mock_process

        # 测试插件
        from data.plugins.datasource.yuque.plugin import YuqueDataSource

        plugin = YuqueDataSource()
        await plugin.initialize({"repo_url": "https://www.yuque.com/test/repo"})

        # 验证命令被正确调用
        assert mock_subprocess.called
```

**Day 5：文档完善与验收**

```markdown
# 更新插件开发指南
# docs/技术文档/插件开发指南.md

## 快速开始

1. 创建插件目录
2. 实现 DataSourcePlugin 接口
3. 创建 config.yaml
4. 复制到 data/plugins/ 目录

## 示例：创建新数据源插件

...详细示例...
```

#### 3.4.3 验收标准

- [ ] 数据库迁移成功
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试全部通过
- [ ] 文档完整准确

---

## 4. 代码实现指南

### 4.1 核心代码模板

#### BasePlugin 模板

```python
# backend/app/plugins/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePlugin(ABC):
    """插件基类模板"""

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        返回插件元数据

        Returns:
            Dict with keys: id, name, version, type, author, description
        """
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        Args:
            config: 配置字典（来自 config.yaml）

        Returns:
            bool: 初始化是否成功
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """清理资源"""
        pass
```

#### DataSourcePlugin 模板

```python
# 数据源插件模板
from app.plugins.interface.datasource import DataSourcePlugin, DataSourceItem
from typing import Dict, Any, AsyncIterator

class MyDataSource(DataSourcePlugin):

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "my_datasource",
            "name": "我的数据源",
            "version": "1.0.0",
            "type": "datasource",
            "author": "Your Name",
            "description": "数据源描述"
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        # 1. 验证配置
        # 2. 初始化连接
        # 3. 返回是否成功
        return True

    async def scan(self, **kwargs) -> AsyncIterator[DataSourceItem]:
        # 扫描数据源，yield DataSourceItem
        pass

    async def get_content(self, item_id: str) -> str:
        # 获取单个数据项内容
        pass

    async def cleanup(self):
        # 清理资源
        pass
```

#### 配置文件模板

```yaml
# config.yaml 模板
plugin:
  id: my_datasource
  name: 我的数据源
  version: "1.0.0"
  type: datasource        # 必须与目录类型匹配
  enabled: true           # 是否启用

datasource:
  # 数据源特定配置
  api_key: ""
  base_url: ""
```

### 4.2 常用代码片段

#### yuque-dl 命令构建

```python
def build_yuque_dl_command(self) -> list:
    cmd = ["npx", "yuque-dl"]  # 或 "yuque-dl"

    # URL
    cmd.append(self.config["repo_url"])

    # 输出目录
    cmd.extend(["-d", str(self.download_dir)])

    # Token（可选）
    if token := self.config.get("token"):
        cmd.extend(["-t", token])

    # 增量下载
    if self.config.get("incremental", True):
        cmd.append("--incremental")

    return cmd
```

#### Front Matter 解析

```python
import re
import yaml

def extract_front_matter(content: str) -> dict:
    """提取 Markdown Front Matter"""
    pattern = r'^---\n(.*?)\n---'
    match = re.match(pattern, content, re.DOTALL)

    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}
        except:
            return {}

    return {}
```

#### 错误处理

```python
import logging

logger = logging.getLogger(__name__)

try:
    # 可能失败的代码
    result = await some_operation()
except Exception as e:
    logger.error(f"操作失败: {e}")
    # 错误隔离：不影响其他插件
    raise
```

---

## 5. 测试验证方案

### 5.1 测试金字塔

```
                    /\
                   /E2E\         ← 端到端测试（少量）
                  /------\
                 /  集成  \       ← 集成测试（适量）
                /----------\
               /   单元测试  \    ← 单元测试（大量）
              /--------------\
```

### 5.2 单元测试

```bash
# 运行所有单元测试
pytest tests/plugins/ -v

# 运行特定测试文件
pytest tests/plugins/test_config_parser.py -v

# 生成覆盖率报告
pytest tests/plugins/ --cov=app/plugins --cov-report=html
```

**关键测试用例**：

| 测试模块 | 测试内容 | 预期结果 |
|---------|---------|---------|
| ConfigParser | 解析有效配置 | 成功解析 |
| ConfigParser | 缺少必需字段 | 返回错误列表 |
| PluginLoader | 发现插件 | 返回插件列表 |
| PluginLoader | 类型不匹配 | 跳过该插件 |
| YuqueDataSource | 工具检测 | 正确检测 npx/全局安装 |

### 5.3 集成测试

```bash
# 运行集成测试
pytest tests/integration/ -v

# Mock 外部依赖
pytest tests/integration/test_yuque_plugin.py --mock-external
```

**关键测试场景**：

1. **插件加载流程**
   - 启动时自动发现插件
   - 配置验证通过后加载
   - 初始化成功

2. **语雀插件流程**
   - yuque-dl 调用成功
   - 文件下载到指定目录
   - 元数据提取正确

3. **索引集成流程**
   - 多数据源扫描
   - 索引构建成功
   - 搜索结果包含数据源信息

### 5.4 手动测试清单

```markdown
## 插件安装测试
- [ ] 复制插件到 data/plugins/datasource/yuque/
- [ ] 启动服务，查看日志确认插件加载
- [ ] 检查插件状态

## 语雀插件测试
- [ ] 配置公开知识库 URL
- [ ] 执行扫描，检查下载文件
- [ ] 搜索内容，验证结果
- [ ] 检查 source_type、source_url 字段

## 本地文件插件测试
- [ ] 配置扫描目录
- [ ] 执行扫描，验证文件发现
- [ ] 搜索内容，验证向后兼容

## 错误处理测试
- [ ] 插件配置错误，系统正常启动
- [ ] yuque-dl 未安装，给出明确提示
- [ ] 网络错误，不影响其他数据源
```

---

## 6. 部署上线方案

### 6.1 部署前检查

```bash
# 1. 代码检查
# 运行所有测试
pytest tests/ -v --cov=app/plugins --cov-report=term-missing

# 代码格式检查
black app/plugins/ --check
isort app/plugins/ --check

# 2. 数据库备份
cp backend/data/xiaoyaosearch.db backend/data/xiaoyaosearch.db.backup

# 3. 依赖检查
pip list | grep -E "pyyaml|pytest"

# 4. 配置检查
ls data/plugins/datasource/*/
```

### 6.2 部署步骤

```bash
# 1. 停止服务
# Windows
taskkill /F /IM python.exe

# 2. 更新代码
git pull origin main

# 3. 安装依赖
cd backend
pip install -r requirements.txt

# 4. 数据库迁移
alembic upgrade head

# 5. 验证插件目录
ls -la data/plugins/datasource/

# 6. 启动服务
python main.py

# 7. 验证日志
# 检查插件加载日志
# 确认无错误信息
```

### 6.3 回滚方案

```bash
# 如果出现问题，回滚步骤

# 1. 停止服务
taskkill /F /IM python.exe

# 2. 恢复数据库
cp backend/data/xiaoyaosearch.db.backup backend/data/xiaoyaosearch.db

# 3. 回滚代码
git checkout <previous_commit>

# 4. 重启服务
python main.py
```

### 6.4 监控指标

| 指标 | 监控方式 | 预期值 |
|------|---------|--------|
| 插件加载成功率 | 日志统计 | 100% |
| 插件扫描耗时 | 日志时间戳 | <5分钟/数据源 |
| 索引构建时间 | 日志统计 | <10分钟 |
| 搜索响应时间 | API 监控 | <500ms |
| 错误率 | 日志错误数 | <1% |

---

## 7. 风险应对预案

### 7.1 风险矩阵

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| yuque-dl 工具不可用 | 中 | 高 | 提供详细安装说明，支持 npx |
| 插件加载失败 | 低 | 中 | 错误隔离，记录详细日志 |
| 数据库迁移失败 | 低 | 高 | 提前备份，提供回滚脚本 |
| 索引构建超时 | 中 | 中 | 分批处理，支持断点续传 |
| Front Matter 解析错误 | 中 | 低 | 容错处理，提供默认值 |

### 7.2 具体应对方案

#### 方案A：yuque-dl 不可用

**问题**：用户环境中没有 Node.js 或 yuque-dl

**应对**：
1. 启动时检测，给出明确安装提示
2. README 提供详细安装步骤
3. 支持 npx 自动调用（无需全局安装）

```python
if not await self._check_yuque_dl():
    logger.error("""
    未找到 yuque-dl，请安装：

    方法1：全局安装
    npm install -g yuque-dl

    方法2：使用 npx（无需安装）
    确保 Node.js 18.4+ 已安装

    参考文档：data/plugins/datasource/yuque/README.md
    """)
    return False
```

#### 方案B：插件初始化失败

**问题**：插件配置错误或初始化失败

**应对**：
1. 配置验证，启动时发现问题
2. 错误隔离，单个插件失败不影响其他
3. 详细日志，便于排查问题

```python
try:
    if await plugin.initialize(config):
        self._loaded_plugins[plugin_id] = plugin
    else:
        logger.warning(f"插件初始化失败: {plugin_id}")
except Exception as e:
    logger.error(f"插件加载异常 {plugin_id}: {e}")
    # 继续加载其他插件
```

#### 方案C：数据库迁移失败

**问题**：迁移脚本执行失败

**应对**：
1. 提前备份数据库
2. 提供回滚脚本
3. 分步迁移，支持中断恢复

```bash
# 迁移前检查
python -c "from alembic.config import Config; from alembic.script import ScriptDirectory; print('OK')"

# 备份数据库
cp data.db data.db.backup

# 执行迁移
alembic upgrade head

# 验证迁移
python -c "import sqlite3; conn = sqlite3.connect('data.db'); print(conn.execute('PRAGMA table_info(files)').fetchall())"
```

---

## 8. 验收标准

### 8.1 功能验收

| 功能项 | 验收标准 | 验证方法 |
|--------|---------|---------|
| **插件基础设施** | | |
| BasePlugin 实现 | 包含所有必需方法 | 代码审查 |
| PluginType 枚举 | 包含 DATASOURCE 和 AI_MODEL | 单元测试 |
| ConfigParser | 能正确解析 YAML，验证类型 | 单元测试 |
| PluginLoader | 能自动发现并加载插件 | 集成测试 |
| **语雀插件** | | |
| yuque-dl 检测 | 支持 npx 和全局安装 | 手动测试 |
| CLI 调用 | 能成功下载知识库 | 集成测试 |
| 元数据提取 | Front Matter 解析正确 | 单元测试 |
| **索引集成** | | |
| 多数据源支持 | 能同时索引多个数据源 | 集成测试 |
| 搜索扩展 | 结果包含 source_type、source_url | API 测试 |
| 向后兼容 | 本地文件搜索正常 | 回归测试 |

### 8.2 性能验收

| 性能指标 | 目标值 | 测量方法 |
|---------|--------|---------|
| 插件加载时间 | <2秒 | 日志时间戳 |
| 单个数据源扫描 | <5分钟 | 性能测试 |
| 索引构建时间 | <10分钟 | 性能测试 |
| 搜索响应时间 | <500ms | API 监控 |
| 内存占用 | <500MB | 资源监控 |

### 8.3 质量验收

| 质量指标 | 目标值 | 测量方法 |
|---------|--------|---------|
| 单元测试覆盖率 | ≥80% | pytest --cov |
| 代码质量 | 无严重问题 | black + isort |
| 文档完整性 | 100% | 文档检查清单 |
| 错误处理 | 所有异常被捕获 | 代码审查 + 日志检查 |

### 8.4 最终验收清单

```markdown
## 代码交付
- [ ] 所有代码提交到 Git
- [ ] 代码通过格式检查
- [ ] 代码通过静态分析

## 测试交付
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过
- [ ] 测试覆盖率 ≥80%
- [ ] 性能测试报告

## 文档交付
- [ ] 技术方案（v2.1）
- [ ] 任务清单（v2.1）
- [ ] 开发排期表（v2.1）
- [ ] 插件开发指南
- [ ] 语雀插件 README

## 部署交付
- [ ] 数据库迁移脚本
- [ ] 回滚脚本
- [ ] 部署文档
- [ ] 监控配置
```

---

## 9. 附录

### 9.1 文件清单

#### 新建文件

```
backend/app/plugins/
├── __init__.py
├── base.py                          # 插件基类
├── interface/
│   ├── __init__.py
│   ├── datasource.py                # 数据源接口
│   └── ai_model.py                  # AI模型接口（预留）
├── config_parser.py                 # 配置解析器
└── loader.py                        # 插件加载器

data/plugins/datasource/
├── yuque/
│   ├── plugin.py                    # 语雀插件实现
│   ├── config.yaml                  # 语雀配置文件
│   ├── requirements.txt             # 依赖说明
│   ├── README.md                    # 使用说明
│   └── data/
│       └── downloaded/              # 下载文件目录
└── filesystem/
    ├── plugin.py                    # 本地文件插件
    └── config.yaml                  # 配置文件

tests/plugins/
├── __init__.py
├── test_config_parser.py
├── test_loader.py
└── test_yuque_plugin.py

tests/integration/
├── __init__.py
└── test_plugin_integration.py

alembic/versions/
└── 002_add_plugin_source_fields.py  # 数据库迁移
```

#### 修改文件

```
backend/app/main.py                   # 启动时加载插件
backend/app/services/unified_index_service.py  # 索引服务扩展
backend/app/api/search.py            # 搜索响应扩展
```

### 9.2 参考资料

| 资源 | 链接 |
|------|------|
| yuque-dl 项目 | https://github.com/gxr404/yuque-dl |
| Python importlib | https://docs.python.org/3/library/importlib.html |
| PyYAML 文档 | https://pyyaml.org/wiki/PyYAMLDocumentation |
| asyncio subprocess | https://docs.python.org/3/library/asyncio-subprocess.html |

### 9.3 联系方式

| 角色 | 联系方式 |
|------|---------|
| 开发者 | - |
| 技术支持 | - |

---

**文档版本**: v2.1
**创建时间**: 2026-02-22
**最后更新**: 2026-02-22 (v2.1 - yuque-dl CLI集成)
**维护者**: 开发者
**文档状态**: 待实施

# 插件化架构与语雀数据源 - 原型说明

> **文档类型**：原型设计说明
> **特性状态**：规划中
> **创建时间**：2026-02-22
> **最后更新**：2026-02-22 (v1.2 - 约定优于配置)

---

## 原型设计说明

### 本特性不包含前端界面设计

**原因**：
- 本特性专注于后端插件架构实现
- 插件通过配置文件管理，无需API接口
- 暂不提供可视化的前端管理界面

---

## 设计原则：约定优于配置

本特性采用"约定优于配置"原则，所有插件管理通过文件系统和配置文件完成：

### 插件目录结构

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

### 插件配置文件示例

```yaml
# data/plugins/yuque/config.yaml
plugin:
  id: yuque
  name: 语雀知识库
  version: "1.0.0"
  enabled: true

datasource:
  type: yuque
  api_token: "your_yuque_api_token_here"
  repo_slug: "username/knowledge_base"
  base_url: "https://www.yuque.com/api/v2"

sync:
  interval: 60          # 同步间隔（分钟）
  batch_size: 50        # 每批处理文档数量
  timeout: 30           # 请求超时时间（秒）
```

---

## 交互方式

### 安装插件

```bash
# 1. 创建插件目录
mkdir -p data/plugins/yuque

# 2. 复制插件文件
cp plugin.py data/plugins/yuque/
cp config.yaml data/plugins/yuque/

# 3. 编辑配置文件
vim data/plugins/yuque/config.yaml

# 4. 重启服务
systemctl restart xiaoyao-search
```

### 配置插件

```bash
# 直接编辑配置文件
vim data/plugins/yuque/config.yaml

# 修改后重启服务生效
systemctl restart xiaoyao-search
```

### 禁用插件

```bash
# 方法1：修改配置文件
# data/plugins/yuque/config.yaml
# plugin.enabled: false

# 方法2：重命名目录
mv data/plugins/yuque data/plugins/yuque.disabled

# 重启服务
systemctl restart xiaoyao-search
```

### 卸载插件

```bash
# 删除插件目录
rm -rf data/plugins/yuque

# 重启服务
systemctl restart xiaoyao-search
```

---

## API接口变更

本特性仅修改搜索API的响应结构，新增数据源信息字段：

### 搜索接口（扩展）

```bash
# 搜索（响应增加数据源信息）
POST /api/search
Body: {"query": "关键词"}

# 响应新增字段
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "file_001",
        "filename": "产品需求文档.md",
        "path": "/docs/产品需求文档.md",
        "content_preview": "这是一个产品需求文档...",
        "score": 0.95,

        # 新增字段
        "source_type": "filesystem",
        "source_url": null,
        "source_name": "本地文件"
      },
      {
        "id": "yuque_001",
        "filename": "API设计规范",
        "path": "https://www.yuque.com/docs/api-design",
        "content_preview": "本文档描述API设计规范...",
        "score": 0.92,

        # 新增字段
        "source_type": "yuque",
        "source_url": "https://www.yuque.com/docs/api-design",
        "source_name": "语雀知识库"
      }
    ]
  }
}
```

---

## 插件开发规范

### 插件接口定义

```python
# app/plugins/interface.py
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any

class DataSourcePlugin(ABC):
    """数据源插件接口"""

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """返回插件元数据"""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass

    @abstractmethod
    async def scan(self) -> AsyncIterator[Dict[str, Any]]:
        """扫描数据源，返回标准化的数据项"""
        pass

    @abstractmethod
    async def cleanup(self):
        """清理资源"""
        pass
```

### 插件实现示例

```python
# data/plugins/yuque/plugin.py
import httpx
from app.plugins.interface import DataSourcePlugin

class YuquePlugin(DataSourcePlugin):
    """语雀知识库数据源插件"""

    def get_metadata(self):
        return {
            "id": "yuque",
            "name": "语雀知识库",
            "version": "1.0.0",
            "author": "XiaoyaoSearch Team",
            "description": "支持语雀知识库文档搜索"
        }

    async def initialize(self, config):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.get("base_url", "https://www.yuque.com/api/v2"),
            headers={"Authorization": f"Bearer {config['api_token']}"}
        )
        return True

    async def scan(self):
        """扫描语雀文档"""
        repo = self.config["repo_slug"]
        response = await self.client.get(f"/repos/{repo}/docs")
        docs = response.json()["data"]

        for doc in docs:
            yield {
                "id": f"yuque_{doc['id']}",
                "filename": doc["title"],
                "path": doc["url"],
                "content": await self._get_doc_content(doc["slug"]),
                "source_type": "yuque",
                "source_url": doc["url"],
                "source_name": "语雀知识库"
            }

    async def _get_doc_content(self, slug):
        """获取文档详情"""
        response = await self.client.get(f"/docs/{slug}")
        return response.json()["data"]["body"]

    async def cleanup(self):
        await self.client.aclose()
```

---

## 系统启动流程

```
系统启动
    ↓
扫描 data/plugins/ 目录
    ↓
发现所有插件目录（yuque/、feishu/等）
    ↓
读取每个插件的 config.yaml
    ↓
验证配置有效性
    ↓
动态加载插件模块（plugin.py）
    ↓
初始化插件实例
    ↓
启动后台同步任务
    ↓
系统就绪，接收搜索请求
```

---

## 配置热重载（未来规划）

当前版本需要重启服务才能加载新插件，未来版本将支持：

- [ ] 监听插件目录变化
- [ ] 自动检测新插件
- [ ] 配置文件变更自动重载
- [ ] 无需重启服务

---

## 后续规划

如需添加前端管理界面，将创建以下原型页面：

1. **数据源列表页面** - 显示所有已加载的数据源插件
2. **数据源配置页面** - 可视化编辑配置文件
3. **同步状态页面** - 显示数据源同步进度和结果
4. **搜索结果优化** - 显示数据来源标识，支持筛选
5. **插件市场** - 浏览和安装社区插件

---

## 相关文档

- [PRD文档](./plugins+yuque-01-prd.md) - 产品需求文档
- [技术方案](./plugins+yuque-03-技术方案.md) - 技术实现方案
- [API增量文档](./plugins+yuque-增量-接口文档.md) - API接口变更
- [数据库增量文档](./plugins+yuque-增量-数据库设计文档.md) - 数据库设计变更

---

## 开发者资源

### 配置项说明

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plugin.id | string | 是 | 插件唯一标识 |
| plugin.name | string | 是 | 插件显示名称 |
| plugin.version | string | 是 | 版本号（semver格式） |
| plugin.enabled | boolean | 是 | 是否启用插件 |
| datasource.type | string | 是 | 数据源类型 |
| sync.interval | integer | 否 | 同步间隔（分钟），默认60 |

### 插件开发脚手架

```bash
# 创建新插件
python -m app.plugins.devtools create my_datasource

# 生成插件模板
# - plugin.py
# - config.yaml
# - requirements.txt
# - README.md
```

---

**文档结束**

> **说明**：
> 1. 本特性采用"约定优于配置"原则
> 2. 插件通过文件系统和配置文件管理
> 3. 无需API接口，重启服务即可生效
> 4. 后续可扩展前端管理界面

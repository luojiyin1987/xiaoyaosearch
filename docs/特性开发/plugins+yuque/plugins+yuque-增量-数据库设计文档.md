# 插件化架构与语雀数据源 - 数据库设计增量

> **特性状态**：规划中
> **创建时间**：2026-02-22
> **最后更新**：2026-02-22 (v1.3 - 插件提供元数据)
> **关联文档**：[技术方案](./plugins+yuque-03-技术方案.md) | [任务清单](./plugins+yuque-04-开发任务清单.md)

---

## 目录

1. [数据库变更概述](#1-数据库变更概述)
2. [表结构变更](#2-表结构变更)
3. [数据库迁移脚本](#3-数据库迁移脚本)
4. [索引优化](#4-索引优化)
5. [数据字典](#5-数据字典)

---

## 1. 数据库变更概述

### 1.1 变更统计

| 类别 | 新增 | 修改 | 删除 |
|------|------|------|------|
| 数据库表 | 0 | 1 | 0 |
| 字段 | 2 | 0 | 0 |
| 索引 | 1 | 0 | 0 |
| 外键约束 | 0 | 0 | 0 |

### 1.2 变更说明

**设计原则**：
1. **约定优于配置**：插件元数据和配置通过文件系统管理，数据库仅存储索引数据
2. **插件提供元数据**：source_type 和 source_url 由插件通过 `get_file_source_info()` 方法提供

**核心优势**：
- ✅ **完全解耦**：索引服务不需要硬编码各数据源的提取规则
- ✅ **易于扩展**：新增数据源只需实现插件接口，无需修改索引服务代码
- ✅ **插件自治**：每个插件最了解自己的文件格式和元数据位置

**变更内容**：
- **不新增表**：无需插件元数据表、配置表、同步记录表
- **修改现有表**：为 `files` 表新增数据源标识字段（source_type、source_url）

### 1.3 ER图扩展

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         插件化架构扩展 ER 图                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                        现有表（扩展字段）                            │ │
│  │  ┌───────────────────────────────────────────────────────────────┐ │ │
│  │  │ files                                                         │ │ │
│  │  │ - id (PK)                                                     │ │ │
│  │  │ - filename                                                    │ │ │
│  │  │ - path                                                        │ │ │
│  │  │ - file_type                                                   │ │ │
│  │  │ - content                                                     │ │ │
│  │  │ - faiss_index_id                                             │ │ │
│  │  │ + source_type ⬅ NEW (数据源类型)                            │ │ │
│  │  │ + source_url ⬅ NEW (原文访问链接)                           │ │ │
│  │  └───────────────────────────────────────────────────────────────┘ │ │
│  │                                                                   │ │
│  │  现有其他表关系保持不变...                                         │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    文件系统（插件管理）                              │ │
│  │  data/plugins/                                                      │ │
│  │  ├── yuque/                                                         │ │
│  │  │   ├── plugin.py      (插件实现)                                 │ │
│  │  │   └── config.yaml   (插件配置)                                 │ │
│  │  ├── feishu/                                                        │ │
│  │  │   ├── plugin.py                                                 │ │
│  │  │   └── config.yaml                                               │ │
│  │  └── filesystem/                                                   │ │
│  │      ├── plugin.py                                                 │ │
│  │      └── config.yaml                                               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 表结构变更

### 2.1 files 表扩展

为现有的 `files` 表新增数据源相关字段，用于标识文件来源。

#### 新增字段

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| source_type | TEXT | 否 | 'filesystem' | 数据源类型（filesystem/yuque/feishu等） |
| source_url | TEXT | 否 | NULL | 原文访问链接（云端数据源使用） |

#### 变更后表结构

```sql
-- 原有字段保持不变
CREATE TABLE files (
    -- 主键和基础信息
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,

    -- 内容索引
    content TEXT,
    faiss_index_id INTEGER,
    whoosh_doc_id TEXT,

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 新增字段：数据源信息
    source_type TEXT DEFAULT 'filesystem',  -- 数据源类型
    source_url TEXT                         -- 原文访问链接
);

-- 新增索引
CREATE INDEX idx_files_source_type ON files(source_type);
```

#### 字段说明

| 字段 | 数据类型 | 默认值 | 说明 | 示例值 |
|------|----------|--------|------|--------|
| source_type | TEXT | 'filesystem' | 数据源类型标识（由插件提供） | 'filesystem' / 'yuque' / 'feishu' |
| source_url | TEXT | NULL | 原文访问链接（由插件从文件内容提取） | NULL / 'https://yuque.com/...' |

**字段获取方式**：

| 字段 | 获取方式 | 说明 |
|------|---------|------|
| `source_type` | 调用插件的 `get_file_source_info()` 方法 | 每个插件返回自己的 source_type |
| `source_url` | 调用插件的 `get_file_source_info()` 方法 | 每个插件从文件内容提取自己的 URL 格式 |

---

## 3. 数据库迁移脚本

### 3.1 SQL 迁移脚本

```sql
-- =====================================================
-- 插件化架构数据库迁移脚本
-- 版本: v1.3.0
-- 日期: 2026-02-22
-- 说明: 为files表新增数据源标识字段（由插件提供）
-- =====================================================

-- 1. 新增 source_type 字段
ALTER TABLE files ADD COLUMN source_type TEXT DEFAULT 'filesystem';

-- 2. 新增 source_url 字段
ALTER TABLE files ADD COLUMN source_url TEXT;

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_files_source_type ON files(source_type);

-- 4. 更新现有记录的source_type
UPDATE files SET source_type = 'filesystem' WHERE source_type IS NULL;

-- 5. 验证迁移结果
SELECT
    COUNT(*) as total_files,
    SUM(CASE WHEN source_type = 'filesystem' THEN 1 ELSE 0 END) as filesystem_count,
    SUM(CASE WHEN source_type != 'filesystem' THEN 1 ELSE 0 END) as plugin_count
FROM files;
```

### 3.2 Alembic 迁移脚本

```python
# alembic/versions/002_add_plugin_source_fields.py
"""添加数据源标识字段（由插件提供元数据）

Revision ID: 002_add_plugin_source_fields
Revises: 001_initial
Create Date: 2026-02-22
说明: source_type 和 source_url 由插件通过 get_file_source_info() 方法提供

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_add_plugin_source_fields'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """升级：添加数据源字段（字段值由插件提供）"""
    # 添加 source_type 字段
    op.add_column(
        'files',
        sa.Column('source_type', sa.Text(), nullable=True, server_default='filesystem')
    )

    # 添加 source_url 字段
    op.add_column(
        'files',
        sa.Column('source_url', sa.Text(), nullable=True)
    )

    # 创建索引
    op.create_index(
        'idx_files_source_type',
        'files',
        ['source_type']
    )

    # 更新现有记录
    op.execute(
        "UPDATE files SET source_type = 'filesystem' WHERE source_type IS NULL"
    )


def downgrade():
    """降级：移除数据源字段"""
    op.drop_index('idx_files_source_type', table_name='files')
    op.drop_column('files', 'source_url')
    op.drop_column('files', 'source_type')
```

### 3.3 回滚脚本

```sql
-- =====================================================
-- 回滚脚本
-- 说明: 移除数据源标识字段
-- =====================================================

-- 1. 删除索引
DROP INDEX IF EXISTS idx_files_source_type;

-- 2. 删除字段
ALTER TABLE files DROP COLUMN source_url;
ALTER TABLE files DROP COLUMN source_type;
```

---

## 4. 索引优化

### 4.1 新增索引

| 索引名 | 字段 | 索引类型 | 说明 |
|--------|------|----------|------|
| idx_files_source_type | source_type | BTREE | 按数据源类型查询优化 |

### 4.2 索引使用示例

```sql
-- 按数据源类型查询文件
SELECT * FROM files WHERE source_type = 'yuque';

-- 统计各数据源文件数量
SELECT source_type, COUNT(*) as count
FROM files
GROUP BY source_type;

-- 联合查询（结合原有索引）
SELECT * FROM files
WHERE source_type = 'yuque'
  AND file_type = 'markdown'
ORDER BY updated_at DESC;
```

### 4.3 索引维护

```sql
-- 分析索引使用情况
ANALYZE files;

-- 重建索引（碎片整理）
REINDEX TABLE files;

-- 查看索引统计信息
SELECT
    name,
    tbl_name,
    sql
FROM sqlite_master
WHERE type = 'index'
  AND tbl_name = 'files';
```

---

## 5. 数据字典

### 5.1 扩展字段详细说明

#### source_type（数据源类型）

| 属性 | 值 |
|------|-----|
| 字段名 | source_type |
| 数据类型 | TEXT |
| 长度 | 无限制 |
| 默认值 | 'filesystem' |
| 可空 | 是 |
| 索引 | 是 |
| **数据来源** | **由插件通过 `get_file_source_info()` 方法提供** |

**枚举值说明**

| 值 | 说明 | 示例 |
|-----|------|------|
| filesystem | 本地文件系统 | `/home/user/docs/file.md` |
| yuque | 语雀知识库 | 语雀文档 |
| feishu | 飞书文档 | 飞书文档 |
| notion | Notion | Notion页面 |
| dingtalk | 钉钉文档 | 钉钉文档 |

#### source_url（原文访问链接）

| 属性 | 值 |
|------|-----|
| 字段名 | source_url |
| 数据类型 | TEXT |
| 长度 | 无限制 |
| 默认值 | NULL |
| 可空 | 是 |
| 索引 | 否 |
| **数据来源** | **由插件从文件内容提取（如语雀文档底部的"原文: <URL>"）** |

**使用说明**
- 本地文件：该字段为 NULL
- 云端数据源：存储原文访问链接

**示例值**

| 数据源类型 | source_url 示例 |
|-----------|-----------------|
| filesystem | NULL |
| yuque | `https://www.yuque.com/docs/abc123` |
| feishu | `https://feishu.cn/docs/xyz789` |

### 5.2 典型查询示例

```sql
-- 查询语雀文档
SELECT id, filename, source_url
FROM files
WHERE source_type = 'yuque'
ORDER BY updated_at DESC
LIMIT 10;

-- 查询所有云端数据源文档
SELECT source_type, COUNT(*) as count
FROM files
WHERE source_type != 'filesystem'
GROUP BY source_type;

-- 全文搜索限制数据源
SELECT f.*, si.score
FROM files f
JOIN search_index si ON f.id = si.file_id
WHERE f.source_type IN ('filesystem', 'yuque')
  AND si.content MATCH '搜索关键词'
ORDER BY si.score DESC;

-- 获取数据源统计信息
SELECT
    source_type,
    COUNT(*) as total_files,
    SUM(file_size) as total_size,
    COUNT(DISTINCT file_type) as file_types
FROM files
GROUP BY source_type;
```

---

## 6. 数据完整性

### 6.1 约束说明

```sql
-- 检查约束（可选，应用层实现）
-- 确保 source_type 只允许预定义的值

CREATE TRIGGER validate_source_type
BEFORE INSERT ON files
BEGIN
    SELECT CASE
        WHEN NEW.source_type NOT IN (
            'filesystem', 'yuque', 'feishu',
            'notion', 'dingtalk'
        ) THEN
            RAISE(ABORT, 'Invalid source_type')
    END;
END;

-- 默认值触发器
CREATE TRIGGER set_default_source_type
BEFORE INSERT ON files
BEGIN
    UPDATE files SET source_type = 'filesystem'
    WHERE id = NEW.id AND source_type IS NULL;
END;
```

### 6.2 数据一致性检查

```sql
-- 检查是否有孤立的云端文档（缺少source_url）
SELECT id, filename, source_type
FROM files
WHERE source_type != 'filesystem'
  AND (source_url IS NULL OR source_url = '');

-- 检查数据源类型分布
SELECT
    source_type,
    COUNT(*) as count,
    MIN(created_at) as first_added,
    MAX(created_at) as last_added
FROM files
GROUP BY source_type
ORDER BY count DESC;
```

---

## 7. 性能考虑

### 7.1 查询优化建议

1. **使用索引覆盖**
   ```sql
   -- 优化前
   SELECT * FROM files WHERE source_type = 'yuque';

   -- 优化后（只查询需要的字段）
   SELECT id, filename, source_url
   FROM files
   WHERE source_type = 'yuque';
   ```

2. **分区查询**
   ```sql
   -- 分数据源类型查询，减少单次查询范围
   SELECT * FROM files WHERE source_type = 'filesystem';
   SELECT * FROM files WHERE source_type = 'yuque';
   ```

3. **批量操作**
   ```sql
   -- 批量更新数据源类型
   UPDATE files
   SET source_type = 'filesystem'
   WHERE source_type IS NULL;
   ```

### 7.2 存储优化

```sql
-- 查看表大小
SELECT
    name,
    (pgsize * 1.0 / 1024) as size_kb
FROM sqlite_master m
JOIN pragma_table_stats(m.name)
WHERE m.type = 'table'
  AND m.name = 'files';

-- 清理优化
VACUUM files;
ANALYZE files;
```

---

## 8. 更新日志

### v1.3.0 (2026-02-22)
- **插件提供元数据** ✅ 规划中
  - source_type 和 source_url 由插件通过 `get_file_source_info()` 方法提供
  - 实现完全解耦，索引服务无需硬编码提取规则
  - 新增数据源只需实现插件接口

### v1.2.0 (2026-02-22)
- **约定优于配置** ✅ 规划中
  - 移除插件元数据表
  - 移除插件配置表
  - 移除同步记录表
  - 仅修改files表新增数据源字段

### v1.1.0 (2026-02-22)
- **简化插件安装方式** ✅ 规划中
  - 插件安装改为文件复制方式
  - 系统启动时自动扫描插件目录

### v1.0.0 (2026-02-22)
- **插件化架构** ✅ 规划中
  - 新增 plugins 插件元数据表（已废弃）
  - 新增 plugin_configs 插件配置表（已废弃）
  - 新增 datasource_sync_records 数据源同步记录表（已废弃）
  - 完整的索引设计（已废弃）

---

## 9. 安全考虑

### 9.1 敏感数据保护

- **配置文件**：插件配置（API Token等）存储在YAML文件中，需要设置文件权限
- **数据库**：source_url 可能有敏感链接，需要考虑访问控制

### 9.2 权限控制

| 操作 | 权限要求 | 说明 |
|------|---------|------|
| 插件安装 | 文件系统访问 | 将插件文件放到data/plugins/目录 |
| 插件配置 | 文件系统访问 | 编辑config.yaml文件 |
| 数据查询 | 所有用户 | 搜索API返回数据源信息 |
| 数据修改 | 管理员 | 仅管理员可修改索引数据 |

---

**文档版本**: v1.3
**创建时间**: 2026-02-22
**最后更新**: 2026-02-22 (v1.3 - 插件提供元数据)
**文档状态**: 已批准
**维护者**: 开发者

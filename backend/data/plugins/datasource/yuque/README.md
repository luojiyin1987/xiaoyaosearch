# 语雀知识库插件

基于 [yuque-dl](https://github.com/gxr404/yuque-dl) 的语雀知识库数据源插件，用于将语雀文档同步到本地进行索引和搜索。

## 功能特性

- ✅ 支持公开和私有知识库
- ✅ 增量下载（只同步变更的文件）
- ✅ Markdown 格式输出
- ✅ 支持多个知识库配置
- ✅ 自动提取原文链接

## 安装依赖

### 1. 安装 Node.js

下载并安装 Node.js 18.4 或更高版本：
- Windows: https://nodejs.org/
- 验证安装: `node --version`

### 2. 安装 yuque-dl

选择以下任一方式：

**方式 A：使用 npx（推荐）**
```bash
# npx 会自动下载最新版本，无需手动安装
npx yuque-dl --version
```

**方式 B：全局安装**
```bash
npm install -g yuque-dl
yuque-dl --version
```

## 配置说明

编辑 `config.yaml` 文件，配置知识库信息：

```yaml
repos:
  - name: "产品文档"
    url: "https://www.yuque.com/your-org/product-docs"
    download_dir: "./data/product-docs"
    token: ""              # 私有库必填，公开库留空
    ignore_images: false
    incremental: true
```

### 配置项说明

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | 是 | 知识库名称（用于日志） |
| `url` | string | 是 | 语雀知识库 URL |
| `download_dir` | string | 否 | 本地下载目录，默认 `./data/downloaded` |
| `token` | string | 否 | 语雀 API Token（私有库必填） |
| `ignore_images` | boolean | 否 | 是否忽略图片，默认 `false` |
| `incremental` | boolean | 否 | 是否增量下载，默认 `true` |

### 获取语雀 URL

1. 打开语雀知识库主页
2. 复制浏览器地址栏中的 URL

### 获取 API Token（私有库）

1. 访问：https://www.yuque.com/settings/tokens
2. 创建新 Token，勾选"读取"权限
3. 复制 Token 到配置文件

## 使用方法

### 自动同步（推荐）

应用启动时会自动执行同步（如果配置 `PLUGIN_AUTO_SYNC_ON_STARTUP=true`）。

### 手动触发同步

```bash
# 启动应用，插件会自动加载并同步
cd backend
python main.py
```

### 查看同步结果

同步的文档保存在：
```
data/plugins/datasource/yuque/data/{download_dir}/
```

## 添加到索引

同步完成后，通过 API 将插件目录添加到索引：

```bash
# 创建索引任务
curl -X POST http://127.0.0.1:8000/api/index/create \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "data/plugins/datasource/yuque/data/product-docs",
    "recursive": true
  }'
```

## 搜索结果

搜索语雀文档时，结果会包含：

```json
{
  "file_name": "产品需求文档.md",
  "source_type": "yuque",
  "source_url": "https://www.yuque.com/your-org/product-docs/xxx",
  "file_path": "data/plugins/datasource/yuque/data/product-docs/产品需求文档.md"
}
```

点击 `source_url` 可直接跳转到语雀原文。

## 故障排查

### 问题：插件加载失败

**可能原因**：缺少 `plugin.py` 或 `config.yaml` 文件

**解决方法**：检查插件目录结构是否正确

### 问题：yuque-dl 未找到

**可能原因**：Node.js 或 yuque-dl 未安装

**解决方法**：
1. 运行 `node --version` 检查 Node.js 是否安装
2. 运行 `npx yuque-dl --version` 测试 yuque-dl

### 问题：同步失败（401 错误）

**可能原因**：Token 无效或过期

**解决方法**：重新生成 Token 并更新配置

### 问题：下载的文档为空

**可能原因**：知识库 URL 不正确或无访问权限

**解决方法**：
1. 检查 URL 是否正确
2. 确认 Token 有读取权限
3. 在浏览器中测试是否能访问知识库

## 高级配置

### 环境变量配置

可以在 `backend/.env` 中配置：

```bash
# 插件根目录
PLUGIN_PLUGIN_DIR=data/plugins

# 启动时自动同步
PLUGIN_AUTO_SYNC_ON_STARTUP=true

# 同步超时时间（秒）
PLUGIN_SYNC_TIMEOUT=300
```

### 多知识库配置

```yaml
repos:
  - name: "产品文档"
    url: "https://www.yuque.com/your-org/product-docs"
    download_dir: "./data/product-docs"

  - name: "技术文档"
    url: "https://www.yuque.com/your-org/tech-docs"
    download_dir: "./data/tech-docs"

  - name: "设计文档"
    url: "https://www.yuque.com/your-org/design-docs"
    download_dir: "./data/design-docs"
```

## 相关链接

- [yuque-dl 项目](https://github.com/gxr404/yuque-dl)
- [语雀官网](https://www.yuque.com)
- [语雀 Token 管理](https://www.yuque.com/settings/tokens)

# Version Upgrade Guide

This document explains how to upgrade XiaoyaoSearch from an old version to a new version.

## 📋 Upgrade Overview

XiaoyaoSearch uses a **data and program separation** design concept. During upgrade, simply copy the entire `data` directory from the old version to the new version to preserve:

- ✅ Built search indexes (Faiss vector index + Whoosh full-text index)
- ✅ Configuration and index records in the database
- ✅ Downloaded AI models
- ✅ User settings and logs

## 🚀 Upgrade Steps

### Option 1: Package Users (Recommended for Regular Users)

> **Target Users**: Users who deployed using the package
> **Supported Platform**: Windows

#### Upgrade Process

**Step 1: Download the New Version Package**

Download the latest Windows package from Baidu Netdisk:
- Link: https://pan.baidu.com/s/1lDaWjMCRXIT-Sqx9UFjerg?pwd=37ed
- Extraction Code: 37ed

Please download the latest version (e.g., `XiaoyaoSearch-Windows-v1.x.x.zip`)

**Step 2: Extract the New Version**

Extract the downloaded package to any directory (avoid paths with Chinese characters)

**Step 3: Backup and Migrate the data Directory**

Copy the entire `data` directory from the old version (e.g., 1.3.0) to the new version directory and overwrite:

```
Old Version Directory/
├── data/                    # Old version's data directory
│   ├── database/            # SQLite database
│   ├── indexes/             # Search indexes
│   │   ├── faiss/          # Faiss vector index
│   │   └── whoosh/          # Whoosh full-text index
│   ├── models/             # AI model files
│   └── logs/               # Log files
└── ...

⬇️ Copy entire data directory ⬇️

New Version Directory/
├── data/                    # Overwrite with old version data
│   ├── database/
│   ├── indexes/
│   ├── models/
│   └── logs/
├── scripts/
└── ...
```

**Step 4: Reinstall Environment**

Double-click `scripts/setup.bat`. The script will automatically:
- Extract Python embedded runtime
- Install backend Python dependencies
- Install frontend Node dependencies
- Generate configuration files
- Create data directories

> **RTX 50 Series GPU Users**: If you use RTX 50 series GPU, run `scripts/setup_rtx50显卡.bat` instead

**Step 5: Launch the New Version**

Double-click `scripts/startup.bat` to launch the new version

---

### Option 2: Developer Users

> **Target Users**: Users who deployed using developer mode
> **Supported Platforms**: Windows / macOS / Linux

#### Upgrade Process

**Step 1: Backup Data (Recommended but Optional)**

Before upgrading, it's recommended to backup your data directory:

```shell
# Backup data directory
cp -r data data_backup_$(date +%Y%m%d)
```

**Step 2: Update Code**

```shell
# Enter project directory
cd xiaoyaosearch

# Pull latest code
git pull origin main
```

**Step 3: Migrate data Directory**

Keep the old version's `data` directory content, only update program code:

```
xiaoyaosearch/
├── backend/                  # Update to new version code
├── frontend/                 # Update to new version code
├── docs/                    # Update to new version docs
├── data/                    # Keep old version's data directory
│   ├── database/            # SQLite database (keep)
│   ├── indexes/             # Search indexes (keep)
│   │   ├── faiss/          # Faiss vector index (keep)
│   │   └── whoosh/         # Whoosh full-text index (keep)
│   ├── models/             # AI model files (keep)
│   └── logs/               # Log files (keep)
└── ...
```

**Step 4: Update Dependencies**

```shell
# Enter backend directory
cd backend

# Install new Python dependencies (if requirements.txt was updated)
pip install -r requirements.txt
```

**Step 5: Start Services**

```shell
# Start backend service
python main.py

# New terminal: start frontend
cd frontend
npm run dev
```

---

## 📊 data Directory Structure

The following directories and data will be preserved during upgrade:

| Directory | Description | Preserved |
|------|------|----------|
| `data/database/` | SQLite database (contains configuration, index records, etc.) | ✅ Keep |
| `data/indexes/faiss/` | Faiss vector index | ✅ Keep |
| `data/indexes/whoosh/` | Whoosh full-text index | ✅ Keep |
| `data/models/` | AI model files (embedding, speech, vision models) | ✅ Keep |
| `data/logs/` | Log files | ✅ Keep |
| `data/test-data/` | Test data | ✅ Keep |

## ⚠️ Important Notes

1. **Backup Important Data**: It is recommended to backup the `data` directory before upgrading to prevent data loss due to upgrade failures

2. **Version Compatibility**:
   - Cross-major version upgrades (e.g., 1.x to 2.x) may have compatibility issues. Please read the version update notes carefully
   - If you encounter index incompatibility issues, you may need to rebuild the indexes

3. **Model Updates**: If the new version requires different model versions, please re-download the corresponding models

4. **Configuration Files**:
   - Package Users: Configuration files will be automatically generated on first run
   - Developer Users: The `.env` file usually doesn't need changes. If there are updates, they will be noted in the Release notes

5. **Index Rebuild**: If search results are abnormal or indexes are corrupted, you can try deleting and rebuilding indexes in the application settings

## 🔧 FAQ

### Q1: Can't find previously indexed files after upgrade?

**Possible Causes**:
- Index not migrated correctly
- New version index format incompatible

**Solutions**:
1. Confirm `data/indexes/` directory was fully migrated
2. If the problem persists, delete indexes in settings and rebuild

### Q2: Startup fails with missing dependencies?

**Solutions**:
1. Re-run `scripts/setup.bat` (Package Users)
2. Or execute `pip install -r requirements.txt` (Developer Users)

### Q3: How to check current version?

- Package: Check in the "About" page of the application
- Developer: Check version in `backend/main.py` or `frontend/package.json`

---

## 📖 Related Documents

- [Package Deployment Guide](docs/部署文档/整合包部署指南.md)
- [Developer Deployment Guide](../README.md#option-2-developer-deployment)
- [FAQ](../README.md)

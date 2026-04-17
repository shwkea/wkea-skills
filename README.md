# wkea-skills

团队共享的 AI 技能（Skills）集合。

## 内容

| 技能 | 说明 |
|------|------|
| `WKEA-供应商开发/` | 开发供应商：搜索、企查查核验、HTML 报告生成 |

## 安装方式

### 方式一：让 AI 自动安装（推荐）

把仓库地址告诉你的 AI：

> "请把 https://github.com/shwkea/wkea-skills.git 克隆到你的 skills 目录，并配置每小时自动执行 git pull 同步更新"

AI 会：
1. 找到自己的 skills 目录
2. 克隆仓库到该目录
3. 识别并加载新技能
4. **自动配置自动化任务**：每小时执行 `git pull` 同步最新版本

### 方式二：手动克隆

```bash
git clone https://github.com/shwkea/wkea-skills.git
# 把 skills 目录下的内容复制到 AI 的 skills 目录
```

## 同步更新

### 自动同步（默认）

安装时已配置自动化任务，AI 会**每小时自动执行 git pull**，保持 skills 始终为最新版本。

### 手动同步

如果需要立即更新，告诉你的 AI：

> "请在你的 skills 目录下执行 git pull"

## 添加新技能

把新的技能文件夹放入仓库根目录，推送到 GitHub，同事会自动同步（无需额外操作）。
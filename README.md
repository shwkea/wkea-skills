# WKea Skills 技能库

WKea 团队内部共享的 WorkBuddy AI 助手技能包集合。

## 目录结构

```
wkea-skills/
├── 供应商开发/           # 供应商开发技能（品牌型号搜索 → 供应商信息采集 → 生成对比报告）
│   ├── SKILL.md         # 技能定义与执行规范
│   ├── scripts/         # Python 脚本工具
│   └── templates/       # HTML 报告模板
└── README.md
```

## 如何安装技能

### 方式一：AI 自动同步（推荐）

让 AI 执行以下命令即可自动完成全部操作：

```
请帮我把 wkea-skills 仓库（git@github.com:shwkea/wkea-skills.git）克隆到 ~/.workbuddy/skills/ 目录，如果目录已存在则先备份再拉取最新版本。
```

AI 将自动执行：
1. 克隆或拉取仓库最新代码
2. 将技能文件夹复制到 `~/.workbuddy/skills/` 下
3. 重启 WorkBuddy 后即可使用

### 方式二：手动安装

```bash
# 克隆仓库
git clone git@github.com:shwkea/wkea-skills.git ~/wkea-skills-temp

# 复制单个技能到 skills 目录
cp -r ~/wkea-skills-temp/供应商开发 ~/.workbuddy/skills/

# 或复制全部技能
cp -r ~/wkea-skills-temp/* ~/.workbuddy/skills/

# 清理临时目录
rm -rf ~/wkea-skills-temp
```

## 如何更新技能

### 方式一：让 AI 更新（推荐）

```
请帮我把 wkea-skills 仓库拉到最新版本，合并到 ~/.workbuddy/skills/ 下。
```

### 方式二：手动更新

```bash
cd ~/wkea-skills-temp  # 或重新 clone
git pull
cp -r 供应商开发 ~/.workbuddy/skills/
```

## 技能列表

### 供应商开发

**触发词**：开发供应商、找供应商、供应商调研、采集供应商

**功能**：根据产品品牌型号搜索供应商，采集联系方式、价格、风险信息，生成可视化对比报告。

**输出**：`供应商开发_[日期]_[时间戳]_[产品名]/` 文件夹，内含：
- `info.json` - 产品信息
- `suppliers/` - 各供应商详细信息（info.json）
- `execution_log.json` - 执行日志
- `report.html` - 可视化对比报告

## 添加新技能

在仓库根目录新建技能文件夹即可，例如：

```
wkea-skills/
├── 供应商开发/
├── 竞品分析/           ← 新技能
│   ├── SKILL.md
│   ├── scripts/
│   └── templates/
└── README.md
```

## 注意事项

- Skills 安装路径：`~/.workbuddy/skills/`
- 技能目录名即为技能名称，WorkBuddy 通过目录名识别技能
- 请勿在 skills 目录下放置个人文件或敏感信息

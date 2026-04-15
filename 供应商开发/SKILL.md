# 供应商开发技能

## 概述
本技能用于自动化执行供应商开发流程，支持单产品和多产品并发处理。通过全网搜索供应商、按核查清单逐项验证、结构化输出结果（JSON 驱动）。

## 触发条件
当用户提到以下关键词时触发：
- "供应商开发"
- "找供应商"
- "开发供应商"
- 附带产品信息并要求寻找供应商

---

## ⚡ 核心加速原则：AI 只负责"检索 + 提取 + 验证"，写文件全部交给脚本

**禁止 AI 做的事（慢）：**
- ❌ 手动写 JSON 文件（write_to_file）
- ❌ 手动编辑 HTML 报告
- ❌ 手动拼接供应商数据后写进文件

**AI 应该做的事（快）：**
- ✅ 调用 `web_search` 搜索供应商
- ✅ 调用 `web_fetch` 抓取页面、提取数据
- ✅ 从页面内容中提取结构化字段（公司名、联系方式、企查查信息等）
- ✅ 把提取到的数据用 `execute_command` 一行命令传给脚本，脚本写文件
- ✅ 每次操作后调用 `save_execution_log.py` 追加日志条目

**标准节奏（每个供应商）：**
1. 搜索 → `save_execution_log.py search ...`
2. 抓页面 → `save_execution_log.py fetch ...`
3. 企查查核实 → `save_execution_log.py verify ...`
4. 提取全部字段 → `save_supplier.py` 写 info.json
5. `save_execution_log.py save 已保存供应商：XX公司`

---

## 执行流程

### 1. 解析产品信息
- 解析用户提供的产品信息（单个或多个）
- 提取关键搜索关键词
- 识别产品类型和技术规格

### 2. 创建根目录
```
工作区/供应商开发_[日期]_[时间戳]/
```
- 日期格式：YYYYMMDD，时间戳：HHMMSS
- 示例：`供应商开发_20260415_101200/`
- 调用：`python scripts/core/init.py <根目录路径> <产品型号>`

### 3. 并发执行（多产品支持）

**单产品模式：** 直接执行单个产品的完整流程

**多产品模式：**
```
主任务：批量供应商开发
├── 子任务1：产品A 供应商开发
├── 子任务2：产品B 供应商开发
└── ...
```

每个子任务独立执行：
1. 初始化产品文件夹（`init.py`）
2. 保存产品信息（`save_product.py`）
3. 全网搜索供应商并逐个核实
4. 保存每个供应商（`save_supplier.py`）
5. 每步记录日志（`save_execution_log.py`）
6. 汇总并生成 HTML（`collect_suppliers.py` → `generate_html.py`）

### 4. 产品文件夹结构

```
[产品型号]/
├── plan.json                      # 执行计划
├── product.json                   # 产品信息（由 save_product.py 生成）
├── suppliers.json                 # 所有供应商汇总（由 collect_suppliers.py 生成）
├── execution_log.json             # 执行日志（由 save_execution_log.py 追加）
├── 产品资料/
│   ├── 产品图片/
│   └── 产品文件/
├── [公司全称]/                    # 供应商目录（以公司名命名）
│   └── info.json                  # 供应商完整信息
└── report.html                    # HTML 可视化报告
```

### 5. 全网深度搜索供应商

**核心原则：搜索 → 点开核实 → 提取字段 → 立即调脚本写入，不要在内存中缓存后批量写。**

**搜索执行流程：**

1. **第一轮：广泛搜索**
   - 调用 `web_search` 搜索产品关键词（型号、品牌、类型等组合）
   - 搜索授权渠道：品牌 + 代理商 / 经销商 / 授权商
   - 立即调用 `save_execution_log.py search` 记录

2. **第二轮：逐个核实**
   - 每个有效结果都调用 `web_fetch` 打开
   - 提取供应商名、联系方式、价格、货期、授权状态
   - 立即调用 `save_execution_log.py fetch` 记录

3. **第三轮：企查查核实**
   - 搜索"公司名称 企查查"获取工商信息
   - 提取：法人、注册资本、成立日期、经营状态、行政处罚、诉讼、失信、股东、知识产权
   - 把全部字段一并打包，调用 `save_supplier.py` 写 info.json
   - 立即调用 `save_execution_log.py verify` 记录

**必须获取的产品字段：**
- 基本属性：产品名称、品牌、型号、类型、分类
- 技术参数（用 key-value 对填入 `specs`）：尺寸、重量、功率、电压、电流、压力、流量、温度范围、材质、防护等级等
- 认证信息：CE、RoHS、UL、CCC、ISO 等（填入 `certifications` 数组）
- 应用范围：`applications` 字段
- 产品图片：至少 3 张（下载到 `产品资料/产品图片/`）
- 产品文件：Datasheet、说明书、3D 模型等（下载到 `产品资料/产品文件/`）
- 来源网址：至少 3 个

**必须获取的供应商字段（全部通过 save_supplier.py 写入）：**

基本：name, short_name, source, source_urls, discovery_url, official_url, qcc_url
授权 & 交易：is_authorized, authorization_cert, price, price_range, moq, delivery, stock_status, payment
联系：contact.name, contact.title, contact.phone, contact.mobile, contact.email, contact.wechat, contact.qq, contact.address, contact.city, contact.website
企查查：qcc_info.full_name, qcc_info.credit_code, qcc_info.legal_person, qcc_info.registered_capital, qcc_info.paid_capital, qcc_info.established_date, qcc_info.business_status, qcc_info.business_scope, qcc_info.registered_address, qcc_info.org_type, qcc_info.industry, qcc_info.annual_revenue, qcc_info.employee_count
风险：qcc_info.penalty_count, qcc_info.lawsuit_count, qcc_info.dishonesty_count, qcc_info.abnormal_status, qcc_info.abnormal_reason, qcc_info.risk_info
股东：qcc_info.shareholders（数组，每项含 name/ratio）, qcc_info.actual_controller
知识产权：qcc_info.patent_count, qcc_info.trademark_count, qcc_info.software_copyright_count
资质：qcc_info.certifications（数组）, qcc_info.honors（数组）
经营：main_products, business_years, service_policy, after_sale
评估：notes, risk_level（低风险/中风险/高风险）, recommendation（推荐/待核实/不推荐）

**搜索渠道（参考）：**

| 渠道类型 | 用途 |
|---------|------|
| 百度/Google/Bing | 广泛搜索，发现供应商 |
| 1688、淘宝、京东、震坤行、米思米 | 价格、货期、产品图片 |
| 品牌官网 | 授权经销商列表、产品资料 |
| 企查查、天眼查、国家企业信用信息公示系统 | 企业资质、风险、股东 |
| 智能制造网、机电之家、化工仪器网等 | 行业供应商发现 |

**执行要求：**
- 每个产品至少收集 5 家供应商信息
- 每个供应商至少核实 3 个来源网址
- 每个产品至少下载 3 张图片
- 所有字段必须从真实网页提取，不得虚构

---

## 脚本调用总表

AI 只调脚本，不手动写文件。所有脚本均位于技能目录 `scripts/` 下。

| 脚本路径 | 用途 | 关键参数 |
|---------|------|---------|
| `scripts/core/init.py` | 初始化文件夹结构 | `<根目录> <产品型号>` |
| `scripts/core/update_plan.py` | 更新执行计划进度 | `<产品目录> <步骤> <状态>` |
| `scripts/data/save_product.py` | 保存产品信息到 product.json | `<产品目录> <JSON字符串>` |
| `scripts/data/save_supplier.py` | 保存供应商信息到 info.json | `<产品目录> <JSON字符串>` |
| `scripts/data/save_execution_log.py` | 追加日志条目 | `<产品目录> <类型> <消息> [URL]` |
| `scripts/data/collect_suppliers.py` | 汇总所有 info.json → suppliers.json | `<产品目录>` |
| `scripts/data/export_excel.py` | 导出 Excel | `<产品目录>` |
| `scripts/report/generate_html.py` | 生成 HTML 报告 | `<产品目录或根目录>` |

### save_execution_log.py 操作类型说明

| 类型 | 含义 | 何时调用 |
|------|------|---------|
| `search` | 搜索操作 | 每次调用 web_search 后 |
| `fetch` | 抓取网页 | 每次调用 web_fetch 后 |
| `verify` | 核查供应商（企查查） | 完成企查查核查后 |
| `download` | 下载文件/图片 | 成功下载文件后 |
| `save` | 保存数据 | 调用 save_*.py 成功后 |
| `note` | 备注 | 策略调整、发现特殊情况 |
| `error` | 错误 | 网页抓取失败、信息缺失 |
| `result` | 阶段结论 | 每个供应商核查完毕 |

### 生成 HTML 报告（必须按顺序）
```bash
# 步骤1：汇总供应商数据
python scripts/data/collect_suppliers.py <产品文件夹绝对路径>

# 步骤2：生成报告
python scripts/report/generate_html.py <产品文件夹绝对路径>
```

---

## 产品信息结构（save_product.py 接受的 JSON）

```json
{
  "name": "产品名称",
  "brand": "品牌",
  "model": "型号",
  "type": "类型",
  "specs": {
    "接口尺寸": "PT1/4",
    "工作压力": "0.1~1.0MPa",
    "温度范围": "-5~70°C",
    "防护等级": "IP65"
  },
  "certifications": ["CE", "RoHS"],
  "applications": "适用于气动系统过滤调压",
  "source_urls": ["https://...", "https://..."],
  "images": ["image1.jpg", "image2.jpg"],
  "files": ["datasheet.pdf"]
}
```

## 供应商信息结构（save_supplier.py 接受的 JSON）

```json
{
  "name": "上海XX自动化设备有限公司",
  "short_name": "XX自动化",
  "source": "1688",
  "source_urls": ["https://...", "https://...", "https://..."],
  "discovery_url": "https://发现该供应商的页面",
  "official_url": "https://供应商官网",
  "qcc_url": "https://企查查页面",
  "is_authorized": true,
  "authorization_cert": "SMC授权经销商证书（2025年）",
  "price": "¥320/个",
  "price_range": "1-9个¥350，10个以上¥320",
  "moq": "1个",
  "delivery": "现货，1-3天发货",
  "stock_status": "现货",
  "payment": "支付宝/微信/对公转账",
  "contact": {
    "name": "张经理",
    "title": "销售经理",
    "phone": "021-12345678",
    "mobile": "138xxxxxxxx",
    "email": "sales@example.com",
    "wechat": "wxid_xxx",
    "address": "上海市嘉定区XX路100号",
    "city": "上海",
    "website": "https://www.example.com"
  },
  "qcc_info": {
    "full_name": "上海XX自动化设备有限公司",
    "credit_code": "91310000XXXXXXXXXX",
    "legal_person": "王XX",
    "registered_capital": "500万人民币",
    "paid_capital": "500万人民币",
    "established_date": "2010-05-12",
    "business_status": "存续",
    "business_scope": "气动元件、自动化设备销售...",
    "registered_address": "上海市嘉定区XX路100号",
    "org_type": "有限责任公司",
    "industry": "机械设备",
    "annual_revenue": "2000万",
    "employee_count": "50人",
    "risk_info": "无风险",
    "penalty_count": 0,
    "lawsuit_count": 0,
    "dishonesty_count": 0,
    "abnormal_status": false,
    "shareholders": [{"name": "王XX", "ratio": "60%"}, {"name": "李XX", "ratio": "40%"}],
    "actual_controller": "王XX",
    "patent_count": 3,
    "trademark_count": 1,
    "certifications": ["ISO9001"],
    "honors": ["专精特新"]
  },
  "main_products": "SMC、CKD、FESTO等品牌气动元件",
  "business_years": "15年",
  "service_policy": "质保一年，支持退换货",
  "after_sale": "7×24技术支持",
  "notes": "SMC授权华东区总代，库存充足",
  "risk_level": "低风险",
  "recommendation": "推荐"
}
```

---

## HTML 报告说明

模板：`scripts/report/templates/report.html`（统一模板，支持单/多产品）

报告展示内容（全面升级）：
- **产品侧栏（左）**：品牌型号、技术规格参数表、产品认证标签、产品图片、来源网址
- **供应商卡片（右，横向滑动）**：每家供应商一张卡片，展示：
  - 💰 交易信息：价格/价格区间、货期、库存状态、最小起订量、结算方式、授权证书
  - 📞 联系方式：联系人（职位）、电话、手机、邮箱、微信、QQ、传真、地址
  - 🏢 工商信息（企查查）：工商全称、统一信用代码、法人、注册资本/实缴、成立日期、经营状态、企业类型、行业、年营业额、员工人数、实际控制人、注册地址、经营范围
  - ⚠️ 风险信息：行政处罚/诉讼/失信/经营异常次数指示灯
  - 👥 股东信息：主要股东及持股比例
  - 🎖 资质知识产权：专利/商标/软著数量，认证标签
  - 📦 经营能力：主营产品、经营年限、服务政策
  - 🔗 来源链接：发现来源、供应商官网、企查查页面

**禁止直接写 HTML 代码，禁止使用 fetch() 读取本地 JSON，必须调用 generate_html.py 生成。**

---

## 注意事项
1. 每次执行创建时间戳根目录，避免冲突
2. 所有数据用 JSON 存储，便于后续处理
3. 供应商文件夹以**公司全称**命名（不加"供应商A_"前缀）
4. `collect_suppliers.py` 会扫描所有含 `info.json` 的子文件夹（不限制前缀）
5. 产品图片必须在 HTML 报告中展示
6. specs 字段必须是 key-value 对象，不要用字符串
7. 执行日志每步操作都要记录，方便追溯

---

## 踩坑经验

（以下由 AI 在实际调用中自动积累，请勿手动删除）

- save_product.py / save_supplier.py / Windows PowerShell：无法通过 argv 直接传 JSON 字符串（引号被 shell 解析），必须先写临时 `_tmp_xxx.json` 文件，再用 `--file <路径>` 参数传入。两个脚本已支持 `--file` 参数。
- init.py：第二个参数是产品数量（int），不是产品型号。产品型号是第一个参数，数量是可选的第二个参数。
- generate_html.py：默认只透传少量供应商字段，已升级为 `dict(s)` 完整透传，产品信息也增加了 specs/certifications/applications/category 字段透传。

import os
import sys
import json
from datetime import datetime

def save_supplier(workspace_path, supplier_data):
    """保存供应商信息（完整版：含企查查、联系方式、价格货期、来源网址、风险等全字段）"""
    
    supplier_name = supplier_data.get("name", "未知供应商")
    supplier_dir = os.path.join(workspace_path, supplier_name)
    os.makedirs(supplier_dir, exist_ok=True)
    
    contact = supplier_data.get("contact", {})
    qcc = supplier_data.get("qcc_info", {})
    
    supplier_json = {
        # ── 基本信息 ──
        "name": supplier_data.get("name", ""),
        "short_name": supplier_data.get("short_name", ""),          # 简称
        "source": supplier_data.get("source", ""),                  # 来源渠道（1688 / 企业官网 / 震坤行 ...）
        "source_urls": supplier_data.get("source_urls", []),        # [发现URL, 公司页URL, 企查查URL ...]
        "discovery_url": supplier_data.get("discovery_url", ""),    # 发现该供应商的页面
        "official_url": supplier_data.get("official_url", ""),      # 供应商官网
        "qcc_url": supplier_data.get("qcc_url", ""),                # 企查查页面链接

        # ── 授权 & 交易信息 ──
        "is_authorized": supplier_data.get("is_authorized", False),
        "authorization_cert": supplier_data.get("authorization_cert", ""),  # 授权证书说明
        "price": supplier_data.get("price", ""),
        "price_range": supplier_data.get("price_range", ""),        # 如 "50-80元/个（阶梯）"
        "moq": supplier_data.get("moq", ""),                        # 最小起订量
        "delivery": supplier_data.get("delivery", ""),
        "stock_status": supplier_data.get("stock_status", ""),      # 现货/期货/需订货
        "payment": supplier_data.get("payment", ""),                # 款到发货/月结/账期

        # ── 联系方式 ──
        "contact": {
            "name": contact.get("name", ""),
            "title": contact.get("title", ""),          # 职位
            "phone": contact.get("phone", ""),
            "mobile": contact.get("mobile", ""),
            "email": contact.get("email", ""),
            "wechat": contact.get("wechat", ""),
            "qq": contact.get("qq", ""),
            "fax": contact.get("fax", ""),
            "address": contact.get("address", ""),
            "city": contact.get("city", ""),            # 城市
            "website": contact.get("website", "")
        },

        # ── 企查查信息（工商） ──
        "qcc_info": {
            "full_name": qcc.get("full_name", ""),                  # 工商全称
            "credit_code": qcc.get("credit_code", ""),              # 统一社会信用代码
            "legal_person": qcc.get("legal_person", ""),            # 法人代表
            "registered_capital": qcc.get("registered_capital", ""), # 注册资本
            "paid_capital": qcc.get("paid_capital", ""),            # 实缴资本
            "established_date": qcc.get("established_date", ""),    # 成立日期
            "business_status": qcc.get("business_status", ""),      # 存续/注销/吊销
            "business_scope": qcc.get("business_scope", ""),        # 经营范围
            "registered_address": qcc.get("registered_address", ""), # 注册地址
            "org_type": qcc.get("org_type", ""),                    # 企业类型（有限公司/股份公司）
            "industry": qcc.get("industry", ""),                    # 所属行业
            "annual_revenue": qcc.get("annual_revenue", ""),        # 年营业额
            "employee_count": qcc.get("employee_count", ""),        # 员工人数
            # 风险信息
            "risk_info": qcc.get("risk_info", ""),                  # 综合风险描述
            "penalty_count": qcc.get("penalty_count", 0),           # 行政处罚次数
            "lawsuit_count": qcc.get("lawsuit_count", 0),           # 法律诉讼次数
            "dishonesty_count": qcc.get("dishonesty_count", 0),     # 失信记录次数
            "abnormal_status": qcc.get("abnormal_status", False),   # 是否经营异常
            "abnormal_reason": qcc.get("abnormal_reason", ""),      # 异常原因
            # 股东信息
            "shareholders": qcc.get("shareholders", []),            # [{name, ratio, amount}]
            "actual_controller": qcc.get("actual_controller", ""),  # 实际控制人
            # 对外投资
            "investments": qcc.get("investments", []),              # [{name, ratio}]
            # 知识产权
            "patent_count": qcc.get("patent_count", 0),             # 专利数量
            "trademark_count": qcc.get("trademark_count", 0),       # 商标数量
            "software_copyright_count": qcc.get("software_copyright_count", 0), # 软著数量
            # 资质认证
            "certifications": qcc.get("certifications", []),        # ["ISO9001", "高新技术企业", ...]
            "honors": qcc.get("honors", [])                         # ["专精特新", "AAA信用"]
        },

        # ── 经营能力 ──
        "main_products": supplier_data.get("main_products", ""),    # 主营产品
        "business_years": supplier_data.get("business_years", ""),  # 经营年限
        "service_policy": supplier_data.get("service_policy", ""),  # 服务政策（质保/退换货）
        "after_sale": supplier_data.get("after_sale", ""),          # 售后支持

        # ── 评估结论 ──
        "notes": supplier_data.get("notes", ""),
        "risk_level": supplier_data.get("risk_level", ""),          # 低风险/中风险/高风险
        "recommendation": supplier_data.get("recommendation", ""),  # 推荐/待核实/不推荐
        "verification_status": supplier_data.get("verification_status", "unverified"),

        "created_at": datetime.now().isoformat()
    }
    
    supplier_json_path = os.path.join(supplier_dir, "info.json")
    with open(supplier_json_path, "w", encoding="utf-8") as f:
        json.dump(supplier_json, f, ensure_ascii=False, indent=2)
    
    print(json.dumps({"status": "success", "path": supplier_json_path}, ensure_ascii=False))
    return supplier_json_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python save_supplier.py <工作目录> <供应商JSON数据或--file 路径>")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    # 支持 --file 参数（解决 Windows PowerShell 引号问题）
    if sys.argv[2] == "--file":
        with open(sys.argv[3], encoding="utf-8") as f:
            supplier_data = json.load(f)
    else:
        supplier_data = json.loads(sys.argv[2])
    save_supplier(workspace_path, supplier_data)
